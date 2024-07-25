import os

from chatbot_api.chains.doc_cypher_chain import traffict_cypher_chain
from chatbot_api.chains.doc_summary_chain import summary_vector_chain
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from chatbot_api.tools.traffic_performance import (
    get_most_productive_reporter,
)

DOC_AGENT_MODEL = os.getenv("DOC_AGENT_MODEL")

# This line pulls the "openai-functions-agent" prompt template from the LangChain hub.
# Check the LangChain hub for the latest updates on the "openai-functions-agent" prompt template.
doc_agent_prompt = hub.pull("hwchase17/openai-functions-agent")

tools = [
    Tool(
        name="Summary",
        func=summary_vector_chain.invoke,
        description="""Useful when you need to answer questions
        about content summary, highlight, or any other qualitative
        question that could be answered about a context of the article content using semantic
        search. Not useful for answering objective questions that involve
        counting, percentages, or aggregations. Use the
        entire prompt as input to the tool. For instance, if the prompt is
        "Give me highlight of what happen on pemilu 2024!", the input should be
        "Give me highlight of what happen on pemilu 2024!".
        """,
    ),
    Tool(
        name="Graph",
        func=traffict_cypher_chain.invoke,
        description="""Useful for answering questions about author, reporter, category, article
        statistics, and article traffict details. Use the entire prompt as
        input to the tool. For instance, if the prompt is "How many pageviews on all article today?", 
        the input should be "How many pageviews on all article today?".
        """,
    ),
    # Tool(
    #     name="Popular",
    #     func=get_popular_articles,
    #     description="""Use when asked about popular or most viewed article at a specific timeline period. 
    #     This tool can only get the list of popular or most viewed articles title and does not have any information about
    #     the article content or summary. 
    #     Pass only words that represent date range as input. For example if the prompt
    #     "Give me the popular article today", the words represent date is today and input should be current date in YYYY-MM-DD format.
    #     "Give me the popular article for the last 7 days", the words represent date is 7 days and input should be the date from 7 days ago from now in YYYY-MM-DD format.
    #     "Give me the popular article for the last 3 month", the words represent date is 3 month and input should be date from 3 month ago from now in YYYY-MM-DD format.
    #     """,
    # ),
    Tool(
        name="Productivity",
        func=get_most_productive_reporter,
        description="""
        Use when you need to find out whos reporter has the most viewed articles. 
        This tool does not have any information about aggregate
        or historical viewed articles. This tool returns a dictionary with the
        reporter name as the key and the total pageviews as the value.
        """,
    ),
]

chat_model = ChatOpenAI(
    model=DOC_AGENT_MODEL,
    temperature=0,
)

doc_rag_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=doc_agent_prompt,
    tools=tools,
)

doc_rag_agent_executor = AgentExecutor(
    agent=doc_rag_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)