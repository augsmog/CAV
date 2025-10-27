"""
NIL and Personal Brand Valuation Module
Estimates player's NIL value and brand strength
"""

import numpy as np
from typing import Dict, List, Optional
from datetime import datetime


class BrandValuationCalculator:
    """
    Calculate player's personal brand value and NIL potential
    """
    
    def __init__(self):
        self.position_brand_multipliers = self._initialize_position_multipliers()
        self.market_size_factors = self._initialize_market_factors()
    
    def _initialize_position_multipliers(self) -> Dict:
        """QB and skill positions have higher brand value"""
        return {
            'QB': 2.5,
            'WR': 1.5,
            'RB': 1.4,
            'TE': 1.1,
            'CB': 1.2,
            'S': 1.1,
            'LB': 1.2,
            'DL': 1.3,
            'OL': 0.9,
            'SPEC': 1.0
        }
    
    def _initialize_market_factors(self) -> Dict:
        """Media market size impact on NIL value"""
        return {
            'tier_1': 1.5,  # Top 10 markets (LA, NYC, Chicago, etc.)
            'tier_2': 1.3,  # Top 25 markets
            'tier_3': 1.1,  # Top 50 markets
            'tier_4': 1.0,  # Other markets
            'tier_5': 0.9   # Small markets
        }
    
    def calculate_brand_score(self,
                            player_profile: Dict,
                            current_program: str,
                            performance_score: float) -> Dict:
        """
        Calculate comprehensive brand score and NIL value estimate
        
        Args:
            player_profile: Player demographics, social media, etc.
            current_program: Current school
            performance_score: Performance rating (0-100)
            
        Returns:
            Dictionary with brand score, NIL estimate, and components
        """
        # Component scores
        social_score = self._calculate_social_media_score(player_profile)
        media_score = self._calculate_media_presence_score(player_profile)
        on_field_score = performance_score  # Performance drives brand
        marketability_score = self._calculate_marketability_score(player_profile)
        market_size_score = self._calculate_market_size_impact(current_program)
        
        # Weighted brand score
        brand_score = (
            social_score * 0.25 +
            media_score * 0.20 +
            on_field_score * 0.30 +
            marketability_score * 0.15 +
            market_size_score * 0.10
        )
        
        # Position multiplier
        position = player_profile.get('position', 'OL')
        position_multiplier = self.position_brand_multipliers.get(position, 1.0)
        
        adjusted_brand_score = brand_score * position_multiplier
        
        # NIL value estimation
        nil_estimate = self._estimate_nil_value(
            adjusted_brand_score,
            current_program,
            player_profile
        )
        
        return {
            'brand_score': min(adjusted_brand_score, 100),
            'raw_brand_score': brand_score,
            'nil_value_estimate': nil_estimate,
            'components': {
                'social_media': social_score,
                'media_presence': media_score,
                'on_field_performance': on_field_score,
                'marketability': marketability_score,
                'market_size': market_size_score
            },
            'position_multiplier': position_multiplier,
            'growth_trajectory': self._calculate_brand_growth_trajectory(player_profile),
            'key_brand_drivers': self._identify_brand_drivers(player_profile, performance_score)
        }
    
    def _calculate_social_media_score(self, profile: Dict) -> float:
        """Calculate score based on social media presence"""
        score = 0
        
        # Instagram (most important for college athletes)
        instagram = profile.get('instagram_followers', 0)
        instagram_score = self._follower_score(instagram, platform='instagram')
        
        # Twitter/X
        twitter = profile.get('twitter_followers', 0)
        twitter_score = self._follower_score(twitter, platform='twitter')
        
        # TikTok (growing importance)
        tiktok = profile.get('tiktok_followers', 0)
        tiktok_score = self._follower_score(tiktok, platform='tiktok')
        
        # Weighted by platform importance
        score = (instagram_score * 0.5 + 
                twitter_score * 0.3 + 
                tiktok_score * 0.2)
        
        # Engagement rate multiplier
        engagement = profile.get('engagement_rate', 0.03)  # 3% average
        if engagement > 0.05:
            score *= 1.2  # High engagement bonus
        elif engagement < 0.02:
            score *= 0.9  # Low engagement penalty
        
        # Follower growth rate
        growth_rate = profile.get('follower_growth_rate', 0)
        if growth_rate > 0.10:  # >10% monthly growth
            score *= 1.15
        
        return min(score, 100)
    
    def _follower_score(self, followers: int, platform: str) -> float:
        """Convert follower count to score using logarithmic scale"""
        if followers == 0:
            return 0
        
        # Platform-specific benchmarks
        benchmarks = {
            'instagram': {'elite': 500000, 'good': 100000, 'avg': 10000},
            'twitter': {'elite': 300000, 'good': 50000, 'avg': 5000},
            'tiktok': {'elite': 1000000, 'good': 200000, 'avg': 20000}
        }
        
        bench = benchmarks.get(platform, benchmarks['instagram'])
        
        if followers >= bench['elite']:
            return 95
        elif followers >= bench['good']:
            # Logarithmic interpolation between good and elite
            return 70 + 25 * (np.log10(followers) - np.log10(bench['good'])) / \
                   (np.log10(bench['elite']) - np.log10(bench['good']))
        elif followers >= bench['avg']:
            return 40 + 30 * (followers - bench['avg']) / (bench['good'] - bench['avg'])
        else:
            return 40 * followers / bench['avg']
    
    def _calculate_media_presence_score(self, profile: Dict) -> float:
        """Calculate score based on traditional media coverage"""
        score = 50  # Base score
        
        # Google search volume
        search_volume = profile.get('google_search_volume', 0)
        if search_volume > 100000:
            score += 30
        elif search_volume > 50000:
            score += 20
        elif search_volume > 10000:
            score += 10
        
        # Media mentions
        media_mentions = profile.get('media_mentions_monthly', 0)
        mention_score = min(media_mentions / 10 * 5, 20)  # Cap at 20 points
        score += mention_score
        
        # National vs local coverage
        national_coverage = profile.get('national_media_coverage', False)
        if national_coverage:
            score += 15
        
        # Awards and recognition
        awards = profile.get('awards', [])
        score += min(len(awards) * 3, 15)  # 3 points per award, cap at 15
        
        return min(score, 100)
    
    def _calculate_marketability_score(self, profile: Dict) -> float:
        """Calculate personal marketability factors"""
        score = 50  # Base
        
        # Personality and likability (would be from surveys/assessments)
        personality = profile.get('personality_rating', 5)  # 1-10 scale
        score += (personality - 5) * 8
        
        # Media skills and interview performance
        media_skills = profile.get('media_skills_rating', 5)
        score += (media_skills - 5) * 6
        
        # Community engagement
        community_work = profile.get('community_engagement_hours', 0)
        score += min(community_work / 10, 10)  # Cap at 10 points
        
        # Controversy/risk factors
        controversies = profile.get('negative_incidents', 0)
        score -= controversies * 15  # Significant penalty
        
        # Hometown hero factor
        if profile.get('playing_in_home_state', False):
            score += 10
        
        # Unique story/background
        if profile.get('compelling_backstory', False):
            score += 15
        
        return max(0, min(score, 100))
    
    def _calculate_market_size_impact(self, program: str) -> float:
        """Calculate impact of program's media market"""
        # Would map programs to their market tiers
        program_markets = {
            # Tier 1 - Major metros
            'USC': 'tier_1', 'UCLA': 'tier_1', 'Miami': 'tier_1',
            # Tier 2 - Large markets
            'Texas': 'tier_2', 'Michigan': 'tier_2', 'Ohio State': 'tier_2',
            'Penn State': 'tier_2', 'Notre Dame': 'tier_2',
            # Tier 3 - Medium markets
            'Alabama': 'tier_3', 'Georgia': 'tier_3', 'Oregon': 'tier_3',
            # etc...
        }
        
        tier = program_markets.get(program, 'tier_4')
        base_score = 50
        
        factor = self.market_size_factors[tier]
        return base_score * factor
    
    def _estimate_nil_value(self,
                          brand_score: float,
                          program: str,
                          profile: Dict) -> Dict:
        """
        Estimate annual NIL value
        
        Returns range: (low, expected, high)
        """
        # Base value from brand score
        base_value = (brand_score / 100) * 100000  # $100k at perfect score
        
        # Program NIL collective strength multiplier
        program_nil_strength = self._get_program_nil_strength(program)
        
        # Adjust for position
        position = profile.get('position', 'OL')
        position_mult = self.position_brand_multipliers.get(position, 1.0)
        
        # Starter vs backup
        starter = profile.get('is_starter', False)
        starter_mult = 1.5 if starter else 0.6
        
        # Years of eligibility (more years = higher total value potential)
        years_remaining = profile.get('eligibility_remaining', 1)
        
        expected_annual = base_value * program_nil_strength * position_mult * starter_mult
        
        # Confidence intervals
        low_estimate = expected_annual * 0.7
        high_estimate = expected_annual * 1.4
        
        # Total career NIL potential
        total_potential = expected_annual * years_remaining
        
        return {
            'annual_expected': round(expected_annual, -3),  # Round to nearest thousand
            'annual_low': round(low_estimate, -3),
            'annual_high': round(high_estimate, -3),
            'career_potential': round(total_potential, -3),
            'confidence': self._calculate_nil_confidence(brand_score, profile)
        }
    
    def _get_program_nil_strength(self, program: str) -> float:
        """
        Get program's NIL collective strength multiplier
        Based on reported collective sizes and activity
        """
        # Top tier programs with strong collectives
        tier_1_programs = ['Texas', 'Texas A&M', 'Miami', 'USC', 'Ohio State', 
                          'Alabama', 'Georgia', 'Oregon']
        tier_2_programs = ['Michigan', 'Florida State', 'Clemson', 'Penn State',
                          'Notre Dame', 'LSU', 'Oklahoma']
        
        if program in tier_1_programs:
            return 1.5
        elif program in tier_2_programs:
            return 1.3
        else:
            return 1.0
    
    def _calculate_brand_growth_trajectory(self, profile: Dict) -> str:
        """Predict brand growth trajectory"""
        current_followers = sum([
            profile.get('instagram_followers', 0),
            profile.get('twitter_followers', 0),
            profile.get('tiktok_followers', 0)
        ])
        
        growth_rate = profile.get('follower_growth_rate', 0)
        media_mentions = profile.get('media_mentions_monthly', 0)
        
        if growth_rate > 0.15 and media_mentions > 50:
            return "Rapidly Growing"
        elif growth_rate > 0.08 or media_mentions > 25:
            return "Growing"
        elif growth_rate > 0:
            return "Stable"
        else:
            return "Declining"
    
    def _calculate_nil_confidence(self, brand_score: float, profile: Dict) -> float:
        """Calculate confidence in NIL estimate"""
        confidence = 70  # Base confidence
        
        # Known NIL deals increase confidence
        if profile.get('known_nil_deals'):
            confidence += 20
        
        # Established social presence increases confidence
        total_followers = sum([
            profile.get('instagram_followers', 0),
            profile.get('twitter_followers', 0)
        ])
        if total_followers > 50000:
            confidence += 10
        
        # Brand score extremes have more uncertainty
        if 30 < brand_score < 70:
            confidence += 10  # Middle range most predictable
        
        return min(confidence, 95)
    
    def _identify_brand_drivers(self, profile: Dict, performance: float) -> List[str]:
        """Identify key factors driving brand value"""
        drivers = []
        
        if performance > 80:
            drivers.append("Elite on-field performance")
        
        total_followers = sum([
            profile.get('instagram_followers', 0),
            profile.get('twitter_followers', 0),
            profile.get('tiktok_followers', 0)
        ])
        
        if total_followers > 200000:
            drivers.append("Strong social media presence")
        
        if profile.get('national_media_coverage'):
            drivers.append("National media recognition")
        
        if profile.get('position') == 'QB':
            drivers.append("Premium position (QB)")
        
        if profile.get('personality_rating', 5) > 7:
            drivers.append("High marketability")
        
        return drivers
    
    def compare_nil_markets(self,
                          player_profile: Dict,
                          current_program: str,
                          target_programs: List[str],
                          performance_score: float) -> Dict:
        """
        Compare potential NIL value across different programs
        """
        comparisons = {}
        
        # Current program
        current_brand = self.calculate_brand_score(
            player_profile,
            current_program,
            performance_score
        )
        
        comparisons[current_program] = {
            'nil_value': current_brand['nil_value_estimate']['annual_expected'],
            'brand_score': current_brand['brand_score'],
            'market_advantage': 0  # Baseline
        }
        
        # Compare with target programs
        for target in target_programs:
            # Temporarily update profile for target program
            temp_profile = player_profile.copy()
            target_brand = self.calculate_brand_score(
                temp_profile,
                target,
                performance_score
            )
            
            nil_diff = (target_brand['nil_value_estimate']['annual_expected'] - 
                       current_brand['nil_value_estimate']['annual_expected'])
            
            comparisons[target] = {
                'nil_value': target_brand['nil_value_estimate']['annual_expected'],
                'brand_score': target_brand['brand_score'],
                'market_advantage': nil_diff,
                'percent_change': (nil_diff / max(current_brand['nil_value_estimate']['annual_expected'], 1)) * 100
            }
        
        # Rank by potential value
        ranked = sorted(
            comparisons.items(),
            key=lambda x: x[1]['nil_value'],
            reverse=True
        )
        
        return {
            'current_program': current_program,
            'current_nil_value': comparisons[current_program]['nil_value'],
            'comparisons': dict(ranked),
            'best_nil_market': ranked[0][0],
            'max_nil_upside': ranked[0][1]['nil_value'] - comparisons[current_program]['nil_value']
        }
