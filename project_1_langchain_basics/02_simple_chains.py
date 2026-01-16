"""
LangChain Basics - Simple Chains
Demonstrates creating and using chains to combine prompts and LLMs
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import LLMChain

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()

def basic_chain():
    """Basic LLMChain combining prompt and LLM"""
    print("=" * 60)
    print("Example 1: Basic Chain")
    print("=" * 60)
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(
        "Translate the following {language} text to English: {text}"
    )
    
    # Create LLM
    llm = get_local_llm(temperature=0.7)
    
    # Create chain
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # Run chain
    result = chain.invoke({
        "language": "French",
        "text": "Bonjour, comment allez-vous?"
    })
    
    print(f"Input: French - 'Bonjour, comment allez-vous?'")
    print(f"Output: {result['text']}\n")


def chain_with_multiple_inputs():
    """Chain with multiple input variables"""
    print("=" * 60)
    print("Example 2: Chain with Multiple Inputs")
    print("=" * 60)
    
    prompt = ChatPromptTemplate.from_template(
        "Write a {style} email to {recipient} about {topic}."
    )
    
    llm = get_local_llm(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    result = chain.invoke({
        "style": "professional",
        "recipient": "a client",
        "topic": "project deadline extension"
    })
    
    print(f"Style: professional")
    print(f"Recipient: a client")
    print(f"Topic: project deadline extension")
    print(f"\nGenerated Email:\n{result['text']}\n")


def chain_with_output_key():
    """Chain with custom output key"""
    print("=" * 60)
    print("Example 3: Chain with Custom Output Key")
    print("=" * 60)
    
    prompt = ChatPromptTemplate.from_template(
        "Summarize this text in one sentence: {text}"
    )
    
    llm = get_local_llm(temperature=0.7)
    
    # Specify output key
    chain = LLMChain(llm=llm, prompt=prompt, output_key="summary")
    
    result = chain.invoke({
        "text": "LangChain is a framework for developing applications powered by language models. "
                "It enables applications to connect a language model to other sources of data and "
                "interact with its environment."
    })
    
    print(f"Input text: LangChain is a framework...")
    print(f"Summary: {result['summary']}\n")


def chain_batch_processing():
    """Processing multiple inputs in batch"""
    print("=" * 60)
    print("Example 4: Batch Processing")
    print("=" * 60)
    
    prompt = ChatPromptTemplate.from_template(
        "Classify the sentiment of this text as positive, negative, or neutral: {text}"
    )
    
    llm = get_local_llm(temperature=0.3)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    texts = [
        "I love this product! It's amazing.",
        "The service was terrible and slow.",
        "The weather is cloudy today."
    ]
    
    # Process in batch
    results = chain.batch([{"text": text} for text in texts])
    
    print("Batch sentiment analysis:")
    for i, (text, result) in enumerate(zip(texts, results), 1):
        print(f"{i}. Text: {text}")
        print(f"   Sentiment: {result['text']}\n")


def chain_async_processing():
    """Async processing for better performance"""
    print("=" * 60)
    print("Example 5: Async Processing")
    print("=" * 60)
    
    import asyncio
    
    prompt = ChatPromptTemplate.from_template(
        "Generate a creative name for a {type} company."
    )
    
    llm = get_local_llm(temperature=0.8)
    chain = LLMChain(llm=llm, prompt=prompt)
    
    async def run_async():
        company_types = ["tech", "coffee", "fitness", "art"]
        
        # Run multiple chains concurrently
        tasks = [chain.ainvoke({"type": ct}) for ct in company_types]
        results = await asyncio.gather(*tasks)
        
        print("Async company name generation:")
        for company_type, result in zip(company_types, results):
            print(f"  {company_type.capitalize()}: {result['text']}")
        print()
    
    asyncio.run(run_async())


if __name__ == "__main__":
    # Check for LM Studio server
    import requests
    try:
        response = requests.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code != 200:
            print("WARNING: LM Studio server may not be running on port 1234")
    except requests.exceptions.RequestException:
        print("WARNING: Cannot connect to LM Studio server at http://localhost:1234")
        print("Make sure LM Studio is running and the server is started.")
    
    try:
        basic_chain()
        chain_with_multiple_inputs()
        chain_with_output_key()
        chain_batch_processing()
        chain_async_processing()
        
        print("=" * 60)
        print("All chain examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

