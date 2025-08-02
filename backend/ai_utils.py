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
                    "max_tokens": 300  # Reduced for more concise responses
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