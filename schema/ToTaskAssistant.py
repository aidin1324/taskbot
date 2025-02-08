from pydantic import BaseModel, Field


class ToTaskAssistant(BaseModel):
    """ Transfer work to a task assistant to manage the task works"""
    
    user_request: str = Field(description="The user request from user")
    
    class Config:
        json_schema_extra = {
            "json_schema_extra": {
                "examples": [
                    {
                        "user_request": "I want to create a task to remind me of my meeting tomorrow"
                    }
                ]
            }
        }