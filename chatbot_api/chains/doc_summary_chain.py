import os

from langchain.chains import RetrievalQA
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    PromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

DOC_QA_MODEL = os.getenv("DOC_QA_MODEL")

neo4j_vector_index = Neo4jVector.from_existing_graph(
    embedding=OpenAIEmbeddings(),
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="articles",
    node_label="Articles",
    text_node_properties=[
        "reporter_name",
        "category_name",
        "body_content",
        "title",
        "published_at",
    ],
    embedding_node_property="embedding",
)

content_template = """Your job is to use article
body_content to answer questions about a specific event or information. Use the following context to answer questions.
Be as detailed as possible, but don't make up any information
that's not from the context. Keep the information language in bahasa indonesia.
If you don't know an answer, say you don't know.
{context}
"""

content_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["context"], template=content_template
    )
)

content_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [content_system_prompt, content_human_prompt]

content_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

summary_vector_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=DOC_QA_MODEL, temperature=0),
    chain_type="stuff",
    retriever=neo4j_vector_index.as_retriever(k=12),
)
summary_vector_chain.combine_documents_chain.llm_chain.prompt = content_prompt