"""08_prepare_features_for_clustering.py

Extract game features and scale them for clustering.
"""
from pathlib import Path
import sqlite3
import pandas as pd
from sklearn.preprocessing import StandardScaler


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    reports_dir = repo_root / "reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    db_path = data_dir / "games.db"
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    output_path = data_dir / "features_for_clustering.csv"

    with sqlite3.connect(db_path) as conn:
        df = pd.read_sql_query(
            """
            SELECT
                g.id AS game_id,
                g.critic_score,
                g.user_score,
                s.na_sales,
                s.eu_sales,
                s.jp_sales,
                s.other_sales,
                s.global_sales
            FROM games g
            JOIN sales s ON s.game_id = g.id
            """,
            conn,
        )

    # Drop rows with missing core features.
    df = df.dropna(
        subset=[
            "critic_score",
            "user_score",
            "na_sales",
            "eu_sales",
            "jp_sales",
            "other_sales",
            "global_sales",
        ]
    )

    feature_cols = [
        "critic_score",
        "user_score",
        "na_sales",
        "eu_sales",
        "jp_sales",
        "other_sales",
        "global_sales",
    ]

    scaler = StandardScaler()
    scaled = scaler.fit_transform(df[feature_cols])
    scaled_df = pd.DataFrame(scaled, columns=feature_cols)
    scaled_df.insert(0, "game_id", df["game_id"].values)

    scaled_df.to_csv(output_path, index=False)

    print(f"Features shape: {scaled_df.shape}")
    print(scaled_df.head())
    print(f"Wrote features to: {output_path}")


if __name__ == "__main__":
    main()
