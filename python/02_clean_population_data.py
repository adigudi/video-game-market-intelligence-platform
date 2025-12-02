"""02_clean_population_data.py

Convert wide Population.csv into a long, tidy table.
"""
from pathlib import Path
import pandas as pd


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"

    population_in = data_dir / "Population.csv"
    population_out = data_dir / "clean_population_data.csv"

    if not population_in.exists():
        raise FileNotFoundError(f"Population data file not found: {population_in}")

    # Source file is tab-delimited.
    df = pd.read_csv(population_in, sep="\t")

    long_df = df.melt(
        id_vars=["Country Name", "Country Code"],
        var_name="year",
        value_name="population",
    )

    long_df = long_df.rename(
        columns={
            "Country Name": "country_name",
            "Country Code": "country_code",
        }
    )

    long_df["year"] = pd.to_numeric(long_df["year"], errors="coerce").astype("Int64")
    long_df["population"] = pd.to_numeric(long_df["population"], errors="coerce")

    long_df = long_df.dropna(subset=["population"])

    long_df.to_csv(population_out, index=False)
    print(f"Wrote cleaned population data to: {population_out}")


if __name__ == "__main__":
    main()
