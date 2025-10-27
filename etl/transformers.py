"""
Data transformation functions
Convert API responses to database models
"""

from typing import Dict, List, Optional
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_string(value: any) -> Optional[str]:
    """Clean and standardize string values"""
    if value is None:
        return None
    return str(value).strip() if value else None


def safe_int(value: any) -> Optional[int]:
    """Safely convert to integer"""
    if value is None or value == '':
        return None
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def safe_float(value: any) -> Optional[float]:
    """Safely convert to float"""
    if value is None or value == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def transform_roster_data(roster_entry: Dict) -> Dict:
    """
    Transform roster API response to Player model format
    
    Args:
        roster_entry: Raw roster data from API
    
    Returns:
        Transformed player data
    """
    # Combine first and last name
    first_name = clean_string(roster_entry.get('firstName') or roster_entry.get('first_name'))
    last_name = clean_string(roster_entry.get('lastName') or roster_entry.get('last_name'))
    
    if first_name and last_name:
        full_name = f"{first_name} {last_name}"
    else:
        full_name = clean_string(roster_entry.get('name') or roster_entry.get('athlete'))
    
    return {
        'cfb_id': clean_string(roster_entry.get('id')),
        'name': full_name,
        'first_name': first_name,
        'last_name': last_name,
        'position': clean_string(roster_entry.get('position')),
        'height': safe_int(roster_entry.get('height')),
        'weight': safe_int(roster_entry.get('weight')),
        'hometown': clean_string(roster_entry.get('homeCity') or roster_entry.get('home_town') or roster_entry.get('hometown')),
        'state': clean_string(roster_entry.get('homeState') or roster_entry.get('home_state') or roster_entry.get('state')),
        'jersey_number': clean_string(roster_entry.get('jersey') or roster_entry.get('number')),
        'class_year': safe_int(roster_entry.get('year') or roster_entry.get('recruit_year')),
        'is_active': True,
        'last_data_refresh': datetime.now()
    }


def transform_stats_data(stats_entry: Dict, season: int) -> Dict:
    """
    Transform stats API response to PerformanceStat model format
    
    Args:
        stats_entry: Raw statistics data from API
        season: Season year
    
    Returns:
        Transformed stats data
    """
    # Build position-specific stats
    passing_stats = None
    rushing_stats = None
    receiving_stats = None
    defensive_stats = None
    
    category = stats_entry.get('category', '').lower()
    
    if 'pass' in category:
        passing_stats = {
            'completions': safe_int(stats_entry.get('completions') or stats_entry.get('C/ATT')),
            'attempts': safe_int(stats_entry.get('attempts') or stats_entry.get('ATT')),
            'yards': safe_int(stats_entry.get('yards') or stats_entry.get('YDS')),
            'touchdowns': safe_int(stats_entry.get('touchdowns') or stats_entry.get('TD')),
            'interceptions': safe_int(stats_entry.get('interceptions') or stats_entry.get('INT')),
            'completion_percentage': safe_float(stats_entry.get('completionPercentage') or stats_entry.get('PCT')),
            'yards_per_attempt': safe_float(stats_entry.get('yardsPerAttempt') or stats_entry.get('YPA')),
            'qbr': safe_float(stats_entry.get('qbr') or stats_entry.get('QBR'))
        }
    
    elif 'rush' in category:
        rushing_stats = {
            'attempts': safe_int(stats_entry.get('attempts') or stats_entry.get('CAR')),
            'yards': safe_int(stats_entry.get('yards') or stats_entry.get('YDS')),
            'touchdowns': safe_int(stats_entry.get('touchdowns') or stats_entry.get('TD')),
            'yards_per_carry': safe_float(stats_entry.get('yardsPerRushAttempt') or stats_entry.get('AVG')),
            'long': safe_int(stats_entry.get('long') or stats_entry.get('LONG'))
        }
    
    elif 'receiv' in category:
        receiving_stats = {
            'receptions': safe_int(stats_entry.get('receptions') or stats_entry.get('REC')),
            'yards': safe_int(stats_entry.get('yards') or stats_entry.get('YDS')),
            'touchdowns': safe_int(stats_entry.get('touchdowns') or stats_entry.get('TD')),
            'yards_per_reception': safe_float(stats_entry.get('yardsPerReception') or stats_entry.get('AVG')),
            'long': safe_int(stats_entry.get('long') or stats_entry.get('LONG'))
        }
    
    elif 'def' in category or 'defense' in category:
        defensive_stats = {
            'tackles': safe_int(stats_entry.get('tackles') or stats_entry.get('TOT')),
            'solo_tackles': safe_int(stats_entry.get('soloTackles') or stats_entry.get('SOLO')),
            'sacks': safe_float(stats_entry.get('sacks') or stats_entry.get('SACKS')),
            'tackles_for_loss': safe_float(stats_entry.get('tacklesForLoss') or stats_entry.get('TFL')),
            'interceptions': safe_int(stats_entry.get('interceptions') or stats_entry.get('INT')),
            'passes_defended': safe_int(stats_entry.get('passesDefended') or stats_entry.get('PD'))
        }
    
    return {
        'season': season,
        'team': clean_string(stats_entry.get('team') or stats_entry.get('school')),
        'games_played': safe_int(stats_entry.get('games')),
        'passing_stats': passing_stats,
        'rushing_stats': rushing_stats,
        'receiving_stats': receiving_stats,
        'defensive_stats': defensive_stats,
        'yards_per_attempt': safe_float(stats_entry.get('yardsPerAttempt')),
        'yards_per_carry': safe_float(stats_entry.get('yardsPerRushAttempt')),
    }


