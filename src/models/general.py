from pydantic import BaseModel
from typing import Optional

class UserQuery(BaseModel):
    user_id: str #UUID maps with Supabase
    problem: str

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
    name: str
    # Directed graph representation
    nodes: list[Node]
    edges: list[Edge]