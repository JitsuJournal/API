# TODO: Handle any errors in the middle, passing msgs w/ appropriate error codes)
# System
from typing import Annotated
# Local
from src.models import Reactflow
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
    return{"message": "Hello world"}

# Actual endpoint for processing a given user problem
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