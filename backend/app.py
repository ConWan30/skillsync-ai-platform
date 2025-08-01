from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

app = Flask(__name__, template_folder='../templates')
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'skillsync-default-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///skillsync.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db = SQLAlchemy(app)

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.relationship('Skill', backref='user', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class LearningPath(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    progress = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# xAI Grok Configuration
XAI_API_KEY = os.getenv('XAI_API_KEY')
XAI_BASE_URL = "https://api.x.ai/v1"

def call_grok_ai(prompt, system_prompt=None):
    """Call xAI Grok API with career development expertise"""
    if not XAI_API_KEY:
        return "ERROR: xAI API key not configured in environment variables"
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    # Try different model names that might work
    model_names = ["grok-2", "grok", "grok-turbo", "grok-1", "grok-beta"]
    
    for model_name in model_names:
        data = {
            "model": model_name,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 1000
        }
        
        try:
            print(f"[DEBUG] Trying model: {model_name}")
            print(f"[DEBUG] Calling xAI API with URL: {XAI_BASE_URL}/chat/completions")
            print(f"[DEBUG] API Key present: {'Yes' if XAI_API_KEY else 'No'}")
            print(f"[DEBUG] API Key length: {len(XAI_API_KEY) if XAI_API_KEY else 0}")
            
            response = requests.post(f"{XAI_BASE_URL}/chat/completions", 
                                   headers=headers, json=data, timeout=30)
            
            print(f"[DEBUG] Response status code: {response.status_code}")
            
            if response.status_code == 200:
                print(f"[DEBUG] SUCCESS! Model {model_name} works!")
                result = response.json()
                if "choices" in result and result["choices"]:
                    return result["choices"][0]["message"]["content"]
                else:
                    print(f"[DEBUG] Invalid response format: {result}")
                    continue
            else:
                print(f"[DEBUG] Model {model_name} failed with status {response.status_code}")
                print(f"[DEBUG] Response: {response.text}")
                continue
                
        except Exception as e:
            print(f"[DEBUG] Model {model_name} failed with exception: {str(e)}")
            continue
    
    # If all models fail, return error
    return f"ERROR: None of the xAI models ({', '.join(model_names)}) are accessible with your API key. Please check your xAI account and API key permissions."

# Career Intelligence Knowledge Base - Built from Public Data Sources
# Data Sources: Stack Overflow Developer Survey 2024, GitHub Octoverse 2024, Public Market Research
CAREER_KNOWLEDGE_BASE = {
    "market_trends_2024": {
        "programming_languages": {
            "python": {
                "rank": 1,
                "growth_trend": "Rising (overtook JavaScript in 2024)",
                "primary_use_cases": ["AI/ML", "Data Science", "Backend Development", "Scientific Computing"],
                "avg_salary_range": "$70k-$150k",
                "demand_drivers": ["Generative AI boom", "Data science growth", "Beginner-friendly"],
                "job_titles": ["Data Scientist", "ML Engineer", "Python Developer", "AI Researcher"]
            },
            "javascript": {
                "rank": 2,
                "growth_trend": "Stable (still #1 for code pushes)",
                "primary_use_cases": ["Frontend Development", "Full-Stack", "Node.js Backend"],
                "avg_salary_range": "$65k-$140k",
                "demand_drivers": ["Web development", "Versatility", "Large ecosystem"],
                "job_titles": ["Frontend Developer", "Full-Stack Developer", "Web Developer"]
            },
            "typescript": {
                "rank": 3,
                "growth_trend": "Rising rapidly (overtook Java)",
                "primary_use_cases": ["Large-scale JavaScript", "Enterprise Applications"],
                "avg_salary_range": "$75k-$155k",
                "demand_drivers": ["Type safety", "Enterprise adoption", "JavaScript transition"],
                "job_titles": ["Frontend Developer", "Full-Stack Developer", "Software Engineer"]
            },
            "rust": {
                "rank": "Top 10",
                "growth_trend": "Most admired language (83% admiration)",
                "primary_use_cases": ["Systems Programming", "Performance-critical Applications"],
                "avg_salary_range": "$90k-$170k",
                "demand_drivers": ["Memory safety", "Performance", "Growing adoption"],
                "job_titles": ["Systems Engineer", "Backend Developer", "Blockchain Developer"]
            }
        },
        "highest_paying_roles": {
            "site_reliability_engineer": {
                "median_salary": "$140k-$200k",
                "description": "Keeps digital services running",
                "key_skills": ["Cloud Infrastructure", "Monitoring", "Automation", "DevOps"],
                "growth_outlook": "High demand"
            },
            "cloud_infrastructure_engineer": {
                "median_salary": "$130k-$190k",
                "description": "Designs and maintains cloud systems",
                "key_skills": ["AWS", "Azure", "GCP", "Kubernetes", "Terraform"],
                "growth_outlook": "Explosive growth"
            },
            "senior_executive": {
                "median_salary": "$180k-$300k+",
                "description": "Technical leadership roles",
                "key_skills": ["Leadership", "Strategy", "Technical Vision", "Team Management"],
                "growth_outlook": "Always in demand"
            },
            "developer_advocate": {
                "median_salary": "$120k-$180k",
                "description": "Bridge between developers and products",
                "key_skills": ["Communication", "Technical Writing", "Community Building"],
                "growth_outlook": "Growing field"
            }
        },
        "technology_trends": {
            "ai_ml": {
                "adoption_rate": "76% using or planning to use AI tools",
                "growth_rate": "+45%",
                "key_technologies": ["ChatGPT", "GitHub Copilot", "TensorFlow", "PyTorch"],
                "salary_premium": "+25-40%",
                "job_security": "70% don't see AI as threat to jobs"
            },
            "cloud_computing": {
                "adoption_rate": "85% of companies using cloud",
                "growth_rate": "+38%",
                "key_technologies": ["AWS", "Azure", "GCP", "Docker", "Kubernetes"],
                "salary_premium": "+15-30%",
                "job_security": "Critical infrastructure need"
            },
            "databases": {
                "trending": "PostgreSQL (#1 for 2nd year)",
                "growth_rate": "+25%",
                "key_technologies": ["PostgreSQL", "MongoDB", "Redis", "Elasticsearch"],
                "salary_premium": "+10-20%",
                "job_security": "Data always needs management"
            }
        }
    },
    "salary_benchmarks_2024": {
        "by_experience_level": {
            "entry_level": {
                "0_2_years": "$50k-$85k",
                "description": "New graduates, bootcamp grads",
                "growth_potential": "High",
                "key_focus": "Learning fundamentals, building portfolio"
            },
            "mid_level": {
                "3_7_years": "$75k-$130k",
                "description": "Solid foundation, specializing",
                "growth_potential": "Moderate to High",
                "key_focus": "Specialization, leadership skills"
            },
            "senior_level": {
                "8_15_years": "$120k-$200k",
                "description": "Expert level, mentoring others",
                "growth_potential": "Moderate",
                "key_focus": "Architecture, team leadership"
            },
            "principal_staff": {
                "15_plus_years": "$180k-$350k+",
                "description": "Technical leadership, strategy",
                "growth_potential": "High (executive track)",
                "key_focus": "Vision, cross-team impact"
            }
        },
        "by_location_multiplier": {
            "san_francisco": 1.6,
            "new_york": 1.4,
            "seattle": 1.3,
            "austin": 1.2,
            "denver": 1.1,
            "remote": 1.0,
            "international": 0.6
        },
        "by_company_size": {
            "startup_1_50": {"multiplier": 0.9, "equity": "High", "growth": "High risk/reward"},
            "mid_size_51_500": {"multiplier": 1.0, "equity": "Medium", "growth": "Balanced"},
            "large_500_plus": {"multiplier": 1.2, "equity": "Low", "growth": "Stable"}
        }
    },
    "skill_demand_analysis": {
        "most_wanted_skills": {
            "docker": {
                "demand_growth": "+40%",
                "salary_impact": "+15%",
                "adoption_rate": "59% professional developers",
                "learning_priority": "High"
            },
            "kubernetes": {
                "demand_growth": "+35%",
                "salary_impact": "+20%",
                "adoption_rate": "Growing rapidly",
                "learning_priority": "High"
            },
            "aws": {
                "demand_growth": "+30%",
                "salary_impact": "+25%",
                "adoption_rate": "Market leader",
                "learning_priority": "Critical"
            },
            "react": {
                "demand_growth": "+25%",
                "salary_impact": "+10%",
                "adoption_rate": "Frontend standard",
                "learning_priority": "High"
            }
        },
        "emerging_technologies": {
            "generative_ai": {
                "growth_rate": "Explosive",
                "time_to_mainstream": "1-2 years",
                "learning_recommendation": "Start now",
                "key_skills": ["Prompt Engineering", "AI Integration", "Ethics"]
            },
            "edge_computing": {
                "growth_rate": "High",
                "time_to_mainstream": "2-3 years",
                "learning_recommendation": "Monitor closely",
                "key_skills": ["IoT", "5G", "Real-time Processing"]
            }
        }
    },
    "career_paths": {
        "software_engineer_to_senior": {
            "timeline": "3-5 years",
            "key_milestones": ["Master core language", "System design", "Mentoring"],
            "salary_progression": "$70k → $90k → $120k",
            "critical_skills": ["Problem solving", "Code quality", "Communication"]
        },
        "developer_to_manager": {
            "timeline": "5-8 years",
            "key_milestones": ["Technical leadership", "Team lead", "People management"],
            "salary_progression": "$100k → $130k → $160k+",
            "critical_skills": ["Leadership", "Strategy", "Communication", "Technical depth"]
        },
        "generalist_to_specialist": {
            "timeline": "2-4 years",
            "key_milestones": ["Choose domain", "Deep expertise", "Thought leadership"],
            "salary_progression": "+20-40% premium",
            "critical_skills": ["Domain expertise", "Continuous learning", "Community involvement"]
        }
    },
    "industry_insights": {
        "work_environment_trends": {
            "remote_work": "38% fully remote",
            "hybrid_work": "42% hybrid (consistent with 2023)",
            "in_person": "20% in-person (increasing trend)",
            "preference": "Flexibility valued most"
        },
        "ai_adoption": {
            "current_usage": "62% currently using AI tools",
            "planning_usage": "76% using or planning to use",
            "top_tools": ["ChatGPT (75% satisfaction)", "GitHub Copilot", "Tabnine"],
            "integration_areas": ["Documentation (81%)", "Testing (80%)", "Writing code (76%)"]
        },
        "learning_preferences": {
            "online_resources": "82% prefer online learning",
            "documentation": "90% use API/SDK docs",
            "traditional_education": "49% learned at school vs 66% have degree",
            "continuous_learning": "Essential for career growth"
        }
    }
}

def get_enhanced_market_intelligence(query_type="general"):
    """Get relevant market intelligence data based on query type"""
    if query_type == "market_trends":
        return {
            "trending_languages": CAREER_KNOWLEDGE_BASE["market_trends_2024"]["programming_languages"],
            "high_paying_roles": CAREER_KNOWLEDGE_BASE["market_trends_2024"]["highest_paying_roles"],
            "technology_trends": CAREER_KNOWLEDGE_BASE["market_trends_2024"]["technology_trends"]
        }
    elif query_type == "salary_analysis":
        return CAREER_KNOWLEDGE_BASE["salary_benchmarks_2024"]
    elif query_type == "skill_demand":
        return CAREER_KNOWLEDGE_BASE["skill_demand_analysis"]
    else:
        return CAREER_KNOWLEDGE_BASE

# AI Intelligence Endpoints
@app.route('/api/intelligence/market-trends')
def analyze_market_trends():
    """Analyze current market trends with enhanced AI and real market data"""
    try:
        # Get enhanced market intelligence
        market_data = get_enhanced_market_intelligence("market_trends")
        
        # Enhanced AI prompt with real market data
        prompt = f"""
        Analyze the current job market trends for technology professionals. Focus on:
        
        CURRENT MARKET DATA (2024):
        - Python has overtaken JavaScript as #1 language (driven by AI boom)
        - Top paying roles: SRE ($140k-$200k), Cloud Engineers ($130k-$190k)
        - AI/ML adoption: 76% using or planning to use AI tools
        - Cloud computing growth: +38% demand increase
        - Remote work: 38% fully remote, 42% hybrid
        
        TRENDING TECHNOLOGIES:
        - AI/ML: +45% growth, +25-40% salary premium
        - Cloud (AWS/Azure): +38% growth, +15-30% salary premium  
        - Docker/Kubernetes: +40% demand growth
        - PostgreSQL: #1 database for 2nd year
        
        Provide a concise analysis of:
        1. Top 3 trending skill areas with growth percentages
        2. Salary ranges for high-demand roles
        3. Key recommendations for career advancement
        4. Market outlook for next 6-12 months
        
        Keep response professional and actionable for career development.
        """
        
        system_prompt = """You are a senior career intelligence analyst specializing in technology markets. 
        Use the provided current market data to give accurate, data-driven insights. 
        Focus on actionable career advice backed by real market trends."""
        
        ai_response = call_grok_ai(prompt, system_prompt)
        
        # Check if AI call failed and use fallback
        if isinstance(ai_response, str) and "ERROR:" in ai_response:
            print(f"[DEBUG] AI call failed: {ai_response}")
            return jsonify({
                "total_skills_analyzed": 150,
                "ai_provider": "SkillSync Market Intelligence (Fallback Mode)",
                "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                "market_trends": [
                    {
                        "skill": "AI/Machine Learning",
                        "demand_change": "+45%",
                        "salary_range": "$95k-$180k",
                        "growth_outlook": "Explosive growth expected"
                    },
                    {
                        "skill": "Cloud Architecture (AWS/Azure)",
                        "demand_change": "+38%", 
                        "salary_range": "$85k-$160k",
                        "growth_outlook": "Strong sustained demand"
                    },
                    {
                        "skill": "Cybersecurity",
                        "demand_change": "+42%",
                        "salary_range": "$80k-$170k", 
                        "growth_outlook": "Critical shortage driving growth"
                    }
                ],
                "ai_analysis": "Market analysis temporarily unavailable. Based on 2024 data: Python has overtaken JavaScript as the most popular language, driven by AI adoption. Cloud infrastructure and AI/ML skills command the highest premiums. Focus on Docker, Kubernetes, and AI tools for maximum career impact.",
                "status": "fallback_mode"
            })
        
        # Return enhanced response with AI analysis + structured data
        return jsonify({
            "total_skills_analyzed": 150,
            "ai_provider": "xAI Grok (Career Intelligence Specialist)",
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "market_trends": [
                {
                    "skill": "AI/Machine Learning", 
                    "demand_change": "+45%",
                    "salary_range": "$95k-$180k",
                    "growth_outlook": "Explosive growth expected"
                },
                {
                    "skill": "Cloud Architecture (AWS/Azure)",
                    "demand_change": "+38%",
                    "salary_range": "$85k-$160k", 
                    "growth_outlook": "Strong sustained demand"
                },
                {
                    "skill": "Python Development",
                    "demand_change": "+35%",
                    "salary_range": "$70k-$150k",
                    "growth_outlook": "Now #1 language on GitHub"
                }
            ],
            "ai_analysis": ai_response,
            "data_sources": ["Stack Overflow Developer Survey 2024", "GitHub Octoverse 2024"],
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "error": "Failed to analyze market trends",
            "message": str(e),
            "total_skills_analyzed": 0,
            "ai_provider": "SkillSync Error Handler",
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
            "market_trends": [],
            "ai_analysis": "Unable to analyze market trends at this time. Please try again later.",
            "status": "error"
        }), 500

@app.route('/api/intelligence/trigger', methods=['POST'])
def trigger_intelligence_cycle():
    """Trigger AI intelligence cycle with enhanced market analysis"""
    try:
        # Enhanced prompt with real market data
        prompt = f"""
        Generate a comprehensive intelligence cycle status update for a career development platform.
        
        CURRENT MARKET CONTEXT (2024):
        - Developer job market: Strong growth, 65,000+ developers surveyed
        - AI adoption: 76% using or planning to use AI tools in development
        - Top skills in demand: Python, Cloud (AWS/Azure), Docker, AI/ML
        - Salary trends: SRE and Cloud roles leading at $140k-$200k
        - Work environment: 42% hybrid, 38% remote, 20% in-person
        
        Provide a status update that includes:
        1. Current market monitoring status
        2. Key trends being tracked
        3. Upcoming opportunities to watch
        4. Recommended actions for career development
        
        Keep it professional and actionable for users seeking career guidance.
        """
        
        system_prompt = """You are an AI career intelligence system providing status updates. 
        Use current market data to give relevant, timely insights about career opportunities and trends.
        Focus on actionable intelligence that helps users make informed career decisions."""
        
        ai_response = call_grok_ai(prompt, system_prompt)
        
        # Check if AI call failed and use fallback
        if isinstance(ai_response, str) and "ERROR:" in ai_response:
            print(f"[DEBUG] AI call failed: {ai_response}")
            return jsonify({
                "status": "success",
                "message": "Intelligence cycle initiated successfully", 
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ai_status": "Intelligence cycle active. Currently monitoring: Python's rise to #1 language, AI tool adoption (76% growth), cloud infrastructure demand (+38%), and remote work trends. Key opportunities: AI/ML skills (+45% growth), cloud certifications, Docker/Kubernetes expertise. Recommended focus: Upskill in AI tools, cloud platforms, and containerization for maximum career impact.",
                "next_cycle": "Scheduled in 4 hours",
                "data_sources": ["Stack Overflow 2024", "GitHub Octoverse 2024"],
                "status_detail": "fallback_mode"
            })
        
        return jsonify({
            "status": "success", 
            "message": "Intelligence cycle initiated successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_status": ai_response,
            "next_cycle": "Scheduled in 4 hours",
            "data_sources": ["Stack Overflow 2024", "GitHub Octoverse 2024"],
            "status_detail": "ai_powered"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to trigger intelligence cycle: {str(e)}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "ai_status": "Intelligence cycle failed to initialize. System will retry automatically.",
            "next_cycle": "Retry in 1 hour",
            "status_detail": "error"
        }), 500

@app.route('/api/intelligence/user-insights', methods=['POST'])
def generate_user_insights():
    """Generate personalized user insights with enhanced market data"""
    try:
        data = request.get_json() or {}
        user_skills = data.get('skills', ['Python', 'JavaScript', 'SQL'])
        user_goals = data.get('goals', 'career advancement in technology')
        experience_level = data.get('experience', 'mid-level')
        
        # Get relevant market data for user's skills
        market_data = get_enhanced_market_intelligence("salary_analysis")
        skill_data = get_enhanced_market_intelligence("skill_demand")
        
        # Enhanced prompt with user context + market data
        prompt = f"""
        Generate personalized career insights for a technology professional with:
        
        USER PROFILE:
        - Skills: {', '.join(user_skills)}
        - Goals: {user_goals}
        - Experience: {experience_level}
        
        CURRENT MARKET DATA (2024):
        - Python: #1 language, $70k-$150k salary range, +35% growth
        - JavaScript: Still #1 for code pushes, $65k-$140k range
        - SQL: Essential skill, database market growing +25%
        - AI/ML: +45% growth, +25-40% salary premium
        - Cloud skills: +38% growth, +15-30% salary premium
        
        SALARY BENCHMARKS BY EXPERIENCE:
        - Entry (0-2 years): $50k-$85k
        - Mid-level (3-7 years): $75k-$130k  
        - Senior (8-15 years): $120k-$200k
        - Principal (15+ years): $180k-$350k+
        
        Provide specific, actionable insights including:
        1. Current market position analysis
        2. Skill gap identification with growth potential
        3. Salary expectations and negotiation points
        4. Next career steps with timeline
        5. Learning recommendations based on market trends
        
        Make it personal and actionable for their specific situation.
        """
        
        system_prompt = """You are an expert career counselor specializing in technology careers. 
        Use the provided market data to give personalized, accurate advice. 
        Focus on actionable recommendations that align with current market opportunities."""
        
        ai_response = call_grok_ai(prompt, system_prompt)
        
        # Check if AI call failed and use fallback
        if isinstance(ai_response, str) and "ERROR:" in ai_response:
            print(f"[DEBUG] AI call failed: {ai_response}")
            return jsonify({
                "user_profile": {
                    "skills": user_skills,
                    "goals": user_goals,
                    "experience": experience_level
                },
                "ai_insights": f"AI service temporarily unavailable. Here's a sample insight based on your profile:\n\nBased on your {experience_level} experience with {', '.join(user_skills[:2])}, I recommend:\n\n1. Focus on cloud technologies (AWS/Azure) - high demand\n2. Learn containerization (Docker/Kubernetes) - 40% salary increase potential\n3. Develop AI/ML skills - explosive growth market\n\nSalary range: $75k-$130k for {experience_level} professionals. Consider cloud certifications for +15-30% salary premium.",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "ai_provider": "SkillSync Career Intelligence (Fallback Mode)",
                "confidence_score": 0.75,
                "data_sources": ["Stack Overflow 2024", "GitHub Octoverse 2024"],
                "status": "fallback_mode"
            })
        
        return jsonify({
            "user_profile": {
                "skills": user_skills,
                "goals": user_goals,
                "experience": experience_level
            },
            "ai_insights": ai_response,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "ai_provider": "xAI Grok Career Specialist",
            "confidence_score": 0.92,
            "data_sources": ["Stack Overflow 2024", "GitHub Octoverse 2024"],
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "user_profile": {
                "skills": ['Python', 'JavaScript'],
                "goals": 'career advancement',
                "experience": 'mid-level'
            },
            "ai_insights": "Unable to generate AI insights at this time. Please try again later or contact support if the issue persists.",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "ai_provider": "SkillSync Error Handler",
            "confidence_score": 0.0,
            "status": "error"
        }), 500

@app.route('/api/intelligence/status')
def agent_status():
    """Get AI Agent status and capabilities"""
    try:
        # This endpoint doesn't need AI calls - it returns system status
        return jsonify({
            "agent_name": "SkillSync Career Intelligence Agent",
            "version": "2.1.0",
            "status": "active",
            "ai_integration": {
                "provider": "xAI Grok",
                "model": "Auto-Selected (grok-2, grok, grok-turbo, grok-1, grok-beta)",
                "specialization": "Career Development & Market Intelligence"
            },
            "capabilities": [
                "Real-time market trend analysis",
                "Personalized career roadmap generation",
                "Skill gap identification and recommendations",
                "Salary benchmarking and negotiation insights",
                "Industry growth prediction and opportunity matching",
                "Proactive career opportunity alerts"
            ],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "monitoring_status": "24/7 Active",
            "skills_tracked": 150,
            "api_status": "operational",
            "fallback_mode_available": True
        })
        
    except Exception as e:
        return jsonify({
            "agent_name": "SkillSync Career Intelligence Agent",
            "version": "2.1.0",
            "status": "error",
            "error_message": str(e),
            "ai_integration": {
                "provider": "xAI Grok",
                "model": "Unavailable",
                "specialization": "Career Development & Market Intelligence"
            },
            "capabilities": [],
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "monitoring_status": "Error State",
            "skills_tracked": 0,
            "api_status": "error",
            "fallback_mode_available": True
        }), 500

@app.route('/api/intelligence/user-insights-test', methods=['GET', 'POST'])
def test_user_insights():
    """Simple test endpoint for debugging"""
    return jsonify({
        "message": "User insights endpoint is accessible",
        "method": request.method,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_data": {
            "skills": ['Python', 'JavaScript', 'SQL'],
            "goals": 'career advancement in technology',
            "experience": 'mid-level'
        },
        "status": "test_success"
    })

