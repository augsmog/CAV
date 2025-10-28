"""
Pillar 5: Intangible Factors & Brand Value
Off-field value drivers including social media, marketability, and personal brand
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class BrandValueResult:
    """Result from brand/intangibles analysis"""
    brand_score: float  # 0-100 brand strength
    nil_premium: float  # Additional NIL value from brand (% boost)
    social_media_score: float
    marketability_score: float
    visibility_score: float
    total_brand_value: float  # Dollar value of brand
    tier: str  # 'mega-influencer', 'strong', 'moderate', 'minimal'
    components: Dict[str, Any]


class BrandIntangiblesModel:
    """
    Calculates off-field brand value and intangible factors
    Social media following, marketability, visibility, personal brand
    """

    # Social media follower benchmarks
    SOCIAL_BENCHMARKS = {
        'mega': {'min_followers': 500_000, 'premium': 0.40},  # 40% NIL boost
        'strong': {'min_followers': 100_000, 'premium': 0.25},
        'moderate': {'min_followers': 25_000, 'premium': 0.10},
        'minimal': {'min_followers': 0, 'premium': 0.02}
    }

    # Position visibility multipliers (media exposure)
    FOOTBALL_POSITION_VISIBILITY = {
        'QB': 2.5,   # Highest visibility
        'RB': 1.8,
        'WR': 1.7,
        'TE': 1.3,
        'EDGE': 1.4,
        'CB': 1.3,
        'LB': 1.2,
        'S': 1.1,
        'DL': 1.2,
        'OL': 0.85,  # Lowest visibility
        'K': 0.9,
        'P': 0.85
    }

    BASKETBALL_POSITION_VISIBILITY = {
        # Basketball more position-neutral
        'PG': 1.3,
        'SG': 1.2,
        'SF': 1.2,
        'PF': 1.1,
        'C': 1.1
    }

    # Engagement rate quality tiers
    ENGAGEMENT_TIERS = {
        'excellent': {'min_rate': 0.08, 'multiplier': 1.30},  # 8%+ engagement
        'great': {'min_rate': 0.05, 'multiplier': 1.20},
        'good': {'min_rate': 0.03, 'multiplier': 1.10},
        'average': {'min_rate': 0.01, 'multiplier': 1.00},
        'poor': {'min_rate': 0, 'multiplier': 0.90}
    }

    def __init__(self, sport: str = 'football'):
        """
        Initialize brand/intangibles model

        Args:
            sport: 'football' or 'basketball'
        """
        self.sport = sport.lower()
        self.position_visibility = (
            self.FOOTBALL_POSITION_VISIBILITY if sport == 'football'
            else self.BASKETBALL_POSITION_VISIBILITY
        )

    def calculate_brand_value(
        self,
        position: str,
        social_media: Optional[Dict[str, Any]] = None,
        performance_score: float = 70,
        school_data: Optional[Dict[str, Any]] = None,
        personal_attributes: Optional[Dict[str, Any]] = None
    ) -> BrandValueResult:
        """
        Calculate brand value and intangible factors

        Args:
            position: Player position
            social_media: Social media metrics (followers, engagement, etc.)
            performance_score: On-field performance (0-100)
            school_data: School context (market size, success, etc.)
            personal_attributes: Charisma, community involvement, etc.

        Returns:
            BrandValueResult with scores and NIL premium
        """
        # 1. Social media score
        social_score, social_premium = self._calculate_social_media_value(
            social_media
        )

        # 2. Position visibility
        visibility_mult = self._calculate_visibility_score(position, school_data)

        # 3. Marketability factors
        marketability = self._calculate_marketability(
            position, performance_score, personal_attributes
        )

        # 4. Regional/hometown appeal
        regional_premium = self._calculate_regional_appeal(
            school_data, personal_attributes
        )

        # Combine into overall brand score (0-100)
        brand_score = (
            social_score * 0.40 +
            visibility_mult * 20 +  # Normalize to 0-100
            marketability * 0.35 +
            regional_premium * 20 * 0.15
        )
        brand_score = min(brand_score, 100)

        # Calculate NIL premium (% boost over base NIL)
        nil_premium = (
            social_premium +
            (visibility_mult - 1.0) * 0.15 +
            (marketability / 100) * 0.10 +
            regional_premium * 0.05
        )

        # Determine tier
        tier = self._determine_brand_tier(social_media, brand_score)

        # Estimate total brand value in dollars
        total_brand_value = self._estimate_brand_dollar_value(
            brand_score, nil_premium, performance_score
        )

        return BrandValueResult(
            brand_score=brand_score,
            nil_premium=nil_premium,
            social_media_score=social_score,
            marketability_score=marketability,
            visibility_score=visibility_mult * 20,  # Normalized to 0-100
            total_brand_value=total_brand_value,
            tier=tier,
            components={
                'social_media_premium': social_premium,
                'visibility_multiplier': visibility_mult,
                'regional_premium': regional_premium,
                'position': position
            }
        )

    def _calculate_social_media_value(
        self, social_media: Optional[Dict[str, Any]]
    ) -> tuple[float, float]:
        """
        Calculate social media score and premium

        Returns:
            (score 0-100, premium as decimal)
        """
        if not social_media:
            return (40.0, 0.02)  # Default minimal

        # Calculate total followers (weighted by platform)
        instagram = social_media.get('instagram_followers', 0)
        twitter = social_media.get('twitter_followers', 0)
        tiktok = social_media.get('tiktok_followers', 0)

        # Weighted sum (Instagram 50%, Twitter 30%, TikTok 20%)
        total_weighted = (instagram * 0.50) + (twitter * 0.30) + (tiktok * 0.20)

        # Determine tier
        tier_info = None
        for tier_name, tier_data in self.SOCIAL_BENCHMARKS.items():
            if total_weighted >= tier_data['min_followers']:
                tier_info = tier_data
                break

        if not tier_info:
            tier_info = self.SOCIAL_BENCHMARKS['minimal']

        base_premium = tier_info['premium']

        # Engagement rate multiplier
        engagement_rate = social_media.get('engagement_rate', 0.02)
        engagement_mult = self._get_engagement_multiplier(engagement_rate)

        # Growth rate bonus
        growth_rate = social_media.get('monthly_growth_rate', 0.0)
        growth_bonus = 1.0
        if growth_rate >= 0.15:  # 15%+ monthly growth
            growth_bonus = 1.20
        elif growth_rate >= 0.10:
            growth_bonus = 1.15
        elif growth_rate >= 0.05:
            growth_bonus = 1.08

        # Calculate final premium
        final_premium = base_premium * engagement_mult * growth_bonus

        # Score (0-100)
        if total_weighted >= 500_000:
            score = 95
        elif total_weighted >= 250_000:
            score = 85
        elif total_weighted >= 100_000:
            score = 75
        elif total_weighted >= 50_000:
            score = 65
        elif total_weighted >= 25_000:
            score = 55
        elif total_weighted >= 10_000:
            score = 45
        else:
            score = 30 + (total_weighted / 10_000 * 15)  # Scale up to 45

        # Adjust for engagement
        score *= engagement_mult

        return (min(score, 100), final_premium)

    def _get_engagement_multiplier(self, engagement_rate: float) -> float:
        """Get engagement quality multiplier"""
        for tier_name, tier_data in self.ENGAGEMENT_TIERS.items():
            if engagement_rate >= tier_data['min_rate']:
                return tier_data['multiplier']
        return 1.0

    def _calculate_visibility_score(
        self,
        position: str,
        school_data: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate visibility multiplier

        Returns:
            Multiplier (0.85 - 2.5)
        """
        # Base position visibility
        position = self._normalize_position(position)
        base_visibility = self.position_visibility.get(position, 1.0)

        # Boost for successful programs (more TV time)
        if school_data:
            playoff_appearances = school_data.get('playoff_appearances_5yr', 0)
            ranked_weeks = school_data.get('ranked_weeks_per_year', 0)

            if self.sport == 'football':
                if playoff_appearances >= 2:
                    school_boost = 1.25
                elif playoff_appearances >= 1 or ranked_weeks >= 10:
                    school_boost = 1.15
                elif ranked_weeks >= 5:
                    school_boost = 1.08
                else:
                    school_boost = 1.00
            else:
                # Basketball
                tournament_runs = school_data.get('tournament_appearances_5yr', 0)
                if tournament_runs >= 4:
                    school_boost = 1.30
                elif tournament_runs >= 3:
                    school_boost = 1.20
                elif tournament_runs >= 2:
                    school_boost = 1.10
                else:
                    school_boost = 1.00
        else:
            school_boost = 1.0

        return base_visibility * school_boost

    def _calculate_marketability(
        self,
        position: str,
        performance_score: float,
        personal_attributes: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate marketability score (0-100)

        Factors: performance, personality, community involvement, controversy
        """
        # Base on performance (50% weight)
        base = performance_score * 0.50

        if not personal_attributes:
            return min(base + 25, 100)  # Default to 75th percentile

        # Personality/charisma (25% weight)
        charisma = personal_attributes.get('charisma', 'average')
        charisma_scores = {
            'exceptional': 95,
            'high': 85,
            'above_average': 75,
            'average': 60,
            'below_average': 45
        }
        charisma_score = charisma_scores.get(charisma, 60) * 0.25

        # Community involvement (15% weight)
        community = personal_attributes.get('community_involvement', 'moderate')
        community_scores = {
            'exceptional': 95,
            'high': 80,
            'moderate': 60,
            'low': 40,
            'none': 20
        }
        community_score = community_scores.get(community, 60) * 0.15

        # Academic excellence bonus (10% weight)
        academic = personal_attributes.get('academic_standing', 'average')
        academic_scores = {
            'academic_all_american': 95,
            'honor_roll': 80,
            'good_standing': 60,
            'average': 50
        }
        academic_score = academic_scores.get(academic, 50) * 0.10

        # Controversy discount (applies as negative)
        controversy = personal_attributes.get('controversy_level', 'none')
        controversy_discount = {
            'none': 0,
            'minor': -5,
            'moderate': -12,
            'major': -25
        }
        discount = controversy_discount.get(controversy, 0)

        total = base + charisma_score + community_score + academic_score + discount

        return max(20, min(total, 100))

    def _calculate_regional_appeal(
        self,
        school_data: Optional[Dict[str, Any]],
        personal_attributes: Optional[Dict[str, Any]]
    ) -> float:
        """
        Calculate regional/hometown appeal multiplier

        Returns:
            Multiplier (0.95 - 1.25)
        """
        if not personal_attributes:
            return 1.0

        # Hometown hero (playing for in-state school)
        hometown_hero = personal_attributes.get('hometown_hero', False)

        # Regional following
        regional_following = personal_attributes.get('regional_following', 'moderate')

        if hometown_hero:
            base = 1.20  # 20% premium for local NIL deals
        elif regional_following == 'strong':
            base = 1.15
        elif regional_following == 'moderate':
            base = 1.05
        else:
            base = 1.00

        return base

    def _normalize_position(self, position: str) -> str:
        """Normalize position to visibility category"""
        position = position.upper()

        if self.sport == 'football':
            mapping = {
                'QB': 'QB',
                'RB': 'RB', 'FB': 'RB',
                'WR': 'WR',
                'TE': 'TE',
                'OT': 'OL', 'OG': 'OL', 'C': 'OL', 'OL': 'OL',
                'DE': 'EDGE', 'EDGE': 'EDGE',
                'DT': 'DL', 'DL': 'DL',
                'LB': 'LB', 'ILB': 'LB', 'OLB': 'LB',
                'CB': 'CB',
                'S': 'S', 'FS': 'S', 'SS': 'S',
                'K': 'K',
                'P': 'P'
            }
            return mapping.get(position, 'WR')
        else:
            return position if position in ['PG', 'SG', 'SF', 'PF', 'C'] else 'SF'

    def _determine_brand_tier(
        self, social_media: Optional[Dict[str, Any]], brand_score: float
    ) -> str:
        """Determine brand tier classification"""
        if not social_media:
            return 'minimal'

        total_followers = (
            social_media.get('instagram_followers', 0) * 0.50 +
            social_media.get('twitter_followers', 0) * 0.30 +
            social_media.get('tiktok_followers', 0) * 0.20
        )

        if total_followers >= 500_000 or brand_score >= 90:
            return 'mega-influencer'
        elif total_followers >= 100_000 or brand_score >= 75:
            return 'strong'
        elif total_followers >= 25_000 or brand_score >= 55:
            return 'moderate'
        else:
            return 'minimal'

    def _estimate_brand_dollar_value(
        self, brand_score: float, nil_premium: float, performance_score: float
    ) -> float:
        """
        Estimate total brand value in dollars

        Returns:
            Estimated annual brand value ($)
        """
        # Base NIL estimate from performance
        if self.sport == 'football':
            base_nil = performance_score * 2500  # Up to $250K for perfect score
        else:
            base_nil = performance_score * 3000  # Basketball slightly higher

        # Apply brand premium
        brand_value = base_nil * (1 + nil_premium)

        # Additional brand-only deals (endorsements, social media)
        brand_only = (brand_score / 100) * 50_000  # Up to $50K for mega-influencers

        return brand_value + brand_only

    def calculate_content_quality_score(
        self, social_media: Optional[Dict[str, Any]]
    ) -> float:
        """
        Assess content quality (professional vs. amateur)

        Returns:
            Quality score (0-100)
        """
        if not social_media:
            return 50

        # Professional content indicators
        has_verified = social_media.get('verified', False)
        posts_per_week = social_media.get('posts_per_week', 2)
        brand_partnerships = social_media.get('brand_partnerships', 0)
        content_quality = social_media.get('content_quality_rating', 'average')

        score = 50  # Base

        if has_verified:
            score += 15

        if posts_per_week >= 5:
            score += 10
        elif posts_per_week >= 3:
            score += 5

        if brand_partnerships >= 3:
            score += 15
        elif brand_partnerships >= 1:
            score += 8

        quality_scores = {
            'professional': 20,
            'high': 15,
            'above_average': 10,
            'average': 0,
            'below_average': -10
        }
        score += quality_scores.get(content_quality, 0)

        return max(20, min(score, 100))
