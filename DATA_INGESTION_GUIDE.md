# Data Ingestion System - Complete Guide

## 🎯 Overview

The CAV Model includes a comprehensive data ingestion system that automatically collects player, team, and performance data from multiple sources and stores it in a local database.

---

## 📋 System Components

### 1. **Database** (`database/`)
- **SQLite** for local development (easy setup, no server required)
- **PostgreSQL** support for production (scalable, concurrent access)
- **8 Main Tables**:
  - `players` - Player biographical information
  - `teams` - Team information
  - `performance_stats` - Season statistics by player
  - `transfers` - Transfer portal activity
  - `social_media` - Brand and social media metrics
  - `nil_deals` - NIL deal information
  - `injuries` - Injury history
  - `scheme_info` - Team schemes by season
  - `data_refresh_log` - Track data collection operations

### 2. **API Client** (`scrapers/cfb_api_client.py`)
- Connects to **collegefootballdata.com** API
- Handles authentication and rate limiting
- Fetches: rosters, stats, transfers, teams, recruiting, etc.

### 3. **Web Scrapers** (`scrapers/`)
- Social media data (Instagram, Twitter followers)
- NIL deal information
- Additional public sources

### 4. **ETL Pipeline** (`etl/`)
- Transforms raw API data to database format
- Validates data quality
- Handles duplicates and updates

### 5. **Configuration** (`config/`)
- Centralized API key management
- Data collection settings
- Database configuration

---

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
pip install sqlalchemy pyyaml requests beautifulsoup4
```

Or install all at once:
```bash
pip install -r requirements.txt
```

### Step 2: Add Your API Key

1. Get a free API key from: https://collegefootballdata.com/
2. Open `config/config.yaml`
3. Add your API key:

```yaml
collegefootballdata:
  api_key: "YOUR_API_KEY_HERE"
```

### Step 3: Initialize Database

```bash
python collect_data.py --init-db
```

This creates the SQLite database at `database/cav_data.db` with all tables.

### Step 4: Test API Connection

```bash
python collect_data.py --test-api
```

You should see: `✓ API connection successful!`

### Step 5: Collect Data

**Collect everything for 2023 season:**
```bash
python collect_data.py --year 2023
```

**Collect specific teams:**
```bash
python collect_data.py --year 2023 --teams Alabama Georgia "Ohio State"
```

**Collect only rosters:**
```bash
python collect_data.py --year 2023 --rosters-only --teams Texas Michigan
```

---

## 📊 Available Data Sources

### collegefootballdata.com (Primary Source)

**What you get:**
- ✅ Player rosters with biographical info
- ✅ Season statistics (passing, rushing, receiving, defense)
- ✅ Advanced stats (PPA, success rate, etc.)
- ✅ Snap counts and usage
- ✅ Transfer portal entries
- ✅ Team information
- ✅ Recruiting data
- ✅ Game results
- ✅ Coaching staff

**API Endpoints Used:**
- `/roster` - Team rosters
- `/stats/player/season` - Player statistics
- `/player/usage` - Snap counts
- `/player/portal` - Transfer portal
- `/teams` - Team information
- `/ppa/players/season` - Advanced metrics

### Additional Sources (Manual Entry Recommended)

**Social Media:**
- Instagram follower counts
- Twitter/X follower counts
- TikTok presence
- Engagement rates

**NIL Data:**
- On3 NIL database
- 247Sports reports
- Public deal announcements

**Note:** Social media APIs have usage restrictions. The system includes placeholders for manual data entry.

---

## 🗄️ Database Schema

### Players Table
```sql
players
├── id (primary key)
├── cfb_id (collegefootballdata.com ID)
├── name, first_name, last_name
├── position, height, weight
├── hometown, state, high_school
├── class_year, eligibility_remaining
├── current_team_id (foreign key to teams)
├── is_active, is_transfer, is_injured
└── created_at, updated_at, last_data_refresh
```

### Performance Stats Table
```sql
performance_stats
├── id (primary key)
├── player_id (foreign key to players)
├── season
├── games_played, games_started, snaps_played
├── passing_stats (JSON)
├── rushing_stats (JSON)
├── receiving_stats (JSON)
├── defensive_stats (JSON)
├── pff_grade, epa_total, success_rate
└── created_at, updated_at
```

### Transfers Table
```sql
transfers
├── id (primary key)
├── player_id (foreign key to players)
├── transfer_date, season
├── from_team, to_team
├── reason_category, portal_entry_timing
├── immediate_starter, first_season_snaps
└── created_at, updated_at
```

---

## 💻 Usage Examples

### Python API Usage

```python
from database import get_session, init_database
from database.models import Player, PerformanceStat, Team
from etl.data_pipeline import DataPipeline

