"""
Basketball-specific database models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class BasketballTeam(Base):
    """College basketball team"""
    __tablename__ = 'basketball_teams'
    
    id = Column(Integer, primary_key=True)
    school = Column(String, unique=True, nullable=False)
    conference = Column(String)
    division = Column(String)  # D1, D2, D3
    mascot = Column(String)
    abbreviation = Column(String)
    
    # Relationships
    players = relationship("BasketballPlayer", back_populates="team")
    
    def __repr__(self):
        return f"<BasketballTeam(school='{self.school}', conference='{self.conference}')>"


class BasketballPlayer(Base):
    """College basketball player"""
    __tablename__ = 'basketball_players'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    team_id = Column(Integer, ForeignKey('basketball_teams.id'))
    season = Column(Integer, nullable=False)  # Season year (e.g., 2023)
    
    # Player info
    position = Column(String)  # PG, SG, SF, PF, C
    height = Column(Integer)  # inches
    weight = Column(Integer)  # pounds
    class_year = Column(String)  # FR, SO, JR, SR
    jersey_number = Column(Integer)
    
    # Location
    hometown = Column(String)
    state = Column(String)
    
    # Academic
    eligibility_remaining = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    team = relationship("BasketballTeam", back_populates="players")
    stats = relationship("BasketballPerformanceStat", back_populates="player")
    
    def __repr__(self):
        return f"<BasketballPlayer(name='{self.name}', position='{self.position}')>"


class BasketballPerformanceStat(Base):
    """Basketball player performance statistics"""
    __tablename__ = 'basketball_performance_stats'
    
    id = Column(Integer, primary_key=True)
    player_id = Column(Integer, ForeignKey('basketball_players.id'), nullable=False)
    season = Column(Integer, nullable=False)
    
    # Basic counting stats
    games_played = Column(Integer)
    games_started = Column(Integer)
    minutes_per_game = Column(Float)
    
    # Scoring
    points_per_game = Column(Float)
    field_goals_made = Column(Float)
    field_goals_attempted = Column(Float)
    field_goal_percentage = Column(Float)
    three_pointers_made = Column(Float)
    three_pointers_attempted = Column(Float)
    three_point_percentage = Column(Float)
    free_throws_made = Column(Float)
    free_throws_attempted = Column(Float)
    free_throw_percentage = Column(Float)
    
    # Rebounds
    rebounds_per_game = Column(Float)
    offensive_rebounds = Column(Float)
    defensive_rebounds = Column(Float)
    
    # Other stats
    assists_per_game = Column(Float)
    steals_per_game = Column(Float)
    blocks_per_game = Column(Float)
    turnovers_per_game = Column(Float)
    fouls_per_game = Column(Float)
    
    # Advanced metrics
    player_efficiency_rating = Column(Float)  # PER
    true_shooting_percentage = Column(Float)  # TS%
    usage_rate = Column(Float)
    assist_percentage = Column(Float)
    rebound_percentage = Column(Float)
    turnover_percentage = Column(Float)
    
    # Raw stats (JSON for flexibility)
    raw_stats = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    player = relationship("BasketballPlayer", back_populates="stats")
    
    # Unique constraint
    __table_args__ = (
        # One stat record per player per season
        # UniqueConstraint('player_id', 'season', name='unique_player_season'),
    )
    
    def __repr__(self):
        return f"<BasketballPerformanceStat(player_id={self.player_id}, season={self.season}, ppg={self.points_per_game})>"


class BasketballTransfer(Base):
    """Basketball transfer portal entry"""
    __tablename__ = 'basketball_transfers'
    
    id = Column(Integer, primary_key=True)
    player_name = Column(String, nullable=False)
    from_team = Column(String)
    to_team = Column(String)
    position = Column(String)
    
    # Transfer details
    entered_portal_date = Column(DateTime)
    committed_date = Column(DateTime)
    eligibility_remaining = Column(Integer)
    
    # Stats from previous school
    previous_ppg = Column(Float)
    previous_rpg = Column(Float)
    previous_apg = Column(Float)
    
    # Season
    season = Column(Integer)
    
    # Status
    status = Column(String)  # 'in_portal', 'committed', 'withdrawn'
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<BasketballTransfer(player='{self.player_name}', from='{self.from_team}', to='{self.to_team}')>"

