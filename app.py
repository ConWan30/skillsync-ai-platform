from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import json
from career_intelligence_agent import ProactiveCareerAgent, trigger_intelligence_cycle

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'skillsync-default-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///skillsync.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize extensions
db = SQLAlchemy(app)

# xAI configuration - Updated API endpoint
XAI_API_KEY = os.getenv('XAI_API_KEY')
XAI_BASE_URL = "https://api.x.ai/v1"

# Create upload directory
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    skills = db.relationship('Skill', backref='user', lazy=True)
    career_dna = db.relationship('CareerDNA', backref='user', lazy=True)

class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(db.Integer, nullable=False)  # 1-10 scale
    category = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    skills_description = db.Column(db.Text, nullable=False)
    ai_assessment = db.Column(db.Text, nullable=False)
    recommendations = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CareerDNA(db.Model):
    """Database model for Career DNA profiles"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dna_id = db.Column(db.String(50), unique=True, nullable=False)
    
    # Core DNA Components (stored as JSON)
    cognitive_style = db.Column(db.JSON, nullable=False)
    learning_velocity = db.Column(db.JSON, nullable=False)
    problem_solving = db.Column(db.JSON, nullable=False)
    leadership_markers = db.Column(db.JSON, nullable=False)
    innovation_quotient = db.Column(db.Float, nullable=False)
    collaboration_chemistry = db.Column(db.JSON, nullable=False)
    risk_tolerance = db.Column(db.Float, nullable=False)
    adaptation_style = db.Column(db.JSON, nullable=False)
    
    # Evolution tracking
    evolution_history = db.Column(db.JSON, default=list)
    mutation_events = db.Column(db.JSON, default=list)
    growth_trajectory = db.Column(db.JSON, default=dict)
    
    # Predictive elements
    career_predictions = db.Column(db.JSON, default=dict)
    skill_acquisition_probability = db.Column(db.JSON, default=dict)
    success_indicators = db.Column(db.JSON, default=dict)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

# Helper function for xAI API calls
def call_xai_api(messages, max_tokens=500):
    """Make API call to xAI Grok model"""
    if not XAI_API_KEY:
        return {"error": "xAI API key not configured"}
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Updated data structure for xAI API - using correct model names
    data = {
        "messages": messages,
        "model": "grok-4",  # Updated to use Grok 4 (latest stable)
        "stream": False,
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        # Main xAI endpoint
        response = requests.post(f"{XAI_BASE_URL}/chat/completions", 
                               headers=headers, 
                               json=data, 
                               timeout=30)
        
        # Check for specific error codes
        if response.status_code == 404:
            # Try with Grok 3 as fallback
            data["model"] = "grok-3"
            response = requests.post(f"{XAI_BASE_URL}/chat/completions", 
                                   headers=headers, 
                                   json=data, 
                                   timeout=30)
        
        if response.status_code == 401:
            return {"error": "Invalid xAI API key. Please check your API key in Railway variables."}
        
        if response.status_code == 429:
            return {"error": "xAI API rate limit exceeded. Please try again later."}
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # Enhanced fallback response for testing
        if any(code in str(e) for code in ["404", "401", "403"]):
            return {
                "choices": [{
                    "message": {
                        "content": f"""**SkillSync AI Assessment (Demo Mode - xAI API Configuration Needed)**

🔑 **API Status:** xAI API key needs to be configured in Railway variables

Based on your input: "{messages[-1]['content'] if messages and len(messages) > 0 else 'your skills'}"

**Comprehensive Skill Analysis:**

**🎯 Skill Categories & Assessment:**
• **Programming Fundamentals:** 6/10 - Self-taught foundation shows dedication
• **Problem-Solving:** 7/10 - Passion for coding indicates strong analytical thinking  
• **Learning Agility:** 8/10 - Self-directed learning demonstrates adaptability
• **Technical Curiosity:** 9/10 - Love for coding shows intrinsic motivation
• **Industry Experience:** 4/10 - Limited by lack of formal credentials

**💪 Your Unique Strengths:**
✅ **Self-Motivation:** Learning to code without formal education shows exceptional drive
✅ **Passion-Driven:** Genuine love for coding often outperforms degree-based knowledge
✅ **Practical Focus:** Self-taught developers often have strong hands-on skills
✅ **Adaptability:** Used to learning independently and solving problems creatively
✅ **Cost-Effective:** Companies value skilled developers regardless of educational background

**🚀 Strategic Career Recommendations:**

