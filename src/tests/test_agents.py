import pytest
from unittest.mock import Mock, patch
from ...config import AgentType, UserProfile
from  ..agents.factory import AgentFactory
from ..agents.budgeting_agent import BudgetingAgent
from ..agents.investment_agent import InvestmentAgent 
from ..agents.debt_management_agent import DebtManagementAgent
from ...orchestrator import FinancialAdvisorOrchestrator


@pytest.fixture
def sample_profile():
    return UserProfile(
        monthly_income=5000,
        monthly_expenses=3500,
        debt_amount=15000,
        debt_interest_rate=18.5,
        savings=10000,
        investment_experience="beginner",
        risk_tolerance="moderate",
        age=30,
        financial_goals="Save for house down payment and retirement"
    )

@pytest.fixture
def api_key():
    return "test-api-key"

class TestAgentFactory:
    def test_create_budgeting_agent(self, api_key):
        agent = AgentFactory.create_agent(AgentType.BUDGETING, api_key)
        assert isinstance(agent, BudgetingAgent)
    
    def test_create_investment_agent(self, api_key):
        agent = AgentFactory.create_agent(AgentType.INVESTMENT, api_key)
        assert isinstance(agent, InvestmentAgent)
    
    def test_create_debt_agent(self, api_key):
        agent = AgentFactory.create_agent(AgentType.DEBT_MANAGEMENT, api_key)
        assert isinstance(agent, DebtManagementAgent)
    
    def test_create_all_agents(self, api_key):
        agents = AgentFactory.create_all_agents(api_key)
        assert len(agents) == 3
        assert AgentType.BUDGETING in agents
        assert AgentType.INVESTMENT in agents
        assert AgentType.DEBT_MANAGEMENT in agents

class TestBudgetingAgent:
    def test_analyze_structure(self, api_key, sample_profile):
        agent = BudgetingAgent(api_key)
        
        with patch.object(agent.llm, 'invoke', return_value=Mock(content="Test analysis")):
            response = agent.analyze(sample_profile)
        
        assert response.agent_type == AgentType.BUDGETING
        assert len(response.recommendations) > 0
        assert "current_savings_rate" in response.key_metrics
        assert len(response.action_items) > 0

class TestInvestmentAgent:
    def test_stock_allocation_moderate(self, api_key):
        agent = InvestmentAgent(api_key)
        profile = UserProfile(
            monthly_income=5000, monthly_expenses=3000,
            age=30, risk_tolerance="moderate"
        )
        allocation = agent._calculate_stock_allocation(profile)
        assert 70 <= allocation <= 85
    
    def test_stock_allocation_aggressive(self, api_key):
        agent = InvestmentAgent(api_key)
        profile = UserProfile(
            monthly_income=5000, monthly_expenses=3000,
            age=30, risk_tolerance="aggressive"
        )
        allocation = agent._calculate_stock_allocation(profile)
        assert allocation >= 85

class TestDebtManagementAgent:
    def test_no_debt_scenario(self, api_key):
        agent = DebtManagementAgent(api_key)
        profile = UserProfile(
            monthly_income=5000, monthly_expenses=3000,
            debt_amount=0, age=30
        )
        
        response = agent.analyze(profile)
        assert response.key_metrics["status"] == "debt_free"
    
    def test_payoff_calculation(self, api_key):
        agent = DebtManagementAgent(api_key)
        months = agent._calculate_payoff_time(
            principal=10000,
            payment=500,
            annual_rate=18
        )
        assert months > 0
        assert months < 999

class TestOrchestrator:
    @pytest.mark.asyncio
    async def test_orchestrator_flow(self, api_key, sample_profile):
        orchestrator = FinancialAdvisorOrchestrator(api_key)
        
        # Mock agent responses
        with patch.object(BudgetingAgent, 'analyze'), \
             patch.object(InvestmentAgent, 'analyze'), \
             patch.object(DebtManagementAgent, 'analyze'):
            
            result = orchestrator.analyze(sample_profile)
            assert isinstance(result, str)
            assert len(result) > 0

# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])