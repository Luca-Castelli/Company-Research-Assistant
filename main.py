from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict

from scrape import scrape_website_text

load_dotenv()

# Initialize the ChatOllama model
local_llm = "llama3"
llama3 = ChatOllama(
    model=local_llm,
    base_url="http://host.docker.internal:11434",
    temperature=0,
)
llama3_json = ChatOllama(
    model=local_llm,
    base_url="http://host.docker.internal:11434",
    format="json",
    temperature=0,
)

# Template for extracting website URL from a user question
website_extractor_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|> 

    You are an expert at extracting a website URL from a user question.
    If the question contains a website URL, route the question to the website scraping stage.
    Otherwise, route the question to the generation stage.
    Give a binary choice 'scrape' or 'generate' based on the question. 
    Return JSON with one key 'website'. The value for key 'website' should be the website URL if there is one,
    otherwise, it should be ''. 
    
    <|eot_id|>
    
    <|start_header_id|>user<|end_header_id|>
    
    Question: {question} 

    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question"],
)

website_extractor_chain = website_extractor_prompt | llama3_json | JsonOutputParser()

# Template for generating a report based on scraped website context
reporter_prompt = PromptTemplate(
    template="""
    
    <|begin_of_text|>
    
    <|start_header_id|>system<|end_header_id|> 

    You are an AI assistant tasked with generating a comprehensive report on a specified company.
    Your report should provide a holistic summary that includes key aspects of the company, suitable for someone unfamiliar with the company.
    Use only the information available in the provided context to construct the report.
    Structure the report to include:

    1. **Overview**: Briefly describe the company, including its industry, founding year, and headquarters location.
    2. **Business Model**: Explain the company's core business activities, primary products or services, and its target market.
    3. **Financial Performance**: Summarize recent financial performance, if data is available, focusing on revenue, profit margins, and any known financial challenges.
    4. **Competitive Position**: Discuss the company's position within the industry compared to its main competitors.
    5. **Management and Leadership**: Mention key executives and their roles, highlighting any well-known figures.
    6. **Recent Developments**: Cover any recent news or significant events that have impacted the company.
    7. **Future Outlook**: Provide insights on the companys future direction, potential growth areas, and any upcoming challenges.

    If the context is empty '', respond with: "I wasn't able to find anything. Please make sure you have included the company website."
    If the context is not empty, format your response as a markdown document and generate the report accordingly.

    <|eot_id|>
    
    <|start_header_id|>user<|end_header_id|>
    
    Question: {question} 
    Context: {context} 

    <|eot_id|>
    
    <|start_header_id|>assistant<|end_header_id|>""",
    input_variables=["question", "context"],
)

reporter_chain = reporter_prompt | llama3 | StrOutputParser()


class GraphState(TypedDict):
    question: str
    website: str
    report: str
    context: str


# Workflow functions
def extract_website(state):
    print("Step: Extracting URL")
    question = state["question"]
    output = website_extractor_chain.invoke({"question": question})
    return {"website": output["website"]}


def scrape_router(state):
    print("Step: Scrape Routing")
    return "scrape" if state["website"] else "generate"


def scrape_website(state):
    print(f'Step: Scraping the website {state["website"]}')
    return {"context": scrape_website_text(state["website"])}


def generate_report(state):
    print("Step: Generating Report")
    report = reporter_chain.invoke(
        {"question": state["question"], "context": state["context"]}
    )
    return {"report": report}


# Configure the workflow graph
workflow = StateGraph(GraphState)
workflow.add_node("extract_website", extract_website)
workflow.add_node("scrape_website", scrape_website)
workflow.add_node("generate_report", generate_report)
workflow.set_entry_point("extract_website")
workflow.add_conditional_edges(
    "extract_website",
    scrape_router,
    {"scrape": "scrape_website", "generate": "generate_report"},
)
workflow.add_edge("scrape_website", "generate_report")
workflow.add_edge("generate_report", END)

local_agent = workflow.compile()


def run_agent(query):
    output = local_agent.invoke({"question": query, "context": ""})
    return output["report"]