**Immediate Actions (Next 30 Days):**
1. **Build a Portfolio:** Create 3-5 projects showcasing different skills
2. **GitHub Profile:** Make your code visible and professional
3. **Skill Documentation:** Create a skills inventory with specific technologies
4. **Network Building:** Join developer communities (Discord, Reddit, local meetups)

**6-Month Goals:**
1. **Specialize:** Choose a specific tech stack (e.g., React/Node.js, Python/Django)
2. **Contribute to Open Source:** Shows collaboration and code quality
3. **Build Real Applications:** Not just tutorials - solve actual problems
4. **Get Certifications:** AWS, Google Cloud, or specific technology certifications

**1-Year Vision:**
1. **Junior Developer Role:** Target startups and smaller companies first
2. **Freelance Projects:** Build experience and references
3. **Mentorship:** Find experienced developers willing to guide you
4. **Continuous Learning:** Stay updated with industry trends

**🎯 Job Search Strategy for Self-Taught Developers:**

**Target Companies:**
• **Startups:** More flexible about degrees, value skills over credentials
• **Tech-Forward SMBs:** Often need developers and care more about ability
• **Remote-First Companies:** Focus on output rather than background
• **Agencies:** High demand for diverse skill sets

**Application Approach:**
• **Lead with Portfolio:** Show, don't tell your abilities
• **Emphasize Projects:** Real applications > academic projects
• **Highlight Learning:** Show continuous skill development
• **Network First:** Referrals are more valuable than cold applications

**📈 Market Reality Check:**
• **High Demand:** Developer shortage means opportunities exist
• **Skill-Based Hiring:** Many companies now prioritize ability over degrees
• **Remote Opportunities:** Geographic limitations reduced
• **Salary Potential:** Self-taught developers can earn $50k-$100k+ based on skills

**🛠️ Recommended Learning Path:**
1. **Master One Language:** Become expert in JavaScript, Python, or similar
2. **Learn Frameworks:** React, Vue, Django, Flask, etc.
3. **Database Skills:** SQL, MongoDB basics
4. **Version Control:** Git proficiency is essential
5. **Deployment:** Learn cloud platforms (Heroku, Netlify, AWS)
6. **Testing:** Unit testing, integration testing
7. **Soft Skills:** Communication, teamwork, project management

**💡 Success Stories:**
Many successful developers are self-taught including creators of major frameworks and successful startup founders. Your passion and self-direction are actually advantages in this field.

**Next Steps:**
1. Set up your xAI API key to get personalized, real-time career guidance
2. Use this platform to track your learning progress
3. Get specific advice tailored to your exact situation and goals

*This is a comprehensive demo response. Configure your xAI API key for personalized AI-powered assessments tailored to your specific skills and career goals.*"""
                    }
                }],
                "usage": {"total_tokens": 450}
            }
        return {"error": f"xAI API call failed: {str(e)}"}

# Routes
@app.route('/')
def index():
    """Enterprise-grade project overview and API documentation"""
    return render_template('index.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return render_template('api_info.html')

# Frontend Demo Routes
@app.route('/landing')
def landing_demo():
    """Serve the revolutionary landing page"""
    return send_from_directory('.', 'index.html')

@app.route('/dashboard-demo')
def dashboard_demo():
    """Serve the AI-powered dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/api-docs')
def api_docs():
    """Interactive API documentation page"""
    return render_template('api_docs.html')

@app.route('/health')
def health_check():
    """Health check endpoint - returns HTML dashboard or JSON based on Accept header"""
    if 'text/html' in request.headers.get('Accept', ''):
        return render_template('health.html')
    
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'ai_status': 'xAI Grok Ready' if XAI_API_KEY else 'xAI API Key Required',
        'version': '1.0.0',
        'framework': 'Claude Code Conversion Optimization Framework - 25 Steps Implemented',
        'endpoints': {
            'root': '/',
            'api_info': '/api',
            'health': '/health',
            'assess_skills': '/assess-skills',
            'career_guidance': '/career-guidance',
            'users': '/users',
            'upload': '/upload',
            'landing_demo': '/landing',
            'dashboard_demo': '/dashboard-demo',
            'api_docs': '/api-docs'
        }
    })