# Initialize database
init_database()

# Create pipeline
pipeline = DataPipeline()

# Collect specific data
pipeline.collect_teams()
pipeline.collect_roster('Alabama', 2023)
pipeline.collect_player_stats(2023)
pipeline.collect_transfers(2023)

# Query the database
session = get_session()

# Get all quarterbacks
qbs = session.query(Player).filter_by(position='QB').all()

# Get Alabama's roster
alabama = session.query(Team).filter_by(name='Alabama').first()
roster = session.query(Player).filter_by(current_team_id=alabama.id).all()

# Get 2023 stats for a player
player = session.query(Player).filter_by(name='Jalen Milroe').first()
stats = session.query(PerformanceStat).filter_by(
    player_id=player.id,
    season=2023
).first()

print(f"Passing yards: {stats.passing_stats['yards']}")

session.close()
```

### Command Line Usage

```bash
# Initialize database
python collect_data.py --init-db

# Test connection
python collect_data.py --test-api

# Collect all data for 2023
python collect_data.py --year 2023

# Collect specific teams
python collect_data.py --year 2023 --teams "Texas A&M" LSU Florida

# Collect only teams info
python collect_data.py --teams-only

# Collect only rosters
python collect_data.py --year 2023 --rosters-only --teams Alabama

# Collect only statistics
python collect_data.py --year 2023 --stats-only

# Collect only transfer portal
python collect_data.py --year 2023 --transfers-only

# Collect multiple seasons
python collect_data.py --year 2020
python collect_data.py --year 2021
python collect_data.py --year 2022
python collect_data.py --year 2023
```

---

## 🔄 Data Update Schedule

### Recommended Refresh Intervals

| Data Type | Frequency | Command |
|-----------|-----------|---------|
| Team Info | Once per season | `--teams-only` |
| Rosters | Weekly in-season | `--rosters-only` |
| Statistics | Daily in-season | `--stats-only` |
| Transfer Portal | 2x daily during portal windows | `--transfers-only` |
| Social Media | Weekly | Manual update |

### Automated Updates (Optional)

Create a scheduled task (Windows) or cron job (Linux/Mac):

**Windows Task Scheduler:**
```
Program: python
Arguments: C:\Users\jones\CAV\collect_data.py --year 2024 --stats-only
Schedule: Daily at 2:00 AM
```

**Linux/Mac Cron:**
```bash
# Edit crontab
crontab -e

# Add daily stats update at 2 AM
0 2 * * * cd /path/to/CAV && python collect_data.py --year 2024 --stats-only
```

---

## 📈 Data Quality & Validation

### Automatic Validation

The system automatically:
- ✅ Validates required fields (name, position, etc.)
- ✅ Checks for duplicate records
- ✅ Converts data types safely
- ✅ Logs errors for failed records
- ✅ Skips incomplete data

### View Collection Logs

```python
from database import get_session
from database.models import DataRefreshLog

session = get_session()

# Get recent collection logs
logs = session.query(DataRefreshLog)\
    .order_by(DataRefreshLog.created_at.desc())\
    .limit(10).all()

for log in logs:
    print(f"{log.data_type} - {log.status}")
    print(f"  Added: {log.records_added}, Updated: {log.records_updated}")
    if log.error_message:
        print(f"  Error: {log.error_message}")
```

---

## 🔧 Configuration Options

### `config/config.yaml`

```yaml
# API Settings
collegefootballdata:
  api_key: "YOUR_KEY"
  base_url: "https://api.collegefootballdata.com"
  rate_limit_per_minute: 60  # Respect API limits

