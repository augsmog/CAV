"""
Basketball Data Adapter
Transforms database records into format expected by basketball valuation models
"""

def adapt_basketball_player_to_valuation_format(player, stat_record, team):
    """
    Transform basketball player and stats from database to valuation format
    
    Args:
        player: BasketballPlayer database object
        stat_record: BasketballPerformanceStat database object
        team: BasketballTeam database object
    
    Returns:
        Dict formatted for BasketballValuationEngine
    """
    # Handle None values safely
    games = stat_record.games_played or 0
    minutes = stat_record.minutes or 0
    
    return {
        # Player info
        'name': player.name,
        'team': team.school if team else 'Unknown',
        'position': player.position or 'SF',
        'conference': team.conference if team else '',
        'season': stat_record.season,
        
        # Games and minutes
        'games': games,
        'minutes': minutes,
        
        # Counting stats (season totals)
        'pts': stat_record.pts or 0,
        'reb': stat_record.reb or 0,
        'oreb': stat_record.oreb or 0,
        'dreb': stat_record.dreb or 0,
        'ast': stat_record.ast or 0,
        'stl': stat_record.stl or 0,
        'blk': stat_record.blk or 0,
        'tov': stat_record.tov or 0,
        'pf': stat_record.pf or 0,
        
        # Shooting percentages
        'fg_pct': stat_record.fg_pct or 0,
        'tp_pct': stat_record.tp_pct or 0,
        'ft_pct': stat_record.ft_pct or 0,
        
        # Shooting made/attempted
        'fgm': stat_record.fgm or 0,
        'fga': stat_record.fga or 0,
        'tpm': stat_record.tpm or 0,
        'tpa': stat_record.tpa or 0,
        'ftm': stat_record.ftm or 0,
        'fta': stat_record.fta or 0,
        
        # Advanced stats
        'per': stat_record.per or 15.0,
        'usage_rate': stat_record.usage_rate or 20.0,
        'ortg': stat_record.ortg or 100.0,
        'drtg': stat_record.drtg or 105.0,
        'ws': stat_record.ws or 0,
        'bpm': stat_record.bpm or 0,
        
        # Metadata
        'player_id': player.id,
        'team_id': team.id if team else None,
    }


def calculate_per_game_stats(player_data: dict) -> dict:
    """
    Add per-game averages to player data
    
    Args:
        player_data: Dict from adapt_basketball_player_to_valuation_format
    
    Returns:
        Enhanced dict with per-game stats
    """
    games = player_data.get('games', 0)
    
    if games == 0:
        return player_data
    
    # Add per-game stats
    player_data['ppg'] = round(player_data.get('pts', 0) / games, 1)
    player_data['rpg'] = round(player_data.get('reb', 0) / games, 1)
    player_data['apg'] = round(player_data.get('ast', 0) / games, 1)
    player_data['spg'] = round(player_data.get('stl', 0) / games, 1)
    player_data['bpg'] = round(player_data.get('blk', 0) / games, 1)
    player_data['topg'] = round(player_data.get('tov', 0) / games, 1)
    player_data['mpg'] = round(player_data.get('minutes', 0) / games, 1)
    
    # Assist-to-turnover ratio
    tov = player_data.get('tov', 0)
    if tov > 0:
        player_data['ast_tov_ratio'] = round(player_data.get('ast', 0) / tov, 2)
    else:
        player_data['ast_tov_ratio'] = float('inf') if player_data.get('ast', 0) > 0 else 0
    
    return player_data

