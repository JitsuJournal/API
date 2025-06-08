# TODO: Handle any errors in the middle, passing msgs w/ appropriate error codes)
# System
from typing import Annotated
# Local
from src.models import Reactflow
from src.models.general import Solution, Sequence, Graph
from src.models.general import Node, Edge # Models using for test endpoint
from src.services.llm import conn_gemini, create_paragraph, create_embedding, ground, extract_sequences, create_flowchart
from src.services.db import conn_supabase, similarity_search, get_techniques
#from src.utils.general import shape_nodes, shape_edges
# Third party
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from google.genai import Client as LlmClient
from supabase import Client as DbClient
# For cross origin resource sharing
from fastapi.middleware.cors import CORSMiddleware

# Initialize fast APi
app = FastAPI()


origins = [
    # TODO: Include production front-end URL
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # allow_methods=["*"], NOTE: Default is GET
    allow_headers=["*"],
)

# Placeholder endpoint for webservice root
@app.get('/')
async def root():
    return {"message": "Hello world"}

"""
@app.get('/test', response_model=Reactflow)
def test():
    # --- NOTE: use " instead of -
    Endpoint that returns ReactFlow friendly nodes
    and edges from Sequence 581. Useful for querying
    multiple times to set positions, redirect,
    or test any other feature in the frontend/client side.
    # ---
    # Define constant nodes based on sequence 581
    node_a = Node(
        id=1,
        #id='269f01de-1574-4896-ba3b-9372e07bbc7c', 
        technique=Technique(
            id=34, name='Triangle', 
            description="A technique where the legs are used to encircle the opponent's neck and one arm, creating a triangle shape that constricts blood flow to the brain.",
            tags=[{'id': 10, 'name': 'artery'}],
            cat_id=2
        )
    )
    node_b = Node(
        #id='3a2913de-59d6-4ac9-a957-eeb329b7b74d', 
        id=2,
        technique=Technique(
            id=9, name='Standard Side Control',
            description="Controlling the opponent from the side while pinning their shoulders and hips, maintaining pressure with chest-to-chest contact.",
            tags=[{'id': 2, 'name': 'seated'},{'id': 1, 'name': 'top'}],
            cat_id=1
        )
    )
    node_c = Node(
        #id='b49ffa65-03e7-411d-be7a-6bbaf06543b9', 
        id=3,
        technique=Technique(
            id=3, name='Low Mount',
            description="Sitting directly on the opponent's stomach with knees close to their hips, providing a stable base and control but with limited submission opportunities.",
            tags=[{'id': 1, 'name': 'top'}],
            cat_id=1
        )
    )
    node_d = Node(
        #id='c0c64f73-a9a4-43f9-ad85-37b5a3b57cec', 
        id=4,
        technique=Technique(
            id=41, name='Americana',
            description="Controlling the opponent from the side while pinning their shoulders and hips, maintaining pressure with chest-to-chest contact.",
            tags=[{'id': 11, 'name': 'shoulder'}],
            cat_id=2
        )
    )
    node_e = Node(
        #id='a766adaa-2f18-4285-9b02-94d02e71d63d', 
        id=5,
        technique=Technique(
            id=39, name='Arm Bar',
            description="A joint lock that hyperextends the elbow joint, typically applied by trapping the opponent's arm between your legs and pulling on the wrist while pushing with the hips.",
            tags=[{'id': 12, 'name': 'elbow'}],
            cat_id=2
        )
    )
    # Define constant edges based on sequence 581
    edge_c_d = Edge(
        id=1,
        source_id=3, 
        target_id=4,
        note='Attempt Americana.'
    )
    edge_c_a = Edge(
        id=2, 
        source_id=3, 
        target_id=1,
        note='Opponent frames on hip, collect arm with knee, crossface, grab armpit, and throw leg over for triangle.'
    )
    edge_b_c = Edge(
        id=3,
        source_id=2, 
        target_id=3,
        note='Transition from side control to mount.'
    )
    edge_d_e = Edge(
        id=4,
        source_id=4, 
        target_id=5,
        note='Opponent defends Americana, transition to arm lock.'
    )
    # Pack raw nodes and edges into a list
    rawNodes: list[Node] = [node_a, node_b, node_c, node_d, node_e]
    rawEdges: list[Edge] = [edge_c_d, edge_c_a, edge_b_c, edge_d_e]

    # reshape the constant nodes and edges
    # generating unique ID's for passing back to the user 
    idMap, reshapedNodes = shape_nodes(nodes=rawNodes)
    reshapedEdges = shape_edges(idMap, rawEdges)

    # Initialize ReactFlow object
    # Pack response into ReactFlow model, ensuring type safety
    # use the sequences name as the graph name
    try:
        jitsujournal = Reactflow(name='Sample Side Sequence', 
                                initialNodes=reshapedNodes, initialEdges=reshapedEdges)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to parse output into ReactFlow model. Error: {str(e)}'
        )

    # Return jitsujournal friendly graph to the user
    # FastAPI automatically dumps the model as JSON
    return jitsujournal
"""

