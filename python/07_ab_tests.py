"""07_ab_tests.py

Run simple A/B (genre) tests on global sales and summarize ESRB rating averages.
"""
from pathlib import Path
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats


def fetch_genre_sales(conn: sqlite3.Connection, genre: str) -> pd.Series:
    sql = """
        SELECT s.global_sales
        FROM sales s
        JOIN games g ON g.id = s.game_id
        WHERE g.genre = ?
    """
    df = pd.read_sql_query(sql, conn, params=(genre,))
    return df["global_sales"].dropna()


def two_sample_test(a: pd.Series, b: pd.Series) -> tuple:
    # Welch's t-test handles unequal variances and sample sizes.
    t_stat, p_val = stats.ttest_ind(a, b, equal_var=False)
    return t_stat, p_val


def rating_genre_summary(conn: sqlite3.Connection) -> pd.DataFrame:
    sql = """
        SELECT g.rating, g.genre, AVG(s.global_sales) AS avg_global_sales, COUNT(*) AS n
        FROM sales s
        JOIN games g ON g.id = s.game_id
        GROUP BY g.rating, g.genre
        ORDER BY avg_global_sales DESC
    """
    return pd.read_sql_query(sql, conn)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    reports_dir = repo_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "games.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    comparisons = [
        ("Action", "Strategy"),
        ("Sports", "Strategy"),
    ]

    lines = []

    with sqlite3.connect(db_path) as conn:
        for g1, g2 in comparisons:
            sales1 = fetch_genre_sales(conn, g1)
            sales2 = fetch_genre_sales(conn, g2)

            if sales1.empty or sales2.empty:
                lines.append(f"{g1} vs {g2}: insufficient data\n")
                continue

            t_stat, p_val = two_sample_test(sales1, sales2)
            lines.append(
                f"{g1} vs {g2}: t={t_stat:.4f}, p={p_val:.4e}, "
                f"mean1={sales1.mean():.2f}, mean2={sales2.mean():.2f}, "
                f"n1={len(sales1)}, n2={len(sales2)}\n"
            )

        rating_summary = rating_genre_summary(conn)

    summary_path = reports_dir / "ab_test_summary.txt"
    rating_head = rating_summary.head() if not rating_summary.empty else rating_summary
    summary_text = (
        "".join(lines)
        + "\nESRB rating x genre averages (top rows):\n"
        + rating_head.to_string(index=False)
        + "\n"
    )
    summary_path.write_text(summary_text)

    # Also print to console for quick visibility.
    print("".join(lines))
    print("ESRB rating x genre averages (top rows):")
    print(rating_summary.head())
    print(f"Wrote summary to: {summary_path}")


if __name__ == "__main__":
    main()
