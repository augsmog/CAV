"""
Data schemas for College Football Player Valuation Model
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import date
from enum import Enum


class Position(Enum):
    """Football positions"""
    QB = "Quarterback"
    RB = "Running Back"
    WR = "Wide Receiver"
    TE = "Tight End"
    OL = "Offensive Line"
    DL = "Defensive Line"
    LB = "Linebacker"
    CB = "Cornerback"
    S = "Safety"
    SPEC = "Special Teams"


class SchemeType(Enum):
    """Offensive/Defensive scheme types"""
    # Offensive
    AIR_RAID = "Air Raid"
    SPREAD = "Spread"
    PRO_STYLE = "Pro Style"
    OPTION = "Option"
    WEST_COAST = "West Coast"
    # Defensive
    THREE_FOUR = "3-4"
    FOUR_THREE = "4-3"
    NICKEL = "Nickel"
    MULTIPLE = "Multiple"


@dataclass
class PlayerBio:
    """Basic player biographical information"""
    player_id: str
    name: str
    position: Position
    height: int  # inches
    weight: int  # pounds
    hometown: str
    state: str
    high_school: str
    class_year: int  # recruiting class year
    eligibility_remaining: int
    birth_date: Optional[date] = None


@dataclass
class PerformanceStats:
    """Season performance statistics"""
    player_id: str
    season: int
    program: str
    conference: str
    games_played: int
    games_started: int
    
    # Counting stats (position-dependent)
    stats: Dict[str, float] = field(default_factory=dict)
    
    # Advanced metrics
    pff_grade: Optional[float] = None
    epa_total: Optional[float] = None
    success_rate: Optional[float] = None
    snaps_played: Optional[int] = None
    
    # Efficiency metrics
    yards_per_attempt: Optional[float] = None
    yards_per_carry: Optional[float] = None
    yards_per_route: Optional[float] = None
    
    # Situational stats
    third_down_conversion_rate: Optional[float] = None
    red_zone_efficiency: Optional[float] = None
    pressure_rate_allowed: Optional[float] = None
    
    # Team context
    team_wins: int = 0
    team_losses: int = 0
    strength_of_schedule: Optional[float] = None


@dataclass
class InjuryHistory:
    """Player injury tracking"""
    player_id: str
    season: int
    injury_type: str
    games_missed: int
    severity: str  # Minor, Moderate, Major, Career-threatening


@dataclass
class FilmGrade:
    """Subjective film evaluation"""
    player_id: str
    season: int
    evaluator: str
    
    # Technical skills (0-100 scale)
    technique_score: float
    instincts_score: float
    athleticism_score: float
    football_iq_score: float
    consistency_score: float
    
    # Projections
    ceiling_grade: str  # NFL Draft round equivalent
    floor_grade: str
    
    # Notes
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    scheme_notes: str = ""


@dataclass
class NILProfile:
    """NIL and personal brand data"""
    player_id: str
    measurement_date: date
    
    # Social media
    twitter_followers: Optional[int] = None
    instagram_followers: Optional[int] = None
    tiktok_followers: Optional[int] = None
    engagement_rate: Optional[float] = None
    
    # Brand metrics
    google_search_volume: Optional[int] = None
    media_mentions: Optional[int] = None
    
    # NIL deals
    known_nil_deals: List[Dict] = field(default_factory=list)
    estimated_nil_value: Optional[float] = None
    
    # Marketability factors
    personality_score: Optional[float] = None
    media_skills_score: Optional[float] = None
    community_engagement_score: Optional[float] = None


@dataclass
class ProgramProfile:
    """Program characteristics and context"""
    program_id: str
    program_name: str
    conference: str
    
    # Market factors
    market_size_rank: int
    media_market_value: float
    avg_attendance: int
    
    # Financial
    athletic_budget: float
    nil_collective_capacity: Optional[float] = None
    revenue_per_win: float
    
    # Success metrics
    five_year_win_pct: float
    playoff_appearances: int
    recruiting_rank_avg: float
    
    # Scheme and coaching
    head_coach: str
    offensive_coordinator: str
    defensive_coordinator: str
    offensive_scheme: SchemeType
    defensive_scheme: SchemeType
    
    # Development track record
    nfl_draft_picks_5yr: int
    position_development_ratings: Dict[Position, float] = field(default_factory=dict)


@dataclass
class SchemeFit:
    """Calculated scheme fit scores"""
    player_id: str
    program_id: str
    season: int
    
    # Fit scores (0-100)
    overall_fit_score: float
    scheme_compatibility: float
    coaching_style_fit: float
    position_need_score: float
    
    # Playing time projection
    projected_snap_share: float
    depth_chart_position: int
    competition_level: float
    
    # Learning curve
    system_familiarity: float
    adjustment_difficulty: float
    time_to_impact: str  # Immediate, Short (1 season), Medium (2 seasons)


@dataclass
class TransferRecord:
    """Historical transfer portal data"""
    player_id: str
    transfer_date: date
    from_program: str
    to_program: str
    
    # Context
    reason_category: str  # Playing time, Coaching change, NIL, Location, etc.
    eligibility_at_transfer: int
    portal_entry_timing: str  # Early, Regular, Late
    
    # Outcomes
    nil_deal_value: Optional[float] = None
    immediate_starter: bool = False
    first_season_snaps: Optional[int] = None
    first_season_performance_grade: Optional[float] = None
    
    # Market competition
    reported_finalists: List[str] = field(default_factory=list)
    decision_timeline_days: Optional[int] = None


@dataclass
class PlayerValuation:
    """Complete player valuation output"""
    player_id: str
    valuation_date: date
    current_program: str
    
    # Component scores (normalized 0-100)
    performance_score: float
    brand_score: float
    scheme_fit_score: float
    positional_value_score: float
    win_impact_score: float
    
    # Risk adjustments
    injury_risk_factor: float
    performance_risk_factor: float
    off_field_risk_factor: float
    
    # Final valuations
    current_program_value: float  # Total value to current program
    market_value: float  # Expected transfer portal value
    value_confidence_interval: tuple  # (low, high)
    
    # Alternative program valuations
    alternative_program_values: Dict[str, float] = field(default_factory=dict)
    
    # Value drivers breakdown
    value_components: Dict[str, float] = field(default_factory=dict)
    key_value_drivers: List[str] = field(default_factory=list)
    
    # Metadata
    model_version: str = "1.0"
    notes: str = ""


@dataclass
class BacktestRecord:
    """Record for model validation"""
    player_id: str
    prediction_date: date
    actual_outcome_date: date
    
    # Predictions
    predicted_market_value: float
    predicted_destination_probabilities: Dict[str, float]
    predicted_performance_grade: float
    
    # Actuals
    actual_nil_value: Optional[float] = None
    actual_destination: Optional[str] = None
    actual_performance_grade: Optional[float] = None
    
    # Error metrics
    value_prediction_error: Optional[float] = None
    destination_prediction_accuracy: Optional[bool] = None
    performance_prediction_error: Optional[float] = None