# Database Settings
database:
  type: "sqlite"  # or "postgresql"
  sqlite:
    path: "database/cav_data.db"

# Data Collection
data_collection:
  seasons:
    start_year: 2020  # Earliest season to collect
    current_year: 2024
  
  positions:  # Positions to track
    - QB
    - RB
    - WR
    - TE
    - OL
    - DL
    - LB
    - CB
    - S

# Web Scraping
scraping:
  request_delay: 2  # Seconds between requests
  timeout: 30       # Request timeout
  retry_attempts: 3
```

---

## 🚨 Troubleshooting

### API Key Error
```
ValueError: API key not provided
```
**Solution:** Add your API key to `config/config.yaml`

### Rate Limit Exceeded
```
Rate limit exceeded. Waiting 60 seconds...
```
**Solution:** This is normal. The system will automatically wait and retry.

### Player Not Found
```
Player not found: John Smith
```
**Solution:** Collect roster data first before collecting stats:
```bash
python collect_data.py --year 2023 --rosters-only --teams Alabama
python collect_data.py --year 2023 --stats-only
```

### Database Locked
```
database is locked
```
**Solution:** Close any other programs accessing the database, or use PostgreSQL for concurrent access.

---

## 📊 Integrating with Valuation Model

### Load Data for Valuation

```python
from database import get_session
from database.models import Player, PerformanceStat, SocialMedia
from models.valuation_engine import create_valuation_engine

session = get_session()
engine = create_valuation_engine()

# Get player with all data
player_db = session.query(Player).filter_by(name='Jalen Milroe').first()
stats_db = session.query(PerformanceStat).filter_by(
    player_id=player_db.id, season=2023
).first()
social_db = session.query(SocialMedia).filter_by(
    player_id=player_db.id
).first()

# Convert to valuation format
player_data = {
    'player_id': player_db.cfb_id,
    'name': player_db.name,
    'position': player_db.position,
    'height': player_db.height,
    'weight': player_db.weight,
    'current_program': player_db.current_team.name,
    'eligibility_remaining': player_db.eligibility_remaining,
    
    # Stats
    'stats': stats_db.passing_stats if stats_db else {},
    'pff_grade': stats_db.pff_grade if stats_db else None,
    'snaps_played': stats_db.snaps_played if stats_db else 0,
    'games_played': stats_db.games_played if stats_db else 0,
    'team_wins': stats_db.team_wins if stats_db else 0,
    'team_losses': stats_db.team_losses if stats_db else 0,
    
    # Social media
    'instagram_followers': social_db.instagram_followers if social_db else 0,
    'twitter_followers': social_db.twitter_followers if social_db else 0,
}

# Calculate valuation
result = engine.calculate_comprehensive_valuation(
    player_data=player_data,
    current_program=player_data['current_program']
)

print(f"Market Value: ${result['market_value']:,.0f}")
```

---

## 🔐 Security & Privacy

### Best Practices

1. **Never commit API keys** to version control
   - Add `config/config.yaml` to `.gitignore`
   - Use environment variables for production

2. **Respect data usage policies**
   - Follow collegefootballdata.com terms of service
   - Rate limit your requests
   - Don't redistribute raw data

3. **Handle player data responsibly**
   - Store locally, don't expose publicly
   - Use for analysis only
   - Comply with privacy regulations

---

## 📞 Support & Resources

### API Documentation
- College Football Data: https://collegefootballdata.com/exampleRequests

### Database Tools
- SQLite Browser: https://sqlitebrowser.org/
- pgAdmin (PostgreSQL): https://www.pgadmin.org/

### Need Help?
1. Check logs: `logs/data_collection.log`
2. Review database refresh logs
3. Test API connection: `python collect_data.py --test-api`

---

## ✅ Quick Reference

```bash
# Setup
pip install -r requirements.txt
python collect_data.py --init-db
python collect_data.py --test-api

# Collect Data
python collect_data.py --year 2023
python collect_data.py --year 2023 --teams Alabama Georgia
python collect_data.py --year 2023 --stats-only

# Query Data (Python)
from database import get_session
from database.models import Player
session = get_session()
players = session.query(Player).all()
```

---

*Data Ingestion System v1.0 | October 2025*

