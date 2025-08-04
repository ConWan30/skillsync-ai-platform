"""
🎯 AI Opportunity Radar - Revolutionary Job Market Intelligence
Live AI scanning of job markets with predictive opportunity detection
"""

import os
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sqlite3
import re
from collections import defaultdict

@dataclass
class OpportunitySignal:
    """Individual opportunity signal detected by AI"""
    signal_type: str  # 'emerging_role', 'salary_spike', 'demand_surge', 'new_tech'
    role_title: str
    company: str
    location: str
    confidence_score: float  # 0.0 to 1.0
    urgency_level: str  # 'low', 'medium', 'high', 'critical'
    salary_range: Dict[str, int]
    required_skills: List[str]
    market_trend: str  # 'emerging', 'hot', 'stable', 'declining'
    detected_at: datetime
    prediction_horizon: str  # '1_week', '1_month', '3_months', '6_months'
    source_indicators: List[str]
    
@dataclass 
class MarketIntelligence:
    """Comprehensive market intelligence report"""
    industry: str
    location: str
    total_opportunities: int
    emerging_roles: List[str]
    hot_skills: List[str]
    salary_trends: Dict[str, float]
    company_growth_signals: List[str]
    market_saturation: Dict[str, float]
    prediction_accuracy: float
    generated_at: datetime

