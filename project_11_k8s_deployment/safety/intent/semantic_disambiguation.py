from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from app.config import settings

class SemanticDisambiguator:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.LM_STUDIO_BASE_URL,
            model=settings.LM_STUDIO_MODEL,
            api_key=settings.LM_STUDIO_API_KEY,
            temperature=0.3
        )

    def check_ambiguity(self, user_input: str, context: List[Dict] = []) -> Dict[str, Any]:
        """
        Check if the input is ambiguous and requires clarification.
        """
        prompt = ChatPromptTemplate.from_template(
            "Analyze if the following user input is ambiguous or has multiple possible interpretations "
            "that could lead to unsafe or unintended actions.\n"
            "Context: {context}\n"
            "Input: {input}\n\n"
            "Respond with 'YES' if ambiguous, followed by a list of possible interpretations. "
            "Respond with 'NO' if clear."
        )
        
        response = self.llm.invoke({
            "input": user_input,
            "context": str(context[-3:]) if context else "None"
        })
        
        content = response.content.strip()
        is_ambiguous = content.upper().startswith("YES")
        
        return {
            "is_ambiguous": is_ambiguous,
            "analysis": content
        }

    def generate_clarification_question(self, user_input: str, analysis: str) -> str:
        """
        Generate a question to clarify the user's intent.
        """
        prompt = ChatPromptTemplate.from_template(
            "The user input '{input}' was found to be ambiguous: {analysis}\n"
            "Generate a polite question to ask the user to clarify their intent."
        )
        
        response = self.llm.invoke({
            "input": user_input,
            "analysis": analysis
        })
        
        return response.content.strip()
