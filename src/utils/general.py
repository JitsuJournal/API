# System
import uuid
# Local
from ..models.general import Node, Edge
# Third Party

def shape_nodes(nodes: list[Node]):
    """
    Given a list of Node objects, this function
    iterates over each item and reshapes them to fit
    react-flow and jitsu-journal's initialNodes structure.

    It also additionally returns a idMap used to keep
    edge's source and target ID's consistent with generated UUID's
    """

    # Initialize dict for storing a map of node IDs and their generated UUIDs
    # used to ensure edges reference the generated ID's
    idMap = {}

    # Update nodes shape and store in initialNodes list
    initialNodes = []
    for node in nodes:
        # Node id's need to be UUIDs
        generatedId = str(uuid.uuid4())
        # To ensure this change ripples to edges, 
        # we need store the UUID in a ID map
        idMap[node.id] = generatedId

        # Flatten tags for react-flow.js
        tags = [tag.model_dump() for tag in node.technique.tags]
        
        # Create and append object replacing current node
        # as initial node for react-flow
        initialNodes.append({
            'id': generatedId,

            # Constant for custom node rendering
            'type': 'technique',
            
            # - Placeholder 0,0 for position, 
            # can be added with autolayout 
            # (or LLM/programtically later)
            'position': {'x': 0, 'y': 0},
            
            # Mostly carried over as is from Graph.Node.Techinque
            'data': {
                'technique_id': node.technique.id,
                'name': node.technique.name,
                'tags': tags,
                'cat_id': node.technique.cat_id
            }
        })

    return idMap, initialNodes

def shape_edges(idMap: dict, edges: list[Edge]) -> list[dict]:
    """
    Given a list of Edge objects, this function
    iterates over each item and reshapes them to fit
    react-flow and jitsu-journal's initialEdges structure.

    To ensure that source/target ID's match updated node IDs,
    an ID map is required {old: new}.
    """
    # Update edges shape and store in initialEdges list
    initialEdges = []
    for edge in edges: 
        # Use ID map to reference the node UUID's
        sourceId = idMap[edge.source_id]
        targetId = idMap[edge.target_id]

        # Generate a new edge ID based on the format below:
        # - xy-edge__sourceID-sourceHandle_targetID-targetHandle
        generatedId = f"xy-edge__{sourceId}-b_{targetId}-a"

        initialEdges.append({
            'id': generatedId,
            'type': 'note',
            'source': sourceId,
            'target': targetId,

            # Set fixed source/target handles for all edges
            'sourceHandle': 'b', # Bottom
            'targetHandle': 'a', # Top
            # Carry over note from Graph.Edges.note
            'data': {'note': edge.note}
        })

    return initialEdges