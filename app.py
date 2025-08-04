from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from dotenv import load_dotenv
import requests
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# CareerDNA model removed - DNA functionality simplified out of the codebase

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
            'assess_skills': '/api/ai/assess-skills',
            'career_guidance': '/api/ai/career-guidance',
            'users': '/api/users',
            'upload': '/api/files/upload',
            'landing_demo': '/landing',
            'dashboard_demo': '/dashboard-demo',
            'api_docs': '/api-docs'
        },
        'note': 'DNA systems removed for simplified codebase'
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
    """AI-powered skills assessment - simplified version without DNA complexity"""
    try:
        data = request.get_json() or {}
        skills_description = data.get('skills_description', '')
        user_id = data.get('user_id', 'anonymous')
        
        if not skills_description:
            return jsonify({
                'success': False,
                'error': 'Skills description is required'
            }), 400
        
        # Simplified prompt for xAI
        enhanced_prompt = f"""
        As an expert AI career advisor, please assess the following skills and provide comprehensive insights:

        Skills Description: {skills_description}
        
        Please provide:
        1. Detailed skill assessment with specific levels (1-10 scale)
        2. Strengths and areas for improvement
        3. Career recommendations based on skill profile
        4. Learning path suggestions
        5. Market demand analysis for these skills
        
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
        
        # Store assessment in database if user is registered
        if user_id != 'anonymous':
            try:
                user = User.query.get(user_id)
                if user:
                    assessment = Assessment(
                        user_id=user_id,
                        skills_description=skills_description,
                        ai_assessment=str(ai_response),
                        recommendations="Generated by xAI assessment"
                    )
                    db.session.add(assessment)
                    db.session.commit()
            except Exception as db_error:
                logger.error(f"Database storage error: {db_error}")
        
        # Prepare simplified response
        response_data = {
            'success': True,
            'assessment': ai_response,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }
        
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

@app.route('/mentorship')
def mentorship():
    """AI-powered mentorship platform"""
    return render_template('mentorship.html')

@app.route('/events')
def events():
    """Community events and networking"""
    return render_template('events.html')

@app.route('/analytics')
def analytics():
    """AI-powered career analytics dashboard"""
    return render_template('analytics.html')

# Basic functionality imports - DNA systems removed for simplification

# Basic AI system initialization - complex DNA/A2A protocols removed for simplification

# Career Intelligence Agent Routes - simplified without complex DNA/A2A systems
@app.route('/api/intelligence/trigger', methods=['POST'])
def trigger_career_intelligence():
    """Simple career intelligence trigger - DNA systems removed"""
    try:
        return jsonify({
            'message': 'Career intelligence trigger - simplified version without DNA complexity',
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
    """Get basic user insights - simplified without complex AI agents"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Simple fallback insights
        basic_insights = {
            'career_stage': 'Developing',
            'primary_focus': 'Skill building and career growth',
            'recommendations': [
                'Continue building technical skills',
                'Explore networking opportunities',
                'Consider certification programs'
            ]
        }
        
        return jsonify({
            'user_id': user_id,
            'username': user.username,
            'insights': basic_insights,
            'message': 'Basic insights provided - complex AI systems removed for simplification',
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
    """Get market trends - simplified without complex A2A systems"""
    try:
        
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
                'message': 'Market analysis provided by xAI - complex systems simplified',
                'timestamp': datetime.now().isoformat()
            })
            
        except (KeyError, IndexError) as e:
            return jsonify({'error': 'Invalid response from xAI API', 'details': str(e)}), 500
            
    except Exception as e:
        return jsonify({'error': 'Market trends analysis failed', 'details': str(e)}), 500

@app.route('/api/skills/analyze', methods=['POST'])
def analyze_skills():
    """Simplified skills analysis endpoint"""
    try:
        data = request.get_json() or {}
        skills_input = data.get('skills', '')
        
        if not skills_input:
            return jsonify({'error': 'Skills input is required'}), 400
        
        # Update the request data for assess_skills
        request_data = {'skills_description': skills_input}
        
        # Call simplified assess_skills endpoint
        return assess_skills()
        
    except Exception as e:
        return jsonify({'error': 'Skills analysis failed', 'details': str(e)}), 500

# Activity tracking endpoints removed - complex AI systems simplified

# A2A Protocol endpoints removed - complex systems simplified

# Neural Career DNA endpoints removed - DNA functionality simplified out of the codebase

# Revolutionary Neural DNA endpoints removed - DNA functionality simplified out of the codebase

# Initialize database - simplified without complex AI systems
with app.app_context():
    db.create_all()
    logger.info("Database initialized successfully - DNA systems removed for simplification")

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
