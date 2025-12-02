"""03_build_region_population.py

Aggregate yearly population by broad regions: North America, Europe, Japan, Other.
"""
from pathlib import Path
import pandas as pd


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"

    population_in = data_dir / "clean_population_data.csv"
    population_out = data_dir / "region_population_by_year.csv"

    if not population_in.exists():
        raise FileNotFoundError(f"Clean population file not found: {population_in}")

    df = pd.read_csv(population_in)

    # Define regions as ISO country-code sets. Any country not in these sets
    # will roll up into "Other".
    north_america = {"USA", "US", "CAN", "MEX"}
    europe = {
        "GBR",
        "DEU",
        "FRA",
        "ESP",
        "ITA",
        "NLD",
        "BEL",
        "CHE",
        "AUT",
        "SWE",
        "NOR",
        "DNK",
        "FIN",
        "IRL",
        "PRT",
        "GRC",
        "POL",
        "CZE",
        "HUN",
        "ROU",
        "BGR",
        "SVK",
        "SVN",
        "HRV",
        "EST",
        "LVA",
        "LTU",
        "UKR",
        "RUS",
        "TUR",
    }
    japan = {"JPN"}

    def normalize_code(code: str) -> str:
        return str(code).strip().upper()

    def to_region(code: str) -> str:
        c = normalize_code(code)
        if c in north_america:
            return "na"
        if c in europe:
            return "eu"
        if c in japan:
            return "jp"
        return "other"

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["population"] = pd.to_numeric(df["population"], errors="coerce")
    df = df.dropna(subset=["year", "population"])

    df["region"] = df["country_code"].map(to_region)

    grouped = (
        df.groupby(["year", "region"], as_index=False)["population"]
        .sum()
        .pivot(index="year", columns="region", values="population")
        .fillna(0)
    )

    final = (
        grouped.reindex(columns=["na", "eu", "jp", "other"], fill_value=0)
        .reset_index()
        .rename(
            columns={
                "year": "year",
                "na": "na_population",
                "eu": "eu_population",
                "jp": "jp_population",
                "other": "other_population",
            }
        )
        .sort_values("year")
    )

    final.to_csv(population_out, index=False)
    print(f"Wrote region population totals to: {population_out}")


if __name__ == "__main__":
    main()
