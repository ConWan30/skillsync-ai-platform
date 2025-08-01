"""
SkillSync Proactive Career Intelligence Agent
Autonomous AI system for proactive career guidance and market analysis
"""

import asyncio
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from dataclasses import dataclass

@dataclass
class MarketInsight:
    skill: str
    demand_change: float  # Percentage change
    salary_trend: str
    job_count: int
    growth_prediction: str
    recommended_action: str

@dataclass
class CareerOpportunity:
    job_title: str
    company: str
    salary_range: str
    required_skills: List[str]
    missing_skills: List[str]
    match_score: float
    urgency: str

class ProactiveCareerAgent:
    """
    Autonomous AI agent that proactively monitors career opportunities,
    analyzes market trends, and generates intelligent recommendations
    """
    
    def __init__(self):
        # Get configuration from environment variables directly
        self.xai_api_key = os.getenv('XAI_API_KEY')
        self.xai_base_url = "https://api.x.ai/v1"
        self.job_apis = {
            'github_jobs': 'https://jobs.github.com/positions.json',
            'remote_ok': 'https://remoteok.io/api',
            'stackoverflow': 'https://stackoverflow.com/jobs/feed'
        }
        self.skill_databases = {
            'stackoverflow_survey': 'https://insights.stackoverflow.com/survey',
            'github_trending': 'https://api.github.com/search/repositories'
        }
    
    def _get_db_models(self):
        """Dynamically import database models to avoid circular imports"""
        try:
            from app import db, User, Skill, Assessment
            return db, User, Skill, Assessment
        except ImportError:
            print("Warning: Could not import database models")
            return None, None, None, None
    
    async def run_daily_intelligence_cycle(self):
        """Main autonomous cycle - runs daily to analyze and notify users"""
        print("🤖 Starting Proactive Career Intelligence Cycle...")
        
        try:
            # Get database models dynamically
            db, User, Skill, Assessment = self._get_db_models()
            if not User:
                print("❌ Database models not available")
                return
            
            # 1. Analyze global market trends
            market_insights = await self.analyze_market_trends()
            
            # 2. Get all active users
            users = User.query.all()
            
            # 3. Generate personalized insights for each user
            for user in users:
                user_insights = await self.generate_user_insights(user, market_insights)
                opportunities = await self.find_career_opportunities(user)
                
                # 4. Send proactive notifications
                await self.send_proactive_notifications(user, user_insights, opportunities)
            
            print(f"✅ Completed intelligence cycle for {len(users)} users")
            
        except Exception as e:
            print(f"❌ Error in intelligence cycle: {str(e)}")
    
    async def analyze_market_trends(self) -> List[MarketInsight]:
        """Analyze global job market and skill demand trends"""
        insights = []
        
        try:
            # Simulate market analysis (in production, integrate with real job APIs)
            trending_skills = [
                "Python", "JavaScript", "React", "Node.js", "AWS", 
                "Docker", "Kubernetes", "Machine Learning", "Data Science",
                "TypeScript", "Go", "Rust", "DevOps", "AI/ML"
            ]
            
            for skill in trending_skills:
                # Use AI to analyze skill trends
                trend_analysis = await self.ai_analyze_skill_trend(skill)
                
                insight = MarketInsight(
                    skill=skill,
                    demand_change=trend_analysis.get('demand_change', 0),
                    salary_trend=trend_analysis.get('salary_trend', 'stable'),
                    job_count=trend_analysis.get('job_count', 100),
                    growth_prediction=trend_analysis.get('growth_prediction', 'moderate'),
                    recommended_action=trend_analysis.get('recommended_action', 'monitor')
                )
                insights.append(insight)
            
            return insights
            
        except Exception as e:
            print(f"Error analyzing market trends: {str(e)}")
            return []
    
    async def ai_analyze_skill_trend(self, skill: str) -> Dict:
        """Use xAI Grok to analyze individual skill trends"""
        if not self.xai_api_key:
            # Fallback simulation when no API key
            return {
                'demand_change': 15.5,
                'salary_trend': 'increasing',
                'job_count': 250,
                'growth_prediction': 'strong',
                'recommended_action': 'learn_now'
            }
        
        try:
            prompt = f"""
            Analyze the current market demand and trends for the skill: {skill}
            
            Consider:
            - Job market demand changes in the last 6 months
            - Salary trends for professionals with this skill
            - Future growth predictions
            - Recommended actions for career development
            
            Respond in JSON format:
            {{
                "demand_change": <percentage_change>,
                "salary_trend": "<increasing/stable/decreasing>",
                "job_count": <estimated_job_openings>,
                "growth_prediction": "<strong/moderate/weak>",
                "recommended_action": "<learn_now/improve/monitor/pivot>"
            }}
            """
            
            response = requests.post(
                f"{self.xai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.xai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                content = ai_response['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    return {
                        'demand_change': 10.0,
                        'salary_trend': 'stable',
                        'job_count': 150,
                        'growth_prediction': 'moderate',
                        'recommended_action': 'monitor'
                    }
            
        except Exception as e:
            print(f"Error in AI skill analysis: {str(e)}")
        
        # Fallback response
        return {
            'demand_change': 5.0,
            'salary_trend': 'stable',
            'job_count': 100,
            'growth_prediction': 'moderate',
            'recommended_action': 'monitor'
        }
    
    async def generate_user_insights(self, user, market_insights: List[MarketInsight]) -> Dict:
        """Generate personalized insights for a specific user"""
        user_skills = [skill.name for skill in user.skills]
        
        # Find relevant market insights for user's skills
        relevant_insights = [
            insight for insight in market_insights 
            if insight.skill.lower() in [s.lower() for s in user_skills]
        ]
        
        # Generate AI-powered personalized recommendations
        personalized_insights = await self.ai_generate_personalized_insights(user, relevant_insights)
        
        return {
            'user_id': user.id,
            'username': user.username,
            'relevant_trends': relevant_insights,
            'personalized_recommendations': personalized_insights,
            'action_items': await self.generate_action_items(user, relevant_insights),
            'skill_gaps': await self.identify_skill_gaps(user, market_insights),
            'generated_at': datetime.now().isoformat()
        }
    
    async def ai_generate_personalized_insights(self, user, insights: List[MarketInsight]) -> str:
        """Use AI to generate personalized career insights"""
        if not self.xai_api_key:
            return f"Based on market analysis, your skills are showing positive trends. Consider focusing on emerging technologies to stay competitive."
        
        try:
            user_skills = [skill.name for skill in user.skills]
            insights_summary = "\n".join([
                f"- {insight.skill}: {insight.demand_change}% demand change, {insight.salary_trend} salary trend"
                for insight in insights[:5]  # Top 5 insights
            ])
            
            prompt = f"""
            Generate personalized career insights for a user with these skills: {', '.join(user_skills)}
            
            Current market trends for their skills:
            {insights_summary}
            
            Provide:
            1. Specific opportunities based on their current skills
            2. Strategic recommendations for career growth
            3. Market timing insights
            4. Actionable next steps
            
            Keep it concise, actionable, and encouraging. Focus on opportunities, not just trends.
            """
            
            response = requests.post(
                f"{self.xai_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.xai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-beta",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.7
                }
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                return ai_response['choices'][0]['message']['content']
                
        except Exception as e:
            print(f"Error generating personalized insights: {str(e)}")
        
        # Fallback response
        return "Your skills are well-positioned in the current market. Consider exploring emerging technologies and building on your existing expertise."
    
    async def find_career_opportunities(self, user) -> List[CareerOpportunity]:
        """Find specific career opportunities for the user"""
        # Simulate job opportunity discovery
        # In production, integrate with real job APIs
        
        user_skills = [skill.name.lower() for skill in user.skills]
        
        # Mock opportunities based on user skills
        opportunities = []
        
        if 'python' in user_skills:
            opportunities.append(CareerOpportunity(
                job_title="Senior Python Developer",
                company="TechCorp Inc.",
                salary_range="$90,000 - $130,000",
                required_skills=["Python", "Django", "PostgreSQL"],
                missing_skills=["Docker", "AWS"],
                match_score=85.0,
                urgency="high"
            ))
        
        if 'javascript' in user_skills:
            opportunities.append(CareerOpportunity(
                job_title="Full Stack Developer",
                company="StartupXYZ",
                salary_range="$80,000 - $120,000",
                required_skills=["JavaScript", "React", "Node.js"],
                missing_skills=["TypeScript", "GraphQL"],
                match_score=78.0,
                urgency="medium"
            ))
        
        return opportunities
    
    async def generate_action_items(self, user, insights: List[MarketInsight]) -> List[str]:
        """Generate specific action items for the user"""
        actions = []
        
        for insight in insights:
            if insight.recommended_action == 'learn_now':
                actions.append(f"🚀 High Priority: Start learning {insight.skill} - demand up {insight.demand_change}%")
            elif insight.recommended_action == 'improve':
                actions.append(f"📈 Improve your {insight.skill} skills - market showing {insight.growth_prediction} growth")
            elif insight.recommended_action == 'pivot':
                actions.append(f"🔄 Consider pivoting from {insight.skill} - market demand declining")
        
        return actions[:5]  # Top 5 actions
    
    async def identify_skill_gaps(self, user, market_insights: List[MarketInsight]) -> List[str]:
        """Identify skills the user should learn based on market trends"""
        user_skills = [skill.name.lower() for skill in user.skills]
        
        high_demand_skills = [
            insight.skill for insight in market_insights
            if insight.demand_change > 10 and insight.skill.lower() not in user_skills
        ]
        
        return high_demand_skills[:3]  # Top 3 skill gaps
    
    async def send_proactive_notifications(self, user, insights: Dict, opportunities: List[CareerOpportunity]):
        """Send proactive notifications to users (email, in-app, etc.)"""
        # For now, we'll store notifications in the database
        # In production, integrate with email/SMS/push notification services
        
        notification_content = self.format_notification(user, insights, opportunities)
        
        # Store notification (you could add a Notification model to your database)
        print(f"📧 Notification for {user.username}:")
        print(notification_content)
        print("-" * 50)
    
    def format_notification(self, user, insights: Dict, opportunities: List[CareerOpportunity]) -> str:
        """Format the notification content"""
        content = f"""
🤖 SkillSync Career Intelligence Update for {user.username}

📊 MARKET INSIGHTS:
{insights['personalized_recommendations']}

🎯 ACTION ITEMS:
{chr(10).join(insights['action_items'])}

💼 NEW OPPORTUNITIES:
"""
        
        for opp in opportunities[:2]:  # Top 2 opportunities
            content += f"""
• {opp.job_title} at {opp.company}
  💰 {opp.salary_range}
  🎯 Match Score: {opp.match_score}%
  📚 Skills to develop: {', '.join(opp.missing_skills)}
"""
        
        content += f"""
🔗 View full analysis: https://skillsync-ai-platform-production.up.railway.app/dashboard

---
Powered by SkillSync AI • Unsubscribe anytime
        """
        
        return content

# Scheduler function for autonomous operation
async def run_autonomous_agent():
    """Main function to run the autonomous agent"""
    agent = ProactiveCareerAgent()
    
    while True:
        try:
            await agent.run_daily_intelligence_cycle()
            
            # Wait 24 hours before next cycle (in production)
            # For testing, you might want to use a shorter interval
            await asyncio.sleep(24 * 60 * 60)  # 24 hours
            
        except Exception as e:
            print(f"Error in autonomous agent: {str(e)}")
            await asyncio.sleep(60)  # Wait 1 minute before retrying

# Manual trigger function for testing
async def trigger_intelligence_cycle():
    """Manually trigger an intelligence cycle for testing"""
    agent = ProactiveCareerAgent()
    await agent.run_daily_intelligence_cycle()

if __name__ == "__main__":
    # For testing - run a single cycle
    asyncio.run(trigger_intelligence_cycle())