# Actual endpoint for processing a given user problem
# NOTE/TODO: Convert to a PUT request to ensure we can send large length
# problems with any special character as required without breaking URL
@app.get('/solve/{problem}', response_model=Graph)#, response_model=Reactflow)
def solve(
        problem: str, 
        gemini: Annotated[LlmClient, Depends(conn_gemini)],
        supabase: Annotated[DbClient, Depends(conn_supabase)],
    ):
    """
    Given a problem faced by the user in their jiu-jitsu practice,
    return a jitsu-journal friendly directed graph/flowchart.
    Passed into the app for creating initial nodes and edges.
    """
    try:
        # Create a hypothetical solution paragraph using the users problem
        hypothetical: Solution = create_paragraph(gemini, problem).parsed
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to create hyde. Error: {str(e)}'
        )

    # Create embedding using the hypothetical solution
    # Used for searching tutorials with similar content
    try:
        embedding = create_embedding(gemini, paragraph=hypothetical.paragraph)
        vector: list[float] = embedding.embeddings[0].values
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to embedd. Error: {str(e)}'
        )

    try:
        # Retrive similar records to the generated solution from Supabase
        # NOTE: Using default match threshold and count for searching
        similar = similarity_search(client=supabase, vector=vector)
        paragraphs: list[str] = [data['content'] for data in similar.data]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to perform vector search. Error: {str(e)}'
        )


    # Use top-k records in similar
    # to gound the hypothetical result
    try:
        grounded: Solution = ground(client=gemini, problem=problem, 
                        paragraphs=paragraphs, solution=hypothetical.paragraph).parsed
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to ground generated solution. Error: {str(e)}'
        )


    # Convert grounded answer into steps in a sequence
    try:
        sequence: Sequence = extract_sequences(client=gemini, paragraph=grounded.paragraph, single=True).parsed
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to extract steps from generated solution. Error: {str(e)}'
        )


    try:
        # Load techniques into memory for passing as context in next stage
        # Using the DB service to fetch from Supabase (w/ joins for tags and cat IDs)
        techniques = get_techniques(client=supabase)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to get techniques from DB. Error: {str(e)}'
        )

    try:
        # Use grounded steps with retrieved techniques
        # and create a basic lightweight directed graph
        flowchart: Graph = create_flowchart(client=gemini, steps=sequence.steps, techniques=techniques).parsed
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to create flowchart using extracted steps. Error: {str(e)}'
        )

    if flowchart==None:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail='Failed to create flowchart, null response.'
        )
    elif flowchart.nodes==None or len(flowchart.nodes)<=0:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail='No nodes generated.'
        )
    elif flowchart.edges==None or len(flowchart.edges)<=0:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail='No edges generated.'
        )

    """
    # Parse nodes and edges into react-flow friendly shapes
    # Swap ID's to UUID's and maintain a map to preserve relations
    try:
        idMap, reshapedNodes = shape_nodes(flowchart.nodes)
        reshapedEdges = shape_edges(idMap, flowchart.edges)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to reformat the nodes and edges. Error: {str(e)}'
        )

    # Pack response into ReactFlow model, ensuring type safety
    # use the sequences name as the graph name
    try:
        jitsujournal = Reactflow(name=sequence.name, 
                                initialNodes=reshapedNodes, initialEdges=reshapedEdges)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to parse output into ReactFlow model. Error: {str(e)}'
        )

    # Return jitsujournal friendly graph to the user
    # FastAPI automatically dumps the model as JSON
    return jitsujournal
    """

    return flowchart


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)