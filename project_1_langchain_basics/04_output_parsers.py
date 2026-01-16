"""
LangChain Basics - Output Parsers
Demonstrates structured output parsing from LLM responses
"""

import os
import sys
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import LLMChain
from langchain_classic.output_parsers import (
    PydanticOutputParser,
    CommaSeparatedListOutputParser,
    StructuredOutputParser,
    ResponseSchema
)
from pydantic import BaseModel, Field
from typing import List

# Add utils to path for utility function
_file_dir = os.path.dirname(os.path.abspath(__file__))
_project_root = os.path.abspath(os.path.join(_file_dir, '..'))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
from utils.llm_config import get_local_llm

# Load environment variables
load_dotenv()

def comma_separated_list_parser():
    """Parse comma-separated list output"""
    print("=" * 60)
    print("Example 1: Comma-Separated List Parser")
    print("=" * 60)
    
    parser = CommaSeparatedListOutputParser()
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate a list of items. Format your response as a comma-separated list."),
        ("human", "List 5 programming languages.")
    ])
    
    llm = get_local_llm(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)
    
    result = chain.invoke({})
    print(f"Parsed output: {result['text']}")
    print(f"Type: {type(result['text'])}\n")


def pydantic_output_parser():
    """Parse structured output using Pydantic models"""
    print("=" * 60)
    print("Example 2: Pydantic Output Parser")
    print("=" * 60)
    
    # Define output structure
    class Person(BaseModel):
        name: str = Field(description="Full name of the person")
        age: int = Field(description="Age of the person")
        occupation: str = Field(description="Job title or occupation")
        skills: List[str] = Field(description="List of skills")
    
    parser = PydanticOutputParser(pydantic_object=Person)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate information about a fictional person. {format_instructions}"),
        ("human", "Create a profile for a software engineer.")
    ])
    
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    llm = get_local_llm(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)
    
    result = chain.invoke({})
    person = result['text']
    
    print(f"Name: {person.name}")
    print(f"Age: {person.age}")
    print(f"Occupation: {person.occupation}")
    print(f"Skills: {', '.join(person.skills)}")
    print(f"\nParsed object type: {type(person)}\n")


def structured_output_parser():
    """Parse using ResponseSchema"""
    print("=" * 60)
    print("Example 3: Structured Output Parser")
    print("=" * 60)
    
    response_schemas = [
        ResponseSchema(name="title", description="Title of the book"),
        ResponseSchema(name="author", description="Author of the book"),
        ResponseSchema(name="genre", description="Genre of the book"),
        ResponseSchema(name="rating", description="Rating out of 10"),
        ResponseSchema(name="summary", description="Brief summary of the plot")
    ]
    
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate information about a book. {format_instructions}"),
        ("human", "Create a book recommendation for a science fiction novel.")
    ])
    
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    llm = get_local_llm(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)
    
    result = chain.invoke({})
    book_info = result['text']
    
    print("Book Information:")
    for key, value in book_info.items():
        print(f"  {key.capitalize()}: {value}")
    print()


def complex_pydantic_parser():
    """Complex nested Pydantic model"""
    print("=" * 60)
    print("Example 4: Complex Nested Pydantic Model")
    print("=" * 60)
    
    class Address(BaseModel):
        street: str = Field(description="Street address")
        city: str = Field(description="City name")
        country: str = Field(description="Country name")
        zip_code: str = Field(description="ZIP or postal code")
    
    class Company(BaseModel):
        name: str = Field(description="Company name")
        industry: str = Field(description="Industry sector")
        employees: int = Field(description="Number of employees")
        address: Address = Field(description="Company address")
        founded: int = Field(description="Year founded")
    
    parser = PydanticOutputParser(pydantic_object=Company)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate company information. {format_instructions}"),
        ("human", "Create a profile for a tech startup company.")
    ])
    
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    llm = get_local_llm(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)
    
    result = chain.invoke({})
    company = result['text']
    
    print("Company Profile:")
    print(f"  Name: {company.name}")
    print(f"  Industry: {company.industry}")
    print(f"  Employees: {company.employees}")
    print(f"  Founded: {company.founded}")
    print(f"  Address:")
    print(f"    Street: {company.address.street}")
    print(f"    City: {company.address.city}")
    print(f"    Country: {company.address.country}")
    print(f"    ZIP: {company.address.zip_code}")
    print()


def list_of_objects_parser():
    """Parse a list of structured objects"""
    print("=" * 60)
    print("Example 5: List of Objects Parser")
    print("=" * 60)
    
    class Product(BaseModel):
        name: str = Field(description="Product name")
        price: float = Field(description="Price in USD")
        category: str = Field(description="Product category")
    
    class ProductList(BaseModel):
        products: List[Product] = Field(description="List of products")
    
    parser = PydanticOutputParser(pydantic_object=ProductList)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Generate a list of products. {format_instructions}"),
        ("human", "Create 3 different products for an online store.")
    ])
    
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    
    llm = get_local_llm(temperature=0.7)
    chain = LLMChain(llm=llm, prompt=prompt, output_parser=parser)
    
    result = chain.invoke({})
    product_list = result['text']
    
    print("Products:")
    for i, product in enumerate(product_list.products, 1):
        print(f"{i}. {product.name}")
        print(f"   Category: {product.category}")
        print(f"   Price: ${product.price:.2f}")
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
        comma_separated_list_parser()
        pydantic_output_parser()
        structured_output_parser()
        complex_pydantic_parser()
        list_of_objects_parser()
        
        print("=" * 60)
        print("All output parser examples completed successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

