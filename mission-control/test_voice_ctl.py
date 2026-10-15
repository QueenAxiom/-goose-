import unittest
from unittest import mock

from voice_ctl import VoiceProcess


def fake_proc(alive=True):
    p = mock.Mock()
    p.poll.return_value = None if alive else 0
    return p


class VoiceProcessTests(unittest.TestCase):
    def test_start_launches_once(self):
        popen = mock.Mock(return_value=fake_proc())
        v = VoiceProcess(popen=popen)
        self.assertTrue(v.start())
        self.assertFalse(v.start())  # already running
        self.assertEqual(popen.call_count, 1)
        self.assertTrue(v.running())

    def test_stop_terminates_and_clears(self):
        proc = fake_proc()
        v = VoiceProcess(popen=mock.Mock(return_value=proc))
        v.start()
        self.assertTrue(v.stop())
        proc.terminate.assert_called_once()
        proc.poll.return_value = 0
        self.assertFalse(v.running())

    def test_stop_when_not_running_is_false(self):
        self.assertFalse(VoiceProcess(popen=mock.Mock()).stop())

    def test_restart_after_process_died(self):
        popen = mock.Mock(side_effect=[fake_proc(alive=False), fake_proc()])
        v = VoiceProcess(popen=popen)
        v.start()
        self.assertFalse(v.running())
        self.assertTrue(v.start())

    def test_start_failure_reports_false_without_raising(self):
        v = VoiceProcess(popen=mock.Mock(side_effect=OSError("boom")))
        self.assertFalse(v.start())


if __name__ == "__main__":
    unittest.main()
