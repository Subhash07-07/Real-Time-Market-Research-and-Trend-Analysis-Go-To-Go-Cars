
import sys
import os

# Ensure the project directory is in the path
sys.path.insert(0, os.path.dirname(__file__))

from database_setup import create_database
from analysis import run_full_analysis
from visualizations import generate_all_charts
from export_to_excel_powerbi import export_all


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["--all"]

    print("╔" + "═" * 62 + "╗")
    print("║                                                              ║")
    print("║   🚗 GO TO GO CARS — MARKET ANALYSIS PROJECT                 ║")
    print("║                                                              ║")
    print("║   Tools: SQL | Pandas | NumPy | Matplotlib | Seaborn         ║")
    print("║          Excel | Power BI (CSV exports)                      ║")
    print("║                                                              ║")
    print("║   Competitors: QuickRide | BlaBlaCar | sRide                 ║")
    print("║   Report Date: July 2026                                     ║")
    print("║                                                              ║")
    print("╚" + "═" * 62 + "╝\n")

    if "--all" in args or len(args) == 0:
        # Step 1: Database
        print("🔧 STEP 1/4: Creating SQLite Database...")
        create_database()

        # Step 2: Analysis
        print("\n📊 STEP 2/4: Running Analysis (SQL + Pandas + NumPy)...")
        run_full_analysis()

        # Step 3: Charts
        print("\n🎨 STEP 3/4: Generating Visualizations (Matplotlib + Seaborn)...")
        generate_all_charts()

        # Step 4: Export
        print("\n📤 STEP 4/4: Exporting (Excel + Power BI CSVs + SQL)...")
        export_all()

    else:
        if "--db" in args:
            create_database()
        if "--analyze" in args:
            run_full_analysis()
        if "--charts" in args:
            generate_all_charts()
        if "--export" in args:
            export_all()

    print("\n" + "═" * 64)
    print("🎉 PROJECT COMPLETE!")
    print("═" * 64)

    project_dir = os.path.dirname(__file__)
    print(f"""
📂 Project Structure:
   {project_dir}/
   ├── main.py                      ← This runner script
   ├── database_setup.py            ← SQLite database creation
   ├── analysis.py                  ← Pandas + NumPy analysis
   ├── visualizations.py            ← Matplotlib + Seaborn charts
   ├── export_to_excel_powerbi.py   ← Excel + Power BI exports
   ├── requirements.txt             ← Python dependencies
   ├── data/
   │   └── market_analysis.db       ← SQLite database
   ├── charts/
   │   ├── 01_market_growth_projection.png
   │   ├── 02_revenue_comparison.png
   │   ├── 03_user_growth_trajectory.png
   │   ├── 04_feature_radar.png
   │   ├── 05_feature_heatmap.png
   │   ├── 06_demographics.png
   │   ├── 07_city_coverage.png
   │   ├── 08_sentiment_analysis.png
   │   ├── 09_swot_impact.png
   │   ├── 10_segment_cagr.png
   │   ├── 11_funding_comparison.png
   │   └── 12_correlation_matrix.png
   ├── exports/
   │   ├── GoToGoCars_Market_Analysis.xlsx  ← Multi-sheet Excel
   │   ├── sql_queries_reference.sql        ← 10 SQL queries
   │   └── powerbi_csvs/                   ← Star-schema CSVs
   │       ├── dim_companies.csv
   │       ├── dim_cities.csv
   │       ├── dim_features.csv
   │       ├── fact_financials.csv
   │       ├── fact_user_growth.csv
   │       ├── fact_market_data.csv
   │       ├── fact_city_coverage.csv
   │       ├── fact_features.csv
   │       ├── fact_demographics.csv
   │       ├── fact_reviews.csv
   │       ├── fact_swot.csv
   │       ├── fact_funding.csv
   │       └── _POWERBI_SETUP_GUIDE.txt
   └── index.html + style.css + script.js  ← Interactive web dashboard
""")


if __name__ == "__main__":
    main()
