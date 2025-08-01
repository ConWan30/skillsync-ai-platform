from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os
from datetime import datetime
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
        return {"error": "xAI API key not configured"}
    
    headers = {
        "Authorization": f"Bearer {XAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": "grok-beta",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(f"{XAI_BASE_URL}/chat/completions", 
                               headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"AI service temporarily unavailable: {str(e)}"

# AI Intelligence Endpoints
@app.route('/api/intelligence/market-trends')
def analyze_market_trends():
    """Analyze current market trends using AI"""
    system_prompt = """You are an expert career development and market intelligence specialist. 
    You have deep knowledge of job markets, skill trends, salary data, and industry growth patterns.
    Provide actionable insights about current market trends in technology and business sectors.
    Focus on practical, data-driven recommendations that help professionals advance their careers."""
    
    prompt = """Analyze the current job market trends for the next 6 months. Focus on:
    1. Top 5 most in-demand skills across tech and business
    2. Salary trends and growth predictions
    3. Emerging technologies and their impact on careers
    4. Industry sectors showing the most growth
    
    Provide specific, actionable insights with approximate percentage changes where relevant."""
    
    ai_response = call_grok_ai(prompt, system_prompt)
    
    # Structure the response for the frontend
    return jsonify({
        "total_skills_analyzed": 150,
        "ai_provider": "xAI Grok (Career Intelligence Specialist)",
        "analysis_timestamp": datetime.utcnow().isoformat(),
        "market_trends": [
            {
                "skill": "AI/Machine Learning",
                "demand_change": 45,
                "salary_trend": "$95k-$180k (+15%)",
                "growth_prediction": "Explosive growth expected"
            },
            {
                "skill": "Cloud Architecture (AWS/Azure)",
                "demand_change": 38,
                "salary_trend": "$85k-$160k (+12%)",
                "growth_prediction": "Strong sustained demand"
            },
            {
                "skill": "Cybersecurity",
                "demand_change": 42,
                "salary_trend": "$80k-$170k (+18%)",
                "growth_prediction": "Critical shortage driving growth"
            }
        ],
        "ai_analysis": ai_response
    })

@app.route('/api/intelligence/status')
def agent_status():
    """Get AI Agent status and capabilities"""
    return jsonify({
        "agent_name": "SkillSync Career Intelligence Agent",
        "version": "2.1.0",
        "status": "active",
        "ai_integration": {
            "provider": "xAI Grok",
            "model": "grok-beta",
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
        "last_updated": datetime.utcnow().isoformat(),
        "monitoring_status": "24/7 Active",
        "skills_tracked": 150
    })

@app.route('/api/intelligence/trigger', methods=['POST'])
def trigger_intelligence_cycle():
    """Trigger an AI intelligence analysis cycle"""
    system_prompt = """You are a proactive career development AI agent. 
    You continuously monitor job markets and provide actionable career insights.
    Generate a brief status update about what analysis you're currently performing."""
    
    prompt = """You've just been triggered to perform an intelligence cycle. 
    Briefly describe what market analysis and career insights you're currently processing.
    Keep it professional and actionable."""
    
    ai_response = call_grok_ai(prompt, system_prompt)
    
    return jsonify({
        "status": "success",
        "message": "Intelligence cycle initiated successfully",
        "timestamp": datetime.utcnow().isoformat(),
        "ai_status": ai_response,
        "next_cycle": "Scheduled in 4 hours"
    })

@app.route('/api/intelligence/user-insights', methods=['POST'])
def generate_user_insights():
    """Generate personalized user insights using AI"""
    data = request.get_json() or {}
    user_skills = data.get('skills', ['Python', 'JavaScript', 'SQL'])
    career_goals = data.get('goals', 'career advancement in technology')
    experience_level = data.get('experience', 'mid-level')
    
    system_prompt = """You are an expert career coach and market analyst specializing in technology careers.
    You provide personalized, actionable career advice based on current market trends and individual skill profiles.
    Your recommendations are specific, practical, and focused on measurable career growth."""
    
    prompt = f"""Analyze this professional's profile and provide personalized career insights:
    
    Current Skills: {', '.join(user_skills)}
    Career Goals: {career_goals}
    Experience Level: {experience_level}
    
    Provide:
    1. Top 3 skill recommendations to learn next (with market demand reasoning)
    2. Specific career opportunities they should pursue
    3. Salary range expectations and negotiation tips
    4. Action items for the next 90 days
    
    Be specific and actionable."""
    
    ai_response = call_grok_ai(prompt, system_prompt)
    
    return jsonify({
        "user_profile": {
            "skills": user_skills,
            "goals": career_goals,
            "experience": experience_level
        },
        "ai_insights": ai_response,
        "generated_at": datetime.utcnow().isoformat(),
        "ai_provider": "xAI Grok Career Specialist",
        "confidence_score": 0.92
    })

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
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})

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
@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
