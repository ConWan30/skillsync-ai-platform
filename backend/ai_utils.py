"""
Shared AI utilities to avoid circular imports
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# xAI configuration
XAI_API_KEY = os.getenv('XAI_API_KEY')
XAI_BASE_URL = "https://api.x.ai/v1"

def call_grok_ai(prompt, system_prompt=None):
    """
    Call xAI Grok API with the given prompt
    """
    if not XAI_API_KEY:
        return "xAI API key not configured"
    
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
        "temperature": 0.7
    }
    
    try:
        response = requests.post(f"{XAI_BASE_URL}/chat/completions", 
                               headers=headers, json=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"AI API Error: {str(e)}"

# Shared career knowledge base
CAREER_KNOWLEDGE_BASE = {
    "tech_trends_2024": {
        "ai_ml": "Artificial Intelligence and Machine Learning continue to dominate",
        "cloud": "Cloud computing skills remain in high demand",
        "devops": "DevOps and automation are essential skills",
        "web3": "Blockchain and Web3 technologies are emerging"
    },
    "salary_ranges": {
        "frontend": {"junior": "60k-80k", "mid": "80k-120k", "senior": "120k-180k"},
        "backend": {"junior": "65k-85k", "mid": "85k-130k", "senior": "130k-200k"},
        "fullstack": {"junior": "70k-90k", "mid": "90k-140k", "senior": "140k-220k"},
        "devops": {"junior": "75k-95k", "mid": "95k-150k", "senior": "150k-250k"}
    }
}