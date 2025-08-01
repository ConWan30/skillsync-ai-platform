from flask import Flask, request, jsonify
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
    
    # Updated data structure for xAI API
    data = {
        "messages": messages,
        "model": "grok-beta",
        "stream": False,
        "temperature": 0.7,
        "max_tokens": max_tokens
    }
    
    try:
        # Try the main xAI endpoint
        response = requests.post(f"{XAI_BASE_URL}/chat/completions", 
                               headers=headers, 
                               json=data, 
                               timeout=30)
        
        # If 404, the API might be at a different endpoint
        if response.status_code == 404:
            # Try alternative endpoint structure
            alt_url = "https://api.x.ai/v1/completions"
            alt_data = {
                "model": "grok-beta",
                "prompt": messages[-1]["content"] if messages else "",
                "max_tokens": max_tokens,
                "temperature": 0.7
            }
            response = requests.post(alt_url, headers=headers, json=alt_data, timeout=30)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # If xAI fails, provide a fallback response for testing
        if "404" in str(e):
            return {
                "choices": [{
                    "message": {
                        "content": f"""**SkillSync AI Assessment (Demo Mode - xAI API Configuration Needed)**

Based on your skills description, here's a comprehensive analysis:

**Skill Categories & Levels:**
• Technical Skills: 7/10 - Strong foundation in web development
• Programming Languages: 6/10 - Good JavaScript and React knowledge
• Backend Development: 5/10 - Basic Node.js experience
• Version Control: 6/10 - Git proficiency
• Deployment: 5/10 - Netlify deployment experience

**Strengths:**
✅ Solid frontend development skills with React
✅ Full-stack awareness with Node.js backend experience
✅ Good development workflow with Git
✅ Practical deployment experience

**Areas for Improvement:**
🎯 Database management (SQL/NoSQL)
🎯 Advanced backend frameworks (Express.js, authentication)
🎯 Testing methodologies (unit, integration testing)
🎯 Cloud services (AWS, Azure, GCP)
🎯 DevOps practices (CI/CD, containerization)

**Career Recommendations:**
🚀 **Immediate Focus:** Strengthen backend skills with Express.js and database integration
🚀 **6-Month Goal:** Build 2-3 full-stack projects showcasing CRUD operations
🚀 **1-Year Goal:** Learn cloud deployment and basic DevOps practices
🚀 **Leadership Path:** Start mentoring junior developers and leading small projects

**Learning Path:**
1. Complete a comprehensive Node.js/Express course
2. Learn PostgreSQL or MongoDB
3. Build a full-stack application with authentication
4. Deploy to AWS or similar cloud platform
5. Learn basic testing frameworks (Jest, Cypress)

**Market Demand:** High demand for full-stack developers, especially with React/Node.js stack. Average salary range: $70k-$120k depending on location and experience.

*Note: This is a demo response. Configure your xAI API key for full AI-powered assessments.*"""
                    }
                }],
                "usage": {"total_tokens": 350}
            }
        return {"error": f"xAI API call failed: {str(e)}"}

# Routes
@app.route('/')
def index():
    return jsonify({
        'message': 'Welcome to SkillSync AI Platform API',
        'version': '1.0.0',
        'status': 'running',
        'ai_provider': 'xAI Grok',
        'features': [
            'AI-Powered Skill Assessment',
            'Personalized Learning Paths', 
            'Career Guidance',
            'File Organization',
            'Progress Tracking'
        ]
    })

@app.route('/api/health')
def health_check():
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'ai_status': 'xAI Grok Ready' if XAI_API_KEY else 'xAI API Key Required'
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
        
        return jsonify({
            'assessment': assessment_text,
            'ai_provider': 'xAI Grok',
            'timestamp': datetime.now().isoformat(),
            'tokens_used': response.get('usage', {}).get('total_tokens', 'unknown')
        })
        
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
        
        return jsonify({
            'career_guidance': guidance,
            'ai_provider': 'xAI Grok',
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

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
