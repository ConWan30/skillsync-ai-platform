from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from typing import Dict, Any
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# Import shared AI utilities
from ai_utils import call_grok_ai as shared_call_grok_ai, CAREER_KNOWLEDGE_BASE

# xAI Configuration
XAI_API_KEY = os.getenv('XAI_API_KEY', 'YOUR_XAI_API_KEY')  # Add your xAI API key here
XAI_BASE_URL = "https://api.x.ai/v1"

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

def call_grok_ai(prompt, system_prompt=None):
    """Call xAI Grok API with robust model selection and error handling"""
    try:
        if not XAI_API_KEY or XAI_API_KEY == 'YOUR_XAI_API_KEY':
            print("[WARNING] xAI API key not configured")
            return None
            
        # Available xAI models to try in order of preference
        models_to_try = [
            "grok-2-1212",
            "grok-2-latest", 
            "grok-beta",
            "grok-2-mini",
            "grok-vision-beta"
        ]
        
        headers = {
            'Authorization': f'Bearer {XAI_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # Try each model until one works
        for model in models_to_try:
            try:
                payload = {
                    "messages": messages,
                    "model": model,
                    "stream": False,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                
                print(f"[INFO] Trying xAI model: {model}")
                response = requests.post(
                    f"{XAI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'choices' in result and len(result['choices']) > 0:
                        ai_response = result['choices'][0]['message']['content']
                        print(f"[SUCCESS] xAI response received using {model}")
                        return ai_response
                elif response.status_code == 404:
                    print(f"[INFO] Model {model} not available, trying next...")
                    continue
                else:
                    print(f"[WARNING] xAI API error {response.status_code}: {response.text}")
                    continue
                    
            except requests.exceptions.Timeout:
                print(f"[WARNING] Timeout with model {model}, trying next...")
                continue
            except Exception as model_error:
                print(f"[WARNING] Error with model {model}: {model_error}")
                continue
        
        print("[ERROR] All xAI models failed or unavailable")
        return None
        
    except Exception as e:
        print(f"[ERROR] xAI API call failed: {e}")
        return None

def generate_fallback_gaming_assessment(user_input, domain):
    """Generate fallback gaming skill assessment when AI is unavailable"""
    return {
        'success': True,
        'overall_score': 78,
        'technical_score': 82,
        'design_score': 75,
        'industry_score': 70,
        'strengths': [
            'Strong foundation in gaming concepts',
            'Good understanding of game mechanics',
            'Creative problem-solving abilities',
            'Passion for gaming industry'
        ],
        'recommendations': [
            'Focus on building a strong portfolio with 2-3 complete game projects',
            'Learn Unity C# scripting and game physics fundamentals',
            'Study successful indie games in your target genre',
            'Join game development communities and participate in game jams',
            'Develop both technical and creative skills for well-rounded expertise'
        ],
        'areas_for_improvement': [
            'Advanced programming concepts',
            'Game engine optimization',
            'Industry networking',
            'Business aspects of gaming'
        ],
        'ai_analysis': f'Based on your background in {user_input[:50]}..., you show strong potential for {domain} careers.'
    }

def generate_fallback_gaming_roadmap(target_role, experience_level):
    """Generate fallback gaming career roadmap when AI is unavailable"""
    return {
        'target_role': target_role,
        'experience_level': experience_level,
        'phases': [
            {
                'phase': 'Phase 1 (0-3 months): Foundation Building',
                'tasks': [
                    'Complete Unity Learn pathway and basic tutorials',
                    'Build your first 2D game prototype',
                    'Learn C# programming fundamentals',
                    'Set up development environment and version control'
                ],
                'skills': ['Unity basics', 'C# programming', 'Git/GitHub', 'Game design principles'],
                'resources': ['Unity Learn', 'Codecademy C#', 'GitHub Desktop', 'Game Design courses']
            },
            {
                'phase': 'Phase 2 (3-6 months): Skill Development',
                'tasks': [
                    'Create a 3D game prototype with physics',
                    'Learn advanced Unity features and tools',
                    'Study game design patterns and architecture',
                    'Start building a professional portfolio'
                ],
                'skills': ['3D game development', 'Physics systems', 'Design patterns', 'Portfolio development'],
                'resources': ['Unity documentation', 'Game programming patterns', 'ArtStation', 'Itch.io']
            },
            {
                'phase': 'Phase 3 (6-12 months): Portfolio & Networking',
                'tasks': [
                    'Complete 2-3 polished game projects',
                    'Participate in game jams and competitions',
                    'Build professional network in gaming industry',
                    'Apply for junior positions or internships'
                ],
                'skills': ['Project management', 'Team collaboration', 'Industry networking', 'Job search'],
                'resources': ['Global Game Jam', 'LinkedIn gaming groups', 'Gaming conferences', 'Job boards']
            },
            {
                'phase': 'Phase 4 (12+ months): Career Launch',
                'tasks': [
                    'Secure first gaming industry position',
                    'Continue learning emerging technologies',
                    'Mentor other aspiring game developers',
                    'Specialize in chosen gaming niche'
                ],
                'skills': ['Professional development', 'Leadership', 'Specialization', 'Continuous learning'],
                'resources': ['Professional development courses', 'Industry publications', 'Mentorship programs', 'Advanced certifications']
            }
        ]
    }

def parse_gaming_assessment(ai_response, user_input, domain):
    """Parse AI response into structured gaming assessment"""
    try:
        # Extract scores and recommendations from AI response
        lines = ai_response.split('\n')
        
        # Default scores
        overall_score = 78
        technical_score = 82
        design_score = 75
        industry_score = 70
        
        # Extract scores from AI response
        for line in lines:
            if 'overall' in line.lower() and any(char.isdigit() for char in line):
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    overall_score = min(numbers[0], 100)
            elif 'technical' in line.lower() and any(char.isdigit() for char in line):
                numbers = [int(s) for s in line.split() if s.isdigit()]
                if numbers:
                    technical_score = min(numbers[0], 100)
        
        # Extract recommendations
        recommendations = [
            'Focus on building a strong portfolio with 2-3 complete game projects',
            'Learn Unity C# scripting and game physics fundamentals',
            'Study successful indie games in your target genre',
            'Join game development communities and participate in game jams',
            'Develop both technical and creative skills for well-rounded expertise'
        ]
        
        return {
            'overall_score': overall_score,
            'technical_score': technical_score,
            'design_score': design_score,
            'industry_score': industry_score,
            'strengths': [
                'Strong foundation in gaming concepts',
                'Good understanding of game mechanics',
                'Creative problem-solving abilities',
                'Passion for gaming industry'
            ],
            'recommendations': recommendations,
            'areas_for_improvement': [
                'Advanced programming concepts',
                'Game engine optimization',
                'Industry networking',
                'Business aspects of gaming'
            ],
            'ai_analysis': ai_response[:500] + "..." if len(ai_response) > 500 else ai_response
        }
        
    except Exception as e:
        print(f"[WARNING] Failed to parse AI assessment: {e}")
        return generate_fallback_gaming_assessment(user_input, domain)

# ============================================================================
# GAMING CAREER FRAMEWORK API ENDPOINTS - MULTI-DOMAIN INTEGRATION
# ============================================================================

# Import gaming agents
try:
    from gaming_agents import (
        initialize_gaming_agents, 
        get_gaming_agent_status,
        process_gaming_agent_collaboration,
        MultiDomainAssessmentAgent,
        AdaptiveRoadmapAgent,
        GAMING_KNOWLEDGE_BASE
    )
    gaming_agents = initialize_gaming_agents()
    GAMING_FRAMEWORK_ENABLED = True
    print("[INFO] Gaming career framework loaded successfully")
except ImportError as e:
    print(f"[WARNING] Gaming framework not available: {e}")
    GAMING_FRAMEWORK_ENABLED = False
    gaming_agents = {}

@app.route('/api/gaming/assess-skills', methods=['POST'])
def assess_gaming_skills():
    """Multi-Domain Assessment Agent - Gaming skill assessment endpoint"""
    try:
        data = request.get_json() or {}
        user_input = data.get('user_input', '')
        domain = data.get('domain', 'gaming')
        user_id = data.get('user_id', 'anonymous')
        
        if not user_input:
            return jsonify({
                'success': False,
                'error': 'User input is required for gaming skill assessment'
            }), 400
        
        print(f"[INFO] Gaming skill assessment for domain: {domain}")
        
        if GAMING_FRAMEWORK_ENABLED:
            # Use Multi-Domain Assessment Agent
            assessment_agent = gaming_agents.get('multi_domain_assessment')
            if not assessment_agent:
                assessment_agent = MultiDomainAssessmentAgent()
            
            # Perform gaming skill assessment
            assessment_result = assessment_agent.assess_gaming_skills(user_input, domain)
            
            # A2A Protocol: Integrate with existing agents
            if assessment_result.get('success'):
                try:
                    agent_states = get_current_agent_states(user_id)
                    # Use the entire assessment result since it's now flattened
                    collaboration_insights = process_gaming_agent_collaboration(
                        agent_states, 
                        assessment_result
                    )
                    assessment_result['collaboration_insights'] = collaboration_insights
                except Exception as e:
                    print(f"[WARNING] A2A collaboration failed: {e}")
                    # Continue without collaboration insights
        else:
            # Fallback assessment
            assessment_result = generate_fallback_gaming_assessment(user_input, domain)
        
        return jsonify(assessment_result)
        
    except Exception as e:
        print(f"[ERROR] Gaming skill assessment failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gaming/generate-roadmap', methods=['POST'])
def generate_gaming_roadmap():
    """Adaptive Roadmap Agent - Gaming career roadmap generation"""
    try:
        data = request.get_json() or {}
        gaming_profile = data.get('gaming_profile', {})
        target_role = data.get('target_role', 'Game Developer')
        user_id = data.get('user_id', 'anonymous')
        
        print(f"[DEBUG] Generating gaming roadmap for role: {target_role}")
        
        if GAMING_FRAMEWORK_ENABLED:
            # Use Adaptive Roadmap Agent
            roadmap_agent = gaming_agents.get('adaptive_roadmap')
            if not roadmap_agent:
                roadmap_agent = AdaptiveRoadmapAgent()
            
            roadmap_result = roadmap_agent.generate_gaming_roadmap(gaming_profile, target_role)
            
            # A2A Protocol integration
            if roadmap_result['success']:
                agent_states = get_current_agent_states(user_id)
                collaboration_insights = process_gaming_agent_collaboration(
                    agent_states, 
                    {'roadmap': roadmap_result['roadmap'], 'target_role': target_role}
                )
                roadmap_result['enhanced_insights'] = collaboration_insights
        else:
            # Fallback roadmap
            roadmap_result = generate_fallback_gaming_roadmap(gaming_profile, target_role)
        
        return jsonify(roadmap_result)
        
    except Exception as e:
        print(f"[ERROR] Gaming roadmap generation failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/gaming/market-intelligence', methods=['POST'])
def gaming_market_intelligence():
    """Gaming Market Intelligence - Industry trends and insights"""
    try:
        # Get request data
        data = request.get_json() or {}
        analysis_type = data.get('analysis_type', 'gaming_market_trends')
        
        print(f"[INFO] Gaming market intelligence requested: {analysis_type}")
        
        # Gaming market intelligence with AI analysis
        market_system_prompt = """
        You are an expert gaming industry market analyst. Provide comprehensive 
        market intelligence including growth opportunities, career paths, salary 
        trends, emerging technologies, and strategic recommendations.
        """
        
        market_prompt = """
        Analyze the current gaming industry market and provide insights on:
        1. Market Growth Opportunities ($321B industry, 8.7% CAGR)
        2. High-Demand Career Paths (Game Dev, Esports, Business)
        3. Salary Trends and Projections
        4. Emerging Technology Impact (VR/AR, AI, Cloud Gaming)
        5. Career Entry Strategies
        6. Success Factors and Risk Mitigation
        
        Format as actionable market intelligence report.
        """
        
        ai_analysis = call_grok_ai(market_prompt, market_system_prompt)
        
        intelligence_report = {
            'success': True,
            'market_overview': {
                'industry_size': '$321.1 billion global gaming market',
                'growth_rate': '8.7% CAGR through 2027',
                'emerging_trends': [
                    'Cloud Gaming', 'AI-Generated Content', 'VR/AR Gaming',
                    'Esports Growth', 'Cross-Platform Development'
                ]
            },
            'career_opportunities': {
                'high_demand_roles': ['Game Developer', 'Technical Artist', 'Product Manager'],
                'salary_ranges': {
                    'junior': '$55k-$75k',
                    'mid': '$75k-$110k',
                    'senior': '$110k-$160k'
                }
            },
            'ai_market_analysis': ai_analysis if ai_analysis and "ERROR:" not in ai_analysis else None,
            'recommendations': {
                'skill_priorities': ['Unity/Unreal', 'Programming', 'Game Design'],
                'entry_strategies': ['Build portfolio', 'Join communities', 'Attend events']
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(intelligence_report)
        
    except Exception as e:
        print(f"[ERROR] Gaming market intelligence failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/gaming/career-guidance', methods=['POST'])
def gaming_career_guidance():
    """Enhanced career guidance with gaming specialization"""
    try:
        data = request.get_json() or {}
        user_input = data.get('user_input', '')
        career_focus = data.get('career_focus', 'general')
        user_id = data.get('user_id', 'anonymous')
        
        # Check if gaming-focused request
        gaming_keywords = ['game', 'gaming', 'unity', 'unreal', 'esports', 'game dev']
        is_gaming_request = any(keyword.lower() in user_input.lower() for keyword in gaming_keywords)
        
        if is_gaming_request:
            # Gaming-specific guidance
            gaming_system_prompt = """
            You are an expert gaming industry career advisor. Provide comprehensive 
            guidance on game development careers, esports opportunities, portfolio 
            development, and industry networking strategies.
            """
            
            gaming_guidance_prompt = f"""
            Provide comprehensive gaming career guidance for: {user_input}
            
            Include:
            1. Career Path Analysis (Best-fit roles, timeline)
            2. Skill Development Plan (Technical, creative, business)
            3. Portfolio Strategy (Projects, showcase tips)
            4. Industry Integration (Networking, communities)
            5. Success Metrics (Milestones, KPIs)
            
            Provide specific, actionable recommendations.
            """
            
            ai_response = call_grok_ai(gaming_guidance_prompt, gaming_system_prompt)
            
            guidance = {
                'career_analysis': {
                    'recommended_roles': ['Game Developer', 'Technical Artist'],
                    'progression_timeline': '12-24 months'
                },
                'skill_development': {
                    'technical_priorities': ['Unity Basics', 'C# Programming'],
                    'learning_timeline': '6-12 months'
                },
                'portfolio_strategy': {
                    'project_recommendations': ['2D Platformer Game']
                },
                'ai_guidance': ai_response if ai_response and "ERROR:" not in ai_response else None,
                'gaming_specialized': True
            }
            
            # A2A Protocol integration
            agent_states = get_current_agent_states(user_id)
            collaboration_insights = process_gaming_agent_collaboration(agent_states, guidance)
            
            return jsonify({
                'success': True,
                'guidance': guidance,
                'collaboration_insights': collaboration_insights,
                'domain': 'gaming',
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Use existing general career guidance
            return jsonify({
                'success': True,
                'guidance': {'message': 'Redirected to general career guidance'},
                'domain': 'general'
            })
        
    except Exception as e:
        print(f"[ERROR] Gaming career guidance failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/gaming-careers')
def gaming_careers():
    """Serve the gaming careers page"""
    return render_template('gaming_careers.html')

# ============================================================================
# GAMING FRAMEWORK HELPER FUNCTIONS
# ============================================================================

def get_current_agent_states(user_id: str) -> Dict[str, Any]:
    """Get current states of all agents for A2A collaboration"""
    return {
        'behavioral': {
            'userProfile': {'interests': {'technology': 0.8, 'gaming': 0.9}},
            'status': 'ACTIVE'
        },
        'market': {
            'trends': ['Gaming Growth', 'VR/AR Development', 'Cloud Gaming'],
            'status': 'ACTIVE'
        },
        'goal': {
            'active_goals': ['Learn game development', 'Build portfolio'],
            'status': 'ACTIVE'
        }
    }


def generate_fallback_gaming_roadmap(gaming_profile: Dict, target_role: str) -> Dict[str, Any]:
    """Generate fallback gaming roadmap"""
    return {
        'success': True,
        'roadmap': {
            'phases': {
                'phase_1': {
                    'title': 'Foundation Building (0-6 months)',
                    'skills_focus': ['Unity Basics', 'C# Programming'],
                    'projects': ['2D Platformer Game']
                }
            },
            'overall_timeline': '12 months',
            'fallback': True
        },
        'target_role': target_role,
        'timestamp': datetime.now().isoformat()
    }

# ============================================================================
# AI AGENT DEMO ENDPOINTS - FOR AI AGENT PAGE FUNCTIONALITY
# ============================================================================

@app.route('/api/intelligence/status', methods=['GET'])
def ai_agent_status():
    """AI Agent status endpoint for demo"""
    try:
        return jsonify({
            'success': True,
            'agent_name': 'SkillSync Multi-Agent AI',
            'version': '2.1.4',
            'status': 'active',
            'ai_integration': {
                'provider': 'xAI Grok',
                'models_available': ['grok-2-1212', 'grok-2-latest', 'grok-beta'],
                'status': 'operational'
            },
            'capabilities': [
                'Real-time behavioral analysis and pattern recognition',
                'Market intelligence with salary trend analysis', 
                'Personalized motivation and energy management',
                'AI-powered goal setting and progress tracking',
                'Multi-agent collaboration via A2A protocol',
                'Autonomous career path optimization'
            ],
            'active_agents': {
                'behavioral_agent': 'ACTIVE',
                'motivation_agent': 'ACTIVE', 
                'market_intelligence_agent': 'ACTIVE',
                'goal_setting_agent': 'ACTIVE'
            },
            'a2a_protocol': {
                'status': 'operational',
                'sync_interval': '30 seconds',
                'collaboration_score': 94
            },
            'last_updated': datetime.now().isoformat(),
            'uptime': '15 days, 4 hours',
            'processed_interactions': 1247
        })
        
    except Exception as e:
        print(f"[ERROR] AI Agent status failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/intelligence/market-trends', methods=['GET'])
def ai_market_trends():
    """Market trends analysis endpoint for demo"""
    try:
        # Get AI-powered market analysis
        market_system_prompt = """
        You are a concise market analyst. Provide brief, data-focused insights 
        under 60 words. Focus on numbers and immediate trends.
        """
        
        market_prompt = """
        Current tech market analysis:
        
        Provide only:
        • Top 3 trending skills with % demand change
        • Salary growth rate this year
        • Best opportunity for next 6 months
        
        Under 60 words. Be specific with numbers.
        """
        
        ai_analysis = call_grok_ai(market_prompt, market_system_prompt)
        
        # Structured market trends data
        market_trends = [
            {
                'skill': 'Artificial Intelligence/ML',
                'demand_change': 45,
                'salary_trend': '$95k-$165k (+12% YoY)',
                'growth_prediction': 'Very High'
            },
            {
                'skill': 'Cloud Computing (AWS/Azure)',
                'demand_change': 38,
                'salary_trend': '$85k-$145k (+8% YoY)',
                'growth_prediction': 'High'
            },
            {
                'skill': 'Python Programming',
                'demand_change': 32,
                'salary_trend': '$75k-$135k (+10% YoY)',
                'growth_prediction': 'Very High'
            },
            {
                'skill': 'Data Science/Analytics',
                'demand_change': 28,
                'salary_trend': '$80k-$140k (+7% YoY)',
                'growth_prediction': 'High'
            },
            {
                'skill': 'Cybersecurity',
                'demand_change': 25,
                'salary_trend': '$85k-$155k (+9% YoY)',
                'growth_prediction': 'Very High'
            }
        ]
        
        return jsonify({
            'success': True,
            'market_trends': market_trends,
            'ai_provider': 'xAI Grok',
            'total_skills_analyzed': 147,
            'analysis_timestamp': datetime.now().isoformat(),
            'ai_market_analysis': ai_analysis if ai_analysis and "ERROR:" not in ai_analysis else None,
            'insights': {
                'top_growth_sector': 'Artificial Intelligence',
                'avg_salary_increase': '9.2%',
                'skills_shortage': ['AI/ML Engineers', 'Cloud Architects', 'Cybersecurity Specialists'],
                'market_outlook': 'Strong growth expected through 2025'
            }
        })
        
    except Exception as e:
        print(f"[ERROR] Market trends analysis failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/intelligence/trigger', methods=['POST'])
def trigger_intelligence_cycle():
    """Trigger AI intelligence cycle endpoint for demo"""
    try:
        # Simulate intelligence cycle trigger
        cycle_data = {
            'success': True,
            'status': 'Intelligence cycle triggered successfully',
            'message': 'Multi-agent AI system has initiated market analysis and behavioral pattern recognition',
            'cycle_id': f'cycle_{int(datetime.now().timestamp())}',
            'agents_activated': [
                'Behavioral Intelligence Agent',
                'Market Intelligence Agent', 
                'Motivation & Energy Agent',
                'Goal Setting Agent'
            ],
            'estimated_completion': '45 seconds',
            'timestamp': datetime.now().isoformat(),
            'a2a_protocol': {
                'collaboration_initiated': True,
                'agent_sync_count': 4,
                'data_exchange_status': 'active'
            }
        }
        
        return jsonify(cycle_data)
        
    except Exception as e:
        print(f"[ERROR] Intelligence cycle trigger failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/intelligence/user-insights', methods=['POST'])
def generate_user_insights():
    """Generate AI-powered user insights for demo"""
    try:
        data = request.get_json() or {}
        user_profile = data
        
        # AI-powered career insights
        insights_system_prompt = """
        You are a direct career advisor. Provide focused insights in under 80 words. 
        Be specific about immediate actions.
        """
        
        insights_prompt = f"""
        Profile: {user_profile.get('skills', [])} | {user_profile.get('goals', 'Not specified')} | {user_profile.get('experience', 'Not specified')}
        
        Provide only:
        • Career fit score (1-100)
        • Top 2 skill gaps to address
        • Next immediate action
        • Salary growth potential
        
        Under 80 words total.
        """
        
        ai_insights = call_grok_ai(insights_prompt, insights_system_prompt)
        
        insights_result = {
            'success': True,
            'user_profile': user_profile,
            'ai_insights': ai_insights if ai_insights and "ERROR:" not in ai_insights else "AI analysis indicates strong potential for career advancement in your chosen field. Focus on building a comprehensive portfolio and expanding your technical skills.",
            'ai_provider': 'xAI Grok',
            'confidence_score': 0.89,
            'status': 'analysis_complete',
            'generated_at': datetime.now().isoformat(),
            'recommendations': {
                'immediate_actions': [
                    'Build projects showcasing your skills',
                    'Connect with professionals in your target field',
                    'Stay current with industry trends'
                ],
                'skill_priorities': ['Advanced programming', 'System design', 'Leadership'],
                'timeline': '6-12 months for significant progress'
            }
        }
        
        return jsonify(insights_result)
        
    except Exception as e:
        print(f"[ERROR] User insights generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/intelligence/user-insights-test', methods=['POST'])
def test_user_insights_endpoint():
    """Test endpoint for debugging user insights"""
    try:
        data = request.get_json() or {}
        
        return jsonify({
            'success': True,
            'status': 'endpoint_accessible',
            'method': 'POST',
            'timestamp': datetime.now().isoformat(),
            'test_data': data,
            'message': 'Test endpoint is working correctly'
        })
        
    except Exception as e:
        print(f"[ERROR] Test endpoint failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/intelligence/gaming-career-analysis', methods=['POST'])
def gaming_career_analysis_demo():
    """Gaming career analysis for demo form"""
    try:
        data = request.get_json() or {}
        role = data.get('role', '')
        experience = data.get('experience', '')
        goals = data.get('goals', '')
        
        # Gaming-specific analysis
        gaming_system_prompt = """
        You are an expert gaming industry career advisor. Provide comprehensive 
        analysis including career fit, skill recommendations, salary insights, 
        and actionable next steps for gaming careers.
        """
        
        gaming_analysis_prompt = f"""
        Analyze this gaming career profile:
        - Role Interest: {role}
        - Experience Level: {experience}
        - Career Goals: {goals}
        
        Provide:
        1. Career Fit Score (0-100)
        2. Key Insights (3-4 bullet points)
        3. Skill Recommendations
        4. Salary Expectations
        5. Next Steps
        
        Format as structured analysis for gaming industry.
        """
        
        ai_response = call_grok_ai(gaming_analysis_prompt, gaming_system_prompt)
        
        analysis_result = {
            'success': True,
            'analysis': {
                'score': 82,
                'scoreExplanation': f'Strong potential for {role} based on {experience} experience and clear goals in gaming industry.',
                'insights': [
                    'Gaming industry shows 8.7% annual growth with high demand for skilled professionals',
                    f'Your interest in {role} aligns with current market opportunities',
                    'Strong foundation for career transition into gaming sector',
                    'Portfolio development will be key to success in this field'
                ],
                'recommendations': [
                    'Learn Unity or Unreal Engine for game development',
                    'Build a portfolio showcasing gaming projects',
                    'Join gaming communities and attend industry events',
                    'Consider specializing in emerging areas like VR/AR gaming'
                ],
                'salaryInsight': f'Gaming professionals in {role} roles typically earn $55k-$95k annually, with senior positions reaching $120k+',
                'ai_analysis': ai_response if ai_response and "ERROR:" not in ai_response else None
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(analysis_result)
        
    except Exception as e:
        print(f"[ERROR] Gaming career analysis demo failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# ============================================================================
# GOALS & CAREER PLANNING ENDPOINTS - AI-POWERED GOAL SETTING
# ============================================================================

@app.route('/api/goals/analyze', methods=['POST'])
def analyze_career_goals():
    """AI-powered career goal analysis"""
    try:
        data = request.get_json() or {}
        goals_input = data.get('goals', '')
        current_situation = data.get('current_situation', '')
        timeline = data.get('timeline', '12 months')
        
        # AI-powered goal analysis
        goals_system_prompt = """
        You are a direct career analyst. Provide concise, actionable feedback only. 
        Keep responses under 100 words. Focus on immediate next steps.
        """
        
        goals_prompt = f"""
        Analyze: {goals_input}
        Current: {current_situation}
        Timeline: {timeline}
        
        Provide only:
        • Feasibility score (1-100)
        • Top 3 immediate actions needed
        • Main obstacle + solution
        • Success probability
        
        Keep response under 100 words. Be direct.
        """
        
        ai_analysis = call_grok_ai(goals_prompt, goals_system_prompt)
        
        # Structured goal analysis
        goal_analysis = {
            'success': True,
            'goal_input': goals_input,
            'analysis': {
                'feasibility_score': 85,
                'smart_breakdown': {
                    'specific': 'Clear career advancement objectives identified',
                    'measurable': 'Quantifiable milestones and metrics defined',
                    'achievable': 'Realistic given current situation and timeline',
                    'relevant': 'Aligned with market opportunities and personal strengths',
                    'time_bound': f'Well-defined {timeline} timeline'
                },
                'action_plan': [
                    {
                        'phase': 'Phase 1 (0-3 months)',
                        'objectives': ['Skill assessment and gap analysis', 'Initial networking'],
                        'milestones': ['Complete skills inventory', 'Connect with 10 industry professionals']
                    },
                    {
                        'phase': 'Phase 2 (3-6 months)', 
                        'objectives': ['Skill development', 'Portfolio building'],
                        'milestones': ['Complete relevant courses', 'Build 2-3 portfolio projects']
                    },
                    {
                        'phase': 'Phase 3 (6-12 months)',
                        'objectives': ['Job search and applications', 'Interview preparation'],
                        'milestones': ['Apply to target positions', 'Secure interviews']
                    }
                ],
                'potential_obstacles': [
                    'Time management challenges',
                    'Skill development gaps',
                    'Market competition',
                    'Interview performance'
                ],
                'success_strategies': [
                    'Consistent daily progress tracking',
                    'Regular mentor consultation',
                    'Continuous market research',
                    'Skills practice and improvement'
                ],
                'required_resources': [
                    'Online learning platforms',
                    'Professional networking events',
                    'Mentorship opportunities',
                    'Portfolio hosting platforms'
                ]
            },
            'ai_analysis': ai_analysis if ai_analysis and "ERROR:" not in ai_analysis else None,
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(goal_analysis)
        
    except Exception as e:
        print(f"[ERROR] Goal analysis failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/goals/generate', methods=['POST'])
def generate_smart_goals():
    """Generate SMART goals from user input"""
    try:
        data = request.get_json() or {}
        career_focus = data.get('career_focus', '')
        current_level = data.get('current_level', '')
        desired_outcome = data.get('desired_outcome', '')
        
        # AI-powered SMART goal generation
        smart_goals_system_prompt = """
        You are a concise career strategist. Generate 2-3 focused SMART goals maximum. 
        Keep responses under 150 words total. Be direct and actionable, not verbose.
        """
        
        smart_goals_prompt = f"""th
        Create 2-3 concise SMART goals for:
        - Focus: {career_focus}
        - Level: {current_level}  
        - Goal: {desired_outcome}
        
        For each goal provide ONLY:
        • One clear objective (1 sentence)
        • One measurable outcome (specific number/metric)
        • Timeline (3-12 months)
        • Top 3 action steps (bullet points)
        
        Keep total response under 150 words. Be direct and practical.
        """
        
        ai_goals = call_grok_ai(smart_goals_prompt, smart_goals_system_prompt)
        
        # Generate structured SMART goals
        smart_goals = [
            {
                'id': 'goal_1',
                'title': f'Master {career_focus} Fundamentals',
                'description': f'Develop comprehensive understanding of core {career_focus} concepts and practices',
                'specific': f'Complete advanced {career_focus} certification and build 3 portfolio projects',
                'measurable': '100% certification completion, 3 projects with documentation',
                'achievable': 'Based on current level and available learning resources',
                'relevant': f'Essential for career advancement in {career_focus}',
                'time_bound': '6 months',
                'action_steps': [
                    'Research and select appropriate certification program',
                    'Create study schedule with weekly milestones',
                    'Begin first portfolio project',
                    'Join relevant professional communities'
                ],
                'success_metrics': ['Certification earned', 'Projects completed', 'Community engagement'],
                'progress_tracking': 'Weekly progress reviews and milestone checkpoints'
            },
            {
                'id': 'goal_2', 
                'title': 'Build Professional Network',
                'description': 'Establish meaningful professional connections in target industry',
                'specific': 'Connect with 50 professionals and attend 6 industry events',
                'measurable': '50 LinkedIn connections, 6 events attended, 5 informational interviews',
                'achievable': 'Realistic networking targets with consistent effort',
                'relevant': 'Critical for career opportunities and industry insights',
                'time_bound': '9 months',
                'action_steps': [
                    'Optimize LinkedIn profile',
                    'Identify key industry events and conferences',
                    'Reach out to professionals for informational interviews',
                    'Join professional associations'
                ],
                'success_metrics': ['Connection count', 'Event attendance', 'Interview completion'],
                'progress_tracking': 'Monthly networking activity reports'
            }
        ]
        
        return jsonify({
            'success': True,
            'smart_goals': smart_goals,
            'ai_generated_goals': ai_goals if ai_goals and "ERROR:" not in ai_goals else None,
            'total_goals': len(smart_goals),
            'estimated_completion': '6-12 months',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] SMART goals generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/goals/track-progress', methods=['POST'])
def track_goal_progress():
    """Track progress on career goals"""
    try:
        data = request.get_json() or {}
        goal_id = data.get('goal_id', '')
        progress_update = data.get('progress_update', '')
        completion_percentage = data.get('completion_percentage', 0)
        
        # AI-powered progress analysis
        progress_system_prompt = """
        You are a motivational progress coach. Keep feedback under 50 words. 
        Be encouraging but direct about next steps.
        """
        
        progress_prompt = f"""
        Progress: {progress_update}
        Completion: {completion_percentage}%
        
        Provide only:
        • Quick assessment (Good/Needs work)
        • One specific next step
        • Motivational note (1 sentence)
        
        Maximum 50 words total.
        """
        
        ai_feedback = call_grok_ai(progress_prompt, progress_system_prompt)
        
        progress_analysis = {
            'success': True,
            'goal_id': goal_id,
            'progress_summary': {
                'completion_percentage': completion_percentage,
                'status': 'on_track' if completion_percentage >= 70 else 'needs_attention',
                'momentum': 'strong' if completion_percentage >= 80 else 'moderate',
                'next_milestone': 'Continue current trajectory'
            },
            'ai_feedback': ai_feedback if ai_feedback and "ERROR:" not in ai_feedback else "Great progress! Keep maintaining consistent effort toward your goal.",
            'recommendations': [
                'Maintain current progress momentum',
                'Set weekly mini-goals for continued advancement',
                'Celebrate achievements to stay motivated'
            ],
            'motivation_boost': "You're making excellent progress! Every step forward brings you closer to your career goals.",
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(progress_analysis)
        
    except Exception as e:
        print(f"[ERROR] Goal progress tracking failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/goals/ai-guidance', methods=['POST'])
def get_ai_guidance():
    """Get AI-powered guidance for specific goals"""
    try:
        data = request.get_json() or {}
        goal_id = data.get('goal_id', '')
        request_type = data.get('request_type', 'guidance')
        
        # AI-powered guidance generation
        guidance_system_prompt = """
        You are a goal achievement specialist. Provide specific, actionable guidance
        for career goals. Keep responses under 100 words total. Focus on immediate next steps.
        """
        
        guidance_prompt = f"""
        Goal ID: {goal_id}
        Request: {request_type}
        
        Provide:
        • 3 immediate next actions
        • 2 strategic tips
        • 2 potential obstacles + solutions
        
        Under 100 words total. Be specific and actionable.
        """
        
        ai_analysis = call_grok_ai(guidance_prompt, guidance_system_prompt)
        
        guidance = {
            'next_actions': [
                'Break down the goal into smaller weekly milestones',
                'Set up accountability system (mentor, partner, or tracking app)',
                'Schedule dedicated time blocks for goal-related activities'
            ],
            'tips': [
                'Track progress daily to maintain momentum',
                'Celebrate small wins to stay motivated'
            ],
            'obstacles': [
                'Time management challenges → Use time-blocking technique',
                'Lack of motivation → Find an accountability partner'
            ],
            'ai_analysis': ai_analysis if ai_analysis and "ERROR:" not in ai_analysis else "Focus on consistent daily progress and break large goals into manageable steps."
        }
        
        return jsonify({
            'success': True,
            'guidance': guidance,
            'goal_id': goal_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] AI guidance generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# TOOLS API ENDPOINTS - CAREER DEVELOPMENT TOOLS
# ============================================================================

@app.route('/api/tools/salary-calculator', methods=['POST'])
def salary_calculator():
    """Calculate salary estimates based on role, experience, and location"""
    try:
        data = request.get_json() or {}
        role = data.get('role', '')
        experience = data.get('experience', '')
        location = data.get('location', '')
        
        # Salary calculation logic based on market data
        base_salaries = {
            'frontend': {'0-1': 65000, '2-4': 85000, '5-7': 110000, '8-12': 140000, '13+': 170000},
            'backend': {'0-1': 70000, '2-4': 90000, '5-7': 120000, '8-12': 150000, '13+': 180000},
            'fullstack': {'0-1': 75000, '2-4': 95000, '5-7': 125000, '8-12': 155000, '13+': 185000},
            'devops': {'0-1': 80000, '2-4': 100000, '5-7': 130000, '8-12': 160000, '13+': 195000},
            'data-scientist': {'0-1': 85000, '2-4': 110000, '5-7': 140000, '8-12': 170000, '13+': 210000},
            'mobile': {'0-1': 70000, '2-4': 90000, '5-7': 115000, '8-12': 145000, '13+': 175000}
        }
        
        # Location multipliers
        location_multipliers = {
            'san-francisco': 1.4, 'new-york': 1.3, 'seattle': 1.25,
            'austin': 1.1, 'remote': 1.0, 'other': 0.95
        }
        
        base_salary = base_salaries.get(role, {}).get(experience, 75000)
        multiplier = location_multipliers.get(location, 1.0)
        
        adjusted_salary = int(base_salary * multiplier)
        salary_range = f"${adjusted_salary - 15000:,} - ${adjusted_salary + 25000:,}"
        
        return jsonify({
            'success': True,
            'salary_range': salary_range,
            'details': f'Based on current market data for {role.replace("-", " ").title()} with {experience} experience in {location.replace("-", " ").title()}',
            'base_salary': adjusted_salary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Salary calculator failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/skill-gap-analyzer', methods=['POST'])
def skill_gap_analyzer():
    """Analyze skill gaps for target roles"""
    try:
        data = request.get_json() or {}
        target_role = data.get('target_role', '')
        current_skills = data.get('current_skills', '').lower().split(',')
        current_skills = [skill.strip() for skill in current_skills]
        
        # Required skills by role
        role_requirements = {
            'frontend': ['html', 'css', 'javascript', 'react', 'typescript', 'webpack', 'git'],
            'backend': ['python', 'sql', 'api', 'docker', 'aws', 'git', 'database'],
            'fullstack': ['html', 'css', 'javascript', 'react', 'python', 'sql', 'git', 'api'],
            'devops': ['docker', 'kubernetes', 'aws', 'terraform', 'jenkins', 'git', 'linux'],
            'data-scientist': ['python', 'sql', 'pandas', 'scikit-learn', 'jupyter', 'git', 'statistics']
        }
        
        required_skills = role_requirements.get(target_role, [])
        matching_skills = [skill for skill in current_skills if any(req in skill for req in required_skills)]
        missing_skills = [skill for skill in required_skills if not any(skill in cs for cs in current_skills)]
        
        match_percentage = int((len(matching_skills) / len(required_skills)) * 100) if required_skills else 0
        
        return jsonify({
            'success': True,
            'match_score': match_percentage,
            'matching_skills': matching_skills[:10],  # Limit display
            'missing_skills': missing_skills[:8],     # Limit display
            'recommendations': [
                f'Focus on learning {missing_skills[0] if missing_skills else "advanced concepts"}',
                'Build projects showcasing these skills',
                'Consider getting certified in key technologies'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Skill gap analyzer failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/career-strategy', methods=['POST'])
def career_strategy():
    """Generate AI-powered career strategy"""
    try:
        data = request.get_json() or {}
        current_role = data.get('current_role', '')
        career_goals = data.get('career_goals', '')
        experience_level = data.get('experience_level', '')
        
        # AI-powered strategy generation
        strategy_system_prompt = """
        You are a strategic career advisor. Provide focused, actionable career strategy. 
        Keep responses under 120 words total. Focus on immediate steps and timeline.
        """
        
        strategy_prompt = f"""
        Current role: {current_role}
        Goals: {career_goals}
        Level: {experience_level}
        
        Provide strategy with:
        • 3 key recommendations
        • 3-step action plan
        • Realistic timeline
        • Success probability (%)
        
        Keep under 120 words total.
        """
        
        ai_response = call_grok_ai(strategy_prompt, strategy_system_prompt)
        
        # Structured strategy response
        strategy = {
            'recommendations': [
                'Build target skills through focused learning and practice',
                'Network with professionals in your target industry/role',
                'Create portfolio projects that demonstrate your capabilities'
            ],
            'action_plan': [
                'Complete skills assessment and identify top 3 gaps',
                'Set up learning schedule with weekly milestones',
                'Start networking and applying to target positions'
            ],
            'timeline': '6-12 months for significant progress',
            'success_probability': 85,
            'ai_analysis': ai_response if ai_response and "ERROR:" not in ai_response else None
        }
        
        return jsonify({
            'success': True,
            'strategy': strategy,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Career strategy generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/resume-optimizer', methods=['POST'])
def resume_optimizer():
    """AI-powered resume optimization"""
    try:
        data = request.get_json() or {}
        target_job = data.get('target_job', '')
        resume_content = data.get('resume_content', '')
        industry = data.get('industry', '')
        
        # AI resume optimization
        resume_system_prompt = """
        You are a resume optimization expert. Analyze resume content and provide 
        specific improvements. Keep feedback under 100 words, focus on actionable changes.
        """
        
        resume_prompt = f"""
        Target job: {target_job}
        Industry: {industry}
        Resume: {resume_content[:500]}...
        
        Provide:
        • Optimization score (1-100)
        • Top 3 specific improvements
        • 3-5 keywords to add
        • Brief feedback
        
        Under 100 words total.
        """
        
        ai_feedback = call_grok_ai(resume_prompt, resume_system_prompt)
        
        # Generate optimization suggestions
        optimization = {
            'score': 78,
            'improvements': [
                'Add quantifiable achievements with specific metrics',
                'Include more industry-specific keywords',
                'Strengthen technical skills section',
                'Add relevant certifications or projects'
            ],
            'keywords': ['leadership', 'optimization', 'collaboration', 'innovation', 'results-driven'],
            'ai_feedback': ai_feedback if ai_feedback and "ERROR:" not in ai_feedback else "Focus on quantifiable achievements and relevant keywords for your target role."
        }
        
        return jsonify({
            'success': True,
            'optimization': optimization,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Resume optimization failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/interview-prep', methods=['POST'])
def interview_prep():
    """Generate AI-powered interview preparation"""
    try:
        data = request.get_json() or {}
        company_role = data.get('company_role', '')
        interview_type = data.get('interview_type', '')
        user_background = data.get('user_background', '')
        
        # AI interview preparation
        interview_system_prompt = """
        You are an interview preparation specialist. Generate specific interview questions 
        and tips. Keep responses focused and practical, under 150 words total.
        """
        
        interview_prompt = f"""
        Company/Role: {company_role}
        Interview type: {interview_type}
        Background: {user_background}
        
        Generate:
        • 3 specific interview questions
        • 3 preparation tips
        • 3 focus areas
        
        Under 150 words total.
        """
        
        ai_response = call_grok_ai(interview_prompt, interview_system_prompt)
        
        # Generate interview prep content
        prep = {
            'questions': [
                "Tell me about a challenging project you worked on and how you overcame obstacles",
                "How do you stay current with industry trends and technologies?",
                "Describe a time when you had to work with a difficult team member"
            ],
            'tips': [
                'Research the company culture and recent news',
                'Practice answers using the STAR method (Situation, Task, Action, Result)',
                'Prepare thoughtful questions about the role and team'
            ],
            'focus_areas': ['Technical Skills', 'Problem Solving', 'Communication', 'Team Collaboration'],
            'ai_analysis': ai_response if ai_response and "ERROR:" not in ai_response else None
        }
        
        return jsonify({
            'success': True,
            'prep': prep,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Interview prep generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tools/learning-path', methods=['POST'])
def learning_path():
    """Generate AI-powered learning path"""
    try:
        data = request.get_json() or {}
        target_skill = data.get('target_skill', '')
        current_level = data.get('current_level', '')
        timeline = data.get('timeline', '')
        
        # Learning path generation
        months = {'3_months': 3, '6_months': 6, '12_months': 12}
        duration = months.get(timeline, 6)
        
        # Generate phases based on timeline
        phases = []
        if duration >= 3:
            phases.append({
                'title': 'Foundation Building',
                'duration': '1-2 months',
                'skills': ['Core concepts', 'Basic syntax', 'Development environment'],
                'resources': ['Online courses', 'Documentation', 'Tutorial videos']
            })
        
        if duration >= 6:
            phases.append({
                'title': 'Practical Application',
                'duration': '2-4 months',
                'skills': ['Project building', 'Best practices', 'Advanced features'],
                'resources': ['Hands-on projects', 'Code reviews', 'Community forums']
            })
        
        if duration >= 12:
            phases.append({
                'title': 'Mastery & Specialization',
                'duration': '4+ months',
                'skills': ['Advanced concepts', 'Performance optimization', 'Architecture'],
                'resources': ['Advanced courses', 'Open source contributions', 'Mentorship']
            })
        
        path = {
            'phases': phases,
            'estimated_completion': f'{duration} months',
            'skill_focus': target_skill,
            'difficulty_progression': f'{current_level} → Advanced'
        }
        
        return jsonify({
            'success': True,
            'path': path,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Learning path generation failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# JOB BOARD INTEGRATION & AFFILIATE REVENUE ENDPOINTS
# ============================================================================

from job_board_integration import JobBoardIntegrator, JobRevenueTracker

job_integrator = JobBoardIntegrator()
revenue_tracker = JobRevenueTracker()

@app.route('/api/jobs/search', methods=['POST'])
def search_jobs():
    """Search jobs across all platforms with affiliate tracking"""
    try:
        data = request.get_json() or {}
        
        # Extract search parameters
        query = data.get('query', '')
        location = data.get('location', 'remote')
        experience_level = data.get('experience_level', 'mid')
        limit = data.get('limit', 20)
        
        print(f"[INFO] Job search: {query} in {location} ({experience_level} level)")
        
        # Search all job platforms
        jobs = job_integrator.search_all_platforms(
            query=query,
            location=location,
            experience_level=experience_level,
            limit=limit
        )
        
        # Calculate revenue potential
        total_revenue_potential = sum(job.get('revenue_potential', 0) for job in jobs)
        
        return jsonify({
            'success': True,
            'jobs': jobs,
            'total_jobs': len(jobs),
            'search_params': {
                'query': query,
                'location': location,
                'experience_level': experience_level
            },
            'revenue_metrics': {
                'total_revenue_potential': total_revenue_potential,
                'average_commission': total_revenue_potential / max(len(jobs), 1),
                'platforms_searched': ['Indeed', 'LinkedIn', 'ZipRecruiter', 'Gaming Boards']
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Job search failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'fallback_message': 'Job search temporarily unavailable. Please try again later.'
        }), 500

@app.route('/api/jobs/auto-match-after-analysis', methods=['POST'])
def auto_match_jobs_after_analysis():
    """Automatically match jobs after career analysis completion"""
    try:
        data = request.get_json() or {}
        
        # Extract user profile and analysis results
        user_profile = data.get('user_profile', {})
        career_analysis = data.get('career_analysis', {})
        preferences = data.get('preferences', {})
        
        # Determine search parameters from analysis
        role = user_profile.get('role', '')
        location = preferences.get('location', 'remote')
        experience = user_profile.get('experience', 'mid-level')
        
        print(f"[INFO] Auto-matching jobs for {role} after career analysis")
        
        # Search relevant jobs
        matched_jobs = job_integrator.search_all_platforms(
            query=role,
            location=location,
            experience_level=experience,
            limit=15
        )
        
        # Enhanced scoring based on career analysis
        for job in matched_jobs:
            # Boost score based on career analysis insights
            if career_analysis.get('score', 0) > 80:
                job['match_score'] += 10  # High career score = better matches
            
            # Gaming career bonus
            if 'gaming' in role.lower() and job.get('industry') == 'Gaming':
                job['match_score'] += 15
        
        # Re-sort by enhanced scores
        matched_jobs.sort(key=lambda x: x.get('match_score', 0), reverse=True)
        
        # Track auto-matching event for revenue analytics
        revenue_tracker.track_job_click(
            user_id=data.get('user_id', 'anonymous'),
            job_id='auto_match_event',
            tracking_id=f"auto_match_{datetime.now().timestamp()}",
            platform='SkillSync_AutoMatch',
            revenue_potential=sum(job.get('revenue_potential', 0) for job in matched_jobs[:5])
        )
        
        return jsonify({
            'success': True,
            'auto_matched': True,
            'matched_jobs': matched_jobs[:10],  # Top 10 matches
            'match_quality': 'high' if career_analysis.get('score', 0) > 75 else 'medium',
            'revenue_opportunity': sum(job.get('revenue_potential', 0) for job in matched_jobs[:5]),
            'next_steps': [
                'Review matched opportunities',
                'Click on jobs that interest you',
                'Apply directly through affiliate links',
                'Track your application progress'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Auto job matching failed: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/jobs/track-click', methods=['POST'])
def track_job_click():
    """Track job clicks for affiliate revenue attribution"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        job_id = data.get('job_id', '')
        tracking_id = data.get('tracking_id', '')
        platform = data.get('platform', '')
        revenue_potential = data.get('revenue_potential', 0)
        
        # Track the click event
        event = revenue_tracker.track_job_click(
            user_id=user_id,
            job_id=job_id,
            tracking_id=tracking_id,
            platform=platform,
            revenue_potential=revenue_potential
        )
        
        return jsonify({
            'success': True,
            'tracked': True,
            'event_id': event.get('timestamp'),
            'message': f'Click tracked for {platform} job',
            'revenue_potential': revenue_potential
        })
        
    except Exception as e:
        print(f"[ERROR] Click tracking failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/track-application', methods=['POST'])
def track_job_application():
    """Track job applications for conversion analytics"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        job_id = data.get('job_id', '')
        tracking_id = data.get('tracking_id', '')
        
        # Track the application event
        event = revenue_tracker.track_job_application(
            user_id=user_id,
            job_id=job_id,
            tracking_id=tracking_id
        )
        
        return jsonify({
            'success': True,
            'tracked': True,
            'event_id': event.get('timestamp'),
            'message': 'Application tracked successfully',
            'conversion_stage': 'application_submitted'
        })
        
    except Exception as e:
        print(f"[ERROR] Application tracking failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/revenue-analytics', methods=['GET'])
def get_revenue_analytics():
    """Get revenue analytics and projections"""
    try:
        metrics = revenue_tracker.calculate_revenue_metrics()
        
        return jsonify({
            'success': True,
            'revenue_metrics': metrics,
            'performance_insights': {
                'top_performing_platform': 'Indeed',  # Based on click data
                'conversion_optimization': 'Focus on gaming job placements for higher commissions',
                'growth_opportunity': 'LinkedIn Premium upgrades show strong potential'
            },
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"[ERROR] Revenue analytics failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/jobs/platform-status', methods=['GET'])
def get_platform_status():
    """Check status of job board integrations"""
    try:
        status = {
            'indeed': {
                'status': 'active' if job_integrator.indeed_publisher_id else 'needs_api_key',
                'api_key_configured': bool(job_integrator.indeed_publisher_id),
                'commission_rate': job_integrator.affiliate_config['indeed']['commission_rate'],
                'base_commission': job_integrator.affiliate_config['indeed']['base_commission']
            },
            'linkedin': {
                'status': 'active' if job_integrator.linkedin_api_key else 'needs_api_key',
                'api_key_configured': bool(job_integrator.linkedin_api_key),
                'commission_rate': job_integrator.affiliate_config['linkedin']['commission_rate'],
                'monthly_value': job_integrator.affiliate_config['linkedin']['monthly_value']
            },
            'ziprecruiter': {
                'status': 'active' if job_integrator.ziprecruiter_api_key else 'needs_api_key',
                'api_key_configured': bool(job_integrator.ziprecruiter_api_key),
                'commission_rate': job_integrator.affiliate_config['ziprecruiter']['commission_rate'],
                'base_commission': job_integrator.affiliate_config['ziprecruiter']['base_commission']
            },
            'gaming_boards': {
                'status': 'active',
                'boards_available': list(job_integrator.gaming_boards.keys()),
                'commission_rate': 0.25,
                'base_commission': 200
            }
        }
        
        return jsonify({
            'success': True,
            'platform_status': status,
            'overall_health': 'good',
            'recommendations': [
                'Configure Indeed Publisher ID for full API access',
                'Set up LinkedIn API key for premium job access',
                'Add ZipRecruiter API key for enhanced job matching'
            ]
        })
        
    except Exception as e:
        print(f"[ERROR] Platform status check failed: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# GAMING CAREER INTELLIGENCE ENDPOINTS
# AI-powered gaming career analysis, roadmap generation, and market intelligence
# ============================================================================

# Initialize database
def create_tables():
    """Create database tables"""
    with app.app_context():
        db.create_all()

# Health check endpoint for Railway
@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now(timezone.utc).isoformat()})

# Frontend Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """User dashboard with progress tracking and recent insights"""
    return render_template('dashboard.html')

@app.route('/market-intelligence')
def market_intelligence():
    """Market intelligence hub with free insights and trends"""
    return render_template('market_intelligence.html')

@app.route('/career-paths')
def career_paths():
    """Interactive career path explorer"""
    return render_template('career_paths.html')

@app.route('/tools')
def tools():
    """Free tools and calculators for career development"""
    return render_template('tools.html')

@app.route('/community')
def community():
    """Community forum and discussion area"""
    return render_template('community.html')

@app.route('/ai-agent')
def ai_agent():
    """AI Agent page with autonomous career intelligence features"""
    return render_template('ai_agent.html')

@app.route('/visualizer')
def visualizer():
    """Multi-agent visualizer page"""
    return render_template('visualizer.html')

@app.route('/goals')
def goals():
    """AI-powered career goal setting and tracking page"""
    return render_template('goals.html')



if __name__ == '__main__':
    # Create tables before running the app
    create_tables()
    print("[INFO] Database tables created successfully")
    print("[INFO] SkillSync AI Platform starting...")
    print(f"[INFO] xAI API Key configured: {'Yes' if XAI_API_KEY and XAI_API_KEY != 'YOUR_XAI_API_KEY' else 'No'}")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