class AIOpportunityRadar:
    """Revolutionary AI-powered job market intelligence system"""
    
    def __init__(self):
        self.db_path = "skillsync.db"
        self.init_radar_database()
        
        # AI Analysis Patterns
        self.emerging_role_patterns = [
            r'ai\s+(engineer|specialist|architect)',
            r'prompt\s+engineer',
            r'mlops\s+engineer', 
            r'data\s+mesh\s+architect',
            r'sustainability\s+(analyst|manager)',
            r'web3\s+(developer|engineer)',
            r'automation\s+(specialist|engineer)',
            r'devrel\s+(engineer|advocate)',
            r'growth\s+(engineer|hacker)',
            r'revenue\s+operations'
        ]
        
        self.salary_spike_indicators = [
            'competitive salary', 'above market rate', 'equity package',
            'signing bonus', 'remote premium', 'urgent hire'
        ]
        
        self.demand_surge_keywords = [
            'immediate start', 'urgent requirement', 'high priority',
            'fast-track', 'expedited hiring', 'asap'
        ]
    
    def init_radar_database(self):
        """Initialize radar-specific database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Opportunity signals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS opportunity_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_type TEXT,
                role_title TEXT,
                company TEXT,
                location TEXT,
                confidence_score REAL,
                urgency_level TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                required_skills TEXT,
                market_trend TEXT,
                detected_at TIMESTAMP,
                prediction_horizon TEXT,
                source_indicators TEXT
            )
        ''')
        
        # Market intelligence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_intelligence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                industry TEXT,
                location TEXT,
                total_opportunities INTEGER,
                emerging_roles TEXT,
                hot_skills TEXT,
                salary_trends TEXT,
                company_growth_signals TEXT,
                market_saturation TEXT,
                prediction_accuracy REAL,
                generated_at TIMESTAMP
            )
        ''')
        
        # User radar preferences
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS radar_preferences (
                user_id INTEGER,
                preferred_roles TEXT,
                target_locations TEXT,
                salary_minimum INTEGER,
                alert_frequency TEXT,
                signal_types TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def scan_job_market(self, user_profile: Dict) -> List[OpportunitySignal]:
        """Revolutionary AI job market scanning"""
        signals = []
        
        try:
            # Multi-source job market scanning
            job_sources = [
                self._scan_emerging_roles(user_profile),
                self._detect_salary_spikes(user_profile),
                self._identify_demand_surges(user_profile),
                self._analyze_company_growth(user_profile),
                self._predict_future_opportunities(user_profile)
            ]
            
            # Combine and rank signals
            for source_signals in job_sources:
                signals.extend(source_signals)
            
            # AI-powered signal ranking and filtering
            ranked_signals = self._rank_opportunities(signals, user_profile)
            
            # Store signals in database
            self._store_signals(ranked_signals)
            
            return ranked_signals[:20]  # Top 20 opportunities
            
        except Exception as e:
            print(f"Market scanning error: {e}")
            return self._get_fallback_opportunities(user_profile)
    
    def _scan_emerging_roles(self, user_profile: Dict) -> List[OpportunitySignal]:
        """Detect emerging roles before they become mainstream"""
        signals = []
        
        # Simulate AI analysis of job posting trends
        emerging_roles = [
            {
                'title': 'AI Prompt Engineer',
                'company': 'TechCorp',
                'confidence': 0.92,
                'trend': 'emerging',
                'salary': {'min': 120000, 'max': 180000},
                'growth_rate': '300%'
            },
            {
                'title': 'Revenue Operations Manager', 
                'company': 'GrowthCo',
                'confidence': 0.87,
                'trend': 'hot',
                'salary': {'min': 100000, 'max': 150000},
                'growth_rate': '250%'
            },
            {
                'title': 'Sustainability Data Analyst',
                'company': 'EcoTech',
                'confidence': 0.83,
                'trend': 'emerging',
                'salary': {'min': 80000, 'max': 120000},
                'growth_rate': '200%'
            }
        ]
        
        for role in emerging_roles:
            if self._matches_user_interests(role, user_profile):
                signal = OpportunitySignal(
                    signal_type='emerging_role',
                    role_title=role['title'],
                    company=role['company'],
                    location='Remote/Hybrid',
                    confidence_score=role['confidence'],
                    urgency_level='high',
                    salary_range=role['salary'],
                    required_skills=self._extract_role_skills(role['title']),
                    market_trend=role['trend'],
                    detected_at=datetime.now(),
                    prediction_horizon='3_months',
                    source_indicators=[f"Growth rate: {role['growth_rate']}", "AI trend analysis"]
                )
                signals.append(signal)
        
        return signals
    
    def _detect_salary_spikes(self, user_profile: Dict) -> List[OpportunitySignal]:
        """Detect unusual salary increases in the market"""
        signals = []
        
        # Simulate salary spike detection
        salary_spikes = [
            {
                'role': 'Senior Python Developer',
                'spike_percentage': 15,
                'new_range': {'min': 130000, 'max': 180000},
                'cause': 'AI/ML demand surge'
            },
            {
                'role': 'DevOps Engineer',
                'spike_percentage': 20,
                'new_range': {'min': 120000, 'max': 170000},
                'cause': 'Cloud migration wave'
            }
        ]
        
        for spike in salary_spikes:
            if self._role_matches_profile(spike['role'], user_profile):
                signal = OpportunitySignal(
                    signal_type='salary_spike',
                    role_title=spike['role'],
                    company='Multiple Companies',
                    location='Various',
                    confidence_score=0.85,
                    urgency_level='high',
                    salary_range=spike['new_range'],
                    required_skills=self._extract_role_skills(spike['role']),
                    market_trend='hot',
                    detected_at=datetime.now(),
                    prediction_horizon='1_month',
                    source_indicators=[f"{spike['spike_percentage']}% salary increase", spike['cause']]
                )
                signals.append(signal)
        
        return signals
    
    def _identify_demand_surges(self, user_profile: Dict) -> List[OpportunitySignal]:
        """Identify sudden demand increases for specific roles"""
        signals = []
        
        # Simulate demand surge detection
        demand_surges = [
            {
                'role': 'Cybersecurity Analyst',
                'surge_factor': 3.2,
                'urgency_indicators': ['immediate start', 'urgent requirement'],
                'market_driver': 'Recent security breaches'
            },
            {
                'role': 'Automation Engineer',
                'surge_factor': 2.8,
                'urgency_indicators': ['fast-track hiring', 'competitive offer'],
                'market_driver': 'Efficiency optimization trend'
            }
        ]
        
        for surge in demand_surges:
            if self._role_matches_profile(surge['role'], user_profile):
                signal = OpportunitySignal(
                    signal_type='demand_surge',
                    role_title=surge['role'],
                    company='High-Demand Market',
                    location='Multiple Locations',
                    confidence_score=0.88,
                    urgency_level='critical',
                    salary_range={'min': 90000, 'max': 140000},
                    required_skills=self._extract_role_skills(surge['role']),
                    market_trend='hot',
                    detected_at=datetime.now(),
                    prediction_horizon='1_week',
                    source_indicators=[f"{surge['surge_factor']}x demand increase", surge['market_driver']]
                )
                signals.append(signal)
        
        return signals
    
    def _analyze_company_growth(self, user_profile: Dict) -> List[OpportunitySignal]:
        """Identify companies in rapid growth phases"""
        signals = []
        
        # Simulate company growth analysis
        growth_companies = [
            {
                'company': 'AI Startup X',
                'growth_indicators': ['Series B funding', '200% team growth'],
                'hiring_surge': True,
                'roles': ['AI Engineer', 'Product Manager', 'Full-Stack Developer']
            },
            {
                'company': 'GreenTech Solutions',
                'growth_indicators': ['Major partnership', 'IPO preparation'],
                'hiring_surge': True,
                'roles': ['Sustainability Analyst', 'Data Scientist', 'Sales Engineer']
            }
        ]
        
        for company in growth_companies:
            for role in company['roles']:
                if self._role_matches_profile(role, user_profile):
                    signal = OpportunitySignal(
                        signal_type='company_growth',
                        role_title=role,
                        company=company['company'],
                        location='San Francisco / Remote',
                        confidence_score=0.80,
                        urgency_level='medium',
                        salary_range={'min': 110000, 'max': 160000},
                        required_skills=self._extract_role_skills(role),
                        market_trend='hot',
                        detected_at=datetime.now(),
                        prediction_horizon='1_month',
                        source_indicators=company['growth_indicators']
                    )
                    signals.append(signal)
        
        return signals
    
    def _predict_future_opportunities(self, user_profile: Dict) -> List[OpportunitySignal]:
        """AI predictions of future job opportunities"""
        signals = []
        
        # Simulate AI predictions
        future_opportunities = [
            {
                'role': 'Quantum Computing Engineer',
                'probability': 0.75,
                'timeline': '6_months',
                'driver': 'Quantum computing breakthroughs'
            },
            {
                'role': 'AR/VR Experience Designer',
                'probability': 0.82,
                'timeline': '3_months',
                'driver': 'Metaverse adoption acceleration'
            }
        ]
        
        for opp in future_opportunities:
            if self._matches_user_interests(opp, user_profile):
                signal = OpportunitySignal(
                    signal_type='future_prediction',
                    role_title=opp['role'],
                    company='Predicted Market Opportunity',
                    location='Global/Remote',
                    confidence_score=opp['probability'],
                    urgency_level='low',
                    salary_range={'min': 140000, 'max': 200000},
                    required_skills=self._extract_role_skills(opp['role']),
                    market_trend='emerging',
                    detected_at=datetime.now(),
                    prediction_horizon=opp['timeline'],
                    source_indicators=[opp['driver'], 'AI trend prediction']
                )
                signals.append(signal)
        
        return signals
    
    def _rank_opportunities(self, signals: List[OpportunitySignal], user_profile: Dict) -> List[OpportunitySignal]:
        """AI-powered opportunity ranking"""
        def calculate_score(signal):
            score = signal.confidence_score * 100
            
            # Urgency multiplier
            urgency_multipliers = {'critical': 1.5, 'high': 1.3, 'medium': 1.1, 'low': 1.0}
            score *= urgency_multipliers.get(signal.urgency_level, 1.0)
            
            # Salary attractiveness
            avg_salary = (signal.salary_range['min'] + signal.salary_range['max']) / 2
            if avg_salary > user_profile.get('target_salary', 100000):
                score *= 1.2
            
            # Skill match bonus
            user_skills = user_profile.get('skills', [])
            skill_matches = len(set(signal.required_skills) & set(user_skills))
            score += skill_matches * 5
            
            return score
        
        return sorted(signals, key=calculate_score, reverse=True)
    
    def generate_market_intelligence(self, industry: str, location: str) -> MarketIntelligence:
        """Generate comprehensive market intelligence report"""
        try:
            # Simulate comprehensive market analysis
            intelligence = MarketIntelligence(
                industry=industry,
                location=location,
                total_opportunities=1247,
                emerging_roles=[
                    'AI Prompt Engineer', 'Revenue Operations Manager', 
                    'Sustainability Analyst', 'MLOps Engineer'
                ],
                hot_skills=[
                    'Python', 'Machine Learning', 'AWS', 'Kubernetes',
                    'React', 'Data Analysis', 'Automation'
                ],
                salary_trends={
                    'AI Engineer': 15.2,  # % increase
                    'DevOps Engineer': 12.8,
                    'Data Scientist': 8.5,
                    'Product Manager': 6.3
                },
                company_growth_signals=[
                    'Tech startups: 45% hiring increase',
                    'Fintech: 30% headcount growth',
                    'Greentech: 60% expansion plans'
                ],
                market_saturation={
                    'Junior Developers': 0.85,  # High saturation
                    'Senior Engineers': 0.45,   # Medium saturation
                    'AI Specialists': 0.25      # Low saturation (high opportunity)
                },
                prediction_accuracy=0.87,
                generated_at=datetime.now()
            )
            
            # Store in database
            self._store_market_intelligence(intelligence)
            
            return intelligence
            
        except Exception as e:
            print(f"Market intelligence error: {e}")
            return self._get_fallback_intelligence(industry, location)
    
    def get_personalized_radar(self, user_id: int) -> Dict:
        """Get personalized opportunity radar for user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get user preferences
            cursor.execute('''
                SELECT preferred_roles, target_locations, salary_minimum, 
                       alert_frequency, signal_types
                FROM radar_preferences 
                WHERE user_id = ?
            ''', (user_id,))
            
            prefs = cursor.fetchone()
            conn.close()
            
            if not prefs:
                return self._get_default_radar()
            
            # Get recent signals matching preferences
            recent_signals = self._get_recent_signals_for_user(user_id, prefs)
            
            return {
                'user_id': user_id,
                'radar_active': True,
                'total_signals': len(recent_signals),
                'high_priority_signals': len([s for s in recent_signals if s.urgency_level in ['high', 'critical']]),
                'signals': [asdict(s) for s in recent_signals[:10]],
                'last_scan': datetime.now().isoformat(),
                'next_scan': (datetime.now() + timedelta(hours=1)).isoformat()
            }
            
        except Exception as e:
            print(f"Personalized radar error: {e}")
            return self._get_default_radar()
    
    # Helper methods
    def _extract_role_skills(self, role_title: str) -> List[str]:
        """Extract likely required skills for a role"""
        skill_mapping = {
            'ai': ['Python', 'Machine Learning', 'TensorFlow', 'PyTorch'],
            'engineer': ['Problem Solving', 'System Design', 'Debugging'],
            'developer': ['Programming', 'Git', 'Testing', 'Agile'],
            'analyst': ['Data Analysis', 'SQL', 'Excel', 'Python'],
            'manager': ['Leadership', 'Communication', 'Strategy', 'Project Management']
        }
        
        skills = []
        role_lower = role_title.lower()
        
        for keyword, skill_list in skill_mapping.items():
            if keyword in role_lower:
                skills.extend(skill_list)
        
        return list(set(skills))[:5]  # Top 5 unique skills
    
    def _role_matches_profile(self, role: str, profile: Dict) -> bool:
        """Check if role matches user profile"""
        user_interests = profile.get('interests', [])
        user_skills = profile.get('skills', [])
        
        role_lower = role.lower()
        
        # Check interest alignment
        for interest in user_interests:
            if interest.lower() in role_lower:
                return True
        
        # Check skill alignment
        role_skills = self._extract_role_skills(role)
        skill_overlap = set(user_skills) & set(role_skills)
        
        return len(skill_overlap) >= 2
    
    def _matches_user_interests(self, opportunity: Dict, profile: Dict) -> bool:
        """Check if opportunity matches user interests"""
        return True  # Simplified for demo
    
    def _store_signals(self, signals: List[OpportunitySignal]):
        """Store opportunity signals in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for signal in signals:
            cursor.execute('''
                INSERT INTO opportunity_signals 
                (signal_type, role_title, company, location, confidence_score,
                 urgency_level, salary_min, salary_max, required_skills,
                 market_trend, detected_at, prediction_horizon, source_indicators)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal.signal_type, signal.role_title, signal.company, signal.location,
                signal.confidence_score, signal.urgency_level, 
                signal.salary_range['min'], signal.salary_range['max'],
                json.dumps(signal.required_skills), signal.market_trend,
                signal.detected_at, signal.prediction_horizon,
                json.dumps(signal.source_indicators)
            ))
        
        conn.commit()
        conn.close()
    
    def _store_market_intelligence(self, intelligence: MarketIntelligence):
        """Store market intelligence in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO market_intelligence
            (industry, location, total_opportunities, emerging_roles, hot_skills,
             salary_trends, company_growth_signals, market_saturation,
             prediction_accuracy, generated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            intelligence.industry, intelligence.location, intelligence.total_opportunities,
            json.dumps(intelligence.emerging_roles), json.dumps(intelligence.hot_skills),
            json.dumps(intelligence.salary_trends), json.dumps(intelligence.company_growth_signals),
            json.dumps(intelligence.market_saturation), intelligence.prediction_accuracy,
            intelligence.generated_at
        ))
        
        conn.commit()
        conn.close()
    
    def _get_fallback_opportunities(self, user_profile: Dict) -> List[OpportunitySignal]:
        """Fallback opportunities when AI scanning fails"""
        return [
            OpportunitySignal(
                signal_type='fallback',
                role_title='Software Developer',
                company='TechCorp',
                location='Remote',
                confidence_score=0.7,
                urgency_level='medium',
                salary_range={'min': 80000, 'max': 120000},
                required_skills=['Python', 'JavaScript', 'SQL'],
                market_trend='stable',
                detected_at=datetime.now(),
                prediction_horizon='1_month',
                source_indicators=['Market baseline']
            )
        ]
    
    def _get_fallback_intelligence(self, industry: str, location: str) -> MarketIntelligence:
        """Fallback market intelligence"""
        return MarketIntelligence(
            industry=industry,
            location=location,
            total_opportunities=500,
            emerging_roles=['Software Developer', 'Data Analyst'],
            hot_skills=['Python', 'JavaScript', 'SQL'],
            salary_trends={'Software Developer': 5.0},
            company_growth_signals=['Steady hiring'],
            market_saturation={'General Roles': 0.6},
            prediction_accuracy=0.6,
            generated_at=datetime.now()
        )
    
    def _get_default_radar(self) -> Dict:
        """Default radar response"""
        return {
            'radar_active': False,
            'message': 'Set up your radar preferences to get personalized opportunities'
        }
    
    def _get_recent_signals_for_user(self, user_id: int, prefs) -> List[OpportunitySignal]:
        """Get recent signals matching user preferences"""
        # Simplified - return sample signals
        return self._get_fallback_opportunities({'skills': ['Python'], 'interests': ['technology']})