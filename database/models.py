"""
Database models for CAV - College Athlete Valuation
"""

from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Date, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Player(Base):
    """Player biographical and career information"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cfb_id = Column(String(50), unique=True, index=True)  # collegefootballdata.com ID
    name = Column(String(200), nullable=False, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    
    # Physical attributes
    position = Column(String(10), nullable=False, index=True)
    height = Column(Integer)  # inches
    weight = Column(Integer)  # pounds
    
    # Biographical
    hometown = Column(String(200))
    state = Column(String(50))
    country = Column(String(50), default='USA')
    high_school = Column(String(200))
    
    # Career info
    class_year = Column(Integer)  # Recruiting class year
    eligibility_remaining = Column(Integer)
    current_team_id = Column(Integer, ForeignKey('teams.id'), index=True)
    jersey_number = Column(String(5))
    
    # Status
    is_active = Column(Boolean, default=True)
    is_transfer = Column(Boolean, default=False)
    is_injured = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_data_refresh = Column(DateTime(timezone=True))
    
    # Relationships
    current_team = relationship("Team", back_populates="players")
    stats = relationship("PerformanceStat", back_populates="player", cascade="all, delete-orphan")
    transfers = relationship("Transfer", back_populates="player", cascade="all, delete-orphan")
    social_media = relationship("SocialMedia", back_populates="player", uselist=False, cascade="all, delete-orphan")
    nil_deals = relationship("NILDeal", back_populates="player", cascade="all, delete-orphan")
    injuries = relationship("Injury", back_populates="player", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Player(id={self.id}, name='{self.name}', position='{self.position}')>"


class Team(Base):
    """College football teams"""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    cfb_id = Column(String(50), unique=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    school = Column(String(200), nullable=False)
    abbreviation = Column(String(10))
    
    # Conference info
    conference = Column(String(100), index=True)
    division = Column(String(50))
    
    # Location
    city = Column(String(100))
    state = Column(String(50))
    
    # Stadium/Market
    stadium = Column(String(200))
    capacity = Column(Integer)
    market_size_rank = Column(Integer)
    
    # Colors/Branding
    color = Column(String(20))
    alt_color = Column(String(20))
    logo_url = Column(String(500))
    
    # Program info
    head_coach = Column(String(200))
    offensive_coordinator = Column(String(200))
    defensive_coordinator = Column(String(200))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    players = relationship("Player", back_populates="current_team")
    schemes = relationship("SchemeInfo", back_populates="team", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Team(id={self.id}, name='{self.name}', conference='{self.conference}')>"


class PerformanceStat(Base):
    """Player performance statistics by season"""
    __tablename__ = 'performance_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    team = Column(String(200))
    
    # Game participation
    games_played = Column(Integer, default=0)
    games_started = Column(Integer, default=0)
    snaps_played = Column(Integer)
    snap_percentage = Column(Float)
    
    # Position-specific stats (stored as JSON for flexibility)
    passing_stats = Column(JSON)  # completions, attempts, yards, TDs, INTs, etc.
    rushing_stats = Column(JSON)  # attempts, yards, TDs, YPC, etc.
    receiving_stats = Column(JSON)  # receptions, yards, TDs, YPR, etc.
    defensive_stats = Column(JSON)  # tackles, sacks, INTs, PBUs, etc.
    
    # Advanced metrics
    pff_grade = Column(Float)
    pff_pass_grade = Column(Float)
    pff_rush_grade = Column(Float)
    pff_receive_grade = Column(Float)
    pff_defense_grade = Column(Float)
    
    epa_total = Column(Float)
    epa_per_play = Column(Float)
    success_rate = Column(Float)
    
    # Efficiency
    yards_per_attempt = Column(Float)
    yards_per_carry = Column(Float)
    yards_per_route = Column(Float)
    yards_per_reception = Column(Float)
    
    # Team context
    team_wins = Column(Integer)
    team_losses = Column(Integer)
    strength_of_schedule = Column(Float)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="stats")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('player_id', 'season', name='unique_player_season'),
        Index('idx_season_position', 'season', 'player_id'),
    )
    
    def __repr__(self):
        return f"<PerformanceStat(player_id={self.player_id}, season={self.season})>"


class Transfer(Base):
    """Transfer portal activity"""
    __tablename__ = 'transfers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    
    # Transfer details
    transfer_date = Column(Date, index=True)
    from_team = Column(String(200))
    to_team = Column(String(200))
    season = Column(Integer, index=True)
    
    # Context
    reason_category = Column(String(100))  # Playing time, Coaching change, NIL, etc.
    portal_entry_timing = Column(String(50))  # Early, Regular, Late
    eligibility_at_transfer = Column(Integer)
    
    # Outcomes
    immediate_starter = Column(Boolean)
    first_season_snaps = Column(Integer)
    first_season_performance_grade = Column(Float)
    
    # Market data
    reported_finalists = Column(JSON)  # List of schools in consideration
    decision_timeline_days = Column(Integer)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="transfers")
    
    def __repr__(self):
        return f"<Transfer(player_id={self.player_id}, from={self.from_team}, to={self.to_team})>"


class SocialMedia(Base):
    """Player social media presence and brand metrics"""
    __tablename__ = 'social_media'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, unique=True, index=True)
    
    # Social media handles
    twitter_handle = Column(String(100))
    instagram_handle = Column(String(100))
    tiktok_handle = Column(String(100))
    
    # Follower counts
    twitter_followers = Column(Integer)
    instagram_followers = Column(Integer)
    tiktok_followers = Column(Integer)
    total_followers = Column(Integer)
    
    # Engagement metrics
    twitter_engagement_rate = Column(Float)
    instagram_engagement_rate = Column(Float)
    tiktok_engagement_rate = Column(Float)
    average_engagement_rate = Column(Float)
    
    # Growth metrics
    follower_growth_rate_30d = Column(Float)
    follower_growth_rate_90d = Column(Float)
    
    # Brand metrics
    google_search_volume = Column(Integer)
    media_mentions_count = Column(Integer)
    national_media_coverage = Column(Boolean, default=False)
    
    # Scoring
    brand_score = Column(Float)  # Calculated brand strength score
    
    # Metadata
    last_updated = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="social_media")
    
    def __repr__(self):
        return f"<SocialMedia(player_id={self.player_id}, total_followers={self.total_followers})>"


class NILDeal(Base):
    """NIL deals and valuations"""
    __tablename__ = 'nil_deals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    
    # Deal details
    deal_date = Column(Date)
    company = Column(String(200))
    deal_type = Column(String(100))  # Endorsement, Appearance, Social Media, etc.
    
    # Valuation
    reported_value = Column(Float)
    estimated_value = Column(Float)
    annual_value = Column(Float)
    is_recurring = Column(Boolean, default=False)
    
    # Deal terms
    duration_months = Column(Integer)
    performance_based = Column(Boolean, default=False)
    
    # Source
    source = Column(String(200))  # Where the information came from
    verified = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="nil_deals")
    
    def __repr__(self):
        return f"<NILDeal(player_id={self.player_id}, company='{self.company}', value=${self.estimated_value})>"


class Injury(Base):
    """Player injury history"""
    __tablename__ = 'injuries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    player_id = Column(Integer, ForeignKey('players.id'), nullable=False, index=True)
    
    # Injury details
    season = Column(Integer, index=True)
    injury_date = Column(Date)
    injury_type = Column(String(200))
    body_part = Column(String(100))
    
    # Severity
    severity = Column(String(50))  # Minor, Moderate, Major, Career-threatening
    games_missed = Column(Integer, default=0)
    expected_return_date = Column(Date)
    actual_return_date = Column(Date)
    
    # Status
    is_active = Column(Boolean, default=False)
    
    # Source
    source = Column(String(200))
    notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    player = relationship("Player", back_populates="injuries")
    
    def __repr__(self):
        return f"<Injury(player_id={self.player_id}, type='{self.injury_type}', severity='{self.severity}')>"


class SchemeInfo(Base):
    """Team offensive/defensive schemes by season"""
    __tablename__ = 'scheme_info'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, index=True)
    season = Column(Integer, nullable=False, index=True)
    
    # Scheme details
    offensive_scheme = Column(String(100))  # Air Raid, Spread, Pro Style, etc.
    defensive_scheme = Column(String(100))  # 3-4, 4-3, Nickel, Multiple
    
    # Tempo and style
    offensive_tempo = Column(String(50))  # Fast, Average, Slow
    run_pass_ratio = Column(Float)  # % of plays that are runs
    
    # Coaching staff
    head_coach = Column(String(200))
    offensive_coordinator = Column(String(200))
    defensive_coordinator = Column(String(200))
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    team = relationship("Team", back_populates="schemes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('team_id', 'season', name='unique_team_season_scheme'),
    )
    
    def __repr__(self):
        return f"<SchemeInfo(team_id={self.team_id}, season={self.season}, offense='{self.offensive_scheme}')>"


class DataRefreshLog(Base):
    """Track data refresh operations"""
    __tablename__ = 'data_refresh_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Refresh details
    data_type = Column(String(100), nullable=False, index=True)  # players, stats, transfers, etc.
    season = Column(Integer, index=True)
    status = Column(String(50), nullable=False)  # success, failed, partial
    
    # Metrics
    records_added = Column(Integer, default=0)
    records_updated = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)
    
    # Timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    duration_seconds = Column(Float)
    
    # Error info
    error_message = Column(Text)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<DataRefreshLog(type='{self.data_type}', status='{self.status}', records_added={self.records_added})>"

