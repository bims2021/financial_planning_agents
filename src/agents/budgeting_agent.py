from .base_agent import BaseFinancialAgent
from config import UserProfile, AgentResponse, AgentType

class BudgetingAgent(BaseFinancialAgent):
    def get_system_prompt(self) -> str:
        return """You are a Senior Budgeting Advisor with 15+ years of experience in personal finance.
        
Your expertise includes:
- Creating sustainable monthly budgets
- Spending optimization strategies
- Savings recommendations based on income levels
- Emergency fund planning
- Expense categorization and tracking

Analyze the user's financial profile and provide:
1. A detailed monthly budget breakdown (50/30/20 rule or custom)
2. Spending optimization opportunities
3. Realistic savings goals
4. Emergency fund recommendations (3-6 months of expenses)
5. Actionable steps to improve financial health

Be practical, encouraging, and provide specific dollar amounts where possible."""

    def analyze(self, user_profile: UserProfile) -> AgentResponse:
        prompt = self._create_prompt_template()
        
        user_input = f"""
        User Financial Profile:
        - Monthly Income: ${user_profile.monthly_income:,.2f}
        - Monthly Expenses: ${user_profile.monthly_expenses:,.2f}
        - Current Savings: ${user_profile.savings:,.2f}
        - Debt: ${user_profile.debt_amount:,.2f}
        - Age: {user_profile.age}
        - Financial Goals: {user_profile.financial_goals}
        
        Provide a comprehensive budgeting analysis and recommendations.
        """
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_input": user_input,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        # Parse response into structured format
        disposable_income = user_profile.monthly_income - user_profile.monthly_expenses
        savings_rate = (disposable_income / user_profile.monthly_income * 100) if user_profile.monthly_income > 0 else 0
        
        return AgentResponse(
            agent_type=AgentType.BUDGETING,
            recommendations=[
                f"Allocate 50% (${user_profile.monthly_income * 0.5:,.2f}) to needs",
                f"Allocate 30% (${user_profile.monthly_income * 0.3:,.2f}) to wants",
                f"Allocate 20% (${user_profile.monthly_income * 0.2:,.2f}) to savings/debt",
                f"Build emergency fund of ${user_profile.monthly_expenses * 6:,.2f}",
                "Track expenses using budgeting app for 30 days"
            ],
            analysis=response.content,
            key_metrics={
                "current_savings_rate": f"{savings_rate:.1f}%",
                "disposable_income": f"${disposable_income:,.2f}",
                "emergency_fund_target": f"${user_profile.monthly_expenses * 6:,.2f}",
                "monthly_savings_potential": f"${max(0, disposable_income):,.2f}"
            },
            action_items=[
                "Set up automatic transfers to savings account",
                "Review and categorize last 3 months of expenses",
                "Identify 3 areas to reduce discretionary spending",
                "Open high-yield savings account for emergency fund"
            ]
        )