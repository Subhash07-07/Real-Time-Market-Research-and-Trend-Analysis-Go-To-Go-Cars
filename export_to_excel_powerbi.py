import sqlite3
import os
import numpy as np
import pandas as pd
from database_setup import create_database, DB_PATH

# Output directories
EXPORT_DIR = os.path.join(os.path.dirname(__file__), "exports")
CSV_DIR = os.path.join(EXPORT_DIR, "powerbi_csvs")
EXCEL_PATH = os.path.join(EXPORT_DIR, "GoToGoCars_Market_Analysis.xlsx")

os.makedirs(CSV_DIR, exist_ok=True)


def get_connection():
    if not os.path.exists(DB_PATH):
        create_database()
    return sqlite3.connect(DB_PATH)


# ============================================================
# EXPORT 1: MULTI-SHEET EXCEL WORKBOOK
# ============================================================
def export_excel():
    """Export a formatted multi-sheet Excel workbook."""
    conn = get_connection()

    print("\n📊 Generating Excel Workbook...")

    # Load all data
    dataframes = {
        "Dashboard Summary": _create_dashboard_summary(conn),
        "Companies": pd.read_sql_query("SELECT * FROM companies", conn),
        "Financial Data": pd.read_sql_query(
            "SELECT * FROM financials ORDER BY company_name, fiscal_year", conn),
        "User Growth": pd.read_sql_query(
            "SELECT * FROM user_growth ORDER BY company_name, year", conn),
        "Feature Comparison": pd.read_sql_query(
            "SELECT * FROM features ORDER BY category", conn),
        "Market Data": pd.read_sql_query(
            "SELECT * FROM market_data ORDER BY year", conn),
        "Demographics": pd.read_sql_query(
            "SELECT * FROM demographics ORDER BY company_name", conn),
        "City Coverage": pd.read_sql_query(
            "SELECT * FROM city_coverage ORDER BY company_name, estimated_users DESC", conn),
        "App Reviews": pd.read_sql_query(
            "SELECT * FROM app_reviews ORDER BY company_name", conn),
        "SWOT Analysis": pd.read_sql_query(
            "SELECT * FROM swot_analysis ORDER BY swot_type", conn),
        "Funding Rounds": pd.read_sql_query(
            "SELECT * FROM funding_rounds ORDER BY year", conn),
        "Revenue Pivot": _create_revenue_pivot(conn),
        "User Growth Pivot": _create_user_pivot(conn),
        "CAGR Analysis": _create_cagr_analysis(conn),
        "Market Share": _create_market_share(conn),
        "Feature Score Card": _create_feature_scorecard(conn),
    }

    # Write to Excel with formatting
    with pd.ExcelWriter(EXCEL_PATH, engine="xlsxwriter") as writer:
        workbook = writer.book

        # Define formats
        header_fmt = workbook.add_format({
            "bold": True,
            "bg_color": "#6366f1",
            "font_color": "white",
            "border": 1,
            "text_wrap": True,
            "valign": "vcenter",
            "font_size": 11,
        })

        title_fmt = workbook.add_format({
            "bold": True,
            "font_size": 18,
            "font_color": "#6366f1",
        })

        subtitle_fmt = workbook.add_format({
            "italic": True,
            "font_size": 11,
            "font_color": "#666666",
        })

        number_fmt = workbook.add_format({
            "num_format": "#,##0",
            "border": 1,
        })

        pct_fmt = workbook.add_format({
            "num_format": "0.0%",
            "border": 1,
        })

        currency_fmt = workbook.add_format({
            "num_format": "$#,##0.00",
            "border": 1,
        })

        cell_fmt = workbook.add_format({
            "border": 1,
            "text_wrap": True,
            "valign": "vcenter",
        })

        for sheet_name, df in dataframes.items():
            # Write DataFrame
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False, startrow=2)

            worksheet = writer.sheets[sheet_name[:31]]

            # Add title
            worksheet.write(0, 0, sheet_name, title_fmt)
            worksheet.write(1, 0, "Go To Go Cars — Market Analysis | July 2026", subtitle_fmt)

            # Format headers
            for col_num, col_name in enumerate(df.columns):
                worksheet.write(2, col_num, col_name, header_fmt)
                # Auto-width columns
                max_len = max(
                    df[col_name].astype(str).map(len).max() if len(df) > 0 else 0,
                    len(str(col_name))
                ) + 2
                worksheet.set_column(col_num, col_num, min(max_len, 35))

            # Format data cells
            for row_num in range(len(df)):
                for col_num in range(len(df.columns)):
                    value = df.iloc[row_num, col_num]
                    if pd.isna(value):
                        worksheet.write(row_num + 3, col_num, "", cell_fmt)
                    else:
                        worksheet.write(row_num + 3, col_num, value, cell_fmt)

            # Add conditional formatting for numeric columns
            if len(df) > 0:
                for col_num, col_name in enumerate(df.columns):
                    if df[col_name].dtype in ["float64", "int64"]:
                        worksheet.conditional_format(
                            3, col_num, len(df) + 2, col_num,
                            {
                                "type": "3_color_scale",
                                "min_color": "#f87171",
                                "mid_color": "#fbbf24",
                                "max_color": "#22c55e",
                            }
                        )

            # Freeze panes
            worksheet.freeze_panes(3, 1)

        # Add a cover sheet
        _create_cover_sheet(workbook, writer)

    conn.close()
    print(f"  ✅ Excel saved: {EXCEL_PATH}")


