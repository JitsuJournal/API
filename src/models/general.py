from pydantic import BaseModel
from typing import Optional

class Solution(BaseModel):
    name: str
    paragraph: str

class Relevance(BaseModel):
    score: float
    reason: str

class Sequence(BaseModel):
    name: str
    steps: list[str]

class Node(BaseModel):
    id: int # Unique node id
    technique_id: int

class Edge(BaseModel):
    id: int # Unique edge id
    source_id: int # References Node.id
    target_id: int  # References Node.id
    note: Optional[str] = None

class Graph(BaseModel):
    # Directed graph representation
    nodes: list[Node]
    edges: list[Edge]