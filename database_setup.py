import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "market_analysis.db")


def create_database():
    """Create the SQLite database and populate all tables."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --------------------------------------------------
    # TABLE 1: Companies (Master Table)
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            company_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL UNIQUE,
            founded_year    INTEGER,
            headquarters    TEXT,
            focus_area      TEXT,
            funding_total_usd REAL,
            funding_status  TEXT,
            employee_count  TEXT,
            app_rating      REAL,
            total_downloads TEXT,
            website         TEXT
        )
    """)

    companies_data = [
        ("QuickRide", 2014, "Hyderabad, India", "Intra-city Carpooling & Taxi",
         15800000, "Series B", "51-200", 4.5, "1M+", "quickride.in"),
        ("BlaBlaCar", 2006, "Paris, France", "Intercity Carpooling",
         600000000, "Series F", "501-1000", 4.5, "100M+", "blablacar.in"),
        ("sRide", 2015, "Gurugram, India", "Corporate Carpooling",
         0, "Bootstrapped", "11-50", 4.2, "1M+", "sride.co"),
        ("Go To Go Cars", 2026, "India", "Unified Carpool & Taxi",
         0, "Pre-Seed", "1-10", 0, "0", "gotogocars.com"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO companies
        (company_name, founded_year, headquarters, focus_area,
         funding_total_usd, funding_status, employee_count,
         app_rating, total_downloads, website)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, companies_data)

    # --------------------------------------------------
    # TABLE 2: Financial Data (Yearly)
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financials (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            fiscal_year     INTEGER NOT NULL,
            revenue_inr_cr  REAL,
            revenue_usd_mn  REAL,
            yoy_growth_pct  REAL,
            ebitda_positive INTEGER,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    financials_data = [
        # QuickRide
        ("QuickRide", 2021, 12, 1.5, None, 0),
        ("QuickRide", 2022, 22, 2.7, 83.3, 0),
        ("QuickRide", 2023, 35, 4.3, 59.1, 0),
        ("QuickRide", 2024, 55, 6.8, 57.1, 0),
        ("QuickRide", 2025, 75, 9.2, 36.4, 1),
        # BlaBlaCar (Global, EUR → USD approx)
        ("BlaBlaCar", 2021, None, 120, None, 0),
        ("BlaBlaCar", 2022, None, 195, 62.5, 0),
        ("BlaBlaCar", 2023, None, 275, 41.0, 1),
        ("BlaBlaCar", 2024, None, 320, 16.4, 1),
        ("BlaBlaCar", 2025, None, 370, 15.6, 1),
        # sRide (Bootstrapped, estimated)
        ("sRide", 2021, 1.5, 0.18, None, 1),
        ("sRide", 2022, 3.0, 0.37, 100.0, 1),
        ("sRide", 2023, 5.5, 0.68, 83.3, 1),
        ("sRide", 2024, 8.0, 0.98, 45.5, 1),
        ("sRide", 2025, 12.0, 1.47, 50.0, 1),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO financials
        (company_name, fiscal_year, revenue_inr_cr, revenue_usd_mn,
         yoy_growth_pct, ebitda_positive)
        VALUES (?, ?, ?, ?, ?, ?)
    """, financials_data)

    # --------------------------------------------------
    # TABLE 3: User Growth (Monthly/Yearly)
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_growth (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            year            INTEGER NOT NULL,
            users_millions  REAL,
            passengers_millions REAL,
            yoy_growth_pct  REAL,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    user_growth_data = [
        # QuickRide (registered users)
        ("QuickRide", 2020, 0.5, 0.3, None),
        ("QuickRide", 2021, 0.7, 0.45, 40.0),
        ("QuickRide", 2022, 1.0, 0.65, 42.9),
        ("QuickRide", 2023, 1.4, 0.9, 40.0),
        ("QuickRide", 2024, 1.9, 1.3, 35.7),
        ("QuickRide", 2025, 2.5, 1.8, 31.6),
        ("QuickRide", 2026, 3.2, 2.3, 28.0),
        # BlaBlaCar India (passengers)
        ("BlaBlaCar", 2020, 8, 3, None),
        ("BlaBlaCar", 2021, 10, 4.5, 25.0),
        ("BlaBlaCar", 2022, 14, 7, 40.0),
        ("BlaBlaCar", 2023, 18, 9.5, 28.6),
        ("BlaBlaCar", 2024, 24, 13.5, 33.3),
        ("BlaBlaCar", 2025, 32, 20, 47.0),
        ("BlaBlaCar", 2026, 45, 30, 50.0),
        # sRide
        ("sRide", 2020, 0.3, 0.15, None),
        ("sRide", 2021, 0.5, 0.25, 66.7),
        ("sRide", 2022, 0.8, 0.45, 60.0),
        ("sRide", 2023, 1.2, 0.7, 50.0),
        ("sRide", 2024, 1.8, 1.1, 50.0),
        ("sRide", 2025, 2.5, 1.6, 38.9),
        ("sRide", 2026, 3.2, 2.1, 28.0),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO user_growth
        (company_name, year, users_millions, passengers_millions, yoy_growth_pct)
        VALUES (?, ?, ?, ?, ?)
    """, user_growth_data)

    # --------------------------------------------------
    # TABLE 4: Features Comparison
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS features (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            feature_name    TEXT NOT NULL,
            category        TEXT,
            quickride       INTEGER DEFAULT 0,
            blablacar       INTEGER DEFAULT 0,
            sride           INTEGER DEFAULT 0,
            go_to_go        INTEGER DEFAULT 0,
            priority        TEXT
        )
    """)

    features_data = [
        ("Intra-city Carpooling", "Core Service", 1, 0, 1, 1, "Must Have"),
        ("Intercity Carpooling", "Core Service", 0, 1, 0, 1, "Differentiator"),
        ("Taxi/Cab Booking", "Core Service", 1, 0, 0, 1, "Must Have"),
        ("Bike Pooling", "Core Service", 1, 0, 1, 1, "Add Feature"),
        ("Taxipool (Shared Cab)", "Core Service", 0, 0, 1, 1, "Differentiator"),
        ("AI-Powered Matching", "Technology", 0, 0, 1, 1, "Must Have"),
        ("Dynamic Pricing AI", "Technology", 0, 0, 0, 1, "Blue Ocean"),
        ("ML Demand Prediction", "Technology", 0, 0, 0, 1, "Blue Ocean"),
        ("Corporate Email Verify", "Trust & Safety", 1, 0, 1, 1, "Must Have"),
        ("LinkedIn Verification", "Trust & Safety", 0, 0, 1, 1, "Differentiator"),
        ("Aadhaar Verification", "Trust & Safety", 0, 0, 0, 1, "Blue Ocean"),
        ("Live Ride Tracking", "Trust & Safety", 1, 1, 1, 1, "Must Have"),
        ("SOS/Emergency Button", "Trust & Safety", 1, 1, 1, 1, "Must Have"),
        ("Women-Only Pools", "Trust & Safety", 0, 0, 0, 1, "Blue Ocean"),
        ("Guardian Live Share", "Trust & Safety", 0, 0, 0, 1, "Blue Ocean"),
        ("ESG Dashboard", "Corporate", 0, 0, 1, 1, "Differentiator"),
        ("Corporate Admin Panel", "Corporate", 0, 0, 1, 1, "Must Have"),
        ("Employee Transport Mgmt", "Corporate", 0, 0, 0, 1, "Blue Ocean"),
        ("Subscription Model", "Monetization", 0, 1, 0, 1, "Revenue Stream"),
        ("In-App Wallet", "Monetization", 0, 0, 0, 1, "Blue Ocean"),
        ("Loyalty Cashback", "Monetization", 0, 0, 0, 1, "Retention"),
        ("Gamification/Badges", "Engagement", 0, 0, 1, 1, "Retention"),
        ("Leaderboards", "Engagement", 0, 0, 0, 1, "Retention"),
        ("Carbon Offset Tracker", "Engagement", 0, 0, 1, 1, "Differentiator"),
        ("Referral Program", "Growth", 1, 1, 1, 1, "Must Have"),
        ("EV Fleet Integration", "Innovation", 0, 0, 0, 1, "Blue Ocean"),
        ("Multi-modal Transit", "Innovation", 0, 0, 0, 1, "Blue Ocean"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO features
        (feature_name, category, quickride, blablacar, sride, go_to_go, priority)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, features_data)

    # --------------------------------------------------
    # TABLE 5: Market Data (India Shared Mobility)
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_data (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            year            INTEGER NOT NULL,
            total_market_usd_bn     REAL,
            carpooling_segment_bn   REAL,
            ride_hailing_segment_bn REAL,
            ev_shared_segment_bn    REAL,
            bike_share_segment_bn   REAL,
            corporate_mobility_bn   REAL
        )
    """)

    market_data = [
        (2020, 62.0, 1.2, 0.4, 0.1, 0.4, 1.2),
        (2021, 68.0, 1.5, 0.5, 0.2, 0.6, 1.5),
        (2022, 78.0, 1.9, 0.6, 0.3, 0.8, 2.0),
        (2023, 88.0, 2.3, 0.72, 0.4, 1.0, 2.5),
        (2024, 98.0, 2.8, 0.85, 0.6, 1.2, 3.0),
        (2025, 109.5, 3.5, 0.95, 0.8, 1.5, 3.5),
        (2026, 118.0, 4.2, 1.15, 1.2, 1.8, 4.2),
        (2027, 128.0, 5.0, 1.5, 1.8, 2.2, 5.0),
        (2028, 138.0, 6.0, 1.8, 2.5, 2.8, 5.8),
        (2029, 148.0, 7.2, 2.2, 3.5, 3.2, 7.0),
        (2030, 160.0, 8.5, 2.8, 5.0, 3.8, 8.5),
        (2031, 170.0, 9.5, 3.1, 6.5, 4.2, 9.0),
        (2032, 178.0, 10.5, 3.4, 7.5, 4.5, 9.5),
        (2033, 185.0, 11.5, 3.6, 8.5, 4.8, 9.8),
        (2034, 191.2, 12.5, 3.7, 9.5, 5.0, 10.0),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO market_data
        (year, total_market_usd_bn, carpooling_segment_bn,
         ride_hailing_segment_bn, ev_shared_segment_bn,
         bike_share_segment_bn, corporate_mobility_bn)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, market_data)

    # --------------------------------------------------
    # TABLE 6: User Demographics
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS demographics (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            age_group       TEXT NOT NULL,
            percentage      REAL,
            gender_male_pct REAL,
            gender_female_pct REAL,
            booking_channel TEXT,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    demographics_data = [
        # BlaBlaCar
        ("BlaBlaCar", "18-24", 30, 68, 32, "Mobile App"),
        ("BlaBlaCar", "25-34", 40, 65, 35, "Mobile App"),
        ("BlaBlaCar", "35-44", 20, 72, 28, "Mobile App"),
        ("BlaBlaCar", "45+", 10, 75, 25, "Web + App"),
        # QuickRide
        ("QuickRide", "18-24", 15, 70, 30, "Mobile App"),
        ("QuickRide", "25-34", 45, 72, 28, "Mobile App"),
        ("QuickRide", "35-44", 30, 78, 22, "Mobile App"),
        ("QuickRide", "45+", 10, 80, 20, "Mobile App"),
        # sRide
        ("sRide", "18-24", 10, 65, 35, "Mobile App"),
        ("sRide", "25-34", 50, 68, 32, "Mobile App"),
        ("sRide", "35-44", 30, 75, 25, "Mobile App"),
        ("sRide", "45+", 10, 80, 20, "Mobile App"),
        # Go To Go Target
        ("Go To Go Cars", "18-24", 25, 55, 45, "Mobile App"),
        ("Go To Go Cars", "25-34", 40, 55, 45, "Mobile App"),
        ("Go To Go Cars", "35-44", 25, 60, 40, "Mobile App"),
        ("Go To Go Cars", "45+", 10, 65, 35, "Mobile App"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO demographics
        (company_name, age_group, percentage, gender_male_pct,
         gender_female_pct, booking_channel)
        VALUES (?, ?, ?, ?, ?, ?)
    """, demographics_data)

    # --------------------------------------------------
    # TABLE 7: City Coverage
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS city_coverage (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            city            TEXT NOT NULL,
            tier            TEXT,
            is_active       INTEGER DEFAULT 1,
            estimated_users INTEGER,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    cities_data = [
        # QuickRide cities
        ("QuickRide", "Bengaluru", "Tier-1", 1, 500000),
        ("QuickRide", "Hyderabad", "Tier-1", 1, 400000),
        ("QuickRide", "Pune", "Tier-1", 1, 350000),
        ("QuickRide", "Delhi NCR", "Tier-1", 1, 300000),
        ("QuickRide", "Mumbai", "Tier-1", 1, 280000),
        ("QuickRide", "Chennai", "Tier-1", 1, 200000),
        ("QuickRide", "Kolkata", "Tier-1", 1, 150000),
        ("QuickRide", "Kochi", "Tier-2", 1, 80000),
        ("QuickRide", "Trivandrum", "Tier-2", 1, 60000),
        # BlaBlaCar cities (intercity hubs)
        ("BlaBlaCar", "Delhi NCR", "Tier-1", 1, 3000000),
        ("BlaBlaCar", "Mumbai", "Tier-1", 1, 2500000),
        ("BlaBlaCar", "Bengaluru", "Tier-1", 1, 2200000),
        ("BlaBlaCar", "Pune", "Tier-1", 1, 1800000),
        ("BlaBlaCar", "Hyderabad", "Tier-1", 1, 1500000),
        ("BlaBlaCar", "Chennai", "Tier-1", 1, 1200000),
        ("BlaBlaCar", "Kolkata", "Tier-1", 1, 1000000),
        ("BlaBlaCar", "Jaipur", "Tier-2", 1, 800000),
        ("BlaBlaCar", "Ahmedabad", "Tier-1", 1, 700000),
        ("BlaBlaCar", "Lucknow", "Tier-2", 1, 500000),
        ("BlaBlaCar", "Chandigarh", "Tier-2", 1, 400000),
        ("BlaBlaCar", "Indore", "Tier-2", 1, 350000),
        # sRide cities
        ("sRide", "Pune", "Tier-1", 1, 600000),
        ("sRide", "Hyderabad", "Tier-1", 1, 500000),
        ("sRide", "Bengaluru", "Tier-1", 1, 450000),
        ("sRide", "Delhi NCR", "Tier-1", 1, 400000),
        ("sRide", "Mumbai", "Tier-1", 1, 350000),
        ("sRide", "Chennai", "Tier-1", 1, 250000),
        ("sRide", "Kolkata", "Tier-1", 1, 200000),
        ("sRide", "Coimbatore", "Tier-2", 1, 80000),
        ("sRide", "Jaipur", "Tier-2", 1, 70000),
        ("sRide", "Ahmedabad", "Tier-1", 1, 60000),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO city_coverage
        (company_name, city, tier, is_active, estimated_users)
        VALUES (?, ?, ?, ?, ?)
    """, cities_data)

    # --------------------------------------------------
    # TABLE 8: App Reviews / Sentiment Analysis
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_reviews (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            review_category TEXT NOT NULL,
            sentiment       TEXT,
            mention_count   INTEGER,
            avg_rating      REAL,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    reviews_data = [
        # QuickRide
        ("QuickRide", "Ride Matching", "Positive", 1200, 4.2),
        ("QuickRide", "App UI/UX", "Positive", 800, 4.0),
        ("QuickRide", "Safety Features", "Positive", 650, 4.3),
        ("QuickRide", "Pricing", "Mixed", 900, 3.5),
        ("QuickRide", "Customer Support", "Negative", 450, 2.8),
        ("QuickRide", "Driver Quality", "Positive", 700, 4.1),
        ("QuickRide", "Wait Time", "Negative", 550, 3.0),
        # BlaBlaCar
        ("BlaBlaCar", "Ride Matching", "Positive", 3500, 4.4),
        ("BlaBlaCar", "App UI/UX", "Positive", 2200, 4.3),
        ("BlaBlaCar", "Safety Features", "Mixed", 1800, 3.8),
        ("BlaBlaCar", "Pricing", "Positive", 4000, 4.5),
        ("BlaBlaCar", "Customer Support", "Negative", 1200, 2.5),
        ("BlaBlaCar", "Driver Quality", "Mixed", 1500, 3.7),
        ("BlaBlaCar", "Wait Time", "Mixed", 800, 3.5),
        # sRide
        ("sRide", "Ride Matching", "Positive", 800, 4.5),
        ("sRide", "App UI/UX", "Mixed", 500, 3.6),
        ("sRide", "Safety Features", "Positive", 600, 4.4),
        ("sRide", "Pricing", "Positive", 700, 4.3),
        ("sRide", "Customer Support", "Negative", 350, 2.9),
        ("sRide", "Driver Quality", "Positive", 450, 4.2),
        ("sRide", "Wait Time", "Negative", 400, 3.2),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO app_reviews
        (company_name, review_category, sentiment, mention_count, avg_rating)
        VALUES (?, ?, ?, ?, ?)
    """, reviews_data)

    # --------------------------------------------------
    # TABLE 9: SWOT Analysis
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS swot_analysis (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            swot_type       TEXT NOT NULL,
            item            TEXT NOT NULL,
            impact_score    INTEGER,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    swot_data = [
        # Go To Go Cars
        ("Go To Go Cars", "Strength", "Late-mover advantage — learn from competitor mistakes", 8),
        ("Go To Go Cars", "Strength", "Unified platform (intra-city + intercity + taxi) from day one", 10),
        ("Go To Go Cars", "Strength", "AI/ML native architecture — no legacy tech debt", 9),
        ("Go To Go Cars", "Strength", "First EV-integrated carpool platform opportunity", 9),
        ("Go To Go Cars", "Strength", "Women safety features as brand pillar", 8),
        ("Go To Go Cars", "Weakness", "Zero existing user base — cold-start problem", 9),
        ("Go To Go Cars", "Weakness", "No brand recognition or trust yet", 8),
        ("Go To Go Cars", "Weakness", "Competing against VC-funded incumbents", 7),
        ("Go To Go Cars", "Weakness", "Network effects favor established players", 8),
        ("Go To Go Cars", "Weakness", "Regulatory compliance to build from scratch", 6),
        ("Go To Go Cars", "Opportunity", "No single app covers all transport modes", 10),
        ("Go To Go Cars", "Opportunity", "$109.5B market growing at 6.2% CAGR", 9),
        ("Go To Go Cars", "Opportunity", "Government LiFE initiative promotes carpooling", 8),
        ("Go To Go Cars", "Opportunity", "EV fleet integration — untapped niche", 9),
        ("Go To Go Cars", "Opportunity", "Tier-2/3 cities massively underserved", 8),
        ("Go To Go Cars", "Opportunity", "Corporate ESG compliance demand surging", 7),
        ("Go To Go Cars", "Threat", "Uber/Ola can enter carpooling at massive scale", 9),
        ("Go To Go Cars", "Threat", "BlaBlaCar explosive growth (100M user target)", 8),
        ("Go To Go Cars", "Threat", "Price wars in cost-sensitive market", 7),
        ("Go To Go Cars", "Threat", "Regulatory changes may increase costs", 6),
        ("Go To Go Cars", "Threat", "Trust very hard to build in P2P services", 8),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO swot_analysis
        (company_name, swot_type, item, impact_score)
        VALUES (?, ?, ?, ?)
    """, swot_data)

    # --------------------------------------------------
    # TABLE 10: Funding Rounds
    # --------------------------------------------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS funding_rounds (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name    TEXT NOT NULL,
            round_name      TEXT,
            year            INTEGER,
            amount_usd_mn   REAL,
            lead_investor   TEXT,
            FOREIGN KEY (company_name) REFERENCES companies(company_name)
        )
    """)

    funding_data = [
        ("QuickRide", "Seed", 2015, 0.5, "Angel Investors"),
        ("QuickRide", "Series A", 2017, 5.0, "Sequoia Capital"),
        ("QuickRide", "Series B", 2019, 10.3, "Naspers"),
        ("BlaBlaCar", "Series A", 2011, 10.0, "ISAI"),
        ("BlaBlaCar", "Series B", 2012, 10.0, "Accel Partners"),
        ("BlaBlaCar", "Series C", 2014, 100.0, "Index Ventures"),
        ("BlaBlaCar", "Series D", 2015, 200.0, "Insight Partners"),
        ("BlaBlaCar", "Series E", 2018, 115.0, "Vostok New Ventures"),
        ("BlaBlaCar", "Series F", 2021, 115.0, "VNV Global"),
        ("sRide", "Bootstrapped", 2015, 0, "Self-funded"),
    ]

    cursor.executemany("""
        INSERT OR REPLACE INTO funding_rounds
        (company_name, round_name, year, amount_usd_mn, lead_investor)
        VALUES (?, ?, ?, ?, ?)
    """, funding_data)

    conn.commit()
    conn.close()
    print(f"✅ Database created successfully at: {DB_PATH}")
    print("📊 Tables created: companies, financials, user_growth, features,")
    print("   market_data, demographics, city_coverage, app_reviews,")
    print("   swot_analysis, funding_rounds")
    return DB_PATH


if __name__ == "__main__":
    create_database()
