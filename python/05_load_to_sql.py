"""05_load_to_sql.py

Create SQLite database and load cleaned datasets into normalized tables.
"""
from pathlib import Path
import sqlite3
import pandas as pd


def load_schema(conn: sqlite3.Connection, schema_path: Path) -> None:
    schema_sql = schema_path.read_text()
    conn.executescript(schema_sql)


def insert_games(conn: sqlite3.Connection, games_df: pd.DataFrame) -> None:
    records = games_df.to_records(index=False)
    conn.executemany(
        """
        INSERT INTO games (name, platform, year, genre, publisher, critic_score, user_score, rating)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        records,
    )


def insert_sales(conn: sqlite3.Connection, sales_df: pd.DataFrame, game_id_lookup: dict) -> None:
    def row_to_tuple(row):
        key = (row["name"], row["platform"], row["year"])
        game_id = game_id_lookup.get(key)
        if game_id is None:
            return None
        return (
            game_id,
            row["na_sales"],
            row["eu_sales"],
            row["jp_sales"],
            row["other_sales"],
            row["global_sales"],
        )

    tuples = [t for t in (row_to_tuple(row) for _, row in sales_df.iterrows()) if t]
    conn.executemany(
        """
        INSERT INTO sales (game_id, na_sales, eu_sales, jp_sales, other_sales, global_sales)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        tuples,
    )


def insert_region_population(conn: sqlite3.Connection, region_df: pd.DataFrame) -> None:
    conn.executemany(
        """
        INSERT INTO region_population (year, na_population, eu_population, jp_population, other_population)
        VALUES (?, ?, ?, ?, ?)
        """,
        region_df.to_records(index=False),
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    sql_dir = repo_root / "sql"

    db_path = data_dir / "games.db"
    schema_path = sql_dir / "schema.sql"
    merged_path = data_dir / "merged_games_population.csv"
    region_path = data_dir / "region_population_by_year.csv"

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    if not merged_path.exists():
        raise FileNotFoundError(f"Merged data not found: {merged_path}")
    if not region_path.exists():
        raise FileNotFoundError(f"Region population data not found: {region_path}")

    data_dir.mkdir(parents=True, exist_ok=True)

    merged_df = pd.read_csv(merged_path)
    # Ensure key types are consistent.
    merged_df["year"] = pd.to_numeric(merged_df["year"], errors="coerce").astype("Int64")

    games_columns = [
        "name",
        "platform",
        "year",
        "genre",
        "publisher",
        "critic_score",
        "user_score",
        "rating",
    ]
    sales_columns = [
        "name",
        "platform",
        "year",
        "na_sales",
        "eu_sales",
        "jp_sales",
        "other_sales",
        "global_sales",
    ]

    games_df = merged_df[games_columns].drop_duplicates()
    sales_df = merged_df[sales_columns]

    region_df = pd.read_csv(region_path)
    region_df["year"] = pd.to_numeric(region_df["year"], errors="coerce").astype("Int64")

    with sqlite3.connect(db_path) as conn:
        load_schema(conn, schema_path)

        insert_games(conn, games_df)

        # Build lookup from (name, platform, year) to game_id for foreign keys.
        cursor = conn.execute("SELECT id, name, platform, year FROM games")
        game_id_lookup = {
            (row[1], row[2], row[3]): row[0]
            for row in cursor.fetchall()
        }

        insert_sales(conn, sales_df, game_id_lookup)
        insert_region_population(conn, region_df)
        conn.commit()

        for table in ("games", "sales", "region_population", "clusters"):
            count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            print(f"{table}: {count} rows")

    print(f"Database created at: {db_path}")


if __name__ == "__main__":
    main()
