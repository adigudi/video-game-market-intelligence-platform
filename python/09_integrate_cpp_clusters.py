"""09_integrate_cpp_clusters.py

Run the C++ clustering engine and persist cluster assignments into SQLite.
"""
from pathlib import Path
import os
import subprocess
import sqlite3
import pandas as pd


def run_cluster_engine(repo_root: Path) -> None:
    # Pick binary name based on platform.
    exe = Path("cpp") / ("cluster_engine.exe" if os.name == "nt" else "cluster_engine")
    exe_path = repo_root / exe
    if not exe_path.exists():
        raise FileNotFoundError(
            f"Cluster engine not found at {exe_path}. Compile it with: cd cpp && g++ -std=c++17 clustering.cpp -o cluster_engine"
        )

    result = subprocess.run(
        [str(exe_path)],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Cluster engine failed (code {result.returncode}). Stdout: {result.stdout} Stderr: {result.stderr}"
        )
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())


def load_clusters_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"cluster_output.csv not found at {path}")
    df = pd.read_csv(path)
    if not {"game_id", "cluster_id"}.issubset(df.columns):
        raise ValueError("cluster_output.csv must contain game_id and cluster_id columns")
    return df


def upsert_clusters(conn: sqlite3.Connection, clusters_df: pd.DataFrame) -> int:
    rows = list(clusters_df[["game_id", "cluster_id"]].itertuples(index=False, name=None))
    conn.executemany(
        "INSERT OR REPLACE INTO clusters (game_id, cluster_id) VALUES (?, ?)",
        rows,
    )
    return len(rows)


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    data_dir = repo_root / "data"
    db_path = data_dir / "games.db"
    output_csv = data_dir / "cluster_output.csv"

    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")

    run_cluster_engine(repo_root)

    clusters_df = load_clusters_csv(output_csv)

    with sqlite3.connect(db_path) as conn:
        count = upsert_clusters(conn, clusters_df)
        conn.commit()

    print(f"Wrote {count} cluster assignments into clusters table.")


if __name__ == "__main__":
    main()
