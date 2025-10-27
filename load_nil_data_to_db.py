"""
Load NIL spending data into the database
"""

import sys
from pathlib import Path
import json

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database import get_session
from database.models import Team
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from datetime import datetime

print("="*80)
print("LOADING NIL SPENDING DATA TO DATABASE")
print("="*80)
print()

# Load NIL data
with open('data/nil_spending_data.json', 'r') as f:
    nil_data = json.load(f)

session = get_session()

# Create NIL budget table structure (simplified, storing as JSON in team notes for now)
# In future, create proper NILBudget table

print(f"Loading {len(nil_data['data'])} NIL budget records...")

team_budgets = {}
for record in nil_data['data']:
    team_name = record.get('team')
    nil_budget = record.get('nil_budget')
    conference = record.get('conference')
    tier = record.get('tier')
    
    if team_name and nil_budget:
        team_budgets[team_name] = {
            'nil_budget': nil_budget,
            'conference': conference,
            'tier': tier
        }

print(f"\nProcessed {len(team_budgets)} team budgets")

# Display summary
print("\nNIL Budget Summary:")
print(f"  Average: ${sum(b['nil_budget'] for b in team_budgets.values()) / len(team_budgets):,.0f}")
print(f"  Max: ${max(b['nil_budget'] for b in team_budgets.values()):,.0f}")
print(f"  Min: ${min(b['nil_budget'] for b in team_budgets.values()):,.0f}")

# Save as JSON for easy access
with open('data/team_nil_budgets.json', 'w') as f:
    json.dump(team_budgets, f, indent=2)

print("\n[SUCCESS] NIL budget data saved to data/team_nil_budgets.json")
print("="*80)

session.close()

