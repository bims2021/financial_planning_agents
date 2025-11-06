import gradio as gr
import os
from dotenv import load_dotenv
from config import UserProfile
from orchestrator import FinancialAdvisorOrchestrator

load_dotenv()

def create_gradio_interface():
    """Create the Gradio interface"""
    
    def analyze_finances(monthly_income, monthly_expenses, debt_amount, debt_rate, 
                        savings, investment_exp, risk_tolerance, age, goals, api_key):
        """Main analysis function"""
        try:
            profile = UserProfile(
                monthly_income=monthly_income,
                monthly_expenses=monthly_expenses,
                debt_amount=debt_amount,
                debt_interest_rate=debt_rate,
                savings=savings,
                investment_experience=investment_exp,
                risk_tolerance=risk_tolerance,
                age=age,
                financial_goals=goals
            )
            
            orchestrator = FinancialAdvisorOrchestrator(api_key=api_key)
            report = orchestrator.analyze(profile)
            return report
            
        except Exception as e:
            return f"❌ Error: {str(e)}\n\nPlease check your inputs and API key."
    
    # Create interface
    with gr.Blocks(title="AI Financial Advisor", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 🏦 AI Financial Advisory System")
        gr.Markdown("Get personalized financial advice from three specialized AI agents")
        
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 📋 Your Financial Profile")
                
                monthly_income = gr.Number(label="Monthly Income ($)", value=5000, minimum=0)
                monthly_expenses = gr.Number(label="Monthly Expenses ($)", value=3500, minimum=0)
                
                with gr.Row():
                    debt_amount = gr.Number(label="Total Debt ($)", value=0, minimum=0)
                    debt_rate = gr.Number(label="Avg Interest Rate (%)", value=0, minimum=0, maximum=100)
                
                savings = gr.Number(label="Current Savings ($)", value=10000, minimum=0)
                age = gr.Number(label="Age", value=30, minimum=18, maximum=100)
                
                investment_exp = gr.Dropdown(
                    label="Investment Experience",
                    choices=["beginner", "intermediate", "advanced"],
                    value="beginner"
                )
                
                risk_tolerance = gr.Dropdown(
                    label="Risk Tolerance",
                    choices=["conservative", "moderate", "aggressive"],
                    value="moderate"
                )
                
                goals = gr.Textbox(
                    label="Financial Goals",
                    placeholder="E.g., Save for house, retire by 55, pay off student loans...",
                    lines=3
                )
                
                api_key = gr.Textbox(
                    label="OpenAI API Key",
                    placeholder="sk-...",
                    type="password"
                )
                
                analyze_btn = gr.Button("🚀 Analyze My Finances", variant="primary", size="lg")
            
            with gr.Column():
                gr.Markdown("### 📊 Your Personalized Financial Plan")
                output = gr.Textbox(
                    label="Analysis Report",
                    lines=25,
                    show_copy_button=True
                )
        
        analyze_btn.click(
            fn=analyze_finances,
            inputs=[monthly_income, monthly_expenses, debt_amount, debt_rate, 
                   savings, investment_exp, risk_tolerance, age, goals, api_key],
            outputs=output
        )
        
        gr.Markdown("""
        ---
        ### 🤖 About the Agents
        - **Budgeting Agent**: Senior advisor with 15+ years experience
        - **Investment Agent**: CFA charterholder specializing in asset allocation
        - **Debt Management Agent**: Certified credit counselor
        """)
    
    return demo

if __name__ == "__main__":
    app = create_gradio_interface()
    app.launch(share=True)