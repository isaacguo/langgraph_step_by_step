from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .langgraph_app import create_workflow
from .models import UserRequest, AgentResponse
from .config import settings
from safety.observability.metrics_exporter import MetricsExporter
import uuid
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

# Initialize workflow
workflow = create_workflow()

# Initialize metrics exporter
metrics_exporter = MetricsExporter()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(request: UserRequest):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    logger.info(f"Received request {request_id} from user {request.user_id}")
    
    initial_state = {
        "messages": [{"role": "user", "content": request.content}],
        "user_input": request.content,
        "user_id": request.user_id,
        "safety_status": "pending",
        "parsed_intent": {},
        "processing_result": "",
        "errors": []
    }
    
    try:
        # Run the workflow
        result = workflow.invoke(initial_state)
        
        status = "success"
        error_msg = None
        
        if result.get("safety_status") == "blocked":
            status = "blocked"
            error_msg = result.get("errors", ["Blocked by safety system"])[0]
            metrics_exporter.record_violation("blocked")
        elif result.get("errors"):
            status = "error"
            error_msg = str(result.get("errors")[0])
            metrics_exporter.record_violation("error")
        
        # Record metrics
        latency = time.time() - start_time
        metrics_exporter.record_request(status)
        metrics_exporter.record_latency(latency)
            
        return AgentResponse(
            request_id=request_id,
            content=result.get("processing_result", ""),
            safety_score=1.0,  # Placeholder until safety module is integrated
            status=status,
            error=error_msg
        )
        
    except Exception as e:
        logger.error(f"Error processing request {request_id}: {str(e)}")
        metrics_exporter.record_request("exception")
        metrics_exporter.record_violation("exception")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
