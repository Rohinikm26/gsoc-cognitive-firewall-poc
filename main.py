from fastapi import FastAPI
from pydantic import BaseModel
import re

# Initialize the API
app = FastAPI(title="Cognitive Firewall PoC", version="0.1.0")

# 1. Define strict input/output schemas (Proves enterprise readiness)
class AgentRequest(BaseModel):
    prompt: str
    agent_id: str = "default-agent"

class ValidationResponse(BaseModel):
    status: str
    risk_score: int
    reason: str | None = None

# 2. Define our MVP policy rules (The Threat Engine)
INJECTION_PATTERN = [
    r"(?i)ignore (all )?previous instructions",
    r"(?i)system prompt",
    r"(?i)bypass system",
]

# 3. The Interception Endpoint
@app.post("/validate", response_model=ValidationResponse)
async def validate_prompt(request: AgentRequest):
    risk_score = 0
    reasons = []

    # Scan the prompt against our security policies
    for pattern in INJECTION_PATTERN:
        if re.search(pattern, request.prompt):
            risk_score += 80
            reasons.append(f"Matched threat pattern: {pattern}")

    # The Decision Engine
    if risk_score > 70:
        return ValidationResponse(
            status="blocked",
            risk_score=min(risk_score, 100),
            reason=" | ".join(reasons)
        )

    # If clean, allow it through to the LLM
    return ValidationResponse(
        status="allowed",
        risk_score=risk_score,
        reason="Prompt passed basic sanitization."
    )

# 4. Health check for the dashboard
@app.get("/health")
async def health_check():
    return {"status": "active", "policies_loaded": len(INJECTION_PATTERN)}