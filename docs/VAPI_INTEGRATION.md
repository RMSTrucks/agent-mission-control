# VAPI Integration Guide

Complete guide for integrating VAPI phone bot management with Agent Mission Control.

## Overview

VAPI (Voice AI Platform Interface) integration enables:
- Managing phone bot assistants
- Deploying optimized agents to live phone bots
- Phone number management and assignment
- Call history and transcript access

## Setup

### 1. Get VAPI API Key

1. Sign up at [VAPI.ai](https://vapi.ai)
2. Navigate to Settings → API Keys
3. Create a new API key
4. Copy the key (starts with `sk-...`)

### 2. Configure Environment

Set the VAPI API key as an environment variable:

```bash
# Linux/Mac
export VAPI_API_KEY=sk_your_key_here

# Windows
set VAPI_API_KEY=sk_your_key_here

# Or add to .env file in project root
echo "VAPI_API_KEY=sk_your_key_here" >> .env
```

### 3. Restart Backend

```bash
cd backend
uvicorn main:app --reload
```

You should see:
```
SUCCESS: VAPI is connected
```

## Architecture

```
Frontend (Streamlit)
    ↓
Backend API (FastAPI)
    ↓
VAPI Client Wrapper
    ↓
VAPI REST API (https://api.vapi.ai)
```

## Components

### 1. VAPI Client (`integrations/vapi_client.py`)

Python wrapper for VAPI API:

```python
from integrations.vapi_client import VAPIClient

client = VAPIClient(api_key="sk_...")

# List assistants
assistants = client.list_assistants()

# Get assistant
assistant = client.get_assistant("asst_123")

# Update assistant
client.update_assistant("asst_123", {
    "systemPrompt": "You are a helpful assistant...",
    "firstMessage": "Hello! How can I help you today?"
})

# Deploy optimized prompts
client.deploy_agent("asst_123", {
    "systemPrompt": "Optimized system prompt...",
    "firstMessage": "Optimized greeting..."
})
```

**Key Methods:**
- `list_assistants()` - Get all assistants
- `get_assistant(id)` - Get assistant details
- `create_assistant(config)` - Create new assistant
- `update_assistant(id, updates)` - Update assistant
- `delete_assistant(id)` - Delete assistant
- `deploy_agent(id, prompts)` - Deploy optimized prompts
- `list_phone_numbers()` - Get phone numbers
- `update_phone_number(id, assistant_id)` - Assign number
- `list_calls(assistant_id)` - Get call history

### 2. Backend API (`backend/api/vapi.py`)

REST API endpoints for VAPI operations:

**Assistant Management:**
- `GET /api/vapi/assistants` - List all assistants
- `GET /api/vapi/assistants/{id}` - Get assistant details
- `POST /api/vapi/assistants` - Create new assistant
- `PATCH /api/vapi/assistants/{id}` - Update assistant
- `DELETE /api/vapi/assistants/{id}` - Delete assistant

**Deployment:**
- `POST /api/vapi/deploy` - Deploy optimized prompts
- `POST /api/vapi/deploy/{agent_id}` - Auto-deploy by agent ID

**Phone Numbers:**
- `GET /api/vapi/phone-numbers` - List phone numbers
- `GET /api/vapi/phone-numbers/{id}` - Get number details
- `POST /api/vapi/phone-numbers/{id}/assign` - Assign to assistant

**Call History:**
- `GET /api/vapi/calls` - List calls (optional: filter by assistant)
- `GET /api/vapi/calls/{id}` - Get call details with transcript

**Status:**
- `GET /api/vapi/status` - Check VAPI connection

### 3. Frontend UI (`frontend/pages/4_VAPI.py`)

Streamlit interface with 4 tabs:

**Assistants Tab:**
- List all VAPI assistants
- View configuration and prompts
- Edit/delete assistants

**Deploy Agent Tab:**
- Select VAPI assistant
- Enter optimized prompts (system prompt, first message)
- Deploy to live assistant

**Phone Numbers Tab:**
- List all phone numbers
- View assignments
- Assign numbers to assistants

**Call History Tab:**
- View call logs
- Filter by assistant
- View transcripts

## Usage Workflows

### Workflow 1: Create New Phone Bot

1. **Create Assistant** (via VAPI dashboard or API)
2. **View in Mission Control**
   - Go to VAPI page
   - See assistant listed
3. **Optimize Agent**
   - Go to Optimization page
   - Run GEPA optimization
4. **Deploy to VAPI**
   - Go to VAPI → Deploy Agent tab
   - Select assistant
   - Paste optimized prompts
   - Click Deploy
5. **Assign Phone Number**
   - Go to Phone Numbers tab
   - Select number
   - Assign to assistant

### Workflow 2: Update Existing Bot

1. **Run Optimization**
   - Optimization page → Start optimization
   - Wait for completion
2. **Get Optimized Prompts**
   - View optimization results
   - Copy optimized system prompt and first message
3. **Deploy**
   - VAPI page → Deploy Agent tab
   - Select assistant
   - Paste prompts
   - Deploy
4. **Monitor Performance**
   - Call History tab → View recent calls
   - Check for improvements

### Workflow 3: Rollback

If optimized version has issues:

1. **Get Baseline Prompts**
   - Retrieve original prompts from optimization history
2. **Deploy Baseline**
   - VAPI page → Deploy Agent tab
   - Paste baseline prompts
   - Deploy
3. **Verify**
   - Check assistant configuration
   - Test with phone call

## API Examples

### List Assistants

**Request:**
```bash
curl http://localhost:8000/api/vapi/assistants
```

**Response:**
```json
{
  "success": true,
  "assistants": [
    {
      "id": "asst_abc123",
      "name": "REMUS",
      "voice": {
        "provider": "11labs",
        "voiceId": "..."
      },
      "model": {
        "provider": "openai",
        "model": "gpt-4"
      },
      "systemPrompt": "You are REMUS...",
      "firstMessage": "Hello! This is REMUS..."
    }
  ],
  "count": 1
}
```

### Deploy Agent

**Request:**
```bash
curl -X POST http://localhost:8000/api/vapi/deploy \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "asst_abc123",
    "system_prompt": "Optimized system instructions...",
    "first_message": "Optimized greeting..."
  }'
```

**Response:**
```json
{
  "success": true,
  "assistant": {
    "id": "asst_abc123",
    "name": "REMUS",
    "systemPrompt": "Optimized system instructions...",
    "firstMessage": "Optimized greeting..."
  },
  "message": "Agent deployed successfully to assistant asst_abc123"
}
```

### Assign Phone Number

**Request:**
```bash
curl -X POST http://localhost:8000/api/vapi/phone-numbers/phn_123/assign \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "asst_abc123"
  }'
```

**Response:**
```json
{
  "success": true,
  "phone_number": {
    "id": "phn_123",
    "number": "+1234567890",
    "assistantId": "asst_abc123"
  },
  "message": "Phone number assigned to assistant asst_abc123"
}
```

## Error Handling

### VAPI Not Configured

**Error:**
```
503 Service Unavailable
VAPI not configured. Set VAPI_API_KEY environment variable.
```

**Solution:**
Set `VAPI_API_KEY` and restart backend.

### Invalid API Key

**Error:**
```
401 Unauthorized
Invalid API key
```

**Solution:**
Verify API key is correct and active in VAPI dashboard.

### Assistant Not Found

**Error:**
```
404 Not Found
Assistant not found: asst_123
```

**Solution:**
Check assistant ID is correct. List assistants to see available IDs.

## Security

### API Key Protection

**DO NOT:**
- Commit API keys to git
- Share API keys publicly
- Hardcode keys in source code

**DO:**
- Use environment variables
- Use `.env` files (add to `.gitignore`)
- Rotate keys periodically
- Use different keys for dev/prod

### Rate Limiting

VAPI API has rate limits:
- Standard: 100 requests/minute
- Enterprise: 1000 requests/minute

The client handles rate limit errors gracefully.

## Testing

### Manual Testing

1. **Test Connection:**
```bash
curl http://localhost:8000/api/vapi/status
```

2. **Test List:**
```bash
curl http://localhost:8000/api/vapi/assistants
```

3. **Test Deploy:**
Use frontend UI or curl to deploy test prompts.

### Python Testing

```python
from integrations.vapi_client import VAPIClient

client = VAPIClient()

# Test connection
assert client.test_connection()

# Test list
result = client.list_assistants()
assert result.success
print(f"Found {len(result.data)} assistants")

# Test get
if result.data:
    assistant_id = result.data[0]['id']
    assistant = client.get_assistant(assistant_id)
    assert assistant.success
```

## Troubleshooting

### Backend won't start

**Check:**
1. Is `VAPI_API_KEY` set?
2. Is the key valid?
3. Check backend logs

### Frontend shows "Not Connected"

**Check:**
1. Is backend running?
2. Does backend show "VAPI is connected"?
3. Refresh frontend page

### Deploy fails

**Check:**
1. Is assistant ID correct?
2. Are prompts valid?
3. Check backend logs for errors

### Phone number assignment fails

**Check:**
1. Is number ID correct?
2. Is assistant ID correct?
3. Is number already assigned?

## Best Practices

### Deployment

1. **Test First**
   - Test optimized prompts in dev environment
   - Verify improvements before deploying

2. **Deploy During Low Traffic**
   - Deploy outside peak hours
   - Minimize impact on users

3. **Keep Backups**
   - Save baseline prompts
   - Document changes
   - Easy rollback if needed

4. **Monitor After Deployment**
   - Check call history
   - Review transcripts
   - Track performance metrics

### Optimization Workflow

```
1. Baseline Evaluation
   ↓
2. GEPA Optimization (10-20 iterations)
   ↓
3. Compare Results (baseline vs optimized)
   ↓
4. Test in Dev Environment
   ↓
5. Deploy to Production (VAPI)
   ↓
6. Monitor Performance
   ↓
7. Rollback if Issues OR Iterate Further
```

## Future Enhancements

### Phase 5
- [ ] Automatic deployment after optimization
- [ ] A/B testing framework
- [ ] Performance tracking dashboard
- [ ] Alert system for performance degradation

### Phase 6
- [ ] Multi-environment support (dev/staging/prod)
- [ ] Deployment approvals and workflows
- [ ] Automated rollback on errors
- [ ] Integration with monitoring tools

## Resources

- [VAPI Documentation](https://docs.vapi.ai)
- [VAPI API Reference](https://docs.vapi.ai/api-reference)
- [VAPI Dashboard](https://dashboard.vapi.ai)

---

**Version**: 1.0
**Last Updated**: 2024-11-05
**Status**: Phase 4 - VAPI Integration Complete
