import sqlite3
import os
import numpy as np
import pandas as pd
from database_setup import create_database, DB_PATH


def get_connection():
    """Get SQLite database connection. Create DB if it doesn't exist."""
    if not os.path.exists(DB_PATH):
        create_database()
    return sqlite3.connect(DB_PATH)


# ============================================================
# SECTION 1: COMPANY OVERVIEW ANALYSIS
# ============================================================
def analyze_companies():
    """SQL + Pandas analysis of competitor companies."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("📊 SECTION 1: COMPANY OVERVIEW")
    print("=" * 70)

    # SQL query to get company overview
    query = """
        SELECT
            company_name,
            founded_year,
            headquarters,
            focus_area,
            funding_total_usd,
            funding_status,
            app_rating,
            total_downloads
        FROM companies
        ORDER BY funding_total_usd DESC
    """
    df_companies = pd.read_sql_query(query, conn)

    # NumPy calculations
    funded_amounts = df_companies[df_companies["funding_total_usd"] > 0]["funding_total_usd"].values
    print("\n🏢 Company Comparison:")
    print(df_companies.to_string(index=False))
    print(f"\n📈 Funding Statistics (funded companies only):")
    print(f"   Total funding in market:  ${np.sum(funded_amounts):,.0f}")
    print(f"   Average funding:          ${np.mean(funded_amounts):,.0f}")
    print(f"   Median funding:           ${np.median(funded_amounts):,.0f}")
    print(f"   Std deviation:            ${np.std(funded_amounts):,.0f}")

    # Company age analysis
    df_companies["company_age"] = 2026 - df_companies["founded_year"]
    print(f"\n🕐 Company Ages:")
    for _, row in df_companies.iterrows():
        print(f"   {row['company_name']}: {row['company_age']} years "
              f"({'New entrant' if row['company_age'] <= 1 else 'Established'})")

    conn.close()
    return df_companies


# ============================================================
# SECTION 2: FINANCIAL ANALYSIS
# ============================================================
def analyze_financials():
    """Deep financial analysis with SQL + Pandas + NumPy."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("💰 SECTION 2: FINANCIAL ANALYSIS")
    print("=" * 70)

    # SQL: Revenue trends with window functions
    query = """
        SELECT
            company_name,
            fiscal_year,
            revenue_usd_mn,
            yoy_growth_pct,
            ebitda_positive,
            CASE WHEN ebitda_positive = 1 THEN 'Profitable'
                 ELSE 'Not Profitable' END as profitability
        FROM financials
        ORDER BY company_name, fiscal_year
    """
    df_fin = pd.read_sql_query(query, conn)

    # Pivot table: Revenue by company and year
    pivot_revenue = df_fin.pivot_table(
        values="revenue_usd_mn",
        index="fiscal_year",
        columns="company_name",
        aggfunc="sum"
    )
    print("\n💵 Revenue Comparison (USD Million):")
    print(pivot_revenue.to_string())

    # NumPy: Calculate CAGR for each company
    print("\n📊 Compound Annual Growth Rate (CAGR):")
    for company in df_fin["company_name"].unique():
        company_data = df_fin[df_fin["company_name"] == company].dropna(subset=["revenue_usd_mn"])
        if len(company_data) >= 2:
            start_rev = company_data.iloc[0]["revenue_usd_mn"]
            end_rev = company_data.iloc[-1]["revenue_usd_mn"]
            years = company_data.iloc[-1]["fiscal_year"] - company_data.iloc[0]["fiscal_year"]
            if start_rev > 0 and years > 0:
                cagr = (np.power(end_rev / start_rev, 1 / years) - 1) * 100
                print(f"   {company}: {cagr:.1f}% CAGR ({company_data.iloc[0]['fiscal_year']}-{company_data.iloc[-1]['fiscal_year']})")

    # Growth volatility analysis
    print("\n📉 Revenue Growth Volatility (Std Dev of YoY Growth):")
    for company in df_fin["company_name"].unique():
        growth_data = df_fin[(df_fin["company_name"] == company) &
                            (df_fin["yoy_growth_pct"].notna())]["yoy_growth_pct"].values
        if len(growth_data) > 0:
            volatility = np.std(growth_data)
            avg_growth = np.mean(growth_data)
            print(f"   {company}: Avg Growth={avg_growth:.1f}%, Volatility={volatility:.1f}%")

    # Profitability analysis
    print("\n✅ Profitability Timeline:")
    for company in df_fin["company_name"].unique():
        company_data = df_fin[df_fin["company_name"] == company]
        profitable_years = company_data[company_data["ebitda_positive"] == 1]["fiscal_year"].values
        if len(profitable_years) > 0:
            print(f"   {company}: Profitable since {profitable_years[0]}")
        else:
            print(f"   {company}: Not yet profitable")

    conn.close()
    return df_fin


