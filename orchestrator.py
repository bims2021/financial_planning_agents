from typing import Dict, List, TypedDict, Annotated, Optional
from src.agents.factory import AgentFactory
from config import UserProfile, AgentResponse, AgentType
from langgraph.graph import StateGraph, END
import operator

from typing import Dict, List, TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END
import operator

class OrchestratorState(TypedDict):
    user_profile: UserProfile
    budgeting_response: Optional[AgentResponse]
    investment_response: Optional[AgentResponse]
    debt_response: Optional[AgentResponse]
    final_report: Optional[str]
    errors: Annotated[List[str], operator.add]
    agents_completed: Annotated[List[str], operator.add]

class FinancialAdvisorOrchestrator:
    """LangGraph-based orchestrator for coordinating multiple financial agents"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.agents = AgentFactory.create_all_agents(api_key)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow - sequential execution to avoid state conflicts"""
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes
        workflow.add_node("budgeting", self._run_budgeting_agent)
        workflow.add_node("investment", self._run_investment_agent)
        workflow.add_node("debt_management", self._run_debt_management_agent)
        workflow.add_node("synthesize", self._synthesize_recommendations)
        
        # Define edges - sequential to avoid parallel state updates
        workflow.set_entry_point("budgeting")
        workflow.add_edge("budgeting", "investment")
        workflow.add_edge("investment", "debt_management")
        workflow.add_edge("debt_management", "synthesize")
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    def _run_budgeting_agent(self, state: OrchestratorState) -> Dict:
        """Execute budgeting agent"""
        try:
            response = self.agents[AgentType.BUDGETING].analyze(state["user_profile"])
            return {
                "budgeting_response": response,
                "agents_completed": ["budgeting"]
            }
        except Exception as e:
            return {"errors": [f"Budgeting agent error: {str(e)}"]}
    
    def _run_investment_agent(self, state: OrchestratorState) -> Dict:
        """Execute investment agent"""
        try:
            response = self.agents[AgentType.INVESTMENT].analyze(state["user_profile"])
            return {
                "investment_response": response,
                "agents_completed": ["investment"]
            }
        except Exception as e:
            return {"errors": [f"Investment agent error: {str(e)}"]}
    
    def _run_debt_management_agent(self, state: OrchestratorState) -> Dict:
        """Execute debt management agent"""
        try:
            response = self.agents[AgentType.DEBT_MANAGEMENT].analyze(state["user_profile"])
            return {
                "debt_response": response,
                "agents_completed": ["debt_management"]
            }
        except Exception as e:
            return {"errors": [f"Debt management agent error: {str(e)}"]}
    
    def _synthesize_recommendations(self, state: OrchestratorState) -> Dict:
        """Synthesize all agent recommendations into a final report"""
        report_sections = []
        
        # Budgeting Section
        if state.get("budgeting_response"):
            report_sections.append(self._format_agent_report(
                "💰 BUDGETING ANALYSIS",
                state["budgeting_response"]
            ))
        
        # Investment Section
        if state.get("investment_response"):
            report_sections.append(self._format_agent_report(
                "📈 INVESTMENT STRATEGY",
                state["investment_response"]
            ))
        
        # Debt Management Section
        if state.get("debt_response"):
            report_sections.append(self._format_agent_report(
                "💳 DEBT MANAGEMENT",
                state["debt_response"]
            ))
        
        # Priority Actions
        priority_actions = self._extract_priority_actions(state)
        if priority_actions:
            report_sections.append(f"\n🎯 TOP PRIORITY ACTIONS:\n" + "\n".join(
                f"{i+1}. {action}" for i, action in enumerate(priority_actions[:5])
            ))
        
        final_report = "\n\n" + "="*80 + "\n\n".join(report_sections)
        return {"final_report": final_report}
    
    def _format_agent_report(self, title: str, response: AgentResponse) -> str:
        """Format individual agent response"""
        report = f"\n{title}\n{'='*80}\n"
        
        # Key Metrics
        report += "\n📊 Key Metrics:\n"
        for key, value in response.key_metrics.items():
            report += f"  • {key.replace('_', ' ').title()}: {value}\n"
        
        # Recommendations
        report += "\n💡 Recommendations:\n"
        for rec in response.recommendations:
            report += f"  • {rec}\n"
        
        # Action Items
        report += "\n✅ Action Items:\n"
        for action in response.action_items:
            report += f"  • {action}\n"
        
        return report
    
    def _extract_priority_actions(self, state: OrchestratorState) -> List[str]:
        """Extract and prioritize actions across all agents"""
        all_actions = []
        
        if state.get("budgeting_response"):
            all_actions.extend(state["budgeting_response"].action_items[:2])
        
        if state.get("debt_response") and state["user_profile"].debt_amount > 0:
            all_actions.extend(state["debt_response"].action_items[:2])
        
        if state.get("investment_response"):
            all_actions.extend(state["investment_response"].action_items[:2])
        
        return all_actions
    
    def analyze(self, user_profile: UserProfile) -> str:
        """Run the complete financial analysis"""
        initial_state = {
            "user_profile": user_profile,
            "budgeting_response": None,
            "investment_response": None,
            "debt_response": None,
            "final_report": None,
            "errors": [],
            "agents_completed": []
        }
        
        result = self.graph.invoke(initial_state)
        
        if result.get("errors"):
            error_msg = "\n".join(result["errors"])
            return f"⚠️ Errors occurred:\n{error_msg}\n\n{result.get('final_report', '')}"
        
        return result.get("final_report", "Analysis completed but no report generated.")

