"""
Stats Aggregator - Combines individual stat records into player season stats
"""

from typing import List, Dict
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def aggregate_player_stats(stat_records: List[Dict]) -> Dict[str, Dict]:
    """
    Aggregate individual stat records by player
    
    The API returns one record per statType (ATT, YDS, TD, etc.)
    This function groups them by player and creates complete stat dictionaries
    
    Args:
        stat_records: List of individual stat records from API
    
    Returns:
        Dictionary mapping player names to their aggregated stats
    """
    # Group by player
    player_stats = defaultdict(lambda: {
        'player': None,
        'playerId': None,
        'position': None,
        'team': None,
        'conference': None,
        'season': None,
        'category': None,
        'stats': {}
    })
    
    for record in stat_records:
        player_name = record.get('player')
        if not player_name:
            continue
        
        # Use a composite key: player + team (handles same name on different teams)
        key = f"{player_name}|{record.get('team', 'Unknown')}"
        
        # Set base info (same for all records of this player)
        player_stats[key]['player'] = player_name
        player_stats[key]['playerId'] = record.get('playerId')
        player_stats[key]['position'] = record.get('position')
        player_stats[key]['team'] = record.get('team')
        player_stats[key]['conference'] = record.get('conference')
        player_stats[key]['season'] = record.get('season')
        player_stats[key]['category'] = record.get('category')
        
        # Add this stat to the stats dict
        stat_type = record.get('statType')
        stat_value = record.get('stat')
        
        if stat_type and stat_value:
            player_stats[key]['stats'][stat_type] = stat_value
    
    # Convert back to regular dict
    return dict(player_stats)


def convert_stats_to_model_format(aggregated_stats: Dict, season: int) -> Dict:
    """
    Convert aggregated stats to database model format
    
    Args:
        aggregated_stats: Stats dictionary for one player
        season: Season year
    
    Returns:
        Dictionary ready for database insertion
    """
    category = aggregated_stats.get('category', '').lower()
    stats_dict = aggregated_stats.get('stats', {})
    
    # Initialize all stat categories
    passing_stats = None
    rushing_stats = None
    receiving_stats = None
    defensive_stats = None
    
    # Convert to appropriate format based on category
    if 'pass' in category:
        passing_stats = {
            'completions': _safe_int(stats_dict.get('C/ATT', '').split('/')[0] if '/' in str(stats_dict.get('C/ATT', '')) else stats_dict.get('COMPLETIONS')),
            'attempts': _safe_int(stats_dict.get('ATT', stats_dict.get('ATTEMPTS'))),
            'yards': _safe_int(stats_dict.get('YDS', stats_dict.get('YARDS'))),
            'touchdowns': _safe_int(stats_dict.get('TD', stats_dict.get('TOUCHDOWNS'))),
            'interceptions': _safe_int(stats_dict.get('INT', stats_dict.get('INTERCEPTIONS'))),
            'yards_per_attempt': _safe_float(stats_dict.get('YPA', stats_dict.get('AVG'))),
            'completion_percentage': _safe_float(stats_dict.get('PCT', stats_dict.get('COMP_PCT'))),
            'qbr': _safe_float(stats_dict.get('QBR'))
        }
    
    elif 'rush' in category:
        rushing_stats = {
            'attempts': _safe_int(stats_dict.get('CAR', stats_dict.get('ATT', stats_dict.get('ATTEMPTS')))),
            'yards': _safe_int(stats_dict.get('YDS', stats_dict.get('YARDS'))),
            'touchdowns': _safe_int(stats_dict.get('TD', stats_dict.get('TOUCHDOWNS'))),
            'yards_per_carry': _safe_float(stats_dict.get('AVG', stats_dict.get('YPC'))),
            'long': _safe_int(stats_dict.get('LONG', stats_dict.get('LNG')))
        }
    
    elif 'receiv' in category:
        receiving_stats = {
            'receptions': _safe_int(stats_dict.get('REC', stats_dict.get('RECEPTIONS'))),
            'yards': _safe_int(stats_dict.get('YDS', stats_dict.get('YARDS'))),
            'touchdowns': _safe_int(stats_dict.get('TD', stats_dict.get('TOUCHDOWNS'))),
            'yards_per_reception': _safe_float(stats_dict.get('AVG', stats_dict.get('YPC'))),
            'long': _safe_int(stats_dict.get('LONG', stats_dict.get('LNG')))
        }
    
    elif 'def' in category or 'defense' in category:
        defensive_stats = {
            'tackles': _safe_int(stats_dict.get('TOT', stats_dict.get('TOTAL'))),
            'solo_tackles': _safe_int(stats_dict.get('SOLO')),
            'sacks': _safe_float(stats_dict.get('SACKS', stats_dict.get('SACK'))),
            'tackles_for_loss': _safe_float(stats_dict.get('TFL')),
            'interceptions': _safe_int(stats_dict.get('INT')),
            'passes_defended': _safe_int(stats_dict.get('PD', stats_dict.get('PBU')))
        }
    
    return {
        'season': season,
        'team': aggregated_stats.get('team'),
        'passing_stats': passing_stats,
        'rushing_stats': rushing_stats,
        'receiving_stats': receiving_stats,
        'defensive_stats': defensive_stats,
    }