def _create_dashboard_summary(conn):
    """Create a summary DataFrame for the dashboard sheet."""
    data = {
        "Metric": [
            "Total Market Size (2025)",
            "Market CAGR (2025-2034)",
            "Carpooling CAGR",
            "EV Shared CAGR",
            "BlaBlaCar India Users (2025)",
            "QuickRide Revenue (FY25)",
            "sRide Users",
            "Total Competitor Features",
            "Go To Go Target Features",
            "Blue Ocean Opportunities",
            "Cities Covered (All Competitors)",
            "Underserved Tier-2 Cities",
        ],
        "Value": [
            "$109.5 Billion",
            "6.2%",
            "10.6%",
            "31.5%",
            "20 Million",
            "₹50-100 Crore",
            "3 Million+",
            "27 features analyzed",
            "27/27 (100%)",
            "7 unique features",
            "15 unique cities",
            "6+ cities",
        ],
        "Source": [
            "IMARC Group",
            "IMARC Group",
            "Future Market Insights",
            "Calculated",
            "BlaBlaCar Official",
            "Tracxn",
            "sRide Official",
            "Analysis",
            "Target Plan",
            "Gap Analysis",
            "Database",
            "Gap Analysis",
        ],
        "Category": [
            "Market", "Market", "Market", "Market",
            "Competitor", "Competitor", "Competitor",
            "Features", "Features", "Features",
            "Geography", "Geography",
        ]
    }
    return pd.DataFrame(data)


def _create_revenue_pivot(conn):
    """Create revenue pivot table."""
    query = """
        SELECT company_name, fiscal_year, revenue_usd_mn
        FROM financials
        ORDER BY company_name, fiscal_year
    """
    df = pd.read_sql_query(query, conn)
    pivot = df.pivot_table(values="revenue_usd_mn", index="fiscal_year",
                           columns="company_name", aggfunc="sum")
    pivot = pivot.reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(columns={"fiscal_year": "Year"})
    return pivot


def _create_user_pivot(conn):
    """Create user growth pivot table."""
    query = """
        SELECT company_name, year, users_millions, passengers_millions
        FROM user_growth ORDER BY company_name, year
    """
    df = pd.read_sql_query(query, conn)
    pivot = df.pivot_table(values="users_millions", index="year",
                           columns="company_name", aggfunc="sum")
    pivot = pivot.reset_index()
    pivot.columns.name = None
    pivot = pivot.rename(columns={"year": "Year"})
    return pivot


