from functools import partial
from tqdm import tqdm

from src.data import *


METRIC_TIMESPANS = (
    "0h", "1h", "2h", "3h", "4h",
    "0d", "1d", "2d", "3d", "4d",
    "0w", "1w", "2w", "3w", "4w",
)


class TimespanChecker:
    def __init__(self):
        self.ts_conv_funcs = {}
        self.ts_check_funcs = {}
        for ts in METRIC_TIMESPANS:
            value = int(ts[:-1])

            if ts.endswith("h"):
                func = partial(self.quant_hour, 1)
            elif ts.endswith("d"):
                func = self.quant_day
            elif ts.endswith("w"):
                func = self.quant_week
            else:
                raise ValueError(f"Invalid timestamp {ts}")

            self.ts_conv_funcs[ts] = func

            if ts.endswith("h"):
                func = partial(self.distance_hour, value)
            elif ts.endswith("d"):
                func = partial(self.distance_day, value)
            elif ts.endswith("w"):
                func = partial(self.distance_day, value * 7)

            self.ts_check_funcs[ts] = func

        # mapping of timespan-str -> {datetime-str: quantized-datetime}
        self.dates_ts_str_dt = {
            ts: {}
            for ts in METRIC_TIMESPANS
        }

    def test_date(self, d1: str, d2: str) -> Dict[str, int]:
        ret = dict()
        for ts in METRIC_TIMESPANS:
            if self.is_in_timespan(ts, d1, d2):
                ret[ts] = 1
        return ret

    def test_row(self, d1: str, dates: List[str], is_free: List) -> Dict[str, int]:
        ret = {ts: 0 for ts in METRIC_TIMESPANS}
        for i, (d2, free) in enumerate(zip(dates, is_free)):
            if free:
                for ts in METRIC_TIMESPANS:
                    if self.is_in_timespan(ts, d1, d2):
                        ret[ts] = ret[ts] + 1

        return ret

    def is_in_timespan(self, ts: str, d1: str, d2: str) -> bool:
        date1 = self.get_comparison_date(ts, d1)
        date2 = self.get_comparison_date(ts, d2)
        return self.ts_check_funcs[ts](date1, date2)

    def get_comparison_date(self, ts: str, d: str) -> datetime.datetime:
        mapping = self.dates_ts_str_dt[ts]
        if d not in mapping:
            dt = to_datetime(d)
            if ts in self.ts_conv_funcs:
                dt = self.ts_conv_funcs[ts](dt)
            mapping[d] = dt
        return mapping[d]

    @classmethod
    def quant_hour(cls, hour: int, d: datetime.datetime):
        return d.replace(hour=d.hour // max(1, hour) * hour, minute=0, second=0, microsecond=0)

    @classmethod
    def quant_day(cls, d: datetime.datetime):
        return d.replace(hour=0, minute=0, second=0, microsecond=0)

    @classmethod
    def quant_week(cls, d: datetime.datetime):
        d = d.replace(hour=0, minute=0, second=0, microsecond=0)
        return d - datetime.timedelta(days=d.isoweekday() - 1)

    @classmethod
    def distance_hour(cls, hour: int, d1: datetime.datetime, d2: datetime.datetime):
        hours = (d2 - d1).total_seconds() // 60 // 60
        return hours == hour

    @classmethod
    def distance_day(cls, day: int, d1: datetime.datetime, d2: datetime.datetime):
        days = (d2 - d1).total_seconds() // 60 // 60 // 24
        return days == day


def calc_metrics(
        data: Data,
        stash: Optional[dict] = None
) -> Dict[str, pd.DataFrame]:

    print(f"calculating metrics for {data}")

    if stash is None:
        stash = dict()

    cur_free_dates = stash.get("free_dates") or dict()
    cur_appointed_dates = stash.get("appointed_dates") or dict()
    previous_timestamps = stash.get("previous_timestamps") or dict()
    previous_rows = stash.get("previous_rows") or dict()

    metrics = {
        "changed": dict(),
        "appointments": dict(),
        "cancellations": dict(),
        "free_dates": dict(),
        **{
            f"free_dates_{ts}": dict()
            for ts in METRIC_TIMESPANS
        },
        **{
            f"appointments_{ts}": dict()
            for ts in METRIC_TIMESPANS
        },
        **{
            f"cancellations_{ts}": dict()
            for ts in METRIC_TIMESPANS
        },
    }

    for week, source_id, columns, rows in tqdm(data.iter_tables()):
        dates = columns[3:]
        # dates_dt = [to_datetime(d) for d in dates]
        timespan_checker = TimespanChecker()

        for org_row in tqdm(rows):
            timestamp = org_row[0]
            timestamp_dt = to_datetime(timestamp)
            # bucket into exact 15 minute steps
            timestamp_dt = timestamp_dt.replace(minute=timestamp_dt.minute // 15 * 15, second=0, microsecond=0)
            timestamp = str(timestamp_dt)

            loc_id = f"{source_id}/{org_row[2]}"
            date_row = org_row[3:]

            # record appointments/cancellations only between snapshots
            #   that are at most 16 minutes apart
            if loc_id not in previous_timestamps:
                do_calc_booking = False
            else:
                diff = timestamp_dt - previous_timestamps[loc_id]
                do_calc_booking = diff.total_seconds() < 16 * 60
            previous_timestamps[loc_id] = timestamp_dt

            if loc_id not in cur_free_dates:
                cur_free_dates[loc_id] = set()
            if loc_id not in cur_appointed_dates:
                cur_appointed_dates[loc_id] = set()

            # gather these values for current date-row
            num_appointments = 0
            num_cancellations = 0
            num_free_dates = 0
            num_free_dates_ts = timespan_checker.test_row(timestamp, dates, date_row)
            num_appointments_ts = dict()
            num_cancellations_ts = dict()

            for i, v in enumerate(date_row):
                date = dates[i]

                if v:
                    cur_free_dates[loc_id].add(date)
                    num_free_dates += 1

                    if date in cur_appointed_dates[loc_id]:
                        cur_appointed_dates[loc_id].remove(date)
                        if do_calc_booking:
                            num_cancellations += 1
                            num_cancellations_ts = {
                                ts: num_cancellations_ts.get(ts, 0) + v
                                for ts, v in timespan_checker.test_date(timestamp, date).items()
                            }
                else:
                    if date in cur_free_dates[loc_id]:
                        # do not count the first "appointed" date
                        #   because it might just have disappeared in time
                        if do_calc_booking:
                            if date != min(*cur_free_dates[loc_id]) and date != max(*cur_free_dates[loc_id]):
                                num_appointments += 1
                                num_appointments_ts = {
                                    ts: num_appointments_ts.get(ts, 0) + v
                                    for ts, v in timespan_checker.test_date(timestamp, date).items()
                                }

                        cur_free_dates[loc_id].remove(date)
                        cur_appointed_dates[loc_id].add(date)

            # 0: date-row similar, 1: date-row changed
            row_changed = 0
            if previous_rows.get(loc_id):
                if date_row != previous_rows[loc_id]:
                    row_changed = 1
            previous_rows[loc_id] = date_row

            for buckets, value in (
                    (metrics["changed"], row_changed),
                    (metrics["appointments"], num_appointments),
                    (metrics["cancellations"], num_cancellations),
                    (metrics["free_dates"], num_free_dates),
            ) + tuple(
                    (metrics[f"free_dates_{ts}"], num_free_dates_ts.get(ts, 0))
                    for ts in METRIC_TIMESPANS
            ) + tuple(
                (metrics[f"appointments_{ts}"], num_appointments_ts.get(ts, 0))
                for ts in METRIC_TIMESPANS
            ) + tuple(
                (metrics[f"cancellations_{ts}"], num_appointments_ts.get(ts, 0))
                for ts in METRIC_TIMESPANS
            ):
                if timestamp not in buckets:
                    buckets[timestamp] = dict()
                buckets[timestamp][loc_id] = buckets[timestamp].get(loc_id, 0) + value

    stash["free_dates"] = cur_free_dates
    stash["appointed_dates"] = cur_appointed_dates
    stash["previous_timestamps"] = previous_timestamps

    for name, buckets in metrics.items():
        df = pd.DataFrame(buckets).T
        df.index = pd.to_datetime(df.index)
        df.index.rename("date", inplace=True)
        # avoid storing floats and NaNs, convert to str(int) or empty string
        df = df.apply(lambda d: d.astype(str).apply(lambda v: v.split(".")[0])).replace("nan", "")
        metrics[name] = df

    return metrics