def _safe_int(value):
    """Safely convert to integer"""
    if value is None or value == '':
        return None
    try:
        # Handle cases like "237/350" - take first number
        if isinstance(value, str) and '/' in value:
            value = value.split('/')[0]
        return int(float(str(value).strip()))
    except (ValueError, TypeError):
        return None


def _safe_float(value):
    """Safely convert to float"""
    if value is None or value == '':
        return None
    try:
        return float(str(value).strip())
    except (ValueError, TypeError):
        return None


def aggregate_all_categories(all_stats: Dict[str, List[Dict]], season: int) -> List[Dict]:
    """
    Aggregate stats across all categories for each player
    
    Args:
        all_stats: Dictionary with categories as keys (passing, rushing, etc.)
        season: Season year
    
    Returns:
        List of player stat dictionaries ready for database
    """
    # First, aggregate within each category
    aggregated_by_category = {}
    
    for category, records in all_stats.items():
        if not records:
            continue
        
        logger.info(f"Aggregating {len(records)} {category} records...")
        aggregated = aggregate_player_stats(records)
        aggregated_by_category[category] = aggregated
    
    # Now merge all categories for each player
    # Use player name + team as the merge key (same as the aggregation key)
    all_players = {}
    
    for category, player_dict in aggregated_by_category.items():
        for key, stats in player_dict.items():
            # The key is already "player|team"
            if key not in all_players:
                all_players[key] = {
                    'player': stats['player'],
                    'playerId': stats['playerId'],
                    'position': stats['position'],
                    'team': stats['team'],
                    'conference': stats['conference'],
                    'season': season,
                    'passing_stats': None,
                    'rushing_stats': None,
                    'receiving_stats': None,
                    'defensive_stats': None
                }
            
            # Convert and merge this category's stats
            model_format = convert_stats_to_model_format(stats, season)
            
            # Merge stats - don't overwrite if already set
            if model_format.get('passing_stats') and not all_players[key]['passing_stats']:
                all_players[key]['passing_stats'] = model_format['passing_stats']
            if model_format.get('rushing_stats') and not all_players[key]['rushing_stats']:
                all_players[key]['rushing_stats'] = model_format['rushing_stats']
            if model_format.get('receiving_stats') and not all_players[key]['receiving_stats']:
                all_players[key]['receiving_stats'] = model_format['receiving_stats']
            if model_format.get('defensive_stats') and not all_players[key]['defensive_stats']:
                all_players[key]['defensive_stats'] = model_format['defensive_stats']
    
    # Convert to list
    result = list(all_players.values())
    logger.info(f"Aggregated into {len(result)} unique player-team combinations")
    
    return result


# Test the aggregator
if __name__ == '__main__':
    # Example usage
    sample_records = [
        {'player': 'Will Rogers', 'playerId': '102597', 'position': 'QB', 'team': 'Mississippi State', 
         'conference': 'SEC', 'season': 2023, 'category': 'passing', 'statType': 'ATT', 'stat': '450'},
        {'player': 'Will Rogers', 'playerId': '102597', 'position': 'QB', 'team': 'Mississippi State',
         'conference': 'SEC', 'season': 2023, 'category': 'passing', 'statType': 'YDS', 'stat': '3540'},
        {'player': 'Will Rogers', 'playerId': '102597', 'position': 'QB', 'team': 'Mississippi State',
         'conference': 'SEC', 'season': 2023, 'category': 'passing', 'statType': 'TD', 'stat': '28'},
    ]
    
    aggregated = aggregate_player_stats(sample_records)
    print("Aggregated stats:")
    for key, stats in aggregated.items():
        print(f"{key}: {stats}")

