"""
Data Loading Utilities
Functions for loading and processing historical data
"""

import pandas as pd
import json
from typing import Dict, List
from datetime import datetime


class DataLoader:
    """
    Utilities for loading and processing player and transfer data
    """
    
    def __init__(self, data_dir: str = '/home/claude/cfb_valuation_model/data'):
        self.data_dir = data_dir
    
    def load_player_data(self, file_path: str) -> Dict:
        """
        Load player data from CSV or JSON
        
        Expected CSV columns:
        - player_id, name, position, height, weight
        - eligibility_remaining, current_program, conference
        - completion_percentage, yards_per_attempt (stats)
        - instagram_followers, twitter_followers
        - etc.
        """
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            players = {}
            
            for _, row in df.iterrows():
                player_id = row['player_id']
                players[player_id] = self._row_to_player_dict(row)
            
            return players
        
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                return json.load(f)
        
        else:
            raise ValueError("File must be CSV or JSON")
    
    def load_transfer_data(self, file_path: str) -> List[Dict]:
        """
        Load historical transfer data
        
        Expected CSV columns:
        - player_id, transfer_date, from_program, to_program
        - nil_deal_value, reported_finalists
        - first_season_performance_grade
        """
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
            
            # Convert date strings
            df['transfer_date'] = pd.to_datetime(df['transfer_date']).dt.date
            
            # Convert reported_finalists from string to list
            if 'reported_finalists' in df.columns:
                df['reported_finalists'] = df['reported_finalists'].apply(
                    lambda x: x.split(',') if pd.notna(x) else []
                )
            
            return df.to_dict('records')
        
        elif file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Convert date strings
                for record in data:
                    if 'transfer_date' in record:
                        record['transfer_date'] = datetime.strptime(
                            record['transfer_date'], '%Y-%m-%d'
                        ).date()
                return data
        
        else:
            raise ValueError("File must be CSV or JSON")
    
    def _row_to_player_dict(self, row: pd.Series) -> Dict:
        """
        Convert DataFrame row to player dictionary
        """
        player = {}
        
        # Basic info
        basic_fields = ['player_id', 'name', 'position', 'height', 'weight',
                       'hometown', 'state', 'class_year', 'eligibility_remaining',
                       'current_program', 'conference']
        
        for field in basic_fields:
            if field in row:
                player[field] = row[field]
        
        # Stats - collect all stat columns
        stat_columns = [col for col in row.index if col.startswith('stat_')]
        if stat_columns:
            player['stats'] = {}
            for col in stat_columns:
                stat_name = col.replace('stat_', '')
                player['stats'][stat_name] = row[col]
        
        # Skills - collect all skill columns
        skill_columns = [col for col in row.index if col.startswith('skill_')]
        if skill_columns:
            player['skills'] = {}
            for col in skill_columns:
                skill_name = col.replace('skill_', '')
                player['skills'][skill_name] = row[col]
        
        # Social media
        social_fields = ['instagram_followers', 'twitter_followers', 
                        'tiktok_followers', 'engagement_rate']
        for field in social_fields:
            if field in row and pd.notna(row[field]):
                player[field] = row[field]
        
        # Performance
        performance_fields = ['snaps_played', 'games_played', 'games_started',
                             'team_wins', 'team_losses', 'pff_grade']
        for field in performance_fields:
            if field in row and pd.notna(row[field]):
                player[field] = row[field]
        
        return player
    
    def create_sample_dataset(self, output_dir: str):
        """
        Create sample CSV templates for data collection
        """
        # Sample player data
        player_data = {
            'player_id': ['QB001', 'RB001', 'WR001'],
            'name': ['John Smith', 'Mike Johnson', 'Chris Williams'],
            'position': ['QB', 'RB', 'WR'],
            'height': [75, 70, 73],
            'weight': [215, 205, 190],
            'eligibility_remaining': [2, 3, 1],
            'current_program': ['Texas', 'Alabama', 'Ohio State'],
            'conference': ['SEC', 'SEC', 'Big Ten'],
            'stat_completion_percentage': [67.5, None, None],
            'stat_yards_per_attempt': [8.2, None, None],
            'stat_yards_per_carry': [None, 5.8, None],
            'stat_yards_per_route_run': [None, None, 2.5],
            'instagram_followers': [125000, 85000, 200000],
            'twitter_followers': [85000, 45000, 150000],
            'snaps_played': [750, 680, 720],
            'games_played': [12, 11, 12],
            'team_wins': [9, 11, 10],
            'team_losses': [3, 1, 2]
        }
        
        df_players = pd.DataFrame(player_data)
        df_players.to_csv(f'{output_dir}/sample_players.csv', index=False)
        
        # Sample transfer data
        transfer_data = {
            'player_id': ['QB002', 'RB002'],
            'transfer_date': ['2024-01-15', '2024-05-20'],
            'from_program': ['Auburn', 'UCLA'],
            'to_program': ['Miami', 'Oregon'],
            'nil_deal_value': [350000, 200000],
            'reported_finalists': ['Miami,Florida State,USC', 'Oregon,Washington'],
            'first_season_performance_grade': [78.5, 82.0]
        }
        
        df_transfers = pd.DataFrame(transfer_data)
        df_transfers.to_csv(f'{output_dir}/sample_transfers.csv', index=False)
        
        print(f"Sample datasets created in {output_dir}/")
        print("- sample_players.csv")
        print("- sample_transfers.csv")