def _create_cagr_analysis(conn):
    """Create CAGR analysis table."""
    df = pd.read_sql_query("SELECT * FROM market_data WHERE year IN (2025, 2034)", conn)

    segments = {
        "Total Market": "total_market_usd_bn",
        "Carpooling": "carpooling_segment_bn",
        "Ride-Hailing": "ride_hailing_segment_bn",
        "EV Shared": "ev_shared_segment_bn",
        "Bike Share": "bike_share_segment_bn",
        "Corporate Mobility": "corporate_mobility_bn",
    }

    rows = []
    for label, col in segments.items():
        start = df[df["year"] == 2025][col].values[0]
        end = df[df["year"] == 2034][col].values[0]
        cagr = (np.power(end / start, 1 / 9) - 1) * 100
        growth = ((end - start) / start) * 100
        rows.append({
            "Segment": label,
            "2025 (USD Bn)": round(start, 2),
            "2034 (USD Bn)": round(end, 2),
            "Absolute Growth (USD Bn)": round(end - start, 2),
            "Growth (%)": round(growth, 1),
            "CAGR (%)": round(cagr, 1),
        })
    return pd.DataFrame(rows)


def _create_market_share(conn):
    """Create market share analysis."""
    df = pd.read_sql_query("""
        SELECT company_name,
               SUM(estimated_users) as total_users,
               COUNT(city) as cities_covered
        FROM city_coverage
        GROUP BY company_name
    """, conn)
    total = df["total_users"].sum()
    df["Market Share (%)"] = round(df["total_users"] / total * 100, 1)
    df = df.rename(columns={
        "company_name": "Company",
        "total_users": "Total Users",
        "cities_covered": "Cities Covered"
    })
    return df.sort_values("Total Users", ascending=False)


def _create_feature_scorecard(conn):
    """Create feature advantage scorecard."""
    df = pd.read_sql_query("SELECT * FROM features", conn)

    weights = {"Must Have": 3, "Differentiator": 5, "Blue Ocean": 7,
               "Revenue Stream": 4, "Retention": 4, "Add Feature": 2}

    companies = {"quickride": "QuickRide", "blablacar": "BlaBlaCar",
                 "sride": "sRide", "go_to_go": "Go To Go Cars"}

    rows = []
    max_possible = sum(weights.get(row["priority"], 1) for _, row in df.iterrows())

    for comp, label in companies.items():
        total = 0
        features = 0
        for _, row in df.iterrows():
            if row[comp] == 1:
                total += weights.get(row["priority"], 1)
                features += 1
        rows.append({
            "Company": label,
            "Features Supported": features,
            "Total Features": len(df),
            "Coverage (%)": round(features / len(df) * 100, 1),
            "Weighted Score": total,
            "Max Score": max_possible,
            "Score (%)": round(total / max_possible * 100, 1),
        })
    return pd.DataFrame(rows)


