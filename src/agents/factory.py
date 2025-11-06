from enum import Enum
from typing import Dict, List, Any
import math 
from config import AgentType
from .base_agent import BaseFinancialAgent
from .budgeting_agent import BudgetingAgent
from .investment_agent import InvestmentAgent
from .debt_management_agent import DebtManagementAgent


class AgentFactory:
    """Factory pattern for creating specialized financial agents"""
    
    @staticmethod
    def create_agent(agent_type: AgentType, api_key: str) -> BaseFinancialAgent:
        """Create and return the appropriate agent based on type"""
        agents = {
            AgentType.BUDGETING: BudgetingAgent,
            AgentType.INVESTMENT: InvestmentAgent,
            AgentType.DEBT_MANAGEMENT: DebtManagementAgent
        }
        
        agent_class = agents.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        return agent_class(api_key=api_key)
    
    @staticmethod
    def create_all_agents(api_key: str) -> Dict[AgentType, BaseFinancialAgent]:
        """Create all agents at once"""
        return {
            agent_type: AgentFactory.create_agent(agent_type, api_key)
            for agent_type in AgentType
        }