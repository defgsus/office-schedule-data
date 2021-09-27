import unittest

from src.data import *
from src.metrics_calc import TimespanChecker, calc_metrics


class TestMetrics(unittest.TestCase):

    def assertTimespan(self, ts: str, d1: str, d2: str, expect: bool = True):
        checker = TimespanChecker()
        in_timespan = checker.is_in_timespan(ts, d1, d2)
        self.assertEqual(
            expect, in_timespan,
            f"Expected '{expect}' for timespan check {ts}: {d1} {d2}"
        )

    def test_timespan_distance(self):
        self.assertTimespan("0h", "2000-01-01 00:00:00", "2000-01-01 00:59:59", True)
        self.assertTimespan("0h", "2000-01-01 00:40:00", "2000-01-01 00:59:59", True)
        self.assertTimespan("0h", "2000-01-01 00:30:00", "2000-01-01 01:00:00", False)
        self.assertTimespan("0h", "2000-01-01 00:30:00", "2000-01-01 01:30:00", False)

        self.assertTimespan("1h", "2000-01-01 00:00:00", "2000-01-01 00:59:59", False)
        self.assertTimespan("1h", "2000-01-01 00:40:00", "2000-01-01 00:59:59", False)
        self.assertTimespan("1h", "2000-01-01 00:30:00", "2000-01-01 01:00:00", True)
        self.assertTimespan("1h", "2000-01-01 00:30:00", "2000-01-01 01:30:00", True)
        self.assertTimespan("0h", "2000-01-01 00:30:00", "2000-01-01 02:00:00", False)

        self.assertTimespan("0d", "2000-01-01 00:40:00", "2000-01-01 23:59:59", True)
        self.assertTimespan("0d", "2000-01-01 00:30:00", "2000-01-02 00:00:00", False)
        self.assertTimespan("1d", "2000-01-01 00:30:00", "2000-01-02 00:00:00", True)

        # 1999-12-27 / 2000-01-03 is a monday

        self.assertTimespan("0w", "1999-12-27 00:00:00", "2000-01-02 23:59:59", True)
        self.assertTimespan("0w", "2000-01-01 00:00:00", "2000-01-02 23:59:59", True)
        self.assertTimespan("1w", "2000-01-01 00:00:00", "2000-01-03 00:00:00", True)

    def X_test_metrics(self):
        # something that does not exist returns None
        df = Metrics.dataframe("appointments", iso_week_lte=(2000, 1))
        self.assertIsNone(df)

        df = Metrics.dataframe(
            #"appointments",
            iso_week=(2021, 28),
        )
        print(df)


if __name__ == "__main__":
    unittest.main()