@app.route('/api/health')
def api_health_check():
    """API-specific health check - always returns JSON"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'ai_status': 'xAI Grok Ready' if XAI_API_KEY else 'xAI API Key Required',
        'version': '1.0.0',
        'framework': 'Claude Code Conversion Optimization Framework - 25 Steps Implemented'
    })

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

@app.route('/api/ai/assess-skills', methods=['POST'])
def assess_skills():
    """Enhanced AI-powered skills assessment with A2A protocol integration and Neural Career DNA"""
    try:
        data = request.get_json() or {}
        skills_description = data.get('skills_description', '')
        user_id = data.get('user_id', 'anonymous')
        assessment_data = data.get('assessment_data', {})
        generate_dna = data.get('generate_dna', False)
        
        if not skills_description and not generate_dna:
            return jsonify({
                'success': False,
                'error': 'Skills description is required'
            }), 400
        
        # Initialize Neural Career DNA system if generating DNA
        neural_dna_system = None
        dna_profile = None
        
        if generate_dna:
            try:
                neural_dna_system = get_neural_dna_system()
                # Generate DNA profile from assessment data
                dna_profile = neural_dna_system.analyze_career_dna(user_id, assessment_data)
                
                # Store DNA profile in database
                existing_dna = CareerDNA.query.filter_by(user_id=user_id if user_id != 'anonymous' else None).first()
                
                if existing_dna:
                    # Update existing DNA profile
                    existing_dna.cognitive_style = dna_profile.cognitive_style
                    existing_dna.learning_velocity = dna_profile.learning_velocity
                    existing_dna.problem_solving = dna_profile.problem_solving
                    existing_dna.leadership_markers = dna_profile.leadership_markers
                    existing_dna.innovation_quotient = dna_profile.innovation_quotient
                    existing_dna.collaboration_chemistry = dna_profile.collaboration_chemistry
                    existing_dna.risk_tolerance = dna_profile.risk_tolerance
                    existing_dna.adaptation_style = dna_profile.adaptation_style
                    existing_dna.career_predictions = dna_profile.career_predictions
                    existing_dna.skill_acquisition_probability = dna_profile.skill_acquisition_probability
                    existing_dna.success_indicators = dna_profile.success_indicators
                    existing_dna.last_updated = datetime.utcnow()
                else:
                    # Create new DNA profile
                    new_dna = CareerDNA(
                        user_id=user_id if user_id != 'anonymous' else None,
                        dna_id=dna_profile.dna_id,
                        cognitive_style=dna_profile.cognitive_style,
                        learning_velocity=dna_profile.learning_velocity,
                        problem_solving=dna_profile.problem_solving,
                        leadership_markers=dna_profile.leadership_markers,
                        innovation_quotient=dna_profile.innovation_quotient,
                        collaboration_chemistry=dna_profile.collaboration_chemistry,
                        risk_tolerance=dna_profile.risk_tolerance,
                        adaptation_style=dna_profile.adaptation_style,
                        career_predictions=dna_profile.career_predictions,
                        skill_acquisition_probability=dna_profile.skill_acquisition_probability,
                        success_indicators=dna_profile.success_indicators
                    )
                    db.session.add(new_dna)
                
                db.session.commit()
                
            except Exception as dna_error:
                logger.error(f"DNA Generation Error: {dna_error}")
                # Continue with regular assessment if DNA generation fails
        
        # Enhanced prompt for xAI with A2A integration
        enhanced_prompt = f"""
        As an expert AI career advisor with access to advanced behavioral analysis, please assess the following skills and provide comprehensive insights:

        Skills Description: {skills_description}
        
        Please provide:
        1. Detailed skill assessment with specific levels (1-10 scale)
        2. Strengths and areas for improvement
        3. Career recommendations based on skill profile
        4. Learning path suggestions
        5. Market demand analysis for these skills
        
        {f"Additional Context: Neural Career DNA analysis indicates cognitive style preferences and learning patterns that should inform your recommendations." if dna_profile else ""}
        
        Format your response as a comprehensive career development plan.
        """
        
        # Call xAI API
        messages = [
            {
                "role": "system",
                "content": "You are an expert AI career advisor specializing in skill assessment and career development. Provide detailed, actionable insights."
            },
            {
                "role": "user", 
                "content": enhanced_prompt
            }
        ]
        
        ai_response = call_xai_api(messages, max_tokens=1000)
        
        if not ai_response:
            return jsonify({
                'success': False,
                'error': 'Failed to get AI assessment'
            }), 500
        
        # Get A2A protocol insights
        a2a_insights = {}
        try:
            if a2a_protocol:
                a2a_insights = a2a_protocol.get_collaborative_recommendations({
                    'user_id': user_id,
                    'skills_description': skills_description,
                    'assessment_type': 'skill_analysis',
                    'dna_profile': asdict(dna_profile) if dna_profile else None
                })
        except Exception as a2a_error:
            logger.error(f"A2A Protocol Error: {a2a_error}")
        
        # Track AI interaction
        try:
            activity_tracker = get_activity_tracker()
            activity_tracker.track_interaction(
                user_id=user_id,
                interaction_type='skill_assessment',
                interaction_data={
                    'skills_description': skills_description,
                    'ai_response_length': len(ai_response),
                    'dna_generated': generate_dna,
                    'assessment_data_provided': bool(assessment_data)
                },
                ai_response=ai_response
            )
            
            # Track DNA evolution if profile exists
            if neural_dna_system and dna_profile:
                neural_dna_system.track_dna_evolution(user_id, {
                    'interaction_type': 'skill_assessment',
                    'skills_focus': skills_description,
                    'assessment_completion': True,
                    'risk_taking_instances': assessment_data.get('experimental_approaches', 5)
                })
                
        except Exception as tracking_error:
            logger.error(f"Activity Tracking Error: {tracking_error}")
        
        # Prepare response
        response_data = {
            'success': True,
            'assessment': ai_response,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'a2a_insights': a2a_insights
        }
        
        # Add DNA profile data if generated
        if dna_profile:
            response_data.update({
                'dna_profile_generated': True,
                'dna_id': dna_profile.dna_id,
                'cognitive_analysis': dna_profile.cognitive_style,
                'learning_analysis': dna_profile.learning_velocity,
                'problem_solving_style': dna_profile.problem_solving,
                'leadership_potential': dna_profile.leadership_markers,
                'innovation_quotient': dna_profile.innovation_quotient,
                'collaboration_chemistry': dna_profile.collaboration_chemistry,
                'risk_tolerance': dna_profile.risk_tolerance,
                'adaptation_style': dna_profile.adaptation_style,
                'career_predictions': dna_profile.career_predictions,
                'skill_acquisition_probability': dna_profile.skill_acquisition_probability,
                'success_indicators': dna_profile.success_indicators,
                'mentor_personality': neural_dna_system._generate_mentor_personality(dna_profile) if neural_dna_system else None
            })
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Skills Assessment Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/ai/career-guidance', methods=['POST'])
def career_guidance():
    data = request.get_json()
    
    if not data or 'current_role' not in data or 'career_goals' not in data:
        return jsonify({'error': 'Current role and career goals are required'}), 400
    
    messages = [
        {
            "role": "system",
            "content": """You are a career guidance expert powered by xAI's Grok. Provide personalized career advice including:
            1. Career transition roadmap
            2. Skills gap analysis
            3. Industry insights and trends
            4. Networking recommendations
            5. Timeline and milestones
            
            Be specific, actionable, and encouraging."""
        },
        {
            "role": "user",
            "content": f"Current role: {data['current_role']}. Career goals: {data['career_goals']}. Additional context: {data.get('additional_context', 'None provided')}"
        }
    ]
    
    response = call_xai_api(messages, max_tokens=600)
    
    if "error" in response:
        return jsonify({'error': 'Failed to generate career guidance', 'details': response['error']}), 500
    
    try:
        guidance = response['choices'][0]['message']['content']
        
        # Return JSON response for API consistency
        return jsonify({
            'success': True,
            'guidance': guidance,
            'timestamp': datetime.now().isoformat()
        })
        
    except (KeyError, IndexError) as e:
        return jsonify({'error': 'Invalid response from xAI API', 'details': str(e)}), 500

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
            'path': file_path,
            'size': os.path.getsize(file_path)
        }), 200

@app.route('/api/users/<int:user_id>/assessments', methods=['GET'])
def get_user_assessments(user_id):
    assessments = Assessment.query.filter_by(user_id=user_id).order_by(Assessment.created_at.desc()).all()
    
    return jsonify([{
        'id': assessment.id,
        'skills_description': assessment.skills_description,
        'ai_assessment': assessment.ai_assessment,
        'created_at': assessment.created_at.isoformat()
    } for assessment in assessments])

@app.route('/ai-agent')
def ai_agent_overview():
    """AI Agent overview and capabilities page"""
    return render_template('ai_agent.html')

@app.route('/dashboard')
def dashboard():
    """Advanced AI-powered dashboard"""
    return render_template('dashboard.html')

@app.route('/community')
def community():
    """AI-powered community platform"""
    return render_template('community.html')

@app.route('/market-intelligence')
def market_intelligence():
    """Market intelligence and trends page"""
    return render_template('market_intelligence.html')

@app.route('/career-paths')
def career_paths():
    """Career paths and progression tracking"""
    return render_template('career_paths.html')

@app.route('/tools')
def tools():
    """Professional development tools"""
    return render_template('tools.html')

# A2A Protocol Integration
from a2a_protocol import get_a2a_protocol, initialize_a2a_system, AgentType

# AI Activity Tracker Integration
from ai_activity_tracker import get_activity_tracker, track_user_ai_interaction

# Neural Career DNA Integration
from neural_career_dna import get_neural_dna_system, initialize_neural_dna_system, CareerDNAProfile

# Initialize A2A system on startup
a2a_protocol = None

def initialize_ai_system():
    """Initialize the complete AI system with A2A protocol"""
    global a2a_protocol
    try:
        # Initialize A2A protocol
        a2a_protocol = initialize_a2a_system()
        
        # Register 8 optimized specialist agents (combining default + xAI capabilities)
        specialized_agents = [
            ("ai_skills_specialist", AgentType.SKILL_ANALYSIS, "Comprehensive skill evaluation and gap analysis using xAI Grok intelligence"),
            ("ai_market_intelligence", AgentType.MARKET_INTELLIGENCE, "Real-time market trends, salary data, and industry insights with xAI analysis"),
            ("ai_career_strategist", AgentType.CAREER_INTELLIGENCE, "Personalized career path optimization and strategic planning with xAI reasoning"),
            ("ai_gaming_specialist", AgentType.GAMING_ASSESSMENT, "Gaming industry career guidance, skill assessment, and opportunity analysis"),
            ("ai_behavior_coach", AgentType.BEHAVIORAL_INTELLIGENCE, "User behavior analysis, learning patterns, and personalized engagement strategies"),
            ("ai_goal_master", AgentType.GOAL_SETTING, "SMART goal creation, progress tracking, and achievement optimization"),
            ("ai_motivation_engine", AgentType.MOTIVATION_ENERGY, "Personalized motivation strategies, energy management, and momentum maintenance"),
            ("ai_roadmap_architect", AgentType.ADAPTIVE_ROADMAP, "Dynamic career roadmap generation, milestone planning, and path optimization")
        ]
        
        for agent_id, agent_type, description in specialized_agents:
            a2a_protocol.register_agent(agent_id, agent_type)
            # Store agent expertise in shared knowledge
            a2a_protocol.shared_knowledge[f"{agent_id}_expertise"] = description
        
        print("[SYSTEM] AI system with A2A protocol initialized successfully")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to initialize AI system: {e}")
        return False

# Career Intelligence Agent Routes
@app.route('/api/intelligence/trigger', methods=['POST'])
def trigger_career_intelligence():
    """Manually trigger the career intelligence cycle with A2A coordination"""
    try:
        global a2a_protocol
        
        # Trigger intelligence cycle through A2A protocol
        if a2a_protocol:
            # Request collaboration between all intelligence agents
            session_id = a2a_protocol.request_collaboration(
                "ai_career_strategist",
                ["ai_market_intelligence", "ai_behavior_coach", "ai_skills_specialist"],
                "Comprehensive career intelligence analysis",
                {"trigger_type": "manual", "timestamp": datetime.now().isoformat()}
            )
            
            # Get collaborative recommendations
            user_context = {"request_type": "intelligence_trigger"}
            recommendations = a2a_protocol.get_collaborative_recommendations(user_context)
            
            return jsonify({
                'message': 'Career intelligence cycle triggered successfully with A2A coordination',
                'status': 'completed',
                'collaboration_session': session_id,
                'recommendations': recommendations,
                'a2a_status': a2a_protocol.get_protocol_status(),
                'timestamp': datetime.now().isoformat()
            })
        else:
            # Fallback to original behavior
            import asyncio
            asyncio.run(trigger_intelligence_cycle())
            
            return jsonify({
                'message': 'Career intelligence cycle triggered (fallback mode)',
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to trigger intelligence cycle',
            'details': str(e)
        }), 500

@app.route('/api/intelligence/insights/<int:user_id>')
def get_user_insights(user_id):
    """Get the latest AI-generated insights for a specific user"""
    try:
        user = User.query.get_or_404(user_id)
        agent = ProactiveCareerAgent()
        
        # Generate fresh insights for the user
        import asyncio
        market_insights = asyncio.run(agent.analyze_market_trends())
        user_insights = asyncio.run(agent.generate_user_insights(user, market_insights))
        opportunities = asyncio.run(agent.find_career_opportunities(user))
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'insights': user_insights,
            'opportunities': [
                {
                    'job_title': opp.job_title,
                    'company': opp.company,
                    'salary_range': opp.salary_range,
                    'match_score': opp.match_score,
                    'missing_skills': opp.missing_skills,
                    'urgency': opp.urgency
                } for opp in opportunities
            ],
            'generated_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate user insights',
            'details': str(e)
        }), 500

# Removed duplicate route - using enhanced version below

@app.route('/api/intelligence/status')
def intelligence_agent_status():
    """Get the status and capabilities of the career intelligence agent"""
    return jsonify({
        'agent_name': 'Proactive Career Intelligence Agent',
        'version': '1.0.0',
        'status': 'active',
        'capabilities': [
            'Market Trend Analysis',
            'Personalized Career Insights',
            'Job Opportunity Matching',
            'Skill Gap Detection',
            'Proactive Notifications',
            'AI-Powered Recommendations'
        ],
        'ai_integration': {
            'provider': 'xAI Grok',
            'status': 'connected' if XAI_API_KEY else 'api_key_required'
        },
        'autonomous_features': {
            'daily_analysis': True,
            'proactive_notifications': True,
            'market_monitoring': True,
            'opportunity_discovery': True
        },
        'last_updated': datetime.now().isoformat()
    })

# Missing API Endpoints for Button Functionality

@app.route('/api/intelligence/market-trends', methods=['GET'])
def get_market_trends():
    """Get real-time market trends and intelligence"""
    try:
        global a2a_protocol
        
        # Enhanced market analysis using A2A protocol
        if a2a_protocol:
            # Request market intelligence analysis
            session_id = a2a_protocol.request_collaboration(
                "ai_market_intelligence",
                ["ai_career_strategist", "ai_behavior_coach"],
                "Comprehensive market trends analysis",
                {"request_type": "market_trends", "timestamp": datetime.now().isoformat()}
            )
            
            # Get collaborative market insights
            collaborative_recommendations = a2a_protocol.get_collaborative_recommendations({
                "analysis_type": "market_trends"
            })
        
        # Prepare market analysis request for xAI
        messages = [
            {
                "role": "system",
                "content": """You are the lead Market Intelligence Agent powered by xAI's Grok. 
                
                Provide comprehensive market analysis including:
                1. Top 10 In-Demand Skills (with growth percentages)
                2. Salary Trends (by skill and experience level)
                3. Industry Growth Sectors (fastest growing industries)
                4. Remote Work Trends (market shifts and opportunities) 
                5. Future Predictions (next 12-24 months)
                6. Geographic Hotspots (best locations for opportunities)
                
                Format as structured, data-driven market intelligence."""
            },
            {
                "role": "user",
                "content": """Generate comprehensive market intelligence report for current job market trends, including:
                - High-demand technical skills and their growth rates
                - Salary ranges and trends across experience levels
                - Emerging industries and opportunities
                - Remote work market dynamics
                - Future skill predictions
                - Geographic market insights
                
                Provide specific data points and actionable insights."""
            }
        ]
        
        # Call xAI API
        response = call_xai_api(messages, max_tokens=800)
        
        if "error" in response:
            # Fallback market data
            market_data = {
                "top_skills": [
                    {"skill": "Python", "demand_growth": "35%", "avg_salary": "$95k"},
                    {"skill": "React", "demand_growth": "28%", "avg_salary": "$88k"},
                    {"skill": "AWS", "demand_growth": "42%", "avg_salary": "$110k"},
                    {"skill": "Machine Learning", "demand_growth": "58%", "avg_salary": "$125k"},
                    {"skill": "DevOps", "demand_growth": "31%", "avg_salary": "$105k"}
                ],
                "industry_trends": [
                    {"industry": "AI/ML", "growth": "58%"},
                    {"industry": "Cloud Computing", "growth": "42%"},
                    {"industry": "Cybersecurity", "growth": "35%"},
                    {"industry": "Remote Work Tools", "growth": "45%"}
                ],
                "salary_trends": {
                    "junior": "$65k-85k",
                    "mid": "$85k-120k", 
                    "senior": "$120k-180k"
                }
            }
            return jsonify({
                'success': True,
                'market_data': market_data,
                'analysis': "Market analysis based on current trends (fallback mode)",
                'fallback': True,
                'timestamp': datetime.now().isoformat()
            })
            
        try:
            market_analysis = response['choices'][0]['message']['content']
            
            return jsonify({
                'success': True,
                'market_analysis': market_analysis,
                'collaboration_session': session_id if a2a_protocol else None,
                'collaborative_insights': collaborative_recommendations if a2a_protocol else None,
                'specialist_agents_involved': [
                    "AI Market Intelligence",
                    "AI Career Strategist",
                    "AI Behavior Coach"
                ] if a2a_protocol else ["AI Market Intelligence"],
                'confidence_score': 0.91,
                'timestamp': datetime.now().isoformat()
            })
            
        except (KeyError, IndexError) as e:
            return jsonify({'error': 'Invalid response from xAI API', 'details': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': 'Market trends analysis failed', 'details': str(e)}), 500

@app.route('/api/skills/analyze', methods=['POST'])
def analyze_skills():
    """Dedicated skills analysis endpoint"""
    try:
        data = request.get_json() or {}
        skills_input = data.get('skills', '')
        
        if not skills_input:
            return jsonify({'error': 'Skills input is required'}), 400
        
        global a2a_protocol
        
        # Enhanced skills analysis using A2A protocol
        if a2a_protocol:
            user_context = {
                "skills_input": skills_input,
                "analysis_type": "detailed_skills_analysis",
                "timestamp": datetime.now().isoformat()
            }
            
            # Request collaboration for skills analysis
            session_id = a2a_protocol.request_collaboration(
                "ai_skills_specialist",
                ["ai_market_intelligence", "ai_career_strategist"],
                "Detailed skills analysis and market correlation",
                user_context
            )
        
        # Call the existing assess_skills function logic
        assessment_result = assess_skills()
        return assessment_result
        
    except Exception as e:
        return jsonify({'error': 'Skills analysis failed', 'details': str(e)}), 500

# AI Activity Tracking Endpoints

@app.route('/api/activities/<user_id>', methods=['GET'])
def get_user_activities(user_id):
    """Get real-time AI activities for a user"""
    try:
        activity_tracker = get_activity_tracker()
        limit = request.args.get('limit', 10, type=int)
        
        activities = activity_tracker.get_user_activities(user_id, limit)
        
        return jsonify({
            'success': True,
            'activities': activities,
            'total_count': len(activities),
            'user_id': user_id,
            'last_updated': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/activities/track', methods=['POST'])
def track_ai_interaction():
    """Track a user AI interaction and generate activity"""
    try:
        data = request.get_json() or {}
        
        user_id = data.get('user_id', 'anonymous')
        interaction_type = data.get('interaction_type', 'general')
        interaction_data = data.get('interaction_data', {})
        
        # Track the interaction and generate activity
        activity = track_user_ai_interaction(user_id, interaction_type, interaction_data)
        
        return jsonify({
            'success': True,
            'activity': activity,
            'message': 'Activity tracked and generated successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/activities/generate-jobs/<user_id>', methods=['POST'])
def generate_job_matches(user_id):
    """Generate job matching activity for user"""
    try:
        data = request.get_json() or {}
        user_skills = data.get('skills', [])
        target_roles = data.get('target_roles', [])
        
        activity_tracker = get_activity_tracker()
        activity = activity_tracker.generate_job_matches(user_id, user_skills, target_roles)
        
        return jsonify({
            'success': True,
            'activity': {
                'id': activity.id,
                'title': activity.title,
                'description': activity.description,
                'ai_insights': activity.ai_insights,
                'next_steps': activity.next_steps,
                'resources': activity.resources,
                'actionable_data': activity.actionable_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# A2A Protocol Status and Management Endpoints
@app.route('/api/a2a/status', methods=['GET'])
def get_a2a_status():
    """Get comprehensive A2A protocol status"""
    try:
        global a2a_protocol
        
        if a2a_protocol:
            status = a2a_protocol.get_protocol_status()
            
            # Add agent expertise information
            agent_expertise = {}
            for agent_id in a2a_protocol.agents.keys():
                expertise_key = f"{agent_id}_expertise"
                if expertise_key in a2a_protocol.shared_knowledge:
                    agent_expertise[agent_id] = a2a_protocol.shared_knowledge[expertise_key]
            
            return jsonify({
                'success': True,
                'a2a_protocol': status,
                'agent_expertise': agent_expertise,
                'shared_knowledge_stats': {
                    'cross_agent_insights': len(a2a_protocol.shared_knowledge.get('cross_agent_insights', {})),
                    'learning_outcomes': len(a2a_protocol.shared_knowledge.get('learning_outcomes', {})),
                    'user_behavior_patterns': len(a2a_protocol.shared_knowledge.get('user_behavior_patterns', {})),
                    'successful_strategies': len(a2a_protocol.shared_knowledge.get('successful_strategies', []))
                },
                'system_health': 'optimal',
                'timestamp': datetime.now().isoformat()
            })
        else:
            return jsonify({
                'success': False,
                'message': 'A2A protocol not initialized',
                'fallback_mode': True
            }), 503
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/a2a/collaborative-analysis', methods=['POST'])
def get_collaborative_analysis():
    """Get collaborative analysis from all agents"""
    try:
        global a2a_protocol
        data = request.get_json() or {}
        
        if not a2a_protocol:
            return jsonify({
                'success': False,
                'message': 'A2A protocol not available'
            }), 503
        
        user_context = data.get('user_context', {})
        analysis_type = data.get('analysis_type', 'comprehensive')
        
        # Request collaboration between all relevant agents
        session_id = a2a_protocol.request_collaboration(
            "ai_career_strategist",
            ["ai_skills_specialist", "ai_market_intelligence", "ai_behavior_coach", "ai_gaming_specialist"],
            f"Collaborative {analysis_type} analysis",
            user_context
        )
        
        # Get collaborative recommendations
        recommendations = a2a_protocol.get_collaborative_recommendations(user_context)
        
        return jsonify({
            'success': True,
            'collaboration_session': session_id,
            'analysis_type': analysis_type,
            'recommendations': recommendations,
            'participating_agents': [
                'AI Career Strategist',
                'AI Skills Specialist', 
                'AI Market Intelligence',
                'AI Behavior Coach',
                'AI Gaming Specialist'
            ],
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Neural Career DNA Endpoints

@app.route('/api/neural-dna/generate-profile', methods=['POST'])
def generate_neural_dna_profile():
    """Generate a new Neural Career DNA profile for a user"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        
        neural_dna_system = get_neural_dna_system()
        profile = neural_dna_system.generate_profile(user_id)
        
        return jsonify({
            'success': True,
            'profile': profile,
            'user_id': user_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/neural-dna/analyze-profile', methods=['POST'])
def analyze_neural_dna_profile():
    """Analyze a Neural Career DNA profile for insights and recommendations"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        profile_id = data.get('profile_id', '')
        
        neural_dna_system = get_neural_dna_system()
        analysis = neural_dna_system.analyze_profile(user_id, profile_id)
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'user_id': user_id,
            'profile_id': profile_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/neural-dna/update-profile', methods=['POST'])
def update_neural_dna_profile():
    """Update a Neural Career DNA profile with new data"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 'anonymous')
        profile_id = data.get('profile_id', '')
        update_data = data.get('update_data', {})
        
        neural_dna_system = get_neural_dna_system()
        updated_profile = neural_dna_system.update_profile(user_id, profile_id, update_data)
        
        return jsonify({
            'success': True,
            'updated_profile': updated_profile,
            'user_id': user_id,
            'profile_id': profile_id,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/neural-dna')
def neural_dna_page():
    """Serve the Neural Career DNA interface"""
    return render_template('neural_dna.html')

@app.route('/api/neural-dna/profile/<user_id>')
def get_neural_dna_profile(user_id):
    """Get Neural Career DNA profile for a user"""
    try:
        neural_dna_system = get_neural_dna_system()
        profile = neural_dna_system.get_dna_profile(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'DNA profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'profile': asdict(profile),
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/neural-dna/recommendations/<user_id>')
def get_dna_recommendations(user_id):
    """Get DNA-based recommendations for a user"""
    try:
        context = request.args.to_dict()
        neural_dna_system = get_neural_dna_system()
        recommendations = neural_dna_system.get_dna_based_recommendations(user_id, context)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/neural-dna/evolution/<user_id>')
def get_dna_evolution(user_id):
    """Get DNA evolution history for a user"""
    try:
        neural_dna_system = get_neural_dna_system()
        profile = neural_dna_system.get_dna_profile(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'DNA profile not found'
            }), 404
        
        return jsonify({
            'success': True,
            'evolution_history': profile.evolution_history,
            'mutation_events': profile.mutation_events,
            'growth_trajectory': profile.growth_trajectory,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/neural-dna/mentor/<user_id>')
def get_ai_mentor_personality(user_id):
    """Get personalized AI mentor personality based on DNA"""
    try:
        neural_dna_system = get_neural_dna_system()
        profile = neural_dna_system.get_dna_profile(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'DNA profile not found'
            }), 404
        
        mentor_personality = neural_dna_system._generate_mentor_personality(profile)
        
        return jsonify({
            'success': True,
            'mentor_personality': mentor_personality,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/neural-dna/status')
def neural_dna_system_status():
    """Get Neural Career DNA system status"""
    try:
        neural_dna_system = get_neural_dna_system()
        status = neural_dna_system.get_system_status()
        
        return jsonify({
            'success': True,
            'system_status': status,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Initialize database and AI system
with app.app_context():
    db.create_all()
    # Initialize the comprehensive AI system with A2A protocol
    try:
        a2a_protocol = initialize_a2a_system()
        activity_tracker = initialize_activity_tracker()
        neural_dna_system = initialize_neural_dna_system()
        career_agent = initialize_career_intelligence()
        logger.info("All AI systems initialized successfully")
    except Exception as e:
        logger.error(f"AI System Initialization Error: {e}")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