def transform_usage_data(usage_entry: Dict) -> Dict:
    """
    Transform player usage data (snap counts)
    
    Args:
        usage_entry: Raw usage data from API
    
    Returns:
        Transformed usage data
    """
    return {
        'snaps_played': safe_int(usage_entry.get('total')),
        'snap_percentage': safe_float(usage_entry.get('percentage')),
        'games_played': safe_int(usage_entry.get('games'))
    }


def transform_transfer_data(transfer_entry: Dict) -> Dict:
    """
    Transform transfer portal data to Transfer model format
    
    Args:
        transfer_entry: Raw transfer data from API
    
    Returns:
        Transformed transfer data
    """
    # Parse transfer date
    transfer_date = None
    if transfer_entry.get('transferDate'):
        try:
            # Handle ISO format with Z
            date_str = transfer_entry['transferDate'].replace('Z', '+00:00')
            transfer_date = datetime.fromisoformat(date_str).date()
        except (ValueError, TypeError):
            pass
    
    return {
        'transfer_date': transfer_date,
        'from_team': clean_string(transfer_entry.get('origin') or transfer_entry.get('from')),
        'to_team': clean_string(transfer_entry.get('destination') or transfer_entry.get('to')),
        'season': safe_int(transfer_entry.get('season') or transfer_entry.get('year')),
        'eligibility_at_transfer': None  # Not in simple format from API
    }


def transform_team_data(team_entry: Dict) -> Dict:
    """
    Transform team data to Team model format
    
    Args:
        team_entry: Raw team data from API
    
    Returns:
        Transformed team data
    """
    return {
        'cfb_id': clean_string(team_entry.get('id')),
        'name': clean_string(team_entry.get('school') or team_entry.get('name')),
        'school': clean_string(team_entry.get('school')),
        'abbreviation': clean_string(team_entry.get('abbreviation')),
        'conference': clean_string(team_entry.get('conference')),
        'division': clean_string(team_entry.get('division')),
        'city': clean_string(team_entry.get('location', {}).get('city')),
        'state': clean_string(team_entry.get('location', {}).get('state')),
        'color': clean_string(team_entry.get('color')),
        'alt_color': clean_string(team_entry.get('alt_color')),
        'logo_url': clean_string(team_entry.get('logos', [None])[0] if team_entry.get('logos') else None)
    }


def transform_advanced_stats(adv_stats_entry: Dict) -> Dict:
    """
    Transform advanced statistics (PFF grades, etc.)
    
    Args:
        adv_stats_entry: Raw advanced stats from API
    
    Returns:
        Transformed advanced stats
    """
    return {
        'pff_grade': safe_float(adv_stats_entry.get('pffGrade') or adv_stats_entry.get('grade')),
        'pff_pass_grade': safe_float(adv_stats_entry.get('passingGrade')),
        'pff_rush_grade': safe_float(adv_stats_entry.get('rushingGrade')),
        'pff_receive_grade': safe_float(adv_stats_entry.get('receivingGrade')),
        'pff_defense_grade': safe_float(adv_stats_entry.get('defenseGrade')),
    }


def transform_ppa_stats(ppa_entry: Dict) -> Dict:
    """
    Transform PPA (Predicted Points Added) statistics
    
    Args:
        ppa_entry: Raw PPA data from API
    
    Returns:
        Transformed PPA stats
    """
    return {
        'epa_total': safe_float(ppa_entry.get('totalPPA') or ppa_entry.get('total')),
        'epa_per_play': safe_float(ppa_entry.get('averagePPA') or ppa_entry.get('average')),
        'success_rate': safe_float(ppa_entry.get('successRate'))
    }


def merge_stat_dicts(base_stats: Dict, additional_stats: Dict) -> Dict:
    """
    Merge multiple stat dictionaries, updating base with additional
    
    Args:
        base_stats: Base statistics dictionary
        additional_stats: Additional statistics to merge
    
    Returns:
        Merged dictionary
    """
    merged = base_stats.copy()
    for key, value in additional_stats.items():
        if value is not None:
            merged[key] = value
    return merged


def validate_player_data(player_data: Dict) -> bool:
    """
    Validate that player data meets minimum requirements
    
    Args:
        player_data: Player data dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['name', 'position']
    
    for field in required_fields:
        if not player_data.get(field):
            logger.warning(f"Missing required field: {field}")
            return False
    
    return True


def validate_stats_data(stats_data: Dict) -> bool:
    """
    Validate that stats data meets minimum requirements
    
    Args:
        stats_data: Stats data dictionary
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['season', 'team']
    
    for field in required_fields:
        if not stats_data.get(field):
            logger.warning(f"Missing required field: {field}")
            return False
    
    # Must have at least some stats
    has_stats = any([
        stats_data.get('passing_stats'),
        stats_data.get('rushing_stats'),
        stats_data.get('receiving_stats'),
        stats_data.get('defensive_stats')
    ])
    
    if not has_stats:
        logger.warning("No statistics data found")
        return False
    
    return True

