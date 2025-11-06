from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from config import UserProfile, AgentResponse

class BaseFinancialAgent(ABC):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model,
            temperature=0.3
        )
        self.parser = PydanticOutputParser(pydantic_object=AgentResponse)
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent"""
        pass
    
    @abstractmethod
    def analyze(self, user_profile: UserProfile) -> AgentResponse:
        """Analyze user profile and return recommendations"""
        pass
    
    def _create_prompt_template(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "{user_input}\n\n{format_instructions}")
        ])