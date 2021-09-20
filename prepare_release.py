from tqdm import tqdm

from data import *

PATH = Path(__file__).resolve().parent
STATISTICS_PATH = PATH / "statistics"

SNAPSHOTS_WEEKLY_FILE = STATISTICS_PATH / "snapshots-weekly.csv"
SNAPSHOTS_SUM_FILE = STATISTICS_PATH / "snapshots-sum.csv"


def calc_snapshot_statistics(data: Data) -> Optional[pd.DataFrame]:
    print(f"calc snapshot statistics ({data.filter()})")
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

        stat_rows.append({
            "week": "%s-%02d" % iso_week,
            "source_id": source_id,
            "num_locations": len(set(row[2] for row in rows)),
            "num_snapshots": len(set(row[0] for row in rows)),
            "num_changes": changes,
            "min_date": min(row[0] for row in rows),
            "max_date": max(row[0] for row in rows),
        })

    if not stat_rows:
        return None
    df = pd.DataFrame(stat_rows)
    df.set_index(["week", "source_id"], inplace=True)
    return df


def update_snapshot_statistics():
    filename = SNAPSHOTS_WEEKLY_FILE

    try:
        previous_stats = (
            pd.read_csv(filename)
            .set_index(["week", "source_id"])
        )
        max_date = previous_stats.index.get_level_values("week").max()
        max_date = Data.string_to_iso_week(max_date)

        data = Data(iso_week_gt=max_date)
        stats = calc_snapshot_statistics(data)
        if stats is None:
            print(f"unchanged: {filename}")
            return

    except Exception:
        previous_stats = None
        stats = calc_snapshot_statistics(Data())

    assert stats is not None

    if previous_stats is not None:
        stats = pd.concat([previous_stats, stats])

    stats.to_csv(filename)
    print(stats)


def update_meta_statistics():
    data = Data()

    sn_df = pd.read_csv(SNAPSHOTS_WEEKLY_FILE)
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
        f"[{source_id}]({data.get_meta(source_id, 'url').rstrip('/')}/)" if data.get_meta(source_id, "url") else source_id
    ))
    table_md = df.to_markdown()

    readme = (PATH / "README.md").read_text()
    readme = readme[:readme.index("# Statistics")]
    readme += f"""
# Statistics

- [snapshots-weekly.csv](statistics/snapshots-weekly.csv)
- [snapshots-sum.csv](statistics/snapshots-sum.csv) (below table)

{table_md}
""".strip() + "\n"
    (PATH / "README.md").write_text(readme)


if __name__ == "__main__":
    update_snapshot_statistics()
    update_meta_statistics()
