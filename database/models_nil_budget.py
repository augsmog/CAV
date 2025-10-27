"""
NIL Budget Database Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class NILBudget(Base):
    """Team NIL budget information"""
    __tablename__ = 'nil_budgets'
    
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    team_name = Column(String, nullable=False)
    conference = Column(String)
    
    # Budget information
    nil_budget = Column(Float)  # Total NIL budget in dollars
    tier = Column(String)  # Elite, High, Medium, Low
    
    # Metadata
    season = Column(Integer, default=2023)
    source = Column(String)  # Where data came from
    is_estimate = Column(Boolean, default=True)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    team = relationship("Team", back_populates="nil_budgets")
    
    def __repr__(self):
        return f"<NILBudget(team='{self.team_name}', budget=${self.nil_budget:,.0f}, tier='{self.tier}')>"


# Add relationship to Team model (would need to be added to database/models.py)
# class Team(Base):
#     ...
#     nil_budgets = relationship("NILBudget", back_populates="team")

