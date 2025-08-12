from pydantic import BaseModel

class HealthCheckResponse(BaseModel):
    status: str
    uptime_seconds: float

class RedditPost(BaseModel):
    id: str
    title: str
    score: int
    permalink: str
    # add other fields as needed
