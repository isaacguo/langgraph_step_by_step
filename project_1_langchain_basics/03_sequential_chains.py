"""
LangChain Basics - Sequential Chains
Demonstrates chaining multiple operations together
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import LLMChain, SimpleSequentialChain, SequentialChain

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()

def simple_sequential_chain():
    """Simple sequential chain - output of one becomes input of next"""
    print("=" * 60)
    print("Example 1: Simple Sequential Chain")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    # First chain: Generate a play synopsis
    synopsis_template = ChatPromptTemplate.from_template(
        "Write a synopsis for a play about {topic}"
    )
    synopsis_chain = LLMChain(llm=llm, prompt=synopsis_template)
    
    # Second chain: Review the synopsis
    review_template = ChatPromptTemplate.from_template(
        "Write a review of the following play synopsis:\n{synopsis}"
    )
    review_chain = LLMChain(llm=llm, prompt=review_template)
    
    # Combine into sequential chain
    overall_chain = SimpleSequentialChain(
        chains=[synopsis_chain, review_chain],
        verbose=True
    )
    
    result = overall_chain.invoke("artificial intelligence")
    print(f"\nFinal Review:\n{result['output']}\n")


def sequential_chain_with_variables():
    """Sequential chain with multiple input/output variables"""
    print("=" * 60)
    print("Example 2: Sequential Chain with Multiple Variables")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    # Chain 1: Generate a product name
    name_template = ChatPromptTemplate.from_template(
        "What is a good name for a company that makes {product}?"
    )
    name_chain = LLMChain(
        llm=llm,
        prompt=name_template,
        output_key="company_name"
    )
    
    # Chain 2: Generate a catchphrase
    catchphrase_template = ChatPromptTemplate.from_template(
        "Write a catchphrase for the following company: {company_name}"
    )
    catchphrase_chain = LLMChain(
        llm=llm,
        prompt=catchphrase_template,
        output_key="catchphrase"
    )
    
    # Chain 3: Generate a product description
    description_template = ChatPromptTemplate.from_template(
        "Write a product description for {product} made by {company_name} with the catchphrase: {catchphrase}"
    )
    description_chain = LLMChain(
        llm=llm,
        prompt=description_template,
        output_key="product_description"
    )
    
    # Combine chains
    overall_chain = SequentialChain(
        chains=[name_chain, catchphrase_chain, description_chain],
        input_variables=["product"],
        output_variables=["company_name", "catchphrase", "product_description"],
        verbose=True
    )
    
    result = overall_chain.invoke({"product": "eco-friendly water bottles"})
    
    print(f"Product: eco-friendly water bottles")
    print(f"Company Name: {result['company_name']}")
    print(f"Catchphrase: {result['catchphrase']}")
    print(f"\nProduct Description:\n{result['product_description']}\n")


def conditional_chain_example():
    """Example of conditional logic in chains"""
    print("=" * 60)
    print("Example 3: Conditional Chain Logic")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.3)
    
    # Chain 1: Analyze sentiment
    sentiment_template = ChatPromptTemplate.from_template(
        "Analyze the sentiment of this text and respond with only 'positive', 'negative', or 'neutral': {text}"
    )
    sentiment_chain = LLMChain(
        llm=llm,
        prompt=sentiment_template,
        output_key="sentiment"
    )
    
    # Chain 2: Generate response based on sentiment
    response_template = ChatPromptTemplate.from_template(
        "The text '{text}' has {sentiment} sentiment. Generate an appropriate customer service response."
    )
    response_chain = LLMChain(
        llm=llm,
        prompt=response_template,
        output_key="response"
    )
    
    overall_chain = SequentialChain(
        chains=[sentiment_chain, response_chain],
        input_variables=["text"],
        output_variables=["sentiment", "response"],
        verbose=True
    )
    
    test_texts = [
        "I love this product! Best purchase ever!",
        "This is terrible. I want a refund immediately.",
        "The product arrived on time."
    ]
    
    for text in test_texts:
        result = overall_chain.invoke({"text": text})
        print(f"Text: {text}")
        print(f"Sentiment: {result['sentiment']}")
        print(f"Response: {result['response']}\n")


def multi_step_workflow():
    """Complex multi-step workflow"""
    print("=" * 60)
    print("Example 4: Multi-Step Workflow")
    print("=" * 60)
    
    llm = get_local_llm(temperature=0.7)
    
    # Step 1: Extract key points
    extract_template = ChatPromptTemplate.from_template(
        "Extract the 3 most important points from this text:\n{text}"
    )
    extract_chain = LLMChain(
        llm=llm,
        prompt=extract_template,
        output_key="key_points"
    )
    
    # Step 2: Generate questions
    questions_template = ChatPromptTemplate.from_template(
        "Based on these key points: {key_points}\nGenerate 3 discussion questions."
    )
    questions_chain = LLMChain(
        llm=llm,
        prompt=questions_template,
        output_key="questions"
    )
    
    # Step 3: Create summary
    summary_template = ChatPromptTemplate.from_template(
        "Create a concise summary of:\nKey Points: {key_points}\nDiscussion Questions: {questions}"
    )
    summary_chain = LLMChain(
        llm=llm,
        prompt=summary_template,
        output_key="summary"
    )
    
    overall_chain = SequentialChain(
        chains=[extract_chain, questions_chain, summary_chain],
        input_variables=["text"],
        output_variables=["key_points", "questions", "summary"],
        verbose=True
    )
    
    text = """
    Artificial Intelligence is transforming industries across the globe. 
    Machine learning algorithms can now process vast amounts of data to identify patterns 
    that humans might miss. However, ethical considerations around AI bias and job 
    displacement remain important concerns that need to be addressed.
    """
    
    result = overall_chain.invoke({"text": text})
    
    print("Input Text:")
    print(text.strip())
    print("\n" + "=" * 60)
    print("Key Points:")
    print(result['key_points'])
    print("\n" + "=" * 60)
    print("Discussion Questions:")
    print(result['questions'])
    print("\n" + "=" * 60)
    print("Summary:")
    print(result['summary'])
    print()


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
        simple_sequential_chain()
        sequential_chain_with_variables()
        conditional_chain_example()
        multi_step_workflow()
        
        print("=" * 60)
        print("All sequential chain examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

