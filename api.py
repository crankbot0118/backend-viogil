from fastapi import FastAPI
from pydantic import BaseModel
import paramiko

# --------------------------------------------------
# APP INITIALIZATION
# --------------------------------------------------

app = FastAPI(
    title="Vigil Monitoring Backend",
    description="Backend APIs for monitoring and health check execution",
    version="1.0.0"
)

# --------------------------------------------------
# INSTANCE INVENTORY
# --------------------------------------------------

INSTANCES = {
    "cust_instance1": {
        "host": "54.80.214.20",
        "username": "ec2-user",
        "pem_file": "/home/ec2-user/key.pem"
    },

    "cust_instance2": {
        "host": "54.84.52.99",
        "username": "ec2-user",
        "pem_file": "/home/ec2-user/key.pem"
    }
}

# --------------------------------------------------
# REQUEST MODEL
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

    # ----------------------------------------------
    # VALIDATE INSTANCE
    # ----------------------------------------------

    if request.instance_name not in INSTANCES:
        return {
            "status": "failed",
            "message": "Invalid instance selected"
        }

    instance = INSTANCES[request.instance_name]

    # ----------------------------------------------
    # HEALTH CHECK COMMAND
    # ----------------------------------------------

    command = r'''
    echo "=================================================="
    echo "              SYSTEM HEALTH REPORT"
    echo "=================================================="

    echo
    echo "================ HOST INFO ======================="
    printf "%-20s : %s\n" "Hostname" "$(hostname)"
    printf "%-20s : %s\n" "Date" "$(date)"

    echo
    echo "================ UPTIME =========================="
    uptime

    echo
    echo "================ MEMORY USAGE ===================="
    free -h
    '''

    ssh = paramiko.SSHClient()

    ssh.set_missing_host_key_policy(
        paramiko.AutoAddPolicy()
    )

    try:

        # ------------------------------------------
        # CONNECT TO REMOTE INSTANCE
        # ------------------------------------------

        ssh.connect(
            hostname=instance["host"],
            username=instance["username"],
            key_filename=instance["pem_file"]
        )

        # ------------------------------------------
        # EXECUTE COMMAND
        # ------------------------------------------

        stdin, stdout, stderr = ssh.exec_command(command)

        output = stdout.read().decode()

        error = stderr.read().decode()

        ssh.close()

        # ------------------------------------------
        # HANDLE STDERR
        # ------------------------------------------

        if error:
            return {
                "status": "failed",
                "task": request.task_name,
                "instance": request.instance_name,
                "error": error
            }

        # ------------------------------------------
        # SUCCESS RESPONSE
        # ------------------------------------------

        return {
            "status": "success",
            "task": request.task_name,
            "instance": request.instance_name,
            "output": output
        }

    except Exception as e:

        return {
            "status": "failed",
            "task": request.task_name,
            "instance": request.instance_name,
            "error": str(e)
        }