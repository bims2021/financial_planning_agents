from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from enum import Enum

class AgentType(str, Enum):
    BUDGETING = "budgeting"
    INVESTMENT = "investment"
    DEBT_MANAGEMENT = "debt_management"

class UserProfile(BaseModel):
    monthly_income: float = Field(..., gt=0, description="Monthly income in dollars")
    monthly_expenses: float = Field(..., ge=0, description="Current monthly expenses")
    debt_amount: float = Field(default=0, ge=0, description="Total debt amount")
    debt_interest_rate: float = Field(default=0, ge=0, le=100, description="Average debt interest rate")
    savings: float = Field(default=0, ge=0, description="Current savings")
    investment_experience: str = Field(default="beginner", description="Investment experience level")
    risk_tolerance: str = Field(default="moderate", description="Risk tolerance (conservative/moderate/aggressive)")
    age: int = Field(..., gt=0, lt=120, description="Age")
    financial_goals: str = Field(default="", description="Financial goals and priorities")

class AgentResponse(BaseModel):
    agent_type: AgentType
    recommendations: List[str]
    analysis: str
    key_metrics: Dict[str, Any]
    action_items: List[str]
