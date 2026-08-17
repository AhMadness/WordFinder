import unittest

from wordfinder_core import find_matching_segments, format_segment_timestamp, format_timestamp


class TimestampTests(unittest.TestCase):
    def test_formats_sub_hour_timestamp(self):
        self.assertEqual(format_timestamp(65.432), "01:05.432")
        self.assertEqual(format_segment_timestamp(65.432), "01:05")

    def test_formats_timestamp_with_hours(self):
        self.assertEqual(format_segment_timestamp(3661.9), "01:01:01")

    def test_rejects_negative_timestamps(self):
        with self.assertRaises(ValueError):
            format_timestamp(-1)


class MatchingTests(unittest.TestCase):
    def test_matches_terms_case_insensitively(self):
        segments = [
            {"start": 2.1, "text": " First important update "},
            {"start": 70, "text": "Nothing relevant here"},
            {"start": 3605, "text": "GENERAL status report"},
        ]

        self.assertEqual(
            find_matching_segments(segments, ["important", "general"]),
            [
                "00:02 - First important update\n\n",
                "01:00:05 - GENERAL status report\n\n",
            ],
        )

    def test_ignores_blank_terms(self):
        self.assertEqual(
            find_matching_segments([{"start": 0, "text": "anything"}], ["", "  "]),
            [],
        )


if __name__ == "__main__":
    unittest.main()
