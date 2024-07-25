import dotenv
from langchain import hub
from langchain.agents import AgentExecutor, Tool, create_openai_functions_agent
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.schema.runnable import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

SURVEY_CHROMA_PATH = "chroma_data/"

dotenv.load_dotenv()

chat_template_str = """Your job is to use user
survey result to answer questions about their experience as a developer. 
Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. If you don't know an answer, say
you don't know.

{context}
"""

# Create a system message prompt template using the provided chat template string.
# This template will use the "context" variable to fill in the details.
chat_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=chat_template_str
    )
)

chat_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [chat_system_prompt, chat_human_prompt]

chat_prompt_template = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

chat_model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0)

output_parser = StrOutputParser()

reviews_vector_db = Chroma(
    persist_directory=SURVEY_CHROMA_PATH,
    embedding_function=OpenAIEmbeddings(),
)

survey_retriever = reviews_vector_db.as_retriever(k=10)

chat_chain = (
    {"context": survey_retriever, "question": RunnablePassthrough()}
    | chat_prompt_template
    | chat_model
    | StrOutputParser()
)

tools = [
    Tool(
        name="Reviews",
        func=chat_chain.invoke,
        description="""Useful when you need to answer questions
        about developer experiences at their company or the tools they use at work.
        Pass the entire question as input to the tool. 
        For instance, if the question is "What is developer biggest problem in their company?",
        the input should be "What is developer biggest problem in their company?"
        """,
    ),
]

survey_agent_prompt = hub.pull("hwchase17/openai-functions-agent")

agent_chat_model = ChatOpenAI(
    model="gpt-3.5-turbo-1106",
    temperature=0,
)

survey_agent = create_openai_functions_agent(
    llm=agent_chat_model,
    prompt=survey_agent_prompt,
    tools=tools,
)

survey_agent_executor = AgentExecutor(
    agent=survey_agent,
    tools=tools,
    return_intermediate_steps=True,
    verbose=True,
)