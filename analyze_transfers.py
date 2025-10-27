"""
Transfer Portal Analysis
Analyze player movement patterns and validate model predictions
"""

from database import get_session
from database.models import Player, Team, Transfer, PerformanceStat
from collections import defaultdict
import json

session = get_session()

print("="*80)
print("TRANSFER PORTAL ANALYSIS - 2023 Season")
print("="*80)

# Get all transfers
transfers = session.query(Transfer).filter_by(season=2023).all()
print(f"\nTotal Transfers: {len(transfers)}")

# Analyze transfer patterns
transfer_patterns = {
    'total_transfers': len(transfers),
    'with_destination': 0,
    'entering_portal': 0,
    'by_month': defaultdict(int),
    'top_destinations': defaultdict(int),
    'top_sources': defaultdict(int)
}

for transfer in transfers:
    if transfer.to_team:
        transfer_patterns['with_destination'] += 1
        transfer_patterns['top_destinations'][transfer.to_team] += 1
    else:
        transfer_patterns['entering_portal'] += 1
    
    if transfer.from_team:
        transfer_patterns['top_sources'][transfer.from_team] += 1
    
    # Track by month if date available
    if transfer.transfer_date:
        month = transfer.transfer_date.month
        transfer_patterns['by_month'][month] += 1

print(f"Transfers with destination: {transfer_patterns['with_destination']}")
print(f"Entering portal (no destination yet): {transfer_patterns['entering_portal']}")

# Top destinations
print("\n" + "-"*80)
print("TOP 20 TRANSFER DESTINATIONS")
print("-"*80)
top_destinations = sorted(transfer_patterns['top_destinations'].items(), 
                         key=lambda x: x[1], reverse=True)[:20]
for i, (team, count) in enumerate(top_destinations, 1):
    print(f"{i:2}. {team:30} - {count:3} transfers IN")

# Top sources (most players leaving)
print("\n" + "-"*80)
print("TOP 20 SCHOOLS WITH MOST DEPARTURES")
print("-"*80)
top_sources = sorted(transfer_patterns['top_sources'].items(), 
                    key=lambda x: x[1], reverse=True)[:20]
for i, (team, count) in enumerate(top_sources, 1):
    print(f"{i:2}. {team:30} - {count:3} transfers OUT")

# Calculate net transfer balance (IN - OUT)
print("\n" + "-"*80)
print("NET TRANSFER BALANCE (Top 20 Gainers)")
print("-"*80)

all_teams = set(list(transfer_patterns['top_destinations'].keys()) + 
                list(transfer_patterns['top_sources'].keys()))

net_balance = {}
for team in all_teams:
    transfers_in = transfer_patterns['top_destinations'].get(team, 0)
    transfers_out = transfer_patterns['top_sources'].get(team, 0)
    net_balance[team] = transfers_in - transfers_out

top_gainers = sorted(net_balance.items(), key=lambda x: x[1], reverse=True)[:20]
for i, (team, balance) in enumerate(top_gainers, 1):
    sign = "+" if balance >= 0 else ""
    print(f"{i:2}. {team:30} - {sign}{balance}")

# Bottom 20 (most net losses)
print("\n" + "-"*80)
print("NET TRANSFER BALANCE (Top 20 Losers)")
print("-"*80)
top_losers = sorted(net_balance.items(), key=lambda x: x[1])[:20]
for i, (team, balance) in enumerate(top_losers, 1):
    print(f"{i:2}. {team:30} - {balance}")

# Transfer timing analysis
print("\n" + "-"*80)
print("TRANSFER TIMING (By Month)")
print("-"*80)
month_names = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December"
}

for month in sorted(transfer_patterns['by_month'].keys()):
    count = transfer_patterns['by_month'][month]
    pct = (count / len(transfers) * 100) if transfers else 0
    bar = "█" * int(pct / 2)
    print(f"{month_names[month]:10} - {count:4} ({pct:5.1f}%) {bar}")

# Find players who transferred with stats
print("\n" + "-"*80)
print("HIGH-PERFORMING TRANSFERS (Had Stats Before Transfer)")
print("-"*80)

transfers_with_stats = []
for transfer in transfers[:100]:  # Sample first 100
    player = session.query(Player).filter_by(id=transfer.player_id).first()
    if player:
        # Check if they had stats in 2022 (before 2023 transfer)
        stats_2022 = session.query(PerformanceStat).filter_by(
            player_id=player.id,
            season=2022
        ).first()
        
        if stats_2022 and (stats_2022.passing_stats or stats_2022.rushing_stats or stats_2022.receiving_stats):
            transfers_with_stats.append({
                'player': player.name,
                'position': player.position,
                'from': transfer.from_team,
                'to': transfer.to_team,
                'had_2022_stats': True
            })

if transfers_with_stats:
    print(f"\nFound {len(transfers_with_stats)} transfers with prior statistics (sample)")
    for i, t in enumerate(transfers_with_stats[:10], 1):
        print(f"{i:2}. {t['player']:25} ({t['position']}) - {t['from']} → {t['to']}")
else:
    print("\nNote: To see which transfers had stats, collect 2022 season data:")
    print("  python collect_data.py --year 2022")

# Transfer movement types
print("\n" + "-"*80)
print("TRANSFER ANALYSIS SUMMARY")
print("-"*80)
print(f"Total Players in Portal: {len(transfers)}")
print(f"Completed Transfers (have destination): {transfer_patterns['with_destination']}")
print(f"Portal Entries (no known destination): {transfer_patterns['entering_portal']}")
print(f"Unique Destination Schools: {len(transfer_patterns['top_destinations'])}")
print(f"Unique Source Schools: {len(transfer_patterns['top_sources'])}")

# Export transfer analysis
output = {
    'season': 2023,
    'total_transfers': len(transfers),
    'summary': transfer_patterns,
    'top_destinations': dict(top_destinations[:20]),
    'top_sources': dict(top_sources[:20]),
    'net_balance_top_gainers': dict(top_gainers[:20]),
    'net_balance_top_losers': dict(top_losers[:20])
}

with open('outputs/transfer_analysis_2023.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n[SUCCESS] Transfer analysis exported to outputs/transfer_analysis_2023.json")

print("\n" + "="*80)
print("Transfer Portal Analysis Complete!")
print("="*80)

session.close()