def _create_cover_sheet(workbook, writer):
    """Create a cover sheet for the Excel workbook."""
    worksheet = workbook.add_worksheet("Cover")
    writer.sheets["Cover"] = worksheet

    # Move cover to first position
    worksheet.set_first_sheet()

    title_fmt = workbook.add_format({
        "bold": True, "font_size": 28, "font_color": "#6366f1",
        "align": "center", "valign": "vcenter"
    })
    subtitle_fmt = workbook.add_format({
        "font_size": 16, "font_color": "#666666",
        "align": "center", "valign": "vcenter"
    })
    info_fmt = workbook.add_format({
        "font_size": 12, "font_color": "#333333",
        "align": "center", "valign": "vcenter"
    })
    sheet_fmt = workbook.add_format({
        "font_size": 11, "font_color": "#6366f1",
        "align": "left", "valign": "vcenter", "bold": True
    })
    desc_fmt = workbook.add_format({
        "font_size": 10, "font_color": "#888888",
        "align": "left", "text_wrap": True
    })

    worksheet.set_column("A:A", 5)
    worksheet.set_column("B:B", 35)
    worksheet.set_column("C:C", 60)

    worksheet.merge_range("A2:C2", "🚗 GO TO GO CARS", title_fmt)
    worksheet.merge_range("A3:C3", "Competitive Market & Trend Analysis", subtitle_fmt)
    worksheet.merge_range("A5:C5", "Report Date: July 2026 | Tools: SQL, Pandas, NumPy, "
                          "Matplotlib, Seaborn", info_fmt)
    worksheet.merge_range("A6:C6", "Competitors: QuickRide | BlaBlaCar | sRide", info_fmt)

    # Sheet index
    worksheet.write("B8", "Sheet Name", workbook.add_format({
        "bold": True, "font_size": 12, "bottom": 2
    }))
    worksheet.write("C8", "Description", workbook.add_format({
        "bold": True, "font_size": 12, "bottom": 2
    }))

    sheets_info = [
        ("Dashboard Summary", "Key metrics and findings at a glance"),
        ("Companies", "Master company data — funding, ratings, downloads"),
        ("Financial Data", "Revenue trends (2021-2025) for all competitors"),
        ("User Growth", "User & passenger growth trajectory (2020-2026)"),
        ("Feature Comparison", "27-feature comparison matrix with priorities"),
        ("Market Data", "India shared mobility market projections (2020-2034)"),
        ("Demographics", "User age/gender distribution by company"),
        ("City Coverage", "Geographic presence and estimated users per city"),
        ("App Reviews", "Sentiment analysis — ratings by review category"),
        ("SWOT Analysis", "Strengths, Weaknesses, Opportunities, Threats"),
        ("Funding Rounds", "Historical funding round details"),
        ("Revenue Pivot", "Revenue pivot table — companies as columns"),
        ("User Growth Pivot", "User growth pivot — for chart creation"),
        ("CAGR Analysis", "Compound Annual Growth Rate by market segment"),
        ("Market Share", "Market share by total user base"),
        ("Feature Score Card", "Weighted feature advantage scoring"),
    ]

    for i, (name, desc) in enumerate(sheets_info, start=9):
        worksheet.write(f"B{i}", name, sheet_fmt)
        worksheet.write(f"C{i}", desc, desc_fmt)


# ============================================================
# EXPORT 2: CSV FILES FOR POWER BI
# ============================================================
def export_csvs():
    """Export individual CSV files optimized for Power BI import."""
    conn = get_connection()

    print("\n📁 Generating CSV files for Power BI...")

    tables = {
        "dim_companies": "SELECT * FROM companies",
        "dim_cities": """
            SELECT DISTINCT city, tier FROM city_coverage
        """,
        "dim_features": """
            SELECT feature_name, category, priority FROM features
        """,
        "fact_financials": """
            SELECT company_name, fiscal_year as year,
                   revenue_inr_cr, revenue_usd_mn,
                   yoy_growth_pct, ebitda_positive
            FROM financials
        """,
        "fact_user_growth": """
            SELECT company_name, year,
                   users_millions, passengers_millions,
                   yoy_growth_pct
            FROM user_growth
        """,
        "fact_market_data": """
            SELECT * FROM market_data
        """,
        "fact_city_coverage": """
            SELECT company_name, city, tier,
                   estimated_users
            FROM city_coverage
        """,
        "fact_features": """
            SELECT feature_name, category,
                   quickride, blablacar, sride, go_to_go,
                   priority
            FROM features
        """,
        "fact_demographics": """
            SELECT company_name, age_group,
                   percentage, gender_male_pct, gender_female_pct
            FROM demographics
        """,
        "fact_reviews": """
            SELECT company_name, review_category,
                   sentiment, mention_count, avg_rating
            FROM app_reviews
        """,
        "fact_swot": """
            SELECT company_name, swot_type,
                   item, impact_score
            FROM swot_analysis
        """,
        "fact_funding": """
            SELECT company_name, round_name,
                   year, amount_usd_mn, lead_investor
            FROM funding_rounds
        """,
    }

    for filename, query in tables.items():
        df = pd.read_sql_query(query, conn)
        filepath = os.path.join(CSV_DIR, f"{filename}.csv")
        df.to_csv(filepath, index=False, encoding="utf-8-sig")
        print(f"  ✅ {filename}.csv ({len(df)} rows)")

    # Create a Power BI relationships guide
    _create_powerbi_guide()

    conn.close()
    print(f"\n📂 All CSVs saved to: {CSV_DIR}")