# ============================================================
# SECTION 3: USER GROWTH ANALYSIS
# ============================================================
def analyze_user_growth():
    """User growth trajectory analysis."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("👥 SECTION 3: USER GROWTH ANALYSIS")
    print("=" * 70)

    query = """
        SELECT
            company_name,
            year,
            users_millions,
            passengers_millions,
            yoy_growth_pct
        FROM user_growth
        ORDER BY company_name, year
    """
    df_users = pd.read_sql_query(query, conn)

    # Pivot: Users over time
    pivot_users = df_users.pivot_table(
        values="users_millions",
        index="year",
        columns="company_name",
        aggfunc="sum"
    )
    print("\n👤 Registered Users (Millions):")
    print(pivot_users.to_string())

    # Growth rate comparison
    print("\n📈 Average Annual Growth Rate:")
    growth_summary = df_users.groupby("company_name")["yoy_growth_pct"].agg(
        ["mean", "min", "max", "std"]
    ).round(1)
    growth_summary.columns = ["Avg Growth %", "Min Growth %", "Max Growth %", "Std Dev"]
    print(growth_summary.to_string())

    # Predict 2027–2030 using NumPy polynomial fit
    print("\n🔮 Growth Projections (2027–2030) — Linear Trend Extrapolation:")
    for company in df_users["company_name"].unique():
        company_data = df_users[df_users["company_name"] == company]
        x = company_data["year"].values.astype(float)
        y = company_data["users_millions"].values

        # Fit a 2nd degree polynomial
        coeffs = np.polyfit(x, y, 2)
        poly = np.poly1d(coeffs)

        projections = []
        for proj_year in [2027, 2028, 2029, 2030]:
            predicted = max(poly(proj_year), y[-1])  # At least current level
            projections.append(f"{proj_year}: {predicted:.1f}M")

        print(f"   {company}: {', '.join(projections)}")

    # Market share analysis (2026)
    latest = df_users[df_users["year"] == 2026]
    total_users = latest["users_millions"].sum()
    print(f"\n🥧 Market Share by Users (2026):")
    for _, row in latest.iterrows():
        share = (row["users_millions"] / total_users) * 100
        print(f"   {row['company_name']}: {row['users_millions']}M users ({share:.1f}%)")

    conn.close()
    return df_users


# ============================================================
# SECTION 4: FEATURE GAP ANALYSIS
# ============================================================
def analyze_features():
    """Feature comparison and gap analysis."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("🔍 SECTION 4: FEATURE GAP ANALYSIS")
    print("=" * 70)

    query = """
        SELECT
            feature_name,
            category,
            quickride,
            blablacar,
            sride,
            go_to_go,
            priority
        FROM features
        ORDER BY category, feature_name
    """
    df_features = pd.read_sql_query(query, conn)

    # Feature count per company
    print("\n📋 Feature Coverage (Total Features: {})".format(len(df_features)))
    competitors = ["quickride", "blablacar", "sride", "go_to_go"]
    labels = ["QuickRide", "BlaBlaCar", "sRide", "Go To Go Cars"]
    for comp, label in zip(competitors, labels):
        count = df_features[comp].sum()
        pct = (count / len(df_features)) * 100
        print(f"   {label}: {count}/{len(df_features)} features ({pct:.0f}%)")

    # Category-wise analysis
    print("\n📂 Feature Coverage by Category:")
    category_summary = df_features.groupby("category")[competitors].sum()
    category_total = df_features.groupby("category").size()
    for cat in category_summary.index:
        total = category_total[cat]
        print(f"\n   [{cat}] ({total} features):")
        for comp, label in zip(competitors, labels):
            count = category_summary.loc[cat, comp]
            print(f"      {label}: {count}/{total}")

    # Blue Ocean features (only Go To Go has them)
    blue_ocean = df_features[df_features["priority"] == "Blue Ocean"]
    print(f"\n🌊 Blue Ocean Opportunities (unique to Go To Go): {len(blue_ocean)}")
    for _, row in blue_ocean.iterrows():
        print(f"   ★ {row['feature_name']} [{row['category']}]")

    # Competitive advantage score using NumPy
    print("\n🏆 Feature Advantage Score (NumPy weighted analysis):")
    weights = {"Must Have": 3, "Differentiator": 5, "Blue Ocean": 7,
               "Revenue Stream": 4, "Retention": 4, "Add Feature": 2}
    for comp, label in zip(competitors, labels):
        scores = []
        for _, row in df_features.iterrows():
            if row[comp] == 1:
                weight = weights.get(row["priority"], 1)
                scores.append(weight)
        total_score = np.sum(scores)
        max_possible = sum(weights.get(row["priority"], 1) for _, row in df_features.iterrows())
        print(f"   {label}: {total_score}/{max_possible} "
              f"({(total_score / max_possible * 100):.0f}%)")

    conn.close()
    return df_features


