# TODO: Handle any errors in the middle, passing msgs w/ appropriate error codes)
# System
from typing import Annotated
# Local
from src.models.reactflow import Reactflow, Node, NodeData, Edge # Last 3 used for test
from src.models.general import Solution, Sequence, Graph
from src.services.llm import conn_gemini, create_paragraph, create_embedding, ground, extract_sequences, create_flowchart
from src.services.db import conn_supabase, similarity_search, get_techniques
from src.utils.general import shape_nodes, shape_edges
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


@app.get('/test')
def test():
    """
    Endpoint that returns ReactFlow friendly nodes
    and edges from Sequence 581. Useful for querying
    multiple times to set positions, redirect,
    or test any other feature in the frontend/client side.
    """
    node_a = Node(
        id='269f01de-1574-4896-ba3b-9372e07bbc7c', 
        data=NodeData(
            technique_id=34,name='Triangle', 
            tags=[{'id': 10, 'name': 'artery'}],
            cat_id=2
        )
    )
    node_b = Node(
        id='3a2913de-59d6-4ac9-a957-eeb329b7b74d', 
        data=NodeData(
            technique_id=9,name='Standard Side Control', 
            tags=[{'id': 2, 'name': 'seated'},{'id': 1, 'name': 'top'}],
            cat_id=1
        )
    )
    node_c = Node(
        id='b49ffa65-03e7-411d-be7a-6bbaf06543b9', 
        data=NodeData(
            technique_id=3,name='Low Mount', 
            tags=[{'id': 1, 'name': 'top'}],
            cat_id=1
        )
    )
    node_d = Node(
        id='c0c64f73-a9a4-43f9-ad85-37b5a3b57cec', 
        data=NodeData(
            technique_id=41,name='Americana',
            tags=[{'id': 11, 'name': 'shoulder'}],
            cat_id=2
        )
    )
    node_e = Node(
        id='a766adaa-2f18-4285-9b02-94d02e71d63d', 
        data=NodeData(
            technique_id=39,name='Arm Bar', 
            tags=[{'id': 12, 'name': 'elbow'}],
            cat_id=2
        )
    )

    initialNodes: list[Node] = [node_a, node_b, node_c, node_d, node_e]
    print(initialNodes)


    # Setup edges





    # Initialize ReactFlow object
    



    return {"message": "Testing endpoint to pipe data into generateSolution"}


# Actual endpoint for processing a given user problem
# NOTE/TODO: Convert to a PUT request to ensure we can send large length
# problems with any special character as required without breaking URL
@app.get('/solve/{problem}', response_model=Reactflow)
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


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)