def _create_powerbi_guide():
    """Create a guide for setting up Power BI relationships."""
    guide = """
# Power BI Data Model Guide
# Go To Go Cars — Market Analysis
# ==========================================

## How to Import into Power BI:
1. Open Power BI Desktop
2. Click "Get Data" → "Text/CSV"
3. Import all CSV files from this folder
4. Set up relationships as described below

## Star Schema Relationships:

### Dimension Tables:
- dim_companies (company_name = Primary Key)
- dim_cities (city = Primary Key)
- dim_features (feature_name = Primary Key)

### Fact Tables:
- fact_financials → dim_companies (company_name)
- fact_user_growth → dim_companies (company_name)
- fact_city_coverage → dim_companies (company_name), dim_cities (city)
- fact_features → dim_features (feature_name)
- fact_demographics → dim_companies (company_name)
- fact_reviews → dim_companies (company_name)
- fact_swot → dim_companies (company_name)
- fact_funding → dim_companies (company_name)
- fact_market_data → standalone (year-based time series)

## Recommended Power BI Visuals:
1. KPI Cards: Total Market Size, CAGR, User Count
2. Clustered Bar: Revenue comparison by year
3. Line Chart: User growth trajectory
4. Matrix: Feature comparison heatmap
5. Map: City coverage (if lat/long added)
6. Treemap: Market share by users
7. Gauge: Feature coverage %
8. Waterfall: Funding rounds cumulative
9. Donut: Age demographics
10. Stacked Bar: Sentiment by category

## DAX Measures (Suggested):
```
Total Users = SUM(fact_city_coverage[estimated_users])
Market Share = DIVIDE([Total Users], CALCULATE([Total Users], ALL(dim_companies)))
CAGR = POWER(DIVIDE(MAX(fact_market_data[total_market_usd_bn]),
              MIN(fact_market_data[total_market_usd_bn])),
              1/DATEDIFF(MIN(fact_market_data[year]),
              MAX(fact_market_data[year]), YEAR)) - 1
Feature Coverage = DIVIDE(COUNTROWS(FILTER(fact_features, [value] = 1)),
                          COUNTROWS(fact_features))
```
"""
    guide_path = os.path.join(CSV_DIR, "_POWERBI_SETUP_GUIDE.txt")
    with open(guide_path, "w", encoding="utf-8") as f:
        f.write(guide)
    print("  ✅ Power BI setup guide created")


