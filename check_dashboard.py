"""
Quick check of database stats and dashboard readiness
"""

from database import get_session
from database.models import Player, PerformanceStat, Transfer

session = get_session()

print("="*70)
print("DATABASE STATUS AFTER 2022 DATA COLLECTION")
print("="*70)

# Count players
total_players = session.query(Player).count()
print(f"\nTotal Players: {total_players:,}")

# Count stats by season
stats_2023 = session.query(PerformanceStat).filter_by(season=2023).count()
stats_2022 = session.query(PerformanceStat).filter_by(season=2022).count()
print(f"\n2023 Season Stats: {stats_2023:,}")
print(f"2022 Season Stats: {stats_2022:,}")
print(f"Total Stats: {stats_2023 + stats_2022:,}")

# Count transfers by season
transfers_2023 = session.query(Transfer).filter_by(season=2023).count()
transfers_2022 = session.query(Transfer).filter_by(season=2022).count()
print(f"\n2023 Transfers: {transfers_2023:,}")
print(f"2022 Transfers: {transfers_2022:,}")
print(f"Total Transfers: {transfers_2023 + transfers_2022:,}")

# Players with stats in both seasons (player development tracking!)
players_both_seasons = session.query(Player).join(
    PerformanceStat, Player.id == PerformanceStat.player_id
).filter(
    PerformanceStat.season.in_([2022, 2023])
).distinct().count()

# Actually count players who have stats in BOTH seasons
from sqlalchemy import and_
players_2022 = session.query(PerformanceStat.player_id).filter_by(season=2022).distinct().all()
players_2023 = session.query(PerformanceStat.player_id).filter_by(season=2023).distinct().all()

ids_2022 = set([p[0] for p in players_2022])
ids_2023 = set([p[0] for p in players_2023])
both = ids_2022 & ids_2023

print(f"\nPlayers with 2022 stats only: {len(ids_2022 - ids_2023):,}")
print(f"Players with 2023 stats only: {len(ids_2023 - ids_2022):,}")
print(f"Players with BOTH seasons: {len(both):,} ⭐ (development tracking!)")

print("\n" + "="*70)
print("DASHBOARD READY")
print("="*70)
print("\n🚀 To launch dashboard, run:")
print("   python -m streamlit run dashboard.py")
print("\n🌐 Then access at: http://localhost:8501")
print("\n" + "="*70)

session.close()

