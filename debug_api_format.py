"""
Debug script to examine actual API response format
"""

from scrapers.cfb_api_client import CollegeFootballDataAPI
import json

client = CollegeFootballDataAPI()

print("="*70)
print("Testing API Response Formats")
print("="*70)

# Test 1: Roster format
print("\n1. ROSTER FORMAT (Alabama 2023):")
print("-"*70)
roster = client.get_roster('Alabama', 2023)
if roster and len(roster) > 0:
    print(f"Total players: {len(roster)}")
    print("\nFirst player data structure:")
    print(json.dumps(roster[0], indent=2))
    print("\nKeys available:", roster[0].keys())
else:
    print("No roster data returned")

# Test 2: Player stats format
print("\n\n2. PLAYER STATS FORMAT (2023 Passing):")
print("-"*70)
stats = client.get_player_season_stats(2023, stat_category='passing')
if stats and len(stats) > 0:
    print(f"Total stat records: {len(stats)}")
    print("\nFirst stat record:")
    print(json.dumps(stats[0], indent=2))
    print("\nKeys available:", stats[0].keys())
else:
    print("No stats data returned")

# Test 3: Transfer portal format
print("\n\n3. TRANSFER PORTAL FORMAT (2023):")
print("-"*70)
transfers = client.get_transfer_portal(2023)
if transfers and len(transfers) > 0:
    print(f"Total transfers: {len(transfers)}")
    print("\nFirst transfer record:")
    print(json.dumps(transfers[0], indent=2))
    print("\nKeys available:", transfers[0].keys())
else:
    print("No transfer data returned")

print("\n" + "="*70)
print("Done! Use this information to fix the transformers.")
print("="*70)

