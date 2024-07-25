# RAG Agent with Neo4J GraphDB

This project simulates a Retrieval-Augmented Generation (RAG) agent system using Neo4j GraphDB. It includes an ETL process, a Backend API, and a Frontend User Interface with AI capabilities. The project leverages OpenAI models as the Language Learning Model (LLM).

## Table of Contents
- [Requirements](#requirements)
- [Installation](#installation)
- [Environment Variables](#environment-variables)
- [Publisher Neo4j ETL](#publisher-neo4j-etl)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Requirements

- A Neo4j Graph DB account
- An OpenAI API key


### Environment Variables
Set your .env environment by filling constant on the .env_sample


## Installation

The preparation of the project need to be done in several steps below :

```bash
# Clone the repository
git clone https://github.com/yourusername/yourproject.git

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate

# On Unix or MacOS
source venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt
```

## Publisher Neo4j ETL

This project is designed to load structured articles and traffic data into a Neo4j database. The data is sourced from CSV files on data directory and follows a specific ontology to create nodes and relationships in the graph database.
Before run the etl, make sure the CSV file uploaded into a public url in order the ETL to works, since it will read the data from public url.
Run this command to execute the ETL :
```bash
publisher_neo4j_etl/src/entrypoint.sh
```

## Usage

There are 2 parts of service on this project :
The Backend RAG API services on chatbot_api directory
The Frontend UI on fe directory
Run these services separately by following these steps :

### Run Backend

Run this command, and it will make the API service available on your localhost port 8000
```bash
chatbot_api/entrypoint.sh
```
It works, you can check on your browser with this url : http://localhost:8000/
It should display the running status

### Run Frontend

Since we use streamlit for the frontend UI, it should be easy to run the service just execute this command :
```bash
streamlit run fe/main.py 
```
If it works, you can check on your browser using this url : http://localhost:8501/