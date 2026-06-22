# src/queries.py
import os

QUERIES_DIR = os.path.join(os.path.dirname(__file__), "queries")

def get_query(query_name: str) -> str:
    file_path = os.path.join(QUERIES_DIR, f"{query_name}.sparql")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()