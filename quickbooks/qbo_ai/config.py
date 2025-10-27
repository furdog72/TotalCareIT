"""
Configuration management
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()


class QBOConfig(BaseModel):
    """QuickBooks Online configuration"""

    client_id: str = Field(default_factory=lambda: os.getenv("QBO_CLIENT_ID", ""))
    client_secret: str = Field(default_factory=lambda: os.getenv("QBO_CLIENT_SECRET", ""))
    redirect_uri: str = Field(default_factory=lambda: os.getenv("QBO_REDIRECT_URI", "http://localhost:8000/callback"))
    environment: str = Field(default_factory=lambda: os.getenv("QBO_ENVIRONMENT", "sandbox"))
    company_id: Optional[str] = Field(default_factory=lambda: os.getenv("QBO_COMPANY_ID"))

    class Config:
        env_prefix = "QBO_"
