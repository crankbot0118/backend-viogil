from fastapi import FastAPI
from pydantic import BaseModel

# --------------------------------------------------
# APP INITIALIZATION
# --------------------------------------------------

app = FastAPI(
    title="Vigil Monitoring Backend",
    description="Backend APIs for monitoring and health check execution",
    version="1.0.0"
)

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class HealthCheckRequest(BaseModel):
    instance_name: str
    task_name: str

# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Vigil Backend API is running"
    }

# --------------------------------------------------
# HEALTH CHECK EXECUTION ENDPOINT
# --------------------------------------------------

@app.post("/tasks/pre-health-check/execute")
def execute_pre_health_check(request: HealthCheckRequest):

    return {
        "status": "success",
        "task": request.task_name,
        "instance": request.instance_name,
        "output": "Pre health check executed successfully"
    }