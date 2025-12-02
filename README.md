🎮 Video Game Market Intelligence Platform

A Full-Stack Data Analytics Project (SQL · Python · C++ · Tableau)

---

📌 Overview

End-to-end analytics pipeline that cleans raw console sales and population data, builds a SQLite warehouse, runs Python EDA/KPIs and A/B tests, clusters games with a C++ engine, and exports a single flat table for Tableau dashboards.

---

🛠️ Tech Stack
- Data: pandas, numpy, scipy, matplotlib, scikit-learn
- Storage: SQLite (sql/schema.sql, data/games.db)
- Compute: Python analytics + C++17 clustering engine
- Viz: Tableau (tableau/games_for_tableau.csv)
- Glue: pathlib, sqlite3, subprocess, g++

---

🏗️ Architecture

```
Console_Data + Population
         |
         v
   Python cleaning
         |
         v
      SQLite DB
         |
         v
  Python analytics
         |
         v
   C++ clustering
         |
         v
  SQLite clusters
         |
         v
      Tableau
```

---

📁 Repository Structure

├── data/          # Raw and cleaned datasets, games.db, clustering outputs  
├── sql/           # schema.sql for SQLite tables  
├── python/        # Cleaning, ETL, analytics, clustering integration, exports  
├── cpp/           # C++ clustering engine source & binary  
├── tableau/       # Tableau-ready extracts  
└── reports/       # Plots, summaries

---

🚀 How to Run (from repo root)
1) Clean & merge data  
   - `python python/01_clean_console_data.py`  
   - `python python/02_clean_population_data.py`  
   - `python python/03_build_region_population.py`  
   - `python python/04_merge_games_with_population.py`

2) Create DB & load data  
   - `python python/05_load_to_sql.py`

3) Analytics & KPIs  
   - `python python/06_eda_and_kpis.py` (plots to reports/)  
   - `python python/07_ab_tests.py` (text summary to reports/)

4) Feature prep & clustering  
   - `python python/08_prepare_features_for_clustering.py`  
   - `cd cpp && g++ -std=c++17 clustering.cpp -o cluster_engine && cd ..`  
   - `python python/09_integrate_cpp_clusters.py` (runs C++ engine, loads clusters to DB)

5) Export for Tableau  
   - `python python/10_export_for_tableau.py` → `tableau/games_for_tableau.csv`

---

📜 License

MIT License (optional — you can choose later)

---

👤 Author

Adi Gudi  
📧 agudi24@gmail.com  
🔗 LinkedIn: https://www.linkedin.com/in/adigudi/

---
