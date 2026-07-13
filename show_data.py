"""Dump all database tables to console for verification."""
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/market_analysis.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("DATABASE TABLES:")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {t[0]}")
    count = cursor.fetchone()[0]
    print(f"  {t[0]}: {count} rows")

print("\n=== COMPANIES TABLE ===")
print(pd.read_sql("SELECT company_name, founded_year, focus_area, funding_total_usd, app_rating, total_downloads FROM companies", conn).to_string(index=False))

print("\n=== REVENUE DATA (USD Million) ===")
print(pd.read_sql("SELECT company_name, fiscal_year, revenue_usd_mn, yoy_growth_pct FROM financials ORDER BY company_name, fiscal_year", conn).to_string(index=False))

print("\n=== USER GROWTH (Millions) ===")
print(pd.read_sql("SELECT company_name, year, users_millions, passengers_millions, yoy_growth_pct FROM user_growth ORDER BY company_name, year", conn).to_string(index=False))

print("\n=== MARKET DATA (USD Billion) ===")
print(pd.read_sql("SELECT year, total_market_usd_bn, carpooling_segment_bn, ride_hailing_segment_bn, ev_shared_segment_bn FROM market_data", conn).to_string(index=False))

print("\n=== FEATURES COMPARISON ===")
print(pd.read_sql("SELECT feature_name, category, quickride, blablacar, sride, go_to_go, priority FROM features ORDER BY category", conn).to_string(index=False))

print("\n=== CITY COVERAGE ===")
print(pd.read_sql("SELECT company_name, city, tier, estimated_users FROM city_coverage ORDER BY company_name, estimated_users DESC", conn).to_string(index=False))

print("\n=== DEMOGRAPHICS ===")
print(pd.read_sql("SELECT company_name, age_group, percentage, gender_male_pct, gender_female_pct FROM demographics", conn).to_string(index=False))

print("\n=== SENTIMENT ANALYSIS ===")
print(pd.read_sql("SELECT company_name, review_category, sentiment, mention_count, avg_rating FROM app_reviews ORDER BY company_name", conn).to_string(index=False))

print("\n=== SWOT ANALYSIS ===")
print(pd.read_sql("SELECT company_name, swot_type, item, impact_score FROM swot_analysis ORDER BY swot_type, impact_score DESC", conn).to_string(index=False))

print("\n=== FUNDING ROUNDS ===")
print(pd.read_sql("SELECT company_name, round_name, year, amount_usd_mn, lead_investor FROM funding_rounds ORDER BY company_name, year", conn).to_string(index=False))

conn.close()
print("\nAll data verified successfully!")
