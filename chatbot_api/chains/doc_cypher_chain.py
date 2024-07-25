import os

from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI

DOC_QA_MODEL = os.getenv("DOC_QA_MODEL")
DOC_CYPHER_MODEL = os.getenv("DOC_CYPHER_MODEL")

graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

graph.refresh_schema()

cypher_generation_template = """
Task:
Generate Cypher query for a Neo4j graph database.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema:
{schema}

Note:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than
for you to construct a Cypher statement. Do not include any text except
the generated Cypher statement. Make sure the direction of the relationship is
correct in your queries. Make sure you alias both entities and relationships
properly. Do not run any queries that would add to or delete from
the database. Make sure to alias all statements that follow as with
statement (e.g. WITH spv as screenPageViews, c.activeUsers as Active_users)
If you need to divide numbers, make sure to
filter the denominator to be non zero.

Examples:
# What is the latest article titled?
MATCH (a:Articles)
RETURN a.title AS latest_article, a.published_at
ORDER BY a.published_at DESC
LIMIT 1

# How many article on Regional category name?
MATCH (c:Category)-[:CONTAIN]->(a:Articles) 
WHERE c.category_name = "Regional"
RETURN count(a.title);

# Give me the article list on Regional category name?
MATCH (c:Category)-[:CONTAIN]->(a:Articles) 
WHERE c.category_name = "Regional"
RETURN a.title, a.published_at, a.lead;

# How many article on does reporter Muhamad Ridlo wrote?
MATCH (r:Reporter)-[:WROTE]->(a:Articles) 
WHERE r.reporter_name = "Muhamad Ridlo"
RETURN count(a.title);

# Give me the list of article wrote by Muhamad Ridlo!
MATCH (r:Reporter)-[:WROTE]->(a:Articles) 
WHERE r.reporter_name = "Muhamad Ridlo"
RETURN a.title, a.published_at;

# How does the performance of each articles?
MATCH (a:Articles)-[g:GAIN]->(t:Traffic) 
RETURN a.title, sum(g.sessions) AS tot_session, sum(g.screenPageViews) as tot_pageviews, sum(g.activeUsers) as tot_users
ORDER BY tot_session DESC


Make sure to use IS NULL or IS NOT NULL when analyzing missing properties.
Never return embedding properties in your queries. 
You must never include the statement "GROUP BY" in your query. 
Make sure to alias all statements that follow as with statement (e.g. WITH s as sessions, g.screenPageViews as screen_page_views)
If you need to divide numbers, make sure to filter the denominator to be non zero.

The question is:
{question}
"""

cypher_generation_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=cypher_generation_template
)

qa_generation_template = """You are an assistant that takes the results
from a Neo4j Cypher query and forms a human-readable response. The
query results section contains the results of a Cypher query that was
generated based on a users natural language question. The provided
information is authoritative, you must never doubt it or try to use
your internal knowledge to correct it. Make the answer sound like a
response to the question.

Query Results:
{context}

Question:
{question}

If the provided information is empty, say you don't know the answer.
Empty information looks like this: []

If the information is not empty, you must provide an answer using the
results. If the question involves a time duration, assume the query
results are in units of days unless otherwise specified.

When names are provided in the query results, such as reporter names or category names,
beware  of any names that have commas or other punctuation in them.
For instance, 'Muhammad Ali, Tim News' is a single reporter name,
not multiple reporters. Make sure you return any list of names in
a way that isn't ambiguous and allows someone to tell what the full
names are.

Never say you don't have the right information if there is data in
the query results. Make sure to show all the relevant query results
if you're asked.

Helpful Answer:
"""

qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template
)

traffict_cypher_chain = GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(model=DOC_CYPHER_MODEL, temperature=0),
    qa_llm=ChatOpenAI(model=DOC_QA_MODEL, temperature=0),
    graph=graph,
    verbose=True,
    qa_prompt=qa_generation_prompt,
    cypher_prompt=cypher_generation_prompt,
    validate_cypher=True,
    top_k=100,
)