"""
Lightweight react-flow representation with
techniques/notes flattened and id's represented in strings.
"""
from pydantic import BaseModel
from typing import Optional

class Node(BaseModel):
    id: str
    name: str
    tags: list[str]

class Edge(BaseModel):
    id: str
    source_id: str
    target_id: str
    note: Optional[str] = None