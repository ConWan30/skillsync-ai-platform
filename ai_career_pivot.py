"""
🔄 AI Career Pivot Pathfinder - Revolutionary Career Transition Intelligence
Systematic AI-powered career change planning with bridge role identification
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re

@dataclass
class TransferableSkill:
    """Skills that transfer between careers"""
    skill_name: str
    source_context: str  # Where you used it before
    target_relevance: str  # How it applies to new career
    transferability_score: float  # 0.0 to 1.0
    market_value: int  # Salary impact in target field
    validation_method: str  # How to prove you have this skill

@dataclass
class BridgeRole:
    """Intermediate roles that facilitate career transitions"""
    role_title: str
    company_type: str
    duration_months: int
    skill_bridge_value: float  # How well it bridges careers
    salary_range: Dict[str, int]
    required_skills: List[str]
    skills_you_will_gain: List[str]
    next_step_roles: List[str]
    risk_level: str  # 'low', 'medium', 'high'
    success_probability: float

@dataclass
class PivotPath:
    """Complete career pivot pathway"""
    source_career: str
    target_career: str
    total_duration_months: int
    bridge_roles: List[BridgeRole]
    skill_gaps: List[str]
    learning_plan: Dict[str, Any]
    financial_impact: Dict[str, int]
    risk_assessment: Dict[str, Any]
    success_probability: float
    timeline_milestones: List[Dict[str, Any]]

@dataclass
class PivotRisk:
    """Risk assessment for career pivot"""
    risk_type: str  # 'financial', 'time', 'market', 'skill'
    severity: str  # 'low', 'medium', 'high', 'critical'
    probability: float
    mitigation_strategies: List[str]
    impact_description: str

class AICareerPivotPathfinder:
    """Revolutionary AI system for career transition planning"""
    
    def __init__(self):
        self.db_path = "skillsync.db"
        self.init_pivot_database()
        
        # Career transition knowledge base
        self.career_skill_matrix = self._build_career_skill_matrix()
        self.transition_patterns = self._load_transition_patterns()
        self.bridge_role_catalog = self._build_bridge_role_catalog()
        
    def init_pivot_database(self):
        """Initialize career pivot database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Pivot pathways table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pivot_pathways (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                source_career TEXT,
                target_career TEXT,
                total_duration INTEGER,
                success_probability REAL,
                financial_impact TEXT,
                risk_assessment TEXT,
                created_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Bridge roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bridge_roles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pathway_id INTEGER,
                role_title TEXT,
                duration_months INTEGER,
                salary_min INTEGER,
                salary_max INTEGER,
                required_skills TEXT,
                gained_skills TEXT,
                risk_level TEXT,
                FOREIGN KEY (pathway_id) REFERENCES pivot_pathways (id)
            )
        ''')
        
        # Transferable skills analysis
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transferable_skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                skill_name TEXT,
                source_context TEXT,
                target_relevance TEXT,
                transferability_score REAL,
                market_value INTEGER,
                validated_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def analyze_career_pivot(self, user_profile: Dict, target_career: str) -> PivotPath:
        """Revolutionary AI career pivot analysis"""
        try:
            current_career = user_profile.get('current_role', 'Software Developer')
            user_skills = user_profile.get('skills', [])
            experience_years = user_profile.get('experience_years', 3)
            
            # Step 1: Analyze transferable skills
            transferable_skills = self._analyze_transferable_skills(
                current_career, target_career, user_skills
            )
            
            # Step 2: Identify skill gaps
            skill_gaps = self._identify_skill_gaps(
                current_career, target_career, user_skills
            )
            
            # Step 3: Find optimal bridge roles
            bridge_roles = self._find_bridge_roles(
                current_career, target_career, transferable_skills, experience_years
            )
            
            # Step 4: Create learning plan
            learning_plan = self._create_learning_plan(skill_gaps, bridge_roles)
            
            # Step 5: Calculate financial impact
            financial_impact = self._calculate_financial_impact(
                current_career, target_career, bridge_roles, user_profile
            )
            
            # Step 6: Assess risks
            risk_assessment = self._assess_pivot_risks(
                current_career, target_career, user_profile, bridge_roles
            )
            
            # Step 7: Calculate success probability
            success_probability = self._calculate_success_probability(
                transferable_skills, skill_gaps, bridge_roles, user_profile
            )
            
            # Step 8: Generate timeline
            timeline = self._generate_pivot_timeline(
                bridge_roles, learning_plan, skill_gaps
            )
            
            pivot_path = PivotPath(
                source_career=current_career,
                target_career=target_career,
                total_duration_months=sum(br.duration_months for br in bridge_roles) + 6,  # +6 for preparation
                bridge_roles=bridge_roles,
                skill_gaps=skill_gaps,
                learning_plan=learning_plan,
                financial_impact=financial_impact,
                risk_assessment=risk_assessment,
                success_probability=success_probability,
                timeline_milestones=timeline
            )
            
            # Store in database
            self._store_pivot_path(user_profile.get('user_id', 1), pivot_path)
            
            return pivot_path
            
        except Exception as e:
            print(f"Career pivot analysis error: {e}")
            return self._get_fallback_pivot_path(user_profile, target_career)
    
    def _analyze_transferable_skills(self, source: str, target: str, user_skills: List[str]) -> List[TransferableSkill]:
        """AI analysis of which skills transfer between careers"""
        transferable = []
        
        # Get skill mappings for both careers
        source_skills = self.career_skill_matrix.get(source.lower(), [])
        target_skills = self.career_skill_matrix.get(target.lower(), [])
        
        # Find overlapping and transferable skills
        for skill in user_skills:
            skill_lower = skill.lower()
            
            # Direct skill overlap
            if skill_lower in source_skills and skill_lower in target_skills:
                transferable.append(TransferableSkill(
                    skill_name=skill,
                    source_context=f"Used in {source}",
                    target_relevance=f"Directly applicable to {target}",
                    transferability_score=0.95,
                    market_value=self._get_skill_market_value(skill, target),
                    validation_method="Portfolio/certification"
                ))
            
            # High-value transferable skills
            elif self._is_high_value_transferable(skill, source, target):
                transferable.append(TransferableSkill(
                    skill_name=skill,
                    source_context=f"Core skill in {source}",
                    target_relevance=self._get_transfer_relevance(skill, target),
                    transferability_score=self._calculate_transferability_score(skill, source, target),
                    market_value=self._get_skill_market_value(skill, target),
                    validation_method=self._suggest_validation_method(skill, target)
                ))
        
        # Add universal transferable skills
        universal_skills = [
            'Communication', 'Problem Solving', 'Project Management',
            'Leadership', 'Data Analysis', 'Customer Focus'
        ]
        
        for skill in universal_skills:
            if skill not in [t.skill_name for t in transferable]:
                transferable.append(TransferableSkill(
                    skill_name=skill,
                    source_context="Professional experience",
                    target_relevance=f"Essential for {target} success",
                    transferability_score=0.8,
                    market_value=self._get_skill_market_value(skill, target),
                    validation_method="Examples and stories"
                ))
        
        return transferable[:10]  # Top 10 transferable skills
    
    def _identify_skill_gaps(self, source: str, target: str, user_skills: List[str]) -> List[str]:
        """Identify critical skills missing for target career"""
        target_requirements = self.career_skill_matrix.get(target.lower(), [])
        user_skills_lower = [s.lower() for s in user_skills]
        
        gaps = []
        for required_skill in target_requirements:
            if required_skill not in user_skills_lower:
                gaps.append(required_skill.title())
        
        # Add career-specific critical gaps
        critical_gaps = self._get_critical_gaps(source, target)
        for gap in critical_gaps:
            if gap not in gaps:
                gaps.append(gap)
        
        return gaps[:8]  # Top 8 most critical gaps
    
    def _find_bridge_roles(self, source: str, target: str, transferable_skills: List[TransferableSkill], experience: int) -> List[BridgeRole]:
        """Find optimal bridge roles for career transition"""
        bridge_roles = []
        
        # Get potential bridge roles from catalog
        potential_bridges = self.bridge_role_catalog.get(f"{source}->{target}", [])
        
        for bridge_data in potential_bridges:
            # Calculate how well this role bridges the gap
            bridge_value = self._calculate_bridge_value(
                bridge_data, transferable_skills, source, target
            )
            
            # Adjust for user experience level
            if experience < 3 and 'senior' in bridge_data['title'].lower():
                continue  # Skip senior roles for junior developers
            
            bridge_role = BridgeRole(
                role_title=bridge_data['title'],
                company_type=bridge_data['company_type'],
                duration_months=bridge_data['duration'],
                skill_bridge_value=bridge_value,
                salary_range=bridge_data['salary_range'],
                required_skills=bridge_data['required_skills'],
                skills_you_will_gain=bridge_data['skills_gained'],
                next_step_roles=bridge_data['next_steps'],
                risk_level=bridge_data['risk_level'],
                success_probability=self._calculate_bridge_success_probability(
                    bridge_data, transferable_skills, experience
                )
            )
            
            bridge_roles.append(bridge_role)
        
        # Sort by bridge value and success probability
        bridge_roles.sort(key=lambda x: (x.skill_bridge_value + x.success_probability), reverse=True)
        
        return bridge_roles[:3]  # Top 3 bridge roles
    
    def _create_learning_plan(self, skill_gaps: List[str], bridge_roles: List[BridgeRole]) -> Dict[str, Any]:
        """Create comprehensive learning plan for career pivot"""
        learning_plan = {
            'preparation_phase': {
                'duration_weeks': 12,
                'skills_to_learn': skill_gaps[:4],  # Most critical skills first
                'learning_methods': {},
                'budget_estimate': 0
            },
            'bridge_phase': {
                'duration_months': sum(br.duration_months for br in bridge_roles),
                'on_job_learning': [],
                'supplementary_skills': skill_gaps[4:],
                'certifications_to_pursue': []
            },
            'transition_phase': {
                'duration_weeks': 8,
                'portfolio_projects': [],
                'networking_strategy': [],
                'job_search_approach': []
            }
        }
        
        # Add specific learning methods for each skill
        for skill in skill_gaps[:4]:
            learning_plan['preparation_phase']['learning_methods'][skill] = \
                self._suggest_learning_method(skill)
            learning_plan['preparation_phase']['budget_estimate'] += \
                self._estimate_learning_cost(skill)
        
        # Add on-the-job learning from bridge roles
        for bridge_role in bridge_roles:
            learning_plan['bridge_phase']['on_job_learning'].extend(
                bridge_role.skills_you_will_gain
            )
        
        # Add certifications
        target_certs = self._suggest_certifications(skill_gaps)
        learning_plan['bridge_phase']['certifications_to_pursue'] = target_certs
        
        # Add portfolio projects
        learning_plan['transition_phase']['portfolio_projects'] = \
            self._suggest_portfolio_projects(skill_gaps)
        
        return learning_plan
    
    def _calculate_financial_impact(self, source: str, target: str, bridge_roles: List[BridgeRole], profile: Dict) -> Dict[str, int]:
        """Calculate comprehensive financial impact of career pivot"""
        current_salary = profile.get('current_salary', 80000)
        target_salary = self._get_career_salary_range(target)['median']
        
        # Calculate bridge role salaries
        bridge_salaries = []
        for bridge_role in bridge_roles:
            avg_bridge_salary = (bridge_role.salary_range['min'] + bridge_role.salary_range['max']) / 2
            bridge_salaries.append(avg_bridge_salary)
        
        # Learning costs
        learning_costs = sum([
            2000,  # Courses and certifications
            1500,  # Books and resources  
            3000,  # Potential bootcamp or program
            1000   # Portfolio/project costs
        ])
        
        # Opportunity cost (potential lost income during transition)
        transition_months = sum(br.duration_months for br in bridge_roles) + 6
        opportunity_cost = (current_salary / 12) * min(3, transition_months)  # Max 3 months loss
        
        return {
            'current_salary': current_salary,
            'target_salary': target_salary,
            'bridge_salary_average': int(sum(bridge_salaries) / len(bridge_salaries)) if bridge_salaries else current_salary,
            'learning_investment': learning_costs,
            'opportunity_cost': int(opportunity_cost),
            'total_investment': learning_costs + int(opportunity_cost),
            'salary_increase_potential': target_salary - current_salary,
            'roi_months': max(12, int((learning_costs + opportunity_cost) / max(1, (target_salary - current_salary) / 12))),
            'five_year_financial_gain': (target_salary - current_salary) * 5 - learning_costs
        }
    
    def _assess_pivot_risks(self, source: str, target: str, profile: Dict, bridge_roles: List[BridgeRole]) -> Dict[str, Any]:
        """Comprehensive risk assessment for career pivot"""
        risks = []
        
        # Financial risks
        if profile.get('current_salary', 80000) > 100000:
            risks.append(PivotRisk(
                risk_type='financial',
                severity='medium',
                probability=0.6,
                mitigation_strategies=[
                    'Save 6-12 months emergency fund',
                    'Consider part-time transition',
                    'Negotiate flexible arrangements'
                ],
                impact_description='Potential temporary salary reduction during transition'
            ))
        
        # Market saturation risk
        target_demand = self._get_market_demand(target)
        if target_demand < 0.3:
            risks.append(PivotRisk(
                risk_type='market',
                severity='high',
                probability=0.7,
                mitigation_strategies=[
                    'Focus on niche specialization',
                    'Build strong portfolio',
                    'Network extensively in target field'
                ],
                impact_description='High competition in target field'
            ))
        
        # Skill gap risk
        if len(self._identify_skill_gaps(source, target, profile.get('skills', []))) > 5:
            risks.append(PivotRisk(
                risk_type='skill',
                severity='medium',
                probability=0.5,
                mitigation_strategies=[
                    'Intensive upskilling program',
                    'Find mentor in target field',
                    'Take on relevant side projects'
                ],
                impact_description='Significant skill development required'
            ))
        
        # Time risk
        total_months = sum(br.duration_months for br in bridge_roles) + 6
        if total_months > 24:
            risks.append(PivotRisk(
                risk_type='time',
                severity='medium',
                probability=0.4,
                mitigation_strategies=[
                    'Accelerated learning approach',
                    'Parallel skill development',
                    'Consider bootcamp or intensive program'
                ],
                impact_description='Extended transition timeline'
            ))
        
        return {
            'total_risks': len(risks),
            'risk_breakdown': [asdict(risk) for risk in risks],
            'overall_risk_level': self._calculate_overall_risk(risks),
            'mitigation_priority': self._prioritize_risk_mitigation(risks)
        }
    
    def _calculate_success_probability(self, transferable_skills: List[TransferableSkill], 
                                     skill_gaps: List[str], bridge_roles: List[BridgeRole], 
                                     profile: Dict) -> float:
        """Calculate probability of successful career pivot"""
        
        # Base probability factors
        transferable_score = sum(skill.transferability_score for skill in transferable_skills) / len(transferable_skills)
        gap_penalty = min(0.3, len(skill_gaps) * 0.03)  # Max 30% penalty for gaps
        bridge_quality = sum(br.success_probability for br in bridge_roles) / len(bridge_roles) if bridge_roles else 0.5
        
        # Experience factor
        experience_years = profile.get('experience_years', 3)
        experience_factor = min(1.0, experience_years / 5)  # 5+ years = full factor
        
        # Learning commitment factor (assume high commitment)
        learning_factor = 0.8
        
        # Calculate final probability
        success_probability = (
            transferable_score * 0.3 +
            (1 - gap_penalty) * 0.2 +
            bridge_quality * 0.25 +
            experience_factor * 0.15 +
            learning_factor * 0.1
        )
        
        return min(0.95, max(0.2, success_probability))  # Clamp between 20% and 95%
    
    def _generate_pivot_timeline(self, bridge_roles: List[BridgeRole], 
                               learning_plan: Dict, skill_gaps: List[str]) -> List[Dict[str, Any]]:
        """Generate detailed timeline for career pivot"""
        timeline = []
        current_date = datetime.now()
        
        # Preparation phase
        timeline.append({
            'phase': 'Preparation',
            'start_date': current_date.isoformat(),
            'end_date': (current_date + timedelta(weeks=12)).isoformat(),
            'duration': '3 months',
            'key_activities': [
                f'Learn {skill_gaps[0]} and {skill_gaps[1]}',
                'Build portfolio projects',
                'Network in target industry',
                'Update resume and LinkedIn'
            ],
            'success_metrics': [
                'Complete 2 portfolio projects',
                'Obtain relevant certification',
                'Make 20 industry connections'
            ]
        })
        
        current_date += timedelta(weeks=12)
        
        # Bridge role phases
        for i, bridge_role in enumerate(bridge_roles):
            timeline.append({
                'phase': f'Bridge Role {i+1}: {bridge_role.role_title}',
                'start_date': current_date.isoformat(),
                'end_date': (current_date + timedelta(days=bridge_role.duration_months * 30)).isoformat(),
                'duration': f'{bridge_role.duration_months} months',
                'key_activities': [
                    f'Excel in {bridge_role.role_title} position',
                    f'Develop skills: {", ".join(bridge_role.skills_you_will_gain[:3])}',
                    'Build internal network',
                    'Document achievements for portfolio'
                ],
                'success_metrics': [
                    'Strong performance review',
                    'Gain target skills',
                    'Expand professional network'
                ]
            })
            current_date += timedelta(days=bridge_role.duration_months * 30)
        
        # Final transition
        timeline.append({
            'phase': 'Final Transition',
            'start_date': current_date.isoformat(),
            'end_date': (current_date + timedelta(weeks=8)).isoformat(),
            'duration': '2 months',
            'key_activities': [
                'Apply for target career roles',
                'Interview preparation',
                'Portfolio refinement',
                'Salary negotiation'
            ],
            'success_metrics': [
                'Land target role',
                'Negotiate competitive salary',
                'Smooth transition'
            ]
        })
        
        return timeline
    
    # Helper methods and data structures
    def _build_career_skill_matrix(self) -> Dict[str, List[str]]:
        """Build comprehensive career-skill mapping"""
        return {
            'software developer': [
                'programming', 'python', 'javascript', 'sql', 'git', 'testing',
                'debugging', 'algorithms', 'system design', 'agile'
            ],
            'data scientist': [
                'python', 'r', 'machine learning', 'statistics', 'sql', 'visualization',
                'pandas', 'numpy', 'scikit-learn', 'jupyter'
            ],
            'product manager': [
                'product strategy', 'user research', 'data analysis', 'roadmapping',
                'stakeholder management', 'agile', 'prioritization', 'market research'
            ],
            'marketing manager': [
                'digital marketing', 'analytics', 'content strategy', 'seo', 'social media',
                'campaign management', 'brand management', 'market research'
            ],
            'sales engineer': [
                'technical sales', 'product demos', 'customer relationships', 'crm',
                'technical communication', 'problem solving', 'negotiation'
            ],
            'devops engineer': [
                'aws', 'docker', 'kubernetes', 'ci/cd', 'terraform', 'monitoring',
                'linux', 'scripting', 'automation', 'security'
            ]
        }
    
    def _load_transition_patterns(self) -> Dict[str, Dict]:
        """Load successful career transition patterns"""
        return {
            'software_developer->product_manager': {
                'success_rate': 0.75,
                'avg_duration_months': 18,
                'key_challenges': ['business acumen', 'stakeholder management']
            },
            'software_developer->data_scientist': {
                'success_rate': 0.65,
                'avg_duration_months': 24,
                'key_challenges': ['statistics', 'domain expertise']
            }
        }
    
    def _build_bridge_role_catalog(self) -> Dict[str, List[Dict]]:
        """Build catalog of bridge roles for different transitions"""
        return {
            'software developer->product manager': [
                {
                    'title': 'Technical Product Manager',
                    'company_type': 'Tech Startup',
                    'duration': 12,
                    'salary_range': {'min': 110000, 'max': 150000},
                    'required_skills': ['Programming', 'Product Sense', 'Analytics'],
                    'skills_gained': ['Product Strategy', 'User Research', 'Roadmapping'],
                    'next_steps': ['Senior Product Manager', 'Group Product Manager'],
                    'risk_level': 'medium'
                },
                {
                    'title': 'Developer Relations Manager',
                    'company_type': 'SaaS Company',
                    'duration': 15,
                    'salary_range': {'min': 100000, 'max': 140000},
                    'required_skills': ['Programming', 'Communication', 'Community Building'],
                    'skills_gained': ['Developer Marketing', 'Product Feedback', 'Technical Writing'],
                    'next_steps': ['Product Marketing Manager', 'Product Manager'],
                    'risk_level': 'low'
                }
            ],
            'software developer->data scientist': [
                {
                    'title': 'Data Engineer',
                    'company_type': 'Data-driven Company',
                    'duration': 18,
                    'salary_range': {'min': 120000, 'max': 160000},
                    'required_skills': ['Python', 'SQL', 'ETL', 'Cloud Platforms'],
                    'skills_gained': ['Data Pipelines', 'Big Data', 'Data Modeling'],
                    'next_steps': ['Senior Data Engineer', 'Data Scientist'],
                    'risk_level': 'low'
                },
                {
                    'title': 'Analytics Engineer',
                    'company_type': 'Growth Company',
                    'duration': 12,
                    'salary_range': {'min': 95000, 'max': 130000},
                    'required_skills': ['SQL', 'Python', 'Business Analysis'],
                    'skills_gained': ['Statistical Analysis', 'Business Intelligence', 'Data Visualization'],
                    'next_steps': ['Data Scientist', 'Analytics Manager'],
                    'risk_level': 'medium'
                }
            ]
        }
    
    # Additional helper methods
    def _get_skill_market_value(self, skill: str, target_career: str) -> int:
        """Get market value of skill in target career"""
        skill_values = {
            'python': 15000, 'machine learning': 20000, 'aws': 12000,
            'product management': 18000, 'leadership': 10000,
            'data analysis': 8000, 'communication': 5000
        }
        return skill_values.get(skill.lower(), 5000)
    
    def _is_high_value_transferable(self, skill: str, source: str, target: str) -> bool:
        """Check if skill is high-value transferable"""
        high_value_skills = [
            'python', 'sql', 'data analysis', 'project management',
            'leadership', 'communication', 'problem solving'
        ]
        return skill.lower() in high_value_skills
    
    def _get_transfer_relevance(self, skill: str, target: str) -> str:
        """Get how skill transfers to target career"""
        relevance_map = {
            'python': f"Core programming language for {target}",
            'sql': f"Essential for data work in {target}",
            'leadership': f"Critical for senior {target} roles"
        }
        return relevance_map.get(skill.lower(), f"Valuable skill for {target}")
    
    def _calculate_transferability_score(self, skill: str, source: str, target: str) -> float:
        """Calculate how well skill transfers"""
        # Simplified scoring logic
        if skill.lower() in ['python', 'sql', 'data analysis']:
            return 0.9
        elif skill.lower() in ['leadership', 'communication', 'project management']:
            return 0.85
        else:
            return 0.7
    
    def _suggest_validation_method(self, skill: str, target: str) -> str:
        """Suggest how to validate/prove skill"""
        methods = {
            'python': 'GitHub portfolio + coding challenges',
            'machine learning': 'Kaggle competitions + projects',
            'leadership': 'Success stories + references',
            'communication': 'Blog posts + presentations'
        }
        return methods.get(skill.lower(), 'Portfolio examples + testimonials')
    
    def _get_critical_gaps(self, source: str, target: str) -> List[str]:
        """Get critical skill gaps for specific transitions"""
        gaps = {
            'software developer->product manager': [
                'User Research', 'Market Analysis', 'Product Strategy', 'Stakeholder Management'
            ],
            'software developer->data scientist': [
                'Statistics', 'Machine Learning', 'Domain Expertise', 'Data Visualization'
            ]
        }
        key = f"{source.lower()}->{target.lower()}"
        return gaps.get(key, ['Business Acumen', 'Industry Knowledge'])
    
    def _calculate_bridge_value(self, bridge_data: Dict, transferable_skills: List[TransferableSkill], source: str, target: str) -> float:
        """Calculate how well a role bridges career gap"""
        # Simplified calculation
        required_skills = bridge_data['required_skills']
        user_transferable = [skill.skill_name for skill in transferable_skills]
        
        skill_match = len(set(required_skills) & set(user_transferable)) / len(required_skills)
        target_alignment = len(set(bridge_data['skills_gained']) & set(self.career_skill_matrix.get(target.lower(), []))) / 5
        
        return (skill_match + target_alignment) / 2
    
    def _calculate_bridge_success_probability(self, bridge_data: Dict, transferable_skills: List[TransferableSkill], experience: int) -> float:
        """Calculate probability of success in bridge role"""
        base_prob = 0.7
        
        # Adjust for skill match
        required_skills = bridge_data['required_skills']
        user_skills = [skill.skill_name for skill in transferable_skills]
        skill_match_ratio = len(set(required_skills) & set(user_skills)) / len(required_skills)
        
        # Adjust for experience
        experience_factor = min(1.0, experience / 3)  # 3+ years = full factor
        
        return min(0.9, base_prob * (0.7 + skill_match_ratio * 0.2 + experience_factor * 0.1))
    
    def _suggest_learning_method(self, skill: str) -> Dict[str, Any]:
        """Suggest best learning method for skill"""
        methods = {
            'machine learning': {
                'primary': 'Online course (Coursera ML Specialization)',
                'secondary': 'Kaggle competitions',
                'duration_weeks': 12,
                'cost': 500
            },
            'user research': {
                'primary': 'UX Research bootcamp',
                'secondary': 'Volunteer user research projects',
                'duration_weeks': 8,
                'cost': 800
            }
        }
        return methods.get(skill.lower(), {
            'primary': 'Online courses + practice projects',
            'secondary': 'Professional workshops',
            'duration_weeks': 10,
            'cost': 400
        })
    
    def _estimate_learning_cost(self, skill: str) -> int:
        """Estimate cost to learn skill"""
        costs = {
            'machine learning': 600,
            'user research': 800,
            'product strategy': 500,
            'data visualization': 300
        }
        return costs.get(skill.lower(), 400)
    
    def _suggest_certifications(self, skill_gaps: List[str]) -> List[str]:
        """Suggest relevant certifications"""
        cert_map = {
            'machine learning': 'Google ML Engineer Certificate',
            'aws': 'AWS Solutions Architect',
            'product management': 'Certified Product Manager',
            'data analysis': 'Google Data Analytics Certificate'
        }
        
        suggestions = []
        for skill in skill_gaps:
            if skill.lower() in cert_map:
                suggestions.append(cert_map[skill.lower()])
        
        return suggestions[:3]  # Top 3 certifications
    
    def _suggest_portfolio_projects(self, skill_gaps: List[str]) -> List[str]:
        """Suggest portfolio projects to demonstrate skills"""
        projects = [
            'End-to-end data analysis project',
            'Product feature specification document',
            'Machine learning model deployment',
            'User research study with insights'
        ]
        return projects[:3]
    
    def _get_career_salary_range(self, career: str) -> Dict[str, int]:
        """Get salary range for career"""
        ranges = {
            'product manager': {'min': 120000, 'median': 150000, 'max': 200000},
            'data scientist': {'min': 110000, 'median': 140000, 'max': 180000},
            'marketing manager': {'min': 80000, 'median': 110000, 'max': 150000},
            'sales engineer': {'min': 90000, 'median': 120000, 'max': 160000}
        }
        return ranges.get(career.lower(), {'min': 80000, 'median': 100000, 'max': 130000})
    
    def _get_market_demand(self, career: str) -> float:
        """Get market demand score for career (0.0 to 1.0)"""
        demand = {
            'data scientist': 0.8,
            'product manager': 0.7,
            'devops engineer': 0.9,
            'marketing manager': 0.5
        }
        return demand.get(career.lower(), 0.6)
    
    def _calculate_overall_risk(self, risks: List[PivotRisk]) -> str:
        """Calculate overall risk level"""
        if not risks:
            return 'low'
        
        high_risks = len([r for r in risks if r.severity in ['high', 'critical']])
        if high_risks >= 2:
            return 'high'
        elif high_risks == 1 or len(risks) >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _prioritize_risk_mitigation(self, risks: List[PivotRisk]) -> List[str]:
        """Prioritize risk mitigation strategies"""
        priorities = []
        for risk in sorted(risks, key=lambda x: x.probability * (['low', 'medium', 'high', 'critical'].index(x.severity) + 1), reverse=True):
            priorities.extend(risk.mitigation_strategies[:2])  # Top 2 strategies per risk
        return priorities[:5]  # Top 5 overall strategies
    
    def _store_pivot_path(self, user_id: int, pivot_path: PivotPath):
        """Store pivot path in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO pivot_pathways
            (user_id, source_career, target_career, total_duration,
             success_probability, financial_impact, risk_assessment, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, pivot_path.source_career, pivot_path.target_career,
            pivot_path.total_duration_months, pivot_path.success_probability,
            json.dumps(pivot_path.financial_impact), 
            json.dumps(pivot_path.risk_assessment),
            datetime.now()
        ))
        
        pathway_id = cursor.lastrowid
        
        # Store bridge roles
        for bridge_role in pivot_path.bridge_roles:
            cursor.execute('''
                INSERT INTO bridge_roles
                (pathway_id, role_title, duration_months, salary_min, salary_max,
                 required_skills, gained_skills, risk_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pathway_id, bridge_role.role_title, bridge_role.duration_months,
                bridge_role.salary_range['min'], bridge_role.salary_range['max'],
                json.dumps(bridge_role.required_skills),
                json.dumps(bridge_role.skills_you_will_gain),
                bridge_role.risk_level
            ))
        
        conn.commit()
        conn.close()
    
    def _get_fallback_pivot_path(self, user_profile: Dict, target_career: str) -> PivotPath:
        """Fallback pivot path when analysis fails"""
        return PivotPath(
            source_career=user_profile.get('current_role', 'Current Role'),
            target_career=target_career,
            total_duration_months=18,
            bridge_roles=[],
            skill_gaps=['Domain Knowledge', 'Industry Experience'],
            learning_plan={'preparation_phase': {'duration_weeks': 12}},
            financial_impact={'current_salary': 80000, 'target_salary': 100000},
            risk_assessment={'total_risks': 1, 'overall_risk_level': 'medium'},
            success_probability=0.7,
            timeline_milestones=[]
        )