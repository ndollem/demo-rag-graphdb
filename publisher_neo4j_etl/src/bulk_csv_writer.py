import logging
import os

from neo4j import GraphDatabase
from retry import retry

ARTICLES_CSV_PATH = os.getenv("ARTICLES_CSV_PATH")
TRAFFIC_CSV_PATH = os.getenv("TRAFFIC_CSV_PATH")

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

LOGGER = logging.getLogger(__name__)

NODES = ["Reporter", "Category", "Articles", "Traffic"]

def _set_uniqueness_constraints(tx, node):
    query = f"""CREATE CONSTRAINT IF NOT EXISTS FOR (n:{node})
        REQUIRE n.id IS UNIQUE;"""
    _ = tx.run(query, {})

@retry(tries=100, delay=10)
def load_publisher_graph_from_csv() -> None:
    """Load structured articles CSV data following
    a specific ontology into Neo4j"""

    driver = GraphDatabase.driver(
        NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )

    LOGGER.info("Setting uniqueness constraints on nodes")
    with driver.session(database="neo4j") as session:
        for node in NODES:
            session.execute_write(_set_uniqueness_constraints, node)

    LOGGER.info("Loading article nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{ARTICLES_CSV_PATH}' AS row
        MERGE (articles:Articles {{article_id: toInteger(row.article_id)}})
            ON CREATE SET articles.title= row.title, articles.published_at = row.published_at, articles.source = row.source, articles.lead = row.lead, articles.body_content = row.body_content
        MERGE(reporter:Reporter{{reporter_name: row.reporter_name}})
        MERGE(category:Category{{category_name: row.category_name}});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'WROTE' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{ARTICLES_CSV_PATH}' AS row
            MATCH (articles:Articles {{article_id: toInteger(row.article_id)}})
            MATCH (reporter:Reporter {{reporter_name: row.reporter_name}})
            MERGE (reporter)-[wrote:WROTE]->(articles);
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'CONTAIN' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{ARTICLES_CSV_PATH}' AS row
            MATCH (articles:Articles {{article_id: toInteger(row.article_id)}})
            MATCH (category:Category {{category_name: row.category_name}})
            MERGE (category)-[contain:CONTAIN]->(articles);
        """
        _ = session.run(query, {})


    LOGGER.info("Loading traffic nodes")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS
        FROM '{TRAFFIC_CSV_PATH}' AS row
        MERGE (traffic:Traffic {{traffic_date: row.traffic_date}});
        """
        _ = session.run(query, {})

    LOGGER.info("Loading 'GAIN' relationships")
    with driver.session(database="neo4j") as session:
        query = f"""
        LOAD CSV WITH HEADERS FROM '{TRAFFIC_CSV_PATH}' AS row
            MATCH (traffic:Traffic {{traffic_date: row.traffic_date}})
            MATCH (articles:Articles {{article_id: toInteger(row.article_id)}})
            MERGE (articles)-[gain:GAIN]->(traffic)
            ON CREATE SET 
                gain.activeUsers = toInteger(row.activeUsers), 
                gain.sessions = toInteger(row.sessions), 
                gain.screenPageViews = toInteger(row.screenPageViews), 
                gain.screenPageViewsPerSession = toFloat(row.screenPageViewsPerSession), 
                gain.screenPageViewsPerUser = toFloat(row.screenPageViewsPerUser);
        """
        _ = session.run(query, {})


if __name__ == "__main__":
    load_publisher_graph_from_csv()