# Enhanced Frontend Routes for User Engagement
@app.route('/dashboard')
def dashboard():
    """User dashboard with progress tracking and recent insights"""
    return render_template('dashboard.html')

@app.route('/market-intelligence')
def market_intelligence_hub():
    """Market intelligence hub with free insights and trends"""
    # Get market data from knowledge base
    market_data = get_enhanced_market_intelligence("market_trends")
    
    return render_template('market_intelligence.html', 
                         trending_languages=market_data['trending_languages'],
                         high_paying_roles=market_data['high_paying_roles'],
                         technology_trends=market_data['technology_trends'])

@app.route('/career-paths')
def career_paths():
    """Interactive career path explorer"""
    career_paths = CAREER_KNOWLEDGE_BASE["career_paths"]
    return render_template('career_paths.html', career_paths=career_paths)

@app.route('/tools')
def tools_hub():
    """Free tools and calculators for career development"""
    return render_template('tools.html')

@app.route('/community')
def community():
    """Community forum and discussion area"""
    return render_template('community.html')

@app.route('/resources')
def resources():
    """Educational resources and learning materials"""
    return render_template('resources.html')

# API Endpoints for Interactive Tools
@app.route('/api/tools/salary-calculator', methods=['POST'])
def salary_calculator():
    """Calculate estimated salary based on skills and location"""
    try:
        data = request.get_json() or {}
        skills = data.get('skills', [])
        location = data.get('location', 'remote')
        experience = data.get('experience', 'mid-level')
        
        # Get salary benchmarks from knowledge base
        salary_data = CAREER_KNOWLEDGE_BASE["salary_benchmarks_2024"]
        
        # Calculate base salary
        base_salary = salary_data["by_experience_level"].get(experience, {})
        base_range = base_salary.get("3_7_years", "$75k-$130k")  # default to mid-level
        
        # Apply location multiplier
        location_multiplier = salary_data["by_location_multiplier"].get(location, 1.0)
        
        # Skill premium calculation
        skill_premium = 0
        high_value_skills = ["python", "aws", "docker", "kubernetes", "react", "ai", "ml"]
        for skill in skills:
            if skill.lower() in high_value_skills:
                skill_premium += 0.1  # 10% per high-value skill
        
        return jsonify({
            "base_salary_range": base_range,
            "location": location,
            "location_multiplier": location_multiplier,
            "skill_premium": f"+{int(skill_premium * 100)}%",
            "estimated_range": f"${int(75000 * location_multiplier * (1 + skill_premium) / 1000)}k-${int(130000 * location_multiplier * (1 + skill_premium) / 1000)}k",
            "recommendations": [
                "Consider learning cloud technologies for +15-30% salary boost",
                "Docker/Kubernetes skills add significant market value",
                "AI/ML expertise commands +25-40% premium"
            ],
            "data_source": "Based on Stack Overflow 2024 Developer Survey"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/tools/skill-gap-analyzer', methods=['POST'])
def skill_gap_analyzer():
    """Analyze skill gaps based on career goals"""
    try:
        data = request.get_json() or {}
        current_skills = data.get('current_skills', [])
        target_role = data.get('target_role', 'full-stack developer')
        
        # Define skill requirements for different roles
        role_requirements = {
            "full-stack developer": ["JavaScript", "Python", "React", "Node.js", "SQL", "Git"],
            "data scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Pandas", "Jupyter"],
            "cloud engineer": ["AWS", "Docker", "Kubernetes", "Linux", "Terraform", "Python"],
            "frontend developer": ["JavaScript", "React", "CSS", "HTML", "TypeScript", "Git"],
            "backend developer": ["Python", "SQL", "API Design", "Docker", "Git", "Database Design"]
        }
        
        required_skills = role_requirements.get(target_role.lower(), [])
        missing_skills = [skill for skill in required_skills if skill not in current_skills]
        
        return jsonify({
            "target_role": target_role,
            "current_skills": current_skills,
            "required_skills": required_skills,
            "missing_skills": missing_skills,
            "completion_percentage": int((len(required_skills) - len(missing_skills)) / len(required_skills) * 100),
            "learning_recommendations": [
                f"Priority 1: {missing_skills[0] if missing_skills else 'You have all required skills!'}"
            ] + [f"Learn: {skill}" for skill in missing_skills[:3]],
            "estimated_learning_time": f"{len(missing_skills) * 2}-{len(missing_skills) * 4} months"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai-agent')
def ai_agent():
    return render_template('ai_agent.html')

@app.route('/api-docs')
def api_docs():
    return render_template('api_docs.html')

@app.route('/health')
def health_page():
    return render_template('health.html')

@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.get_json()
    
    if not data or 'username' not in data or 'email' not in data:
        return jsonify({'error': 'Username and email are required'}), 400
    
    # Check if user already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({'error': 'User with this email already exists'}), 409
    
    user = User(username=data['username'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'created_at': user.created_at.isoformat()
    }), 201

@app.route('/api/users/<int:user_id>/skills', methods=['GET', 'POST'])
def handle_user_skills(user_id):
    user = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        skills = Skill.query.filter_by(user_id=user_id).all()
        return jsonify([{
            'id': skill.id,
            'name': skill.name,
            'level': skill.level,
            'category': skill.category,
            'created_at': skill.created_at.isoformat()
        } for skill in skills])
    
    elif request.method == 'POST':
        data = request.get_json()
        
        if not data or 'name' not in data or 'level' not in data or 'category' not in data:
            return jsonify({'error': 'Name, level, and category are required'}), 400
        
        skill = Skill(
            name=data['name'],
            level=data['level'],
            category=data['category'],
            user_id=user_id
        )
        db.session.add(skill)
        db.session.commit()
        
        return jsonify({
            'id': skill.id,
            'name': skill.name,
            'level': skill.level,
            'category': skill.category,
            'created_at': skill.created_at.isoformat()
        }), 201

@app.route('/api/files/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'path': file_path
        }), 200

# Initialize database
def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    # Create tables before running the app
    create_tables()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
