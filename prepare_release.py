import os
from tqdm import tqdm

from data import *

PATH = Path(__file__).resolve().parent
METRICS_PATH = PATH / "metrics"

SNAPSHOTS_WEEKLY_FILE = METRICS_PATH / "snapshots-weekly.csv"
SNAPSHOTS_SUM_FILE = METRICS_PATH / "snapshots-sum.csv"


def to_date(s: str) -> datetime.datetime:
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S")


def calc_snapshot_metrics(data: Data) -> Optional[pd.DataFrame]:
    print(f"calc snapshot metrics of {data}")

    df_changes = dict()
    for change_type in ("appointments", "cancellations"):
        df = Metrics.changes(
            type=change_type,
            iso_week_gt=data.iso_week_gt,
            iso_week_gte=data.iso_week_gte,
            iso_week_lt=data.iso_week_lt,
            iso_week_lte=data.iso_week_lte,
            as_int=True,
        )
        if df is not None:
            # hard clip on appointments data
            #   to throw out the complicated and nonsense stuff
            df = df.clip(0, 1)
            df["week"] = df.index.map(lambda d: d.isocalendar()[:2])
            df = df.groupby("week").sum()

        df_changes[change_type] = df

    stat_rows = []
    for iso_week, source_id, columns, rows in tqdm(data.iter_tables(as_int=False)):

        changes = 0
        prev_dates_free = dict()
        for row in rows:
            loc_id = row[2]
            dates_free = row[3:]
            if loc_id in prev_dates_free:
                if prev_dates_free[loc_id] != dates_free:
                   changes += 1

            prev_dates_free[loc_id] = dates_free

        num_changes = {f"num_{change_type}": -1 for change_type in df_changes}
        for change_type in df_changes:
            if df_changes[change_type] is not None:
                df = df_changes[change_type]
                # filter this iso-week
                df = df[df.index == iso_week]
                # filter this source_id
                df = df.loc[:, [c for c in df.columns if c.startswith(f"{source_id}/")]]
                # get the sum
                num_changes[f"num_{change_type}"] = df.sum().sum()

        stat_rows.append({
            "week": "%s-%02d" % iso_week,
            "source_id": source_id,
            "num_locations": len(set(row[2] for row in rows)),
            "num_snapshots": len(set(row[0] for row in rows)),
            "num_changes": changes,
            **num_changes,
            "min_date": min(row[0] for row in rows),
            "max_date": max(row[0] for row in rows),
        })

    if not stat_rows:
        return None
    df = pd.DataFrame(stat_rows)
    df.set_index(["week", "source_id"], inplace=True)
    return df


def update_metrics_weekly():
    filename = SNAPSHOTS_WEEKLY_FILE

    try:
        previous_stats = (
            pd.read_csv(filename)
            .set_index(["week", "source_id"])
        )
        max_date = previous_stats.index.get_level_values("week").max()
        max_date = Data.string_to_iso_week(max_date)

        data = Data(iso_week_gt=max_date)

    except Exception as e:
        previous_stats = None
        data = Data()  # full run over all weeks

    stats = calc_snapshot_metrics(data)
    if stats is None and previous_stats is not None:
        print(f"unchanged: {filename}")
        return

    if previous_stats is not None:
        stats = pd.concat([previous_stats, stats])

    stats.to_csv(filename)


def update_metrics_sum():
    data = Data()

    sn_df = pd.read_csv(SNAPSHOTS_WEEKLY_FILE)
    print(sn_df.to_markdown())
    source_group = sn_df.groupby("source_id")
    df = source_group.sum()
    df["num_locations"] = (source_group["num_locations"].mean() + .5).astype(np.int)
    df["name"] = df.index.map(lambda source_id: data.meta.get(source_id, {}).get("name", "-"))
    df["scraper"] = df.index.map(lambda source_id: data.meta.get(source_id, {}).get("scraper", "-"))
    df = df[df.columns[-2:].append(df.columns[:-2])]
    df["min_date"] = source_group["min_date"].min()
    df["max_date"] = source_group["max_date"].max()
    print(df.to_markdown())
    df.to_csv(SNAPSHOTS_SUM_FILE)

    df.index = df.index.map(lambda source_id: (
        f"[{source_id}]({data.get_meta(source_id, 'url')})" if data.get_meta(source_id, "url") else source_id
    ))

    template_context = {
        "last_exported_date": df["max_date"].max()[:10],
        "metrics_date": datetime.date.today(),
        "num_sources": format(df.index.nunique(), ","),
        "num_locations": format(df["num_locations"].sum(), ","),
        "num_snapshots": format(df["num_snapshots"].sum(), ","),
        "num_appointments": format(df["num_appointments"].sum(), ","),
        "metric_sum_table": df.to_markdown(),
    }

    readme = (PATH / "templates" / "README.md").read_text()
    readme = readme % template_context
    (PATH / "README.md").write_text(readme)


