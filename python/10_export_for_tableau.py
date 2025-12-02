"""10_export_for_tableau.py

Export a flattened table for Tableau analysis.
"""
from pathlib import Path
import sqlite3
import pandas as pd


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    tableau_dir = repo_root / "tableau"
    tableau_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "games.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT
                g.id AS game_id,
                g.name,
                g.platform,
                g.year,
                g.genre,
                g.publisher,
                g.rating,
                g.critic_score,
                g.user_score,
                s.na_sales,
                s.eu_sales,
                s.jp_sales,
                s.other_sales,
                s.global_sales,
                rp.na_population,
                rp.eu_population,
                rp.jp_population,
                rp.other_population,
                c.cluster_id
            FROM games g
            JOIN sales s ON s.game_id = g.id
            LEFT JOIN region_population rp ON rp.year = g.year
            LEFT JOIN clusters c ON c.game_id = g.id
            """,
            conn,
        )

    output_path = tableau_dir / "games_for_tableau.csv"
    df.to_csv(output_path, index=False)

    print(f"Exported Tableau dataset to: {output_path}")
    print(f"Shape: {df.shape}")


if __name__ == "__main__":
    main()
