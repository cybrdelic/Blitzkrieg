from fastapi import FastAPI, HTTPException
import logging

app = FastAPI()
logger = logging.getLogger("api")

@app.get("/connection_details", tags=["Database"])
def get_connection_details():
    try:
        # Here, you'd typically fetch these details from a config or database
        details = {
            "db_host": "localhost",
            "db_port": 5432,
            "db_user": "admin",
            "db_password": "admin"
        }
        return details
    except Exception as e:
        logger.error(f"Failed to get connection details: {e}")
        raise HTTPException(status_code=500, detail="Failed to get connection details")
