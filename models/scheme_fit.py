"""
Scheme Fit Module
Analyzes player fit with different coaching schemes and systems
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SchemeRequirements:
    """Requirements for a specific scheme"""
    scheme_name: str
    position: str
    
    # Physical requirements (ideal ranges)
    height_range: Optional[Tuple[int, int]] = None
    weight_range: Optional[Tuple[int, int]] = None
    speed_requirement: Optional[float] = None  # 40-yard dash
    
    # Skill requirements (importance 0-10)
    skill_weights: Dict[str, float] = None
    
    # Experience/learning curve
    complexity_level: int = 5  # 1-10 scale
    
    def __post_init__(self):
        if self.skill_weights is None:
            self.skill_weights = {}


class SchemeFitCalculator:
    """
    Calculates how well a player fits different schemes
    """
    
    def __init__(self):
        self.scheme_requirements = self._initialize_scheme_requirements()
        self.position_archetypes = self._initialize_position_archetypes()
    
    def _initialize_scheme_requirements(self) -> Dict:
        """
        Define scheme requirements by position
        """
        return {
            'Air Raid': {
                'QB': SchemeRequirements(
                    scheme_name='Air Raid',
                    position='QB',
                    height_range=(70, 78),
                    weight_range=(190, 230),
                    skill_weights={
                        'arm_strength': 7,
                        'quick_release': 9,
                        'accuracy_short': 8,
                        'accuracy_medium': 9,
                        'accuracy_deep': 7,
                        'decision_making': 9,
                        'mobility': 5,
                        'pocket_presence': 8
                    },
                    complexity_level=7
                ),
                'WR': SchemeRequirements(
                    scheme_name='Air Raid',
                    position='WR',
                    skill_weights={
                        'route_running': 9,
                        'separation': 9,
                        'hands': 8,
                        'speed': 7,
                        'release': 8,
                        'yards_after_catch': 6
                    },
                    complexity_level=7
                )
            },
            'Spread': {
                'QB': SchemeRequirements(
                    scheme_name='Spread',
                    position='QB',
                    height_range=(70, 78),
                    weight_range=(195, 235),
                    skill_weights={
                        'arm_strength': 7,
                        'accuracy_short': 8,
                        'accuracy_medium': 8,
                        'decision_making': 8,
                        'mobility': 8,
                        'read_option_skills': 7,
                        'pocket_presence': 6
                    },
                    complexity_level=6
                ),
                'RB': SchemeRequirements(
                    scheme_name='Spread',
                    position='RB',
                    skill_weights={
                        'speed': 9,
                        'agility': 8,
                        'receiving': 7,
                        'vision': 7,
                        'pass_blocking': 5,
                        'power': 5
                    },
                    complexity_level=5
                )
            },
            'Pro Style': {
                'QB': SchemeRequirements(
                    scheme_name='Pro Style',
                    position='QB',
                    height_range=(73, 80),
                    weight_range=(210, 245),
                    skill_weights={
                        'arm_strength': 8,
                        'accuracy_short': 8,
                        'accuracy_medium': 9,
                        'accuracy_deep': 8,
                        'decision_making': 9,
                        'pocket_presence': 9,
                        'pre_snap_reads': 9,
                        'mobility': 4
                    },
                    complexity_level=9
                ),
                'RB': SchemeRequirements(
                    scheme_name='Pro Style',
                    position='RB',
                    skill_weights={
                        'power': 8,
                        'vision': 9,
                        'receiving': 7,
                        'pass_blocking': 8,
                        'patience': 8,
                        'speed': 6
                    },
                    complexity_level=7
                )
            },
            '3-4 Defense': {
                'LB': SchemeRequirements(
                    scheme_name='3-4 Defense',
                    position='LB',
                    weight_range=(235, 265),
                    skill_weights={
                        'pass_rush': 8,
                        'run_defense': 7,
                        'coverage': 7,
                        'versatility': 9,
                        'strength': 8,
                        'speed': 6
                    },
                    complexity_level=8
                )
            },
            '4-3 Defense': {
                'LB': SchemeRequirements(
                    scheme_name='4-3 Defense',
                    position='LB',
                    weight_range=(225, 250),
                    skill_weights={
                        'coverage': 8,
                        'run_defense': 8,
                        'speed': 8,
                        'instincts': 9,
                        'tackle_efficiency': 8,
                        'pass_rush': 5
                    },
                    complexity_level=7
                )
            }
        }
    
    def _return_neutral_fit(self, reason: str) -> Dict:
        """
        Return a neutral/default fit score when scheme or position is not defined
        This allows valuation to proceed for all players even if specific fit isn't calculated
        """
        neutral_score = 70.0  # Neutral/average fit
        return {
            'overall_fit_score': neutral_score,
            'confidence': 0.3,  # Low confidence due to missing data
            'components': {
                'physical_fit': neutral_score,
                'skill_fit': neutral_score,
                'archetype_match': neutral_score,
                'learning_curve': neutral_score,
                'versatility_bonus': 0.0
            },
            'projected_adaptation_time': 6,  # Months (average)
            'key_strengths': [],
            'key_concerns': [reason],
            'scheme_specific_notes': f'Using neutral fit score: {reason}'
        }
    
    def _initialize_position_archetypes(self) -> Dict:
        """
        Define player archetypes for better matching
        """
        return {
            'QB': {
                'Pocket Passer': {
                    'arm_strength': 8, 'accuracy_medium': 9, 'accuracy_deep': 8,
                    'pocket_presence': 9, 'mobility': 3, 'size': 8
                },
                'Dual Threat': {
                    'arm_strength': 7, 'accuracy_medium': 7, 'mobility': 9,
                    'decision_making': 7, 'athleticism': 9, 'size': 6
                },
                'Game Manager': {
                    'accuracy_short': 9, 'decision_making': 9, 'pocket_presence': 8,
                    'arm_strength': 6, 'mobility': 4, 'ball_security': 9
                }
            },
            'RB': {
                'Power Back': {
                    'power': 9, 'size': 9, 'pass_blocking': 8,
                    'speed': 5, 'agility': 5, 'receiving': 5
                },
                'Speed Back': {
                    'speed': 9, 'agility': 9, 'big_play_ability': 9,
                    'power': 4, 'pass_blocking': 4, 'size': 4
                },
                'All-Purpose': {
                    'receiving': 9, 'speed': 7, 'agility': 8,
                    'vision': 8, 'versatility': 9, 'power': 6
                }
            },
            'WR': {
                'Deep Threat': {
                    'speed': 10, 'deep_ball_tracking': 9, 'big_play': 9,
                    'route_running': 6, 'physical': 5
                },
                'Possession': {
                    'route_running': 9, 'hands': 9, 'contested_catch': 7,
                    'speed': 5, 'reliability': 9
                },
                'Slot': {
                    'quickness': 9, 'route_running': 9, 'yards_after_catch': 8,
                    'agility': 9, 'size': 4
                }
            }
        }
    
    def calculate_scheme_fit(self,
                           player_profile: Dict,
                           scheme_name: str,
                           position: str,
                           coaching_staff_profile: Optional[Dict] = None) -> Dict:
        """
        Calculate comprehensive scheme fit score
        
        Args:
            player_profile: Player skills, measurables, and characteristics
            scheme_name: Name of the scheme (e.g., 'Air Raid', 'Pro Style')
            position: Player's position
            coaching_staff_profile: Optional coaching staff characteristics
            
        Returns:
            Dictionary with overall fit score and component breakdowns
        """
        # Handle missing scheme or position gracefully with neutral score
        if scheme_name not in self.scheme_requirements:
            return self._return_neutral_fit(f'Scheme {scheme_name} not found')
        
        if position not in self.scheme_requirements[scheme_name]:
            return self._return_neutral_fit(f'Position {position} not defined for scheme {scheme_name}')
        
        requirements = self.scheme_requirements[scheme_name][position]
        
        # Calculate physical fit
        physical_fit = self._calculate_physical_fit(player_profile, requirements)
        
        # Calculate skill fit
        skill_fit = self._calculate_skill_fit(player_profile, requirements)
        
        # Calculate archetype match
        archetype_match = self._calculate_archetype_match(player_profile, position, scheme_name)
        
        # Calculate learning curve
        learning_curve = self._calculate_learning_curve(
            player_profile,
            requirements,
            coaching_staff_profile
        )
        
        # Calculate position versatility value
        versatility_bonus = self._calculate_versatility_bonus(player_profile, scheme_name)
        
        # Weighted overall score
        overall_score = (
            physical_fit * 0.20 +
            skill_fit * 0.40 +
            archetype_match * 0.25 +
            learning_curve * 0.10 +
            versatility_bonus * 0.05
        )
        
        # Confidence in fit assessment
        confidence = self._calculate_fit_confidence(player_profile)
        
        return {
            'overall_fit_score': overall_score,
            'confidence': confidence,
            'components': {
                'physical_fit': physical_fit,
                'skill_fit': skill_fit,
                'archetype_match': archetype_match,
                'learning_curve': learning_curve,
                'versatility_bonus': versatility_bonus
            },
            'projected_adaptation_time': self._project_adaptation_time(learning_curve),
            'key_strengths': self._identify_key_strengths(player_profile, requirements),
            'key_concerns': self._identify_concerns(player_profile, requirements),
            'scheme_specific_notes': self._generate_scheme_notes(
                player_profile, requirements, scheme_name
            )
        }
    
    def _calculate_physical_fit(self, player: Dict, requirements: SchemeRequirements) -> float:
        """Calculate how well player's physical attributes match scheme"""
        score = 100.0
        
        # Height
        if requirements.height_range:
            height = player.get('height', 0)
            min_h, max_h = requirements.height_range
            if height < min_h:
                score -= (min_h - height) * 2
            elif height > max_h:
                score -= (height - max_h) * 1.5
        
        # Weight
        if requirements.weight_range:
            weight = player.get('weight', 0)
            min_w, max_w = requirements.weight_range
            if weight < min_w:
                score -= (min_w - weight) * 0.5
            elif weight > max_w:
                score -= (weight - max_w) * 0.3
        
        # Speed
        if requirements.speed_requirement:
            forty_time = player.get('forty_yard_dash', 5.0)
            if forty_time > requirements.speed_requirement:
                score -= (forty_time - requirements.speed_requirement) * 10
        
        return max(0, min(100, score))
    
    def _calculate_skill_fit(self, player: Dict, requirements: SchemeRequirements) -> float:
        """Calculate how well player's skills match scheme requirements"""
        player_skills = player.get('skills', {})
        required_skills = requirements.skill_weights
        
        if not required_skills:
            return 50.0  # Neutral if no requirements defined
        
        total_weight = sum(required_skills.values())
        weighted_score = 0
        
        for skill, importance in required_skills.items():
            player_skill_level = player_skills.get(skill, 5.0)  # Default to average
            
            # Normalize to 0-100 scale
            normalized_skill = (player_skill_level / 10) * 100
            
            # Weight by importance
            weighted_score += normalized_skill * (importance / total_weight)
        
        return weighted_score
    
    def _calculate_archetype_match(self, player: Dict, position: str, scheme: str) -> float:
        """Determine how well player matches ideal archetypes for the scheme"""
        if position not in self.position_archetypes:
            return 50.0
        
        archetypes = self.position_archetypes[position]
        player_skills = player.get('skills', {})
        
        best_match_score = 0
        
        for archetype_name, archetype_profile in archetypes.items():
            match_score = 0
            total_traits = len(archetype_profile)
            
            for trait, ideal_value in archetype_profile.items():
                player_value = player_skills.get(trait, 5.0)
                # How close is player to ideal for this trait
                trait_match = 100 - abs(ideal_value - player_value) * 10
                match_score += max(0, trait_match)
            
            avg_match = match_score / total_traits
            best_match_score = max(best_match_score, avg_match)
        
        return best_match_score
    
    def _calculate_learning_curve(self,
                                 player: Dict,
                                 requirements: SchemeRequirements,
                                 coaching_staff: Optional[Dict]) -> float:
        """
        Estimate how quickly player can learn the scheme
        Higher score = faster learning
        """
        base_score = 50.0
        
        # Football IQ
        football_iq = player.get('football_iq', 5.0)
        base_score += (football_iq - 5.0) * 8
        
        # Previous scheme experience
        previous_schemes = player.get('scheme_history', [])
        if requirements.scheme_name in previous_schemes:
            base_score += 30  # Significant bonus for same scheme
        elif any(s in previous_schemes for s in self._get_similar_schemes(requirements.scheme_name)):
            base_score += 15  # Moderate bonus for similar scheme
        
        # Adjust for scheme complexity
        complexity_penalty = (requirements.complexity_level - 5) * 3
        base_score -= complexity_penalty
        
        # Coaching staff development reputation
        if coaching_staff:
            development_rating = coaching_staff.get('player_development_rating', 5.0)
            base_score += (development_rating - 5.0) * 5
        
        # Years of experience
        experience_years = player.get('years_playing', 0)
        base_score += min(experience_years * 3, 15)  # Cap at 15 points
        
        return max(0, min(100, base_score))
    
    def _calculate_versatility_bonus(self, player: Dict, scheme: str) -> float:
        """Bonus for players who can play multiple positions/roles"""
        versatility_score = player.get('positional_versatility', 0)
        
        # Schemes that value versatility more
        high_versatility_schemes = ['Spread', 'Multiple', 'Nickel']
        
        if scheme in high_versatility_schemes:
            return versatility_score * 10
        else:
            return versatility_score * 5
    
    def _calculate_fit_confidence(self, player: Dict) -> float:
        """
        Calculate confidence in the fit assessment
        Based on data completeness and quality
        """
        confidence = 100.0
        
        # Check for missing key data
        required_fields = ['height', 'weight', 'skills', 'football_iq']
        for field in required_fields:
            if field not in player or not player[field]:
                confidence -= 15
        
        # Check film grade availability
        if 'film_grade' not in player:
            confidence -= 10
        
        # Check for recent performance data
        if 'recent_season_stats' not in player:
            confidence -= 10
        
        return max(0, min(100, confidence))
    
    def _project_adaptation_time(self, learning_curve_score: float) -> str:
        """Project how long adaptation will take"""
        if learning_curve_score >= 80:
            return "Immediate Impact"
        elif learning_curve_score >= 60:
            return "1-2 Games"
        elif learning_curve_score >= 40:
            return "Half Season"
        elif learning_curve_score >= 20:
            return "Full Season"
        else:
            return "1-2 Years"
    
    def _identify_key_strengths(self, player: Dict, requirements: SchemeRequirements) -> List[str]:
        """Identify player's key strengths for this scheme"""
        strengths = []
        player_skills = player.get('skills', {})
        
        for skill, importance in requirements.skill_weights.items():
            if importance >= 8:  # Highly important skill
                player_level = player_skills.get(skill, 5.0)
                if player_level >= 7.5:
                    strengths.append(f"Excellent {skill.replace('_', ' ')}")
        
        return strengths[:5]  # Top 5 strengths
    
    def _identify_concerns(self, player: Dict, requirements: SchemeRequirements) -> List[str]:
        """Identify potential concerns for this scheme"""
        concerns = []
        player_skills = player.get('skills', {})
        
        for skill, importance in requirements.skill_weights.items():
            if importance >= 7:  # Important skill
                player_level = player_skills.get(skill, 5.0)
                if player_level < 5.0:
                    concerns.append(f"Below average {skill.replace('_', ' ')}")
        
        # Physical concerns
        if requirements.height_range:
            height = player.get('height', 0)
            min_h, max_h = requirements.height_range
            if height < min_h - 2:
                concerns.append("Height concerns for scheme")
        
        return concerns[:5]  # Top 5 concerns
    
    def _generate_scheme_notes(self,
                              player: Dict,
                              requirements: SchemeRequirements,
                              scheme_name: str) -> str:
        """Generate human-readable notes about the fit"""
        notes = []
        
        fit_score = self._calculate_skill_fit(player, requirements)
        
        if fit_score >= 80:
            notes.append(f"Excellent fit for {scheme_name} system.")
        elif fit_score >= 60:
            notes.append(f"Good fit for {scheme_name} with minor adjustments needed.")
        else:
            notes.append(f"Significant development required for {scheme_name}.")
        
        return " ".join(notes)
    
    def _get_similar_schemes(self, scheme_name: str) -> List[str]:
        """Get list of similar schemes for experience matching"""
        scheme_families = {
            'Air Raid': ['Spread', 'West Coast'],
            'Spread': ['Air Raid', 'Option'],
            'Pro Style': ['West Coast'],
            'Option': ['Spread'],
            '3-4 Defense': ['Multiple'],
            '4-3 Defense': ['Nickel']
        }
        return scheme_families.get(scheme_name, [])
    
    def compare_scheme_fits(self,
                          player: Dict,
                          schemes: List[str],
                          position: str) -> Dict:
        """
        Compare player fit across multiple schemes
        Returns ranked list of schemes
        """
        fits = {}
        
        for scheme in schemes:
            fit_result = self.calculate_scheme_fit(player, scheme, position)
            if 'error' not in fit_result:
                fits[scheme] = fit_result
        
        # Rank by overall fit score
        ranked_schemes = sorted(
            fits.items(),
            key=lambda x: x[1]['overall_fit_score'],
            reverse=True
        )
        
        return {
            'best_fit': ranked_schemes[0][0] if ranked_schemes else None,
            'all_fits': dict(ranked_schemes),
            'fit_differential': ranked_schemes[0][1]['overall_fit_score'] - ranked_schemes[-1][1]['overall_fit_score'] if len(ranked_schemes) > 1 else 0
        }