# ============================================================
# SECTION 5: MARKET SIZE & TREND ANALYSIS
# ============================================================
def analyze_market():
    """Market size, segments, and growth trend analysis."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("📈 SECTION 5: MARKET SIZE & TREND ANALYSIS")
    print("=" * 70)

    query = """
        SELECT * FROM market_data ORDER BY year
    """
    df_market = pd.read_sql_query(query, conn)

    # Current market snapshot
    current = df_market[df_market["year"] == 2025].iloc[0]
    future = df_market[df_market["year"] == 2034].iloc[0]
    print(f"\n🌍 India Shared Mobility Market:")
    print(f"   2025 Size: ${current['total_market_usd_bn']:.1f} Billion")
    print(f"   2034 Projection: ${future['total_market_usd_bn']:.1f} Billion")

    # CAGR calculation per segment
    segments = ["total_market_usd_bn", "carpooling_segment_bn",
                "ride_hailing_segment_bn", "ev_shared_segment_bn",
                "bike_share_segment_bn", "corporate_mobility_bn"]
    segment_labels = ["Total Market", "Carpooling", "Ride-Hailing",
                      "EV Shared Rides", "Bike/Scooter Share", "Corporate Mobility"]

    print(f"\n📊 Segment CAGR Analysis (2025–2034):")
    cagr_data = []
    for seg, label in zip(segments, segment_labels):
        start = df_market[df_market["year"] == 2025][seg].values[0]
        end = df_market[df_market["year"] == 2034][seg].values[0]
        years = 9
        cagr = (np.power(end / start, 1 / years) - 1) * 100
        cagr_data.append({"Segment": label, "2025 ($Bn)": start,
                          "2034 ($Bn)": end, "CAGR (%)": round(cagr, 1)})
        print(f"   {label}: ${start:.1f}B → ${end:.1f}B (CAGR: {cagr:.1f}%)")

    df_cagr = pd.DataFrame(cagr_data)

    # Fastest growing segment
    fastest = df_cagr.loc[df_cagr["CAGR (%)"].idxmax()]
    print(f"\n🚀 Fastest Growing Segment: {fastest['Segment']} ({fastest['CAGR (%)']}% CAGR)")

    # Year-over-year total market growth
    df_market["yoy_growth"] = df_market["total_market_usd_bn"].pct_change() * 100
    print(f"\n📅 Year-over-Year Market Growth:")
    for _, row in df_market.iterrows():
        if not np.isnan(row["yoy_growth"]):
            bar = "█" * int(row["yoy_growth"])
            print(f"   {int(row['year'])}: {row['yoy_growth']:5.1f}% {bar}")

    # Correlation analysis between segments
    segment_cols = ["carpooling_segment_bn", "ride_hailing_segment_bn",
                    "ev_shared_segment_bn", "corporate_mobility_bn"]
    corr_matrix = df_market[segment_cols].corr()
    print(f"\n🔗 Segment Correlation Matrix:")
    print(corr_matrix.round(3).to_string())

    conn.close()
    return df_market


# ============================================================
# SECTION 6: DEMOGRAPHIC ANALYSIS
# ============================================================
def analyze_demographics():
    """User demographic analysis."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("👤 SECTION 6: DEMOGRAPHIC ANALYSIS")
    print("=" * 70)

    query = """
        SELECT
            company_name,
            age_group,
            percentage,
            gender_male_pct,
            gender_female_pct
        FROM demographics
        ORDER BY company_name, age_group
    """
    df_demo = pd.read_sql_query(query, conn)

    # Age distribution pivot
    pivot_age = df_demo.pivot_table(
        values="percentage",
        index="age_group",
        columns="company_name"
    )
    print("\n📊 Age Distribution (%):")
    print(pivot_age.to_string())

    # Gender gap analysis
    print("\n⚧ Gender Distribution Analysis:")
    gender_summary = df_demo.groupby("company_name").agg(
        avg_male=("gender_male_pct", "mean"),
        avg_female=("gender_female_pct", "mean")
    ).round(1)
    for company in gender_summary.index:
        male = gender_summary.loc[company, "avg_male"]
        female = gender_summary.loc[company, "avg_female"]
        gap = male - female
        print(f"   {company}: Male {male}%, Female {female}% (Gap: {gap:.1f}%)")

    # Target demographic identification
    print("\n🎯 Primary Target Demographic per Company:")
    for company in df_demo["company_name"].unique():
        company_data = df_demo[df_demo["company_name"] == company]
        dominant = company_data.loc[company_data["percentage"].idxmax()]
        print(f"   {company}: {dominant['age_group']} ({dominant['percentage']}%)")

    conn.close()
    return df_demo


