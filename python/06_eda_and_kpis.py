"""06_eda_and_kpis.py

Run quick EDA/KPIs from the SQLite database and produce plots.
- Pulls aggregates via SQL (by year, by genre, top genres)
- Saves regional time-series and genre bar charts to reports/
- Prints a short KPI summary to stdout
"""
from pathlib import Path
import os
import sqlite3
import pandas as pd

# Ensure matplotlib writes config/cache to a writable location.
os.environ.setdefault("MPLCONFIGDIR", str(Path("/tmp/matplotlib-config")))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def query_to_df(conn: sqlite3.Connection, sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame."""
    return pd.read_sql_query(sql, conn)


def plot_sales_over_time(df: pd.DataFrame, output_path: Path) -> None:
    """Line plot comparing regional sales over time."""
    plt.figure(figsize=(10, 6))
    x = df["year"].to_numpy()
    for col in ["na_sales", "eu_sales", "jp_sales", "other_sales"]:
        if col in df.columns:
            plt.plot(x, df[col].to_numpy(), label=col.replace("_sales", "").upper())
    plt.title("Regional Sales Over Time")
    plt.xlabel("Year")
    plt.ylabel("Total Sales (units)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def plot_genre_sales(df: pd.DataFrame, output_path: Path) -> None:
    """Grouped bar chart for region totals per genre."""
    pivoted = df.set_index("genre")[["na_sales", "eu_sales", "jp_sales", "other_sales"]]
    ax = pivoted.plot(kind="bar", figsize=(12, 6))
    ax.set_title("Sales by Genre and Region")
    ax.set_xlabel("Genre")
    ax.set_ylabel("Total Sales (units)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "games.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    with sqlite3.connect(db_path) as conn:
        # Aggregate regional totals per year for the time-series chart.
        sales_by_year = query_to_df(
            conn,
            """
            SELECT
                g.year,
                SUM(s.na_sales) AS na_sales,
                SUM(s.eu_sales) AS eu_sales,
                SUM(s.jp_sales) AS jp_sales,
                SUM(s.other_sales) AS other_sales,
                SUM(s.global_sales) AS global_sales
            FROM sales s
            JOIN games g ON g.id = s.game_id
            GROUP BY g.year
            ORDER BY g.year
            """,
        )

        # Aggregate sales by genre for the grouped bar chart.
        sales_by_genre = query_to_df(
            conn,
            """
            SELECT
                g.genre,
                SUM(s.na_sales) AS na_sales,
                SUM(s.eu_sales) AS eu_sales,
                SUM(s.jp_sales) AS jp_sales,
                SUM(s.other_sales) AS other_sales,
                SUM(s.global_sales) AS global_sales
            FROM sales s
            JOIN games g ON g.id = s.game_id
            GROUP BY g.genre
            ORDER BY global_sales DESC
            """,
        )

        # Top 10 genres globally for quick KPI reference.
        top_genres = query_to_df(
            conn,
            """
            SELECT
                g.genre,
                SUM(s.global_sales) AS global_sales
            FROM sales s
            JOIN games g ON g.id = s.game_id
            GROUP BY g.genre
            ORDER BY global_sales DESC
            LIMIT 10
            """,
        )

    plot_sales_over_time(sales_by_year, reports_dir / "sales_by_region_over_time.png")
    plot_genre_sales(
        sales_by_genre, reports_dir / "genre_sales_by_region.png"
    )

    # Simple KPI summary.
    top_genre = top_genres.iloc[0] if not top_genres.empty else None
    total_sales = sales_by_year[["na_sales", "eu_sales", "jp_sales", "other_sales"]].sum()

    print("KPI Summary")
    if top_genre is not None:
        print(f"- Top genre globally: {top_genre['genre']} ({top_genre['global_sales']:.0f} units)")
    print(
        "- Total sales by region (all years): "
        f"NA={total_sales['na_sales']:.0f}, "
        f"EU={total_sales['eu_sales']:.0f}, "
        f"JP={total_sales['jp_sales']:.0f}, "
        f"Other={total_sales['other_sales']:.0f}"
    )
    print(f"- Saved plots to: {reports_dir}")


if __name__ == "__main__":
    main()