def calc_changes(data: Data, stash: Optional[dict] = None):
    print(f"calculating changes of {data}")
    free_dates = stash.get("free_dates") or dict() if stash else dict()
    appointed_dates = stash.get("appointed_dates") or dict() if stash else dict()
    previous_timestamps = stash.get("previous_timestamps") or dict() if stash else dict()
    changes_appointments = dict()
    changes_cancellations = dict()

    for week, source_id, columns, rows in tqdm(data.iter_tables()):
        dates = columns[3:]
        for org_row in rows:
            timestamp = org_row[0]
            timestamp_dt = to_date(timestamp)
            timestamp_dt = timestamp_dt.replace(minute=timestamp_dt.minute // 15 * 15, second=0, microsecond=0)
            timestamp = str(timestamp_dt)

            loc_id = f"{source_id}/{org_row[2]}"
            row = org_row[3:]

            if loc_id not in previous_timestamps:
                do_record = False
            else:
                diff = timestamp_dt - previous_timestamps[loc_id]
                do_record = diff.total_seconds() < 16 * 60
            previous_timestamps[loc_id] = timestamp_dt

            if loc_id not in free_dates:
                free_dates[loc_id] = set()
            if loc_id not in appointed_dates:
                appointed_dates[loc_id] = set()

            appointments = 0
            cancellations = 0

            for i, v in enumerate(row):
                date = dates[i]
                if v:
                    if date in appointed_dates[loc_id]:
                        appointed_dates[loc_id].remove(date)
                        if do_record:
                            cancellations += 1

                    free_dates[loc_id].add(date)
                else:
                    if date in free_dates[loc_id]:
                        # do not count the first cancelled date
                        #   because it might just have disappeared in time
                        if do_record:
                            if date != min(*free_dates[loc_id]) and date != max(*free_dates[loc_id]):
                                appointments += 1

                        free_dates[loc_id].remove(date)
                        appointed_dates[loc_id].add(date)

            for changes, value in (
                    (changes_appointments, appointments),
                    (changes_cancellations, cancellations),
            ):
                if timestamp not in changes:
                    changes[timestamp] = dict()
                changes[timestamp][loc_id] = changes[timestamp].get(loc_id, 0) + value

    if stash:
        stash["free_dates"] = free_dates
        stash["appointed_dates"] = appointed_dates
        stash["previous_timestamps"] = previous_timestamps

    dataframes = []
    for changes in (changes_appointments, changes_cancellations):
        df = pd.DataFrame(changes).T
        df.index = pd.to_datetime(df.index)
        df.index.rename("date", inplace=True)
        # avoid storing floats and NaNs, convert to str(int) and empty string
        df = df.apply(lambda d: d.astype(str).apply(lambda v: v.split(".")[0])).replace("nan", "")
        dataframes.append(df)

    return tuple(dataframes)


def update_changes():
    iso_weeks = [f[0] for f in Data().compressed_files()]

    stash = dict()
    for week in iso_weeks:
        path1 = METRICS_PATH / "appointments" / str(week[0])
        path2 = METRICS_PATH / "cancellations" / str(week[0])
        file1 = path1 / f"{Data.iso_week_to_string(week)}.csv"
        file2 = path2 / f"{Data.iso_week_to_string(week)}.csv"

        if not file1.exists() or not file2.exists():
            data = Data(iso_week_gte=week, iso_week_lte=week)
            df1, df2 = calc_changes(data, stash=stash)

            os.makedirs(path1, exist_ok=True)
            df1.to_csv(file1)
            os.makedirs(path2, exist_ok=True)
            df2.to_csv(file2)


if __name__ == "__main__":
    update_changes()
    update_metrics_weekly()
    update_metrics_sum()
