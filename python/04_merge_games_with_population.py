"""04_merge_games_with_population.py

Merge console sales data with regional population by release year.
"""
from pathlib import Path
import pandas as pd


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"

    console_path = data_dir / "clean_console_data.csv"
    population_path = data_dir / "region_population_by_year.csv"
    output_path = data_dir / "merged_games_population.csv"

    if not console_path.exists():
        raise FileNotFoundError(f"Console data not found: {console_path}")
    if not population_path.exists():
        raise FileNotFoundError(f"Population data not found: {population_path}")

    console_df = pd.read_csv(console_path)
    population_df = pd.read_csv(population_path)

    console_df["year_of_release"] = pd.to_numeric(
        console_df["year_of_release"], errors="coerce"
    ).astype("Int64")
    population_df["year"] = pd.to_numeric(population_df["year"], errors="coerce").astype(
        "Int64"
    )

    merged = console_df.merge(
        population_df,
        left_on="year_of_release",
        right_on="year",
        how="inner",
    )

    merged = merged.drop(columns=["year"]).rename(columns={"year_of_release": "year"})

    column_order = [
        "name",
        "platform",
        "year",
        "genre",
        "publisher",
        "na_sales",
        "eu_sales",
        "jp_sales",
        "other_sales",
        "global_sales",
        "critic_score",
        "user_score",
        "rating",
        "na_population",
        "eu_population",
        "jp_population",
        "other_population",
    ]

    remaining_cols = [c for c in merged.columns if c not in column_order]
    merged = merged[column_order + remaining_cols]

    merged.to_csv(output_path, index=False)

    print(merged.head())
    print(f"Merged shape: {merged.shape}")
    print(f"Wrote merged data to: {output_path}")


if __name__ == "__main__":
    main()
