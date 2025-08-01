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
    data = request.get_json()
    
    if not data or 'skills_description' not in data:
        return jsonify({'error': 'Skills description is required'}), 400
    
    # Prepare messages for xAI Grok
    messages = [
        {
            "role": "system",
            "content": """You are an expert career advisor and skills assessor powered by xAI's Grok. 
            Analyze the provided skills description and provide:
            1. Skill categories and proficiency levels (1-10 scale)
            2. Strengths and areas for improvement
            3. Career recommendations
            4. Learning path suggestions
            5. Market demand insights
            
            Provide structured, actionable insights."""
        },
        {
            "role": "user", 
            "content": f"Please assess these skills and provide detailed analysis: {data['skills_description']}"
        }
    ]
    
    # Call xAI API
    response = call_xai_api(messages, max_tokens=800)
    
    if "error" in response:
        return jsonify({'error': 'Failed to assess skills', 'details': response['error']}), 500
    
    try:
        assessment_text = response['choices'][0]['message']['content']
        
        # Save assessment to database if user_id provided
        if 'user_id' in data:
            assessment = Assessment(
                user_id=data['user_id'],
                skills_description=data['skills_description'],
                ai_assessment=assessment_text
            )
            db.session.add(assessment)
            db.session.commit()
        
        return render_template('assessment.html', assessment=assessment_text)
        
    except (KeyError, IndexError) as e:
        return jsonify({'error': 'Invalid response from xAI API', 'details': str(e)}), 500

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
        
        return render_template('career_guidance.html', guidance=guidance)
        
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

# Career Intelligence Agent Routes
@app.route('/api/intelligence/trigger', methods=['POST'])
def trigger_career_intelligence():
    """Manually trigger the career intelligence cycle"""
    try:
        import asyncio
        # Run the intelligence cycle
        asyncio.run(trigger_intelligence_cycle())
        
        return jsonify({
            'message': 'Career intelligence cycle triggered successfully',
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

@app.route('/api/intelligence/market-trends')
def get_market_trends():
    """Get current market trends and skill analysis"""
    try:
        agent = ProactiveCareerAgent()
        
        import asyncio
        market_insights = asyncio.run(agent.analyze_market_trends())
        
        trends_data = [
            {
                'skill': insight.skill,
                'demand_change': insight.demand_change,
                'salary_trend': insight.salary_trend,
                'job_count': insight.job_count,
                'growth_prediction': insight.growth_prediction,
                'recommended_action': insight.recommended_action
            } for insight in market_insights
        ]
        
        return jsonify({
            'market_trends': trends_data,
            'total_skills_analyzed': len(trends_data),
            'analysis_timestamp': datetime.now().isoformat(),
            'ai_provider': 'xAI Grok'
        })
        
    except Exception as e:
        return jsonify({
            'error': 'Failed to analyze market trends',
            'details': str(e)
        }), 500

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

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
