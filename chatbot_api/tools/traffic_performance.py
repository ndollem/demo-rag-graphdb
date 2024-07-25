import os
from typing import Any

import numpy as np
from langchain_community.graphs import Neo4jGraph

def _get_reporter_names() -> list[str]:
    """Fetch a list of reporter names from a Neo4j database."""
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )

    reporter_list = graph.query(
        """
        MATCH (r:Reporters)
        RETURN r.reporter_name AS reporter_name
        """
    )

    reporter_list = [d["reporter_name"].lower() for d in reporter_list]

    return reporter_list


def _get_current_performance(reporter: str) -> int:
    """Get the current reporter article performances."""

    reporter_list = _get_reporter_names()

    if reporter.lower() not in reporter_list:
        return -1

    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD"),
    )

    performance = graph.query(
        """
        MATCH (r:Reporter)-[:WROTE]->(a:Articles)-[g:GAIN]->(t:Traffic) 
        WHERE r.reporter_name = $reporter
        RETURN sum(g.sessions) AS tot_session
        """,
        parameters={"reporter": reporter}
    )

    if performance:
        return performance[0]["tot_session"]
    else:
        return 0


def get_most_productive_reporter(_: Any) -> dict[str, float]:
    """Find most productive reporter based on the tot_session of their articles"""

    reporter_list = _get_reporter_names()
    
    current_reporter_performance = {
        r: _get_current_performance(r) for r in reporter_list
    }

    most_productive_reporter = max(current_reporter_performance, key=current_reporter_performance.get)
    tot_session = current_reporter_performance[most_productive_reporter]

    return {"reporter_name": most_productive_reporter, "tot_session": tot_session}

    
