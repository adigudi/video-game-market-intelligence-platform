"""01_clean_console_data.py

Cleans data/Console_Data.csv and writes data/clean_console_data.csv.

Operations:
- rename columns to snake_case
- convert year_of_release, critic_score, user_score to numeric (errors='coerce')
- fill missing sales columns with 0.0
- add global_sales as sum of sales columns
- drop rows missing name or genre
- print raw and cleaned shapes
"""
from pathlib import Path
import re
import pandas as pd


def to_snake(name: str) -> str:
    """Convert a column name to snake_case."""
    if not isinstance(name, str):
        return name
    s = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip())
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.strip("_").lower()


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"

    console_in = data_dir / "Console_Data.csv"
    console_out = data_dir / "clean_console_data.csv"

    if not console_in.exists():
        raise FileNotFoundError(f"Console data file not found: {console_in}")

    # read (source is tab-delimited with trailing empty columns)
    raw_df = pd.read_csv(console_in, sep="\t").dropna(axis=1, how="all")
    print(f"Raw shape: {raw_df.shape}")

    # rename columns to snake_case
    df = raw_df.rename(columns={c: to_snake(c) for c in raw_df.columns})

    # convert numerics
    for col in ("year_of_release", "critic_score", "user_score"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # fill missing sales with 0.0
    sales_cols = [c for c in ("na_sales", "eu_sales", "jp_sales", "other_sales") if c in df.columns]
    if sales_cols:
        df[sales_cols] = df[sales_cols].fillna(0.0)

    # add global_sales
    if sales_cols:
        df["global_sales"] = df[sales_cols].sum(axis=1)
    else:
        df["global_sales"] = 0.0

    # drop rows missing name or genre
    req = [c for c in ("name", "genre") if c in df.columns]
    if req:
        df = df.dropna(subset=req)

    print(f"Cleaned shape: {df.shape}")

    # ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    df.to_csv(console_out, index=False)
    print(f"Wrote cleaned console data to: {console_out}")


if __name__ == "__main__":
    main()