def create_data_collection_template():
    """
    Generate a comprehensive data collection template
    """
    template = """
# Data Collection Template

## Player Profile Data

### Required Fields
- player_id: Unique identifier
- name: Player name
- position: QB, RB, WR, TE, OL, DL, LB, CB, S
- height: Height in inches
- weight: Weight in pounds
- eligibility_remaining: Years of eligibility (1-4)
- current_program: Current school
- conference: Conference name

### Performance Stats (Position-Dependent)
**Quarterbacks:**
- stat_completion_percentage
- stat_yards_per_attempt
- stat_td_int_ratio
- stat_qbr
- stat_success_rate
- stat_epa_per_play

**Running Backs:**
- stat_yards_per_carry
- stat_yards_after_contact
- stat_success_rate
- stat_receiving_grade
- stat_epa_per_play

**Wide Receivers:**
- stat_yards_per_route_run
- stat_catch_rate
- stat_yards_after_catch
- stat_contested_catch_rate
- stat_separation_score
- stat_drop_rate

### Brand/Social Media
- instagram_followers
- twitter_followers
- tiktok_followers
- engagement_rate (decimal, e.g., 0.045 for 4.5%)
- follower_growth_rate (monthly, decimal)
- google_search_volume (monthly searches)
- media_mentions_monthly
- national_media_coverage (True/False)

### Skills (1-10 scale, position-dependent)
**QB Skills:**
- skill_arm_strength
- skill_accuracy_short
- skill_accuracy_medium
- skill_accuracy_deep
- skill_decision_making
- skill_mobility
- skill_pocket_presence

**RB Skills:**
- skill_power
- skill_speed
- skill_agility
- skill_vision
- skill_receiving
- skill_pass_blocking

### Context Data
- snaps_played
- games_played
- games_started
- team_wins
- team_losses
- team_total_snaps
- depth_chart_position (1, 2, 3)
- is_starter (True/False)
- pff_grade (0-100)

### Optional But Helpful
- injury_history (JSON list)
- controversies (count)
- personality_rating (1-10)
- media_skills_rating (1-10)
- community_engagement_hours

## Transfer Portal Data

### Required Fields
- player_id: Match to player profile
- transfer_date: YYYY-MM-DD format
- from_program: Previous school
- to_program: New school

### Optional Fields
- nil_deal_value: Reported NIL deal value
- reported_finalists: Comma-separated list of schools
- decision_timeline_days: Days from portal entry to commitment
- first_season_snaps: Snaps in first season at new school
- first_season_performance_grade: PFF grade or similar
- immediate_starter: True/False

## Data Sources

### Statistics
- Sports-Reference (college football)
- Pro Football Focus (PFF grades)
- ESPN/247Sports (team stats)
- Conference websites (official stats)

### Brand/Social
- Social media platforms (direct follower counts)
- Google Trends (search volume)
- On3 NIL Valuation (NIL estimates)
- Media monitoring services

### Transfer Portal
- On3 Transfer Portal Tracker
- 247Sports Transfer Portal
- Rivals Transfer Tracker
- Official school announcements

## Data Quality Checks
1. Verify player positions match scheme analysis needs
2. Ensure stats align with position (QB stats for QBs, etc.)
3. Check for outliers in social media metrics
4. Validate transfer dates and programs
5. Cross-reference NIL values when available
"""
    
    return template


if __name__ == '__main__':
    # Create sample datasets
    loader = DataLoader()
    loader.create_sample_dataset('/home/claude/cfb_valuation_model/data/raw')
    
    # Save data collection template
    template = create_data_collection_template()
    with open('/home/claude/cfb_valuation_model/docs/data_collection_template.txt', 'w') as f:
        f.write(template)
    
    print("\nData collection template saved to:")
    print("docs/data_collection_template.txt")