# ============================================================
# SECTION 7: CITY COVERAGE & GEOGRAPHIC ANALYSIS
# ============================================================
def analyze_cities():
    """Geographic coverage and opportunity analysis."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("🗺️ SECTION 7: CITY COVERAGE & GEOGRAPHIC ANALYSIS")
    print("=" * 70)

    query = """
        SELECT
            company_name,
            city,
            tier,
            estimated_users
        FROM city_coverage
        WHERE is_active = 1
        ORDER BY company_name, estimated_users DESC
    """
    df_cities = pd.read_sql_query(query, conn)

    # City count per company
    city_count = df_cities.groupby("company_name")["city"].count()
    print("\n🏙️ City Coverage:")
    for company, count in city_count.items():
        total_users = df_cities[df_cities["company_name"] == company]["estimated_users"].sum()
        print(f"   {company}: {count} cities, {total_users:,} estimated users")

    # Tier analysis
    print("\n📍 Coverage by City Tier:")
    tier_analysis = df_cities.groupby(["company_name", "tier"]).agg(
        cities=("city", "count"),
        total_users=("estimated_users", "sum")
    )
    print(tier_analysis.to_string())

    # Overlap analysis — cities served by multiple companies
    city_presence = df_cities.groupby("city")["company_name"].apply(list)
    print("\n🔄 City Competition Overlap:")
    for city, companies in city_presence.items():
        if len(companies) > 1:
            print(f"   {city}: {', '.join(companies)} ({len(companies)} competitors)")

    # Underserved cities — only 1 or 0 competitors
    all_cities = df_cities["city"].unique()
    metro_cities = ["Bengaluru", "Delhi NCR", "Mumbai", "Pune", "Hyderabad",
                    "Chennai", "Kolkata", "Ahmedabad"]
    tier2_potential = ["Jaipur", "Lucknow", "Indore", "Nagpur", "Bhopal",
                       "Coimbatore", "Chandigarh", "Vizag", "Kochi",
                       "Trivandrum", "Patna", "Surat"]

    underserved = [c for c in tier2_potential if c not in all_cities or
                   len(city_presence.get(c, [])) <= 1]
    print(f"\n🎯 Underserved Tier-2 Cities (Opportunity for Go To Go):")
    for city in underserved:
        competitors = len(city_presence.get(city, []))
        print(f"   {city}: {competitors} competitor(s) — {'Wide Open' if competitors == 0 else 'Low Competition'}")

    conn.close()
    return df_cities


# ============================================================
# SECTION 8: SENTIMENT & REVIEW ANALYSIS
# ============================================================
def analyze_reviews():
    """App review sentiment analysis."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("💬 SECTION 8: APP REVIEW SENTIMENT ANALYSIS")
    print("=" * 70)

    query = """
        SELECT
            company_name,
            review_category,
            sentiment,
            mention_count,
            avg_rating
        FROM app_reviews
        ORDER BY company_name, mention_count DESC
    """
    df_reviews = pd.read_sql_query(query, conn)

    # Overall sentiment score per company
    print("\n📊 Overall Review Sentiment Score:")
    for company in df_reviews["company_name"].unique():
        company_data = df_reviews[df_reviews["company_name"] == company]
        # Weighted average rating by mention count
        weighted_avg = np.average(
            company_data["avg_rating"].values,
            weights=company_data["mention_count"].values
        )
        total_mentions = company_data["mention_count"].sum()
        print(f"   {company}: {weighted_avg:.2f}/5.0 (based on {total_mentions:,} mentions)")

    # Sentiment breakdown
    print("\n😊 Sentiment Distribution:")
    sentiment_pivot = df_reviews.groupby(
        ["company_name", "sentiment"]
    )["mention_count"].sum().unstack(fill_value=0)
    print(sentiment_pivot.to_string())

    # Pain points (low-rated categories)
    print("\n⚠️ Top Pain Points (Rating < 3.5):")
    pain_points = df_reviews[df_reviews["avg_rating"] < 3.5].sort_values("avg_rating")
    for _, row in pain_points.iterrows():
        print(f"   {row['company_name']} → {row['review_category']}: "
              f"{row['avg_rating']}/5.0 ({row['mention_count']} mentions)")

    # Strengths (high-rated categories)
    print("\n✅ Top Strengths (Rating >= 4.3):")
    strengths = df_reviews[df_reviews["avg_rating"] >= 4.3].sort_values(
        "avg_rating", ascending=False
    )
    for _, row in strengths.iterrows():
        print(f"   {row['company_name']} → {row['review_category']}: "
              f"{row['avg_rating']}/5.0 ({row['mention_count']} mentions)")

    conn.close()
    return df_reviews


