from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.config import settings

class Intent(BaseModel):
    action: str = Field(description="The primary action identified")
    target: str = Field(description="The target of the action")
    confidence: float = Field(description="Confidence score between 0 and 1")
    params: Dict[str, Any] = Field(description="Extracted parameters")

class IntentParser:
    def __init__(self):
        self.llm = ChatOpenAI(
            base_url=settings.LM_STUDIO_BASE_URL,
            model=settings.LM_STUDIO_MODEL,
            api_key=settings.LM_STUDIO_API_KEY,
            temperature=0.0
        )
        self.parser = JsonOutputParser(pydantic_object=Intent)
        
    def parse(self, user_input: str) -> Dict[str, Any]:
        """
        Parse user input into structured intent.
        """
        prompt = ChatPromptTemplate.from_template(
            "Extract the intent from the following user input.\n"
            "{format_instructions}\n"
            "User Input: {input}"
        )
        
        chain = prompt | self.llm | self.parser
        
        try:
            result = chain.invoke({
                "input": user_input,
                "format_instructions": self.parser.get_format_instructions()
            })
            return result
        except Exception as e:
            return {
                "action": "unknown",
                "target": "unknown",
                "confidence": 0.0,
                "params": {},
                "error": str(e)
            }
