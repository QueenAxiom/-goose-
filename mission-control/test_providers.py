import json
import unittest
from unittest import mock

import chat
import providers


class FakeResponse:
    def __init__(self, payload):
        self._body = json.dumps(payload).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def openai_style(text):
    return FakeResponse({"choices": [{"message": {"content": text}}]})


def anthropic_style(text):
    return FakeResponse({"content": [{"type": "text", "text": text}]})


class ConfiguredTests(unittest.TestCase):
    def test_configured_only_when_key_present(self):
        self.assertTrue(providers.configured("gpt", {"OPENAI_API_KEY": "k"}))
        self.assertFalse(providers.configured("gpt", {}))
        self.assertFalse(providers.configured("gpt", {"OPENAI_API_KEY": "  "}))

    def test_each_model_channel_has_its_own_key_name(self):
        keys = {providers.PROVIDERS[c]["env_key"] for c in chat.MODEL_CHANNELS}
        self.assertEqual(keys, {"OPENAI_API_KEY", "DEEPSEEK_API_KEY", "ANTHROPIC_API_KEY"})


class AskTests(unittest.TestCase):
    def test_missing_key_returns_setup_message_without_network(self):
        with mock.patch("providers.urllib.request.urlopen") as net:
            ok, msg = providers.ask("gpt", "hi", {})
        net.assert_not_called()
        self.assertFalse(ok)
        self.assertIn("OPENAI_API_KEY", msg)
        self.assertIn(".env", msg)

    def test_openai_compatible_providers_send_bearer_and_parse_choices(self):
        for channel, key in (("gpt", "OPENAI_API_KEY"), ("deepseek", "DEEPSEEK_API_KEY")):
            with self.subTest(channel=channel), mock.patch("providers.urllib.request.urlopen", return_value=openai_style("hello")) as net:
                ok, reply = providers.ask(channel, "hi", {key: "secret"})
            self.assertEqual((ok, reply), (True, "hello"))
            req = net.call_args.args[0]
            self.assertEqual(req.get_header("Authorization"), "Bearer secret")
            self.assertEqual(json.loads(req.data)["messages"][-1], {"role": "user", "content": "hi"})

    def test_claude_uses_anthropic_headers_and_parses_content(self):
        with mock.patch("providers.urllib.request.urlopen", return_value=anthropic_style("hey")) as net:
            ok, reply = providers.ask("claude", "hi", {"ANTHROPIC_API_KEY": "secret"})
        self.assertEqual((ok, reply), (True, "hey"))
        req = net.call_args.args[0]
        self.assertEqual(req.get_header("X-api-key"), "secret")
        self.assertTrue(req.get_header("Anthropic-version"))
        self.assertEqual(json.loads(req.data)["messages"], [{"role": "user", "content": "hi"}])

    def test_model_can_be_overridden_from_env(self):
        env = {"OPENAI_API_KEY": "k", "MC_GPT_MODEL": "my-model"}
        with mock.patch("providers.urllib.request.urlopen", return_value=openai_style("x")) as net:
            providers.ask("gpt", "hi", env)
        self.assertEqual(json.loads(net.call_args.args[0].data)["model"], "my-model")

    def test_network_failure_returns_fixed_message_without_leaking_key(self):
        with mock.patch("providers.urllib.request.urlopen", side_effect=OSError("boom secret-key")):
            ok, msg = providers.ask("gpt", "hi", {"OPENAI_API_KEY": "secret-key"})
        self.assertFalse(ok)
        self.assertNotIn("secret-key", msg)

    def test_unexpected_payload_is_an_error_not_a_crash(self):
        with mock.patch("providers.urllib.request.urlopen", return_value=FakeResponse({"oops": 1})):
            ok, _ = providers.ask("gpt", "hi", {"OPENAI_API_KEY": "k"})
        self.assertFalse(ok)


class ChatChannelTests(unittest.TestCase):
    def test_all_five_channels_exist_with_names(self):
        self.assertEqual(set(chat.CHANNELS), {"ecc", "axiom", "gpt", "deepseek", "claude"})
        self.assertEqual(chat.NAMES["gpt"], "GPT")
        self.assertEqual(chat.NAMES["deepseek"], "DeepSeek")

    def test_model_prompt_names_assistant_and_puts_message_last(self):
        history = [{"role": "user", "text": "earlier"}, {"role": "assistant", "text": "answer"}]
        prompt = chat.build_chat_prompt("claude", history, "new question", "persona")
        self.assertIn("Claude", prompt)
        self.assertIn("Alan: earlier", prompt)
        self.assertIn("Claude: answer", prompt)
        self.assertTrue(prompt.endswith("Alan: new question"))


if __name__ == "__main__":
    unittest.main()