# ============================================================
# EXPORT 3: QUICK SQL REFERENCE QUERIES
# ============================================================
def export_sql_queries():
    """Export useful SQL queries for reference."""
    queries = """
-- ============================================================
-- GO TO GO CARS — USEFUL SQL QUERIES
-- Database: market_analysis.db (SQLite)
-- ============================================================

-- 1. Company Overview with Latest Revenue
SELECT
    c.company_name,
    c.focus_area,
    c.funding_total_usd,
    c.app_rating,
    f.revenue_usd_mn AS latest_revenue_mn,
    f.fiscal_year
FROM companies c
LEFT JOIN financials f ON c.company_name = f.company_name
    AND f.fiscal_year = (
        SELECT MAX(fiscal_year)
        FROM financials
        WHERE company_name = c.company_name
    )
ORDER BY f.revenue_usd_mn DESC;

-- 2. Revenue Growth Trend (Pivot-style)
SELECT
    fiscal_year,
    MAX(CASE WHEN company_name = 'QuickRide' THEN revenue_usd_mn END) AS QuickRide,
    MAX(CASE WHEN company_name = 'BlaBlaCar' THEN revenue_usd_mn END) AS BlaBlaCar,
    MAX(CASE WHEN company_name = 'sRide' THEN revenue_usd_mn END) AS sRide
FROM financials
GROUP BY fiscal_year
ORDER BY fiscal_year;

-- 3. User Growth with Running Total
SELECT
    company_name,
    year,
    users_millions,
    yoy_growth_pct,
    SUM(users_millions) OVER (
        PARTITION BY company_name ORDER BY year
    ) AS cumulative_users
FROM user_growth
ORDER BY company_name, year;

-- 4. Features Only Available in Go To Go (Blue Ocean)
SELECT feature_name, category, priority
FROM features
WHERE go_to_go = 1
    AND quickride = 0
    AND blablacar = 0
    AND sride = 0
ORDER BY category;

-- 5. City Coverage Overlap Analysis
SELECT
    city,
    GROUP_CONCAT(company_name, ', ') AS present_companies,
    COUNT(company_name) AS num_competitors,
    SUM(estimated_users) AS total_users
FROM city_coverage
GROUP BY city
HAVING num_competitors > 1
ORDER BY total_users DESC;

-- 6. Top Cities for Each Company
SELECT
    company_name,
    city,
    estimated_users,
    tier,
    RANK() OVER (
        PARTITION BY company_name ORDER BY estimated_users DESC
    ) AS rank_in_company
FROM city_coverage
WHERE is_active = 1
ORDER BY company_name, rank_in_company;

-- 7. Market Segment Year-over-Year Growth
SELECT
    year,
    total_market_usd_bn,
    ROUND((total_market_usd_bn - LAG(total_market_usd_bn)
        OVER (ORDER BY year)) / LAG(total_market_usd_bn)
        OVER (ORDER BY year) * 100, 1) AS yoy_growth_pct,
    carpooling_segment_bn,
    ev_shared_segment_bn
FROM market_data
ORDER BY year;

-- 8. Sentiment Analysis — Weighted Average Rating
SELECT
    company_name,
    ROUND(SUM(avg_rating * mention_count) /
          SUM(mention_count), 2) AS weighted_avg_rating,
    SUM(mention_count) AS total_mentions
FROM app_reviews
GROUP BY company_name
ORDER BY weighted_avg_rating DESC;

-- 9. SWOT Summary with Average Impact
SELECT
    swot_type,
    COUNT(*) AS item_count,
    ROUND(AVG(impact_score), 1) AS avg_impact,
    MAX(impact_score) AS max_impact
FROM swot_analysis
WHERE company_name = 'Go To Go Cars'
GROUP BY swot_type
ORDER BY avg_impact DESC;

-- 10. Funding Timeline — Cumulative Investment
SELECT
    company_name,
    round_name,
    year,
    amount_usd_mn,
    SUM(amount_usd_mn) OVER (
        PARTITION BY company_name ORDER BY year
    ) AS cumulative_funding_mn,
    lead_investor
FROM funding_rounds
WHERE amount_usd_mn > 0
ORDER BY company_name, year;
"""
    query_path = os.path.join(EXPORT_DIR, "sql_queries_reference.sql")
    with open(query_path, "w", encoding="utf-8") as f:
        f.write(queries)
    print(f"  ✅ SQL queries reference: {query_path}")


# ============================================================
# MAIN
# ============================================================
def export_all():
    """Run all exports."""
    print("╔" + "═" * 58 + "╗")
    print("║  EXPORTING DATA (Excel + CSV + SQL)                   ║")
    print("╚" + "═" * 58 + "╝")

    if not os.path.exists(DB_PATH):
        create_database()

    export_excel()
    export_csvs()
    export_sql_queries()

    print("\n" + "=" * 60)
    print("✅ ALL EXPORTS COMPLETE")
    print("=" * 60)
    print(f"\n📁 Output directory: {EXPORT_DIR}")
    print(f"📊 Excel workbook: {EXCEL_PATH}")
    print(f"📂 Power BI CSVs: {CSV_DIR}")
    print(f"🔍 SQL Reference: {os.path.join(EXPORT_DIR, 'sql_queries_reference.sql')}")


if __name__ == "__main__":
    export_all()
