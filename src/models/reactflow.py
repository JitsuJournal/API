from pydantic import BaseModel

class Tag(BaseModel):
    id: int
    name: str

class NodeData(BaseModel):
    sequence_id: str
    technique_id:  str
    name: str
    tags: Tag
    cat_id: str

class Node(BaseModel):
    id: str
    type: str = 'technique'
    position: dict[str, int] = {'x': 0, 'y': 0}
    data: NodeData

class Edge(BaseModel):
    id: str
    type: str = 'note'
    source: str
    target: str
    sourceHandle: str = 'b' # Bottom
    targetHandle: str = 'a' # Top
    data: dict[str, str] # {'note': note as string}

# Response model for the jitsujournal friendly
# directed graph/flowchart
class Reactflow(BaseModel):
    name: str | None = None
    description: str | None = None
    initialNodes: list[Node] # list[Nodes] <- React flow friendly
    initialEdges: list[Edge]