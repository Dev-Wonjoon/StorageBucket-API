from pydantic import BaseModel

class DiskUsage(BaseModel):
    total_memory: float
    used_memory: float
    free_memory: float
    percent: float