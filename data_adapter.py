"""
Data Adapter - Transform database stats to model format
"""

def transform_stats_for_model(player, stats, team_name):
    """Transform database stats to model-expected format"""
    
    position = (player.position or '').upper()
    
    # Get actual snap count if available, otherwise estimate based on stats volume
    actual_snaps = stats.snaps_played
    games_played_est = stats.games_played or 0
    games_started_est = stats.games_started or 0
    
    # If no games_played data, estimate from stat volume
    if games_played_est == 0 or actual_snaps is None or actual_snaps == 0:
        # Estimate based on stat volume
        if position == 'QB' and stats.passing_stats:
            passing = stats.passing_stats if isinstance(stats.passing_stats, dict) else {}
            attempts = passing.get('attempts', 0) or 0
            
            if attempts >= 350:  # Full season starter
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 850
            elif attempts >= 250:  # Most games starter
                games_played_est = 12
                games_started_est = 10
                actual_snaps = 700
            elif attempts >= 150:  # Platoon/some starts
                games_played_est = 12
                games_started_est = 6
                actual_snaps = 450
            elif attempts >= 50:  # Backup with reps
                games_played_est = 10
                games_started_est = 2
                actual_snaps = 200
            else:  # Garbage time only
                games_played_est = 8
                games_started_est = 0
                actual_snaps = max(50, attempts)
        
        elif position == 'RB' and stats.rushing_stats:
            rushing = stats.rushing_stats if isinstance(stats.rushing_stats, dict) else {}
            carries = rushing.get('carries', 0) or 0
            
            if carries >= 200:  # Bellcow back
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 600
            elif carries >= 120:  # Starter
                games_played_est = 12
                games_started_est = 10
                actual_snaps = 450
            elif carries >= 60:  # Rotational
                games_played_est = 12
                games_started_est = 4
                actual_snaps = 250
            else:
                games_played_est = 10
                games_started_est = 1
                actual_snaps = max(50, carries * 2)
        
        elif position == 'WR' and stats.receiving_stats:
            receiving = stats.receiving_stats if isinstance(stats.receiving_stats, dict) else {}
            receptions = receiving.get('receptions', 0) or 0
            
            if receptions >= 60:  # WR1
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 650
            elif receptions >= 35:  # WR2/3
                games_played_est = 12
                games_started_est = 8
                actual_snaps = 500
            elif receptions >= 15:  # Rotational
                games_played_est = 12
                games_started_est = 2
                actual_snaps = 250
            else:
                games_played_est = 10
                games_started_est = 0
                actual_snaps = max(50, receptions * 5)
        
        elif position in ['DL', 'DT', 'DE'] and stats.defensive_stats:
            defensive = stats.defensive_stats if isinstance(stats.defensive_stats, dict) else {}
            tackles = defensive.get('tackles', 0) or 0
            
            if tackles >= 50:  # Full-time starter
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 600
            elif tackles >= 30:  # Starter
                games_played_est = 12
                games_started_est = 10
                actual_snaps = 500
            elif tackles >= 15:  # Rotational
                games_played_est = 12
                games_started_est = 4
                actual_snaps = 300
            else:
                games_played_est = 10
                games_started_est = 1
                actual_snaps = max(100, tackles * 8)
        
        elif position in ['LB', 'ILB', 'OLB'] and stats.defensive_stats:
            defensive = stats.defensive_stats if isinstance(stats.defensive_stats, dict) else {}
            tackles = defensive.get('tackles', 0) or 0
            
            if tackles >= 80:  # Elite LB
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 750
            elif tackles >= 50:  # Starter
                games_played_est = 12
                games_started_est = 11
                actual_snaps = 650
            elif tackles >= 25:  # Rotational
                games_played_est = 12
                games_started_est = 5
                actual_snaps = 400
            else:
                games_played_est = 10
                games_started_est = 1
                actual_snaps = max(100, tackles * 6)
        
        elif position in ['CB', 'S', 'DB'] and stats.defensive_stats:
            defensive = stats.defensive_stats if isinstance(stats.defensive_stats, dict) else {}
            tackles = defensive.get('tackles', 0) or 0
            pd = defensive.get('passes_deflected', 0) or 0
            
            if tackles + pd >= 50:  # Full-time starter
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 750
            elif tackles + pd >= 25:  # Starter
                games_played_est = 12
                games_started_est = 10
                actual_snaps = 650
            elif tackles + pd >= 10:  # Rotational
                games_played_est = 12
                games_started_est = 3
                actual_snaps = 350
            else:
                games_played_est = 10
                games_started_est = 0
                actual_snaps = max(100, (tackles + pd) * 8)
        
        elif position == 'TE' and stats.receiving_stats:
            receiving = stats.receiving_stats if isinstance(stats.receiving_stats, dict) else {}
            receptions = receiving.get('receptions', 0) or 0
            
            if receptions >= 40:  # Primary TE
                games_played_est = 12
                games_started_est = 12
                actual_snaps = 550
            elif receptions >= 20:  # Starter
                games_played_est = 12
                games_started_est = 9
                actual_snaps = 450
            else:
                games_played_est = 10
                games_started_est = 3
                actual_snaps = max(100, receptions * 8)
        
        # Fallback if no stats
        if actual_snaps is None or actual_snaps == 0:
            actual_snaps = 200
            games_played_est = 8
            games_started_est = 0
    
    # Base player data
    adapted_data = {
        'player_id': str(player.id),
        'name': player.name,
        'position': position,
        'height': player.height or 72,
        'weight': player.weight or 200,
        'hometown': player.hometown or '',
        'state': player.state or '',
        'class_year': player.class_year or 2023,
        'eligibility_remaining': 1,
        'current_program': team_name,
        'conference': 'FBS',  # Default
        'games_played': games_played_est,
        'games_started': games_started_est,
        'snaps_played': int(actual_snaps),  # Use calculated snaps
        'team_total_snaps': 850,
        'team_wins': 8,
        'team_losses': 4,
        'strength_of_schedule': 1.0,
        'opponent_strength': 1.0,
        'film_grade': 75,
        'football_iq': 7.0,
        'years_playing': 2,
        'current_scheme': 'Spread',
        'scheme_history': ['Spread'],
    }
    
    # Transform stats based on position
    if position == 'QB' and stats.passing_stats:
        passing = stats.passing_stats if isinstance(stats.passing_stats, dict) else {}
        rushing = stats.rushing_stats if isinstance(stats.rushing_stats, dict) else {}
        
        attempts = passing.get('attempts', 0) or 0
        completions = passing.get('completions', 0) or 0
        yards = passing.get('yards', 0) or 0
        tds = passing.get('touchdowns', 0) or 0
        ints = passing.get('interceptions', 0) or 1  # Avoid division by zero
        
        adapted_data['stats'] = {
            'completion_percentage': (completions / attempts * 100) if attempts > 0 else 0,
            'yards_per_attempt': passing.get('yards_per_attempt', 0) or (yards / attempts if attempts > 0 else 0),
            'td_int_ratio': tds / max(ints, 1),
            'qbr': passing.get('qbr', 0) or 75,
            'success_rate': 0.45,
            'epa_per_play': 0.15,
            'passing_yards': yards,
            'passing_tds': tds,
            'interceptions': ints,
        }
        
        # Add rushing for dual-threat QBs
        if rushing:
            rush_yards = rushing.get('yards', 0) or 0
            adapted_data['stats']['rushing_yards'] = rush_yards
            adapted_data['stats']['rushing_tds'] = rushing.get('touchdowns', 0) or 0
        
        adapted_data['skills'] = {
            'arm_strength': 7.5,
            'quick_release': 7.0,
            'accuracy_short': 8.0,
            'accuracy_medium': 7.5,
            'accuracy_deep': 7.0,
            'decision_making': 7.5,
            'mobility': 7.0 if rushing and rush_yards > 200 else 6.0,
            'pocket_presence': 7.5,
            'football_iq': 7.5,
            'pre_snap_reads': 7.0
        }
    
    elif position == 'RB' and stats.rushing_stats:
        rushing = stats.rushing_stats if isinstance(stats.rushing_stats, dict) else {}
        receiving = stats.receiving_stats if isinstance(stats.receiving_stats, dict) else {}
        
        attempts = rushing.get('attempts', 0) or 0
        yards = rushing.get('yards', 0) or 0
        tds = rushing.get('touchdowns', 0) or 0
        ypc = rushing.get('yards_per_carry', 0) or (yards / attempts if attempts > 0 else 0)
        
        adapted_data['stats'] = {
            'rushing_yards': yards,
            'rushing_attempts': attempts,
            'yards_per_carry': ypc,
            'rushing_tds': tds,
            'broken_tackles': int(attempts * 0.15),  # Estimate
            'yards_after_contact': yards * 0.4,  # Estimate
            'success_rate': 0.45,
        }
        
        # Add receiving
        if receiving:
            adapted_data['stats']['receptions'] = receiving.get('receptions', 0) or 0
            adapted_data['stats']['receiving_yards'] = receiving.get('yards', 0) or 0
            adapted_data['stats']['receiving_tds'] = receiving.get('touchdowns', 0) or 0
        
        adapted_data['skills'] = {
            'vision': 7.5,
            'acceleration': 7.0,
            'balance': 7.5,
            'agility': 7.0,
            'elusiveness': 7.0,
            'power': 7.0,
            'pass_blocking': 6.5,
            'route_running': 6.5,
            'hands': 7.0
        }
    
    elif position in ['WR', 'TE'] and stats.receiving_stats:
        receiving = stats.receiving_stats if isinstance(stats.receiving_stats, dict) else {}
        
        receptions = receiving.get('receptions', 0) or 0
        yards = receiving.get('yards', 0) or 0
        tds = receiving.get('touchdowns', 0) or 0
        ypr = receiving.get('yards_per_reception', 0) or (yards / receptions if receptions > 0 else 0)
        
        adapted_data['stats'] = {
            'receptions': receptions,
            'receiving_yards': yards,
            'yards_per_reception': ypr,
            'receiving_tds': tds,
            'targets': int(receptions * 1.5),  # Estimate
            'catch_rate': 0.65,
            'yards_after_catch': yards * 0.4,
            'contested_catches': int(receptions * 0.2),
        }
        
        adapted_data['skills'] = {
            'route_running': 7.5,
            'separation': 7.0,
            'hands': 7.5,
            'speed': 7.0,
            'agility': 7.0,
            'catch_radius': 7.0,
            'yards_after_catch_ability': 7.0,
            'blocking': 6.5 if position == 'TE' else 5.5,
        }
    
    else:
        # Generic stats for other positions
        adapted_data['stats'] = {
            'tackles': 50,
            'tackles_for_loss': 5,
            'sacks': 2.0,
            'interceptions': 1,
            'pass_breakups': 3,
        }
        
        adapted_data['skills'] = {
            'technique': 7.0,
            'power': 7.0,
            'speed': 7.0,
            'agility': 7.0,
            'instincts': 7.0,
        }
    
    # Brand/NIL (placeholders - we don't have this data yet)
    adapted_data.update({
        'instagram_followers': 5000,
        'twitter_followers': 3000,
        'tiktok_followers': 10000,
        'engagement_rate': 0.03,
        'follower_growth_rate': 0.05,
        'google_search_volume': 1000,
        'media_mentions_monthly': 5,
        'national_media_coverage': False,
        'local_media_coverage': True,
        'nil_deal_value': 0,
        'nil_deal_count': 0,
        'marketability_score': 60,
    })
    
    return adapted_data

