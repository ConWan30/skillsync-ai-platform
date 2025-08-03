# SkillSync AI Platform - AI Integration Setup Guide

## Critical: AI Connectivity Configuration

### Environment Variables Required

For full AI functionality, configure these environment variables in Railway:

```bash
# xAI Grok API Configuration
XAI_API_KEY=your_xai_api_key_here

# Optional: Database Configuration  
DATABASE_URL=your_database_url_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
```

### AI Features Requiring API Connectivity

1. **AI Agent Chat** (`/ai-agent`)
   - Real-time career guidance via xAI Grok
   - API Endpoint: `/api/ai/career-guidance`

2. **Tools - Skill Assessment** (`/tools`)
   - AI-powered skill evaluation
   - API Endpoint: `/api/ai/assess-skills`

3. **Tools - Resume Analysis** (`/tools`)
   - Resume optimization with AI
   - API Endpoint: `/api/files/upload`

4. **Career Paths - AI Generation** (`/career-paths`)
   - Personalized path generation
   - API Endpoint: `/api/ai/career-guidance`

5. **Market Intelligence** (`/market-intelligence`)
   - Live market data analysis
   - API Endpoint: `/api/intelligence/market-trends`

### Fallback Behavior

- **WITH API Key**: Full AI functionality using xAI Grok
- **WITHOUT API Key**: Intelligent simulations with static responses

### A2A Protocol Communication

The platform implements Agent-to-Agent communication through:

1. **Frontend ↔ Backend APIs**
   - JavaScript fetch() calls to Flask REST endpoints
   - Real-time data exchange with error handling

2. **Backend ↔ xAI Grok**
   - Direct API integration with xAI's Grok models
   - Fallback to Grok-3 if Grok-4 unavailable

3. **Career Intelligence Agent**
   - Autonomous background agent for proactive insights
   - Market trend analysis and opportunity detection

### Testing AI Connectivity

Check AI status at: `/api/intelligence/status`

Response format:
```json
{
  "status": "connected|api_key_required",
  "ai_model": "grok-4",
  "features": ["career_guidance", "skill_assessment", "market_analysis"]
}
```

### Railway Deployment

1. Add environment variables in Railway dashboard
2. Deploy will automatically use AI if XAI_API_KEY is set
3. Monitor logs for API connectivity status

---

**Status**: AI Integration ready with hybrid approach (real AI + intelligent fallbacks)