# ============================================================
# SECTION 9: STATISTICAL SUMMARY
# ============================================================
def statistical_summary():
    """NumPy/Pandas statistical summary across all datasets."""
    conn = get_connection()

    print("\n" + "=" * 70)
    print("📐 SECTION 9: STATISTICAL SUMMARY")
    print("=" * 70)

    # Revenue statistics
    df_fin = pd.read_sql_query("SELECT * FROM financials", conn)
    print("\n📊 Revenue Distribution (USD Million) — All Companies, All Years:")
    revenue_stats = df_fin["revenue_usd_mn"].dropna().describe()
    print(f"   Count:  {revenue_stats['count']:.0f}")
    print(f"   Mean:   ${revenue_stats['mean']:.2f}M")
    print(f"   Median: ${revenue_stats['50%']:.2f}M")
    print(f"   Std:    ${revenue_stats['std']:.2f}M")
    print(f"   Min:    ${revenue_stats['min']:.2f}M")
    print(f"   Max:    ${revenue_stats['max']:.2f}M")
    print(f"   Skew:   {df_fin['revenue_usd_mn'].dropna().skew():.2f}")
    print(f"   Kurtosis: {df_fin['revenue_usd_mn'].dropna().kurtosis():.2f}")

    # User growth statistics
    df_users = pd.read_sql_query("SELECT * FROM user_growth", conn)
    print(f"\n👥 User Growth Distribution:")
    print(f"   Total data points: {len(df_users)}")
    print(f"   Avg users (millions): {df_users['users_millions'].mean():.2f}M")
    print(f"   Avg YoY growth: {df_users['yoy_growth_pct'].dropna().mean():.1f}%")

    # Market concentration (Herfindahl Index)
    df_city_users = pd.read_sql_query("""
        SELECT company_name, SUM(estimated_users) as total_users
        FROM city_coverage GROUP BY company_name
    """, conn)
    total = df_city_users["total_users"].sum()
    market_shares = (df_city_users["total_users"] / total * 100).values
    hhi = np.sum(market_shares ** 2)
    print(f"\n📏 Market Concentration (HHI): {hhi:.0f}")
    if hhi < 1500:
        print("   → Competitive market (HHI < 1500)")
    elif hhi < 2500:
        print("   → Moderately concentrated (1500 < HHI < 2500)")
    else:
        print("   → Highly concentrated (HHI > 2500)")

    conn.close()


# ============================================================
# MAIN EXECUTION
# ============================================================
def run_full_analysis():
    """Run the complete analysis pipeline."""
    print("╔" + "═" * 68 + "╗")
    print("║  GO TO GO CARS — COMPETITIVE MARKET ANALYSIS                      ║")
    print("║  Using: SQL (SQLite) | Pandas | NumPy                             ║")
    print("║  Report Date: July 2026                                           ║")
    print("╚" + "═" * 68 + "╝")

    # Ensure database exists
    if not os.path.exists(DB_PATH):
        create_database()

    # Run all analysis sections
    df_companies = analyze_companies()
    df_financials = analyze_financials()
    df_users = analyze_user_growth()
    df_features = analyze_features()
    df_market = analyze_market()
    df_demographics = analyze_demographics()
    df_cities = analyze_cities()
    df_reviews = analyze_reviews()
    statistical_summary()

    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    print("Next steps:")
    print("  1. Run visualizations.py for Matplotlib & Seaborn charts")
    print("  2. Run export_to_excel_powerbi.py for Excel & Power BI data")
    print("=" * 70)

    return {
        "companies": df_companies,
        "financials": df_financials,
        "users": df_users,
        "features": df_features,
        "market": df_market,
        "demographics": df_demographics,
        "cities": df_cities,
        "reviews": df_reviews,
    }


if __name__ == "__main__":
    run_full_analysis()
