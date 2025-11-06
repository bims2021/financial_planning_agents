from .base_agent import BaseFinancialAgent
from config import AgentType, AgentResponse, UserProfile

class InvestmentAgent(BaseFinancialAgent):
    def get_system_prompt(self) -> str:
        return """You are a Chief Investment Strategist and CFA charterholder with expertise across multiple asset classes.

Your expertise includes:
- Portfolio construction and asset allocation
- Risk assessment and management
- Tax-efficient investing strategies
- Retirement planning (401k, IRA, Roth IRA)
- Index funds, ETFs, bonds, and alternative investments

Analyze the user's profile and provide:
1. Personalized asset allocation based on age, risk tolerance, and goals
2. Specific investment vehicle recommendations (ETFs, index funds)
3. Tax-advantaged account strategies
4. Expected returns and risk analysis
5. Rebalancing guidelines

Consider the user's investment experience level and explain concepts clearly."""

    def analyze(self, user_profile: UserProfile) -> AgentResponse:
        prompt = self._create_prompt_template()
        
        user_input = f"""
        User Investment Profile:
        - Age: {user_profile.age}
        - Monthly Income: ${user_profile.monthly_income:,.2f}
        - Current Savings: ${user_profile.savings:,.2f}
        - Risk Tolerance: {user_profile.risk_tolerance}
        - Investment Experience: {user_profile.investment_experience}
        - Financial Goals: {user_profile.financial_goals}
        
        Provide a comprehensive investment strategy and portfolio recommendations.
        """
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_input": user_input,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        # Calculate asset allocation based on age and risk tolerance
        stock_allocation = self._calculate_stock_allocation(user_profile)
        bond_allocation = 100 - stock_allocation
        
        return AgentResponse(
            agent_type=AgentType.INVESTMENT,
            recommendations=[
                f"Asset Allocation: {stock_allocation}% stocks, {bond_allocation}% bonds",
                "Invest in low-cost index funds (e.g., VTI, VXUS)",
                f"Max out tax-advantaged accounts (${20500 if user_profile.age < 50 else 27000} 401k annually)",
                "Consider Roth IRA for tax-free growth",
                "Rebalance portfolio quarterly"
            ],
            analysis=response.content,
            key_metrics={
                "recommended_stock_allocation": f"{stock_allocation}%",
                "recommended_bond_allocation": f"{bond_allocation}%",
                "risk_level": user_profile.risk_tolerance,
                "investment_horizon": f"{65 - user_profile.age} years to retirement"
            },
            action_items=[
                "Open brokerage account with low-fee provider (Vanguard, Fidelity, Schwab)",
                "Set up automatic monthly investments",
                f"Invest initial ${min(user_profile.savings * 0.7, 10000):,.0f} following allocation",
                "Review and increase contributions annually with raises"
            ]
        )
    
    def _calculate_stock_allocation(self, profile: UserProfile) -> int:
        """Calculate stock allocation using age-based rule adjusted for risk tolerance"""
        base_allocation = 110 - profile.age
        
        if profile.risk_tolerance == "aggressive":
            return min(90, base_allocation + 10)
        elif profile.risk_tolerance == "conservative":
            return max(30, base_allocation - 10)
        else:
            return base_allocation