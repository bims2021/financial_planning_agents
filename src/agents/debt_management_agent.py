from .base_agent import BaseFinancialAgent
from config import AgentResponse, AgentType, UserProfile


class DebtManagementAgent(BaseFinancialAgent):
    def get_system_prompt(self) -> str:
        return """You are a Certified Debt Management Specialist and Credit Counselor.

Your expertise includes:
- Debt reduction strategies (avalanche vs. snowball methods)
- Interest rate negotiation
- Credit score improvement
- Debt consolidation analysis
- Payment prioritization

Analyze the user's debt situation and provide:
1. Optimal debt repayment strategy
2. Monthly payment recommendations
3. Interest savings calculations
4. Credit improvement strategies
5. Debt-free timeline projection

Be empathetic and encouraging while providing actionable debt elimination plans."""

    def analyze(self, user_profile: UserProfile) -> AgentResponse:
        prompt = self._create_prompt_template()
        
        user_input = f"""
        User Debt Profile:
        - Total Debt: ${user_profile.debt_amount:,.2f}
        - Average Interest Rate: {user_profile.debt_interest_rate}%
        - Monthly Income: ${user_profile.monthly_income:,.2f}
        - Monthly Expenses: ${user_profile.monthly_expenses:,.2f}
        - Age: {user_profile.age}
        
        Provide a comprehensive debt management strategy and repayment plan.
        """
        
        if user_profile.debt_amount == 0:
            return AgentResponse(
                agent_type=AgentType.DEBT_MANAGEMENT,
                recommendations=["No debt detected - focus on maintaining debt-free status"],
                analysis="Congratulations! You're debt-free. Focus on building wealth.",
                key_metrics={"debt_amount": "$0", "status": "debt_free"},
                action_items=["Maintain emergency fund to avoid future debt"]
            )
        
        chain = prompt | self.llm
        response = chain.invoke({
            "user_input": user_input,
            "format_instructions": self.parser.get_format_instructions()
        })
        
        # Calculate debt metrics
        disposable_income = user_profile.monthly_income - user_profile.monthly_expenses
        suggested_payment = min(disposable_income * 0.5, user_profile.debt_amount * 0.05)
        months_to_payoff = self._calculate_payoff_time(
            user_profile.debt_amount,
            suggested_payment,
            user_profile.debt_interest_rate
        )
        
        return AgentResponse(
            agent_type=AgentType.DEBT_MANAGEMENT,
            recommendations=[
                f"Allocate ${suggested_payment:,.2f}/month to debt repayment",
                "Use avalanche method (highest interest first)",
                "Call creditors to negotiate lower interest rates",
                "Consider balance transfer to 0% APR card if credit allows",
                "Avoid new debt while paying off existing balances"
            ],
            analysis=response.content,
            key_metrics={
                "total_debt": f"${user_profile.debt_amount:,.2f}",
                "suggested_monthly_payment": f"${suggested_payment:,.2f}",
                "months_to_debt_free": f"{months_to_payoff:.0f} months",
                "total_interest_saved": f"${self._calculate_interest_saved(user_profile, suggested_payment):,.2f}"
            },
            action_items=[
                "List all debts with balances and interest rates",
                "Contact highest-rate creditor to negotiate lower APR",
                "Set up automatic debt payments",
                "Cut discretionary spending by 10% to accelerate payoff"
            ]
        )
    
    def _calculate_payoff_time(self, principal: float, payment: float, annual_rate: float) -> float:
        """Calculate months to pay off debt"""
        if payment <= 0 or principal <= 0:
            return 0
        
        monthly_rate = annual_rate / 100 / 12
        if monthly_rate == 0:
            return principal / payment
        
        if payment <= principal * monthly_rate:
            return 999  # Payment too small
        
        import math
        months = -math.log(1 - (principal * monthly_rate / payment)) / math.log(1 + monthly_rate)
        return min(months, 360)  # Cap at 30 years
    
    def _calculate_interest_saved(self, profile: UserProfile, monthly_payment: float) -> float:
        """Calculate interest saved with accelerated payment"""
        months = self._calculate_payoff_time(profile.debt_amount, monthly_payment, profile.debt_interest_rate)
        total_paid = monthly_payment * months
        return max(0, total_paid - profile.debt_amount)