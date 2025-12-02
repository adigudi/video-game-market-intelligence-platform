"""01_clean_data.py

Loads and cleans console and population CSVs and writes cleaned CSVs.

- Console: rename columns to snake_case, convert numeric columns, fill missing sales with 0.0,
  drop rows missing name or genre.
- Population: reshape from wide to long with columns: country_name, country_code, year, population.

Saves outputs to data/clean_console_data.csv and data/clean_population_data.csv
"""
from pathlib import Path
import re
import pandas as pd


def to_snake(name: str) -> str:
    """Convert a column name to snake_case."""
    if not isinstance(name, str):
        return name
    # replace non-alphanumeric characters with underscore
    s = re.sub(r"[^0-9a-zA-Z]+", "_", name.strip())
    # insert underscore between camelCase boundaries (aB -> a_B)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    s = s.strip("_").lower()
    return s


def clean_console_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)

    # rename columns to snake_case
    df = df.rename(columns={col: to_snake(col) for col in df.columns})

    # numeric conversions
    for col in ("year_of_release", "critic_score", "user_score"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # fill missing sales columns with 0.0
    sales_cols = [c for c in ("na_sales", "eu_sales", "jp_sales", "other_sales") if c in df.columns]
    if sales_cols:
        df[sales_cols] = df[sales_cols].fillna(0.0)

    # drop rows missing name or genre
    req = [c for c in ("name", "genre") if c in df.columns]
    if req:
        df = df.dropna(subset=req)

    return df


def clean_population_data(path: Path) -> pd.DataFrame:
    import csv

    # try several reasonable parsing modes until one succeeds
    parse_attempts = [('\t', csv.QUOTE_MINIMAL), ('\t', csv.QUOTE_NONE), (',', csv.QUOTE_MINIMAL)]
    df = None
    for sep, quoting in parse_attempts:
        try:
            df = pd.read_csv(path, sep=sep, engine="python", encoding='utf-8-sig', quoting=quoting)
            break
        except Exception:
            df = None
            continue
    if df is None:
        # last-resort: read whole file and split on whitespace-like tabs
        text = Path(path).read_text(encoding='utf-8-sig')
        # replace Windows line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # build dataframe from lines splitting on tabs
        rows = [line.split('\t') for line in text.split('\n') if line.strip()]
        df = pd.DataFrame(rows[1:], columns=rows[0])

    # normalize column names: strip and remove surrounding quotes
    df.columns = [str(c).strip().strip('"').strip("'") for c in df.columns]

    # standardize id columns that may have different capitalization/spaces
    id_cols = None
    for pair in [("Country Name", "Country Code"), ("country name", "country code"), ("CountryName", "CountryCode")]:
        if pair[0] in df.columns and pair[1] in df.columns:
            id_cols = pair
            break
    if id_cols is None:
        # try common snake-case variants
        if "country_name" in df.columns and "country_code" in df.columns:
            id_cols = ("country_name", "country_code")
    if id_cols is None:
        # as a fallback, assume first two columns are country name/code
        id_cols = (df.columns[0], df.columns[1])

    # strip quotes/spaces from id columns' values
    df[id_cols[0]] = df[id_cols[0]].astype(str).str.strip().str.strip('"').str.strip("'")
    df[id_cols[1]] = df[id_cols[1]].astype(str).str.strip().str.strip('"').str.strip("'")

    # melt years into long form
    value_vars = [c for c in df.columns if c not in id_cols]
    pop = pd.melt(df, id_vars=list(id_cols), value_vars=value_vars, var_name="year", value_name="population")

    # rename to requested columns
    pop = pop.rename(columns={id_cols[0]: "country_name", id_cols[1]: "country_code"})

    # clean year and population types
    pop["year"] = pop["year"].astype(str).str.strip()
    pop["year"] = pd.to_numeric(pop["year"], errors="coerce").astype('Int64')
    pop["population"] = pd.to_numeric(pop["population"], errors="coerce")

    # drop rows with missing year
    pop = pop.dropna(subset=["year"]).copy()
    pop["year"] = pop["year"].astype(int)

    # reorder columns
    pop = pop[["country_name", "country_code", "year", "population"]]

    return pop


def main() -> None:
    base = Path(__file__).resolve().parent.parent
    data_dir = base / "data"

    console_in = data_dir / "Console_Data.csv"
    population_in = data_dir / "Population.csv"

    console_out = data_dir / "clean_console_data.csv"
    population_out = data_dir / "clean_population_data.csv"

    if not console_in.exists():
        raise FileNotFoundError(f"Console data file not found: {console_in}")
    if not population_in.exists():
        raise FileNotFoundError(f"Population data file not found: {population_in}")

    console_df = clean_console_data(console_in)
    population_df = clean_population_data(population_in)

    # ensure data directory exists
    data_dir.mkdir(parents=True, exist_ok=True)

    console_df.to_csv(console_out, index=False)
    population_df.to_csv(population_out, index=False)

    print(f"Wrote cleaned console data to: {console_out}")
    print(f"Wrote cleaned population data to: {population_out}")


if __name__ == "__main__":
    main()
