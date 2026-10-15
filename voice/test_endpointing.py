import unittest

from endpointing import Endpointer, noise_floor, threshold_for


class ThresholdTests(unittest.TestCase):
    def test_quiet_room_uses_minimum_threshold(self):
        self.assertEqual(threshold_for(50), 400)

    def test_noisy_room_raises_threshold_above_noise(self):
        self.assertGreater(threshold_for(800), 800)

    def test_noise_floor_ignores_loud_bursts(self):
        samples = [100] * 40 + [3000] * 10  # mostly quiet with speech-like bursts
        self.assertLess(noise_floor(samples), 200)

    def test_noise_floor_of_nothing_is_zero(self):
        self.assertEqual(noise_floor([]), 0)


class EndpointerTests(unittest.TestCase):
    def feed(self, ep, levels):
        state = None
        for lvl in levels:
            state = ep.feed(lvl)
            if state == "done":
                break
        return state

    def test_waits_through_initial_silence_then_records_speech(self):
        ep = Endpointer(threshold=500, end_quiet=5, onset_limit=20, max_chunks=100)
        self.assertEqual(self.feed(ep, [50] * 8 + [2000] * 5), "speaking")

    def test_ends_after_quiet_following_speech(self):
        ep = Endpointer(threshold=500, end_quiet=5, onset_limit=20, max_chunks=100)
        self.assertEqual(self.feed(ep, [2000] * 5 + [50] * 5), "done")
        self.assertTrue(ep.heard_speech)

    def test_short_pause_inside_speech_does_not_end_it(self):
        ep = Endpointer(threshold=500, end_quiet=5, onset_limit=20, max_chunks=100)
        self.assertEqual(self.feed(ep, [2000] * 5 + [50] * 3 + [2000] * 5), "speaking")

    def test_gives_up_when_nobody_speaks(self):
        ep = Endpointer(threshold=500, end_quiet=5, onset_limit=10, max_chunks=100)
        self.assertEqual(self.feed(ep, [50] * 12), "done")
        self.assertFalse(ep.heard_speech)

    def test_hard_cap_ends_endless_noise(self):
        ep = Endpointer(threshold=500, end_quiet=5, onset_limit=10, max_chunks=30)
        self.assertEqual(self.feed(ep, [2000] * 40), "done")


if __name__ == "__main__":
    unittest.main()
