# TODO: Handle any errors in the middle, passing msgs w/ appropriate error codes)
# System
import json
from typing import Annotated
# Local
from src.models.general import Sequence, Graph
from src.services.llm import conn_gemini, create_paragraph, create_embedding, ground, extract_sequences, create_flowchart
from src.services.db import conn_supabase, similarity_search, get_techniques
# Third party
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, Body
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
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Placeholder endpoint for webservice root
@app.get('/')
async def root():
    return {"message": "Hello world"}

@app.get('/test', response_model=Graph)
def test():
    """
    Endpoint that returns a basic list of nodes with technique ID
    and edges that reference the nodes as source/target using ID's,
    and finally also contains optional notes describing transitions
    in more detail.
    """
    data = {
        "name": "Mount Attack Sequence",
        "nodes": [
            {
            "id": 1,
            "technique_id": 3
            },
            {
            "id": 2,
            "technique_id": 31
            },
            {
            "id": 3,
            "technique_id": 32
            },
            {
            "id": 5,
            "technique_id": 25
            },
            {
            "id": 6,
            "technique_id": 32
            }
        ],
        "edges": [
            {
            "id": 1,
            "source_id": 1,
            "target_id": 2,
            "note": "Option 1: Cross-Collar Choke"
            },
            {
            "id": 2,
            "source_id": 1,
            "target_id": 3,
            "note": "If opponent defends choke by pushing your arm, transition to armbar"
            },
            {
            "id": 3,
            "source_id": 1,
            "target_id": 5,
            "note": "If opponent turns away from armbar, take their back"
            },
            {
            "id": 4,
            "source_id": 5,
            "target_id": 6,
            "note": "From back control, secure collar control, tilt head, lengthen arm for choke."
            }
        ]
    }
    return Graph(**data)

# Actual endpoint for processing a given user problem
# NOTE/TODO: Convert to a PUT request to ensure we can send large length
# problems with any special character as required without breaking URL
@app.post('/solve/', response_model=Graph)#, response_model=Reactflow)
def solve(
        problem: Annotated[str, Body()],
        gemini: Annotated[LlmClient, Depends(conn_gemini)],
        supabase: Annotated[DbClient, Depends(conn_supabase)],
    ):
    """
    Given a problem faced by the user in their jiu-jitsu practice,
    return a jitsu-journal friendly directed graph/flowchart.
    Passed into the app for creating initial nodes and edges.
    """
    try:
        # Create a hypothetical solution using the users problem
        hypothetical: str = create_paragraph(gemini, problem).text
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to create hyde. Error: {str(e)}'
        )

    # Create embedding using the hypothetical solution
    # Used for searching tutorials with similar content
    try:
        embedding = create_embedding(gemini, paragraph=hypothetical)
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
        # Flatten into a json string to pass to LLM for grounding
        paragraphs: str = json.dumps([{
                'name': sequence['name'],
                'paragraph': sequence['content']
            } for sequence in similar.data]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to perform vector search. Error: {str(e)}'
        )


    # Use top-k records in similar
    # to gound the hypothetical result
    try:
        grounded = ground(client=gemini, problem=problem, 
                        solution=hypothetical, similar=paragraphs)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_424_FAILED_DEPENDENCY,
            detail=f'Failed to ground generated solution. Error: {str(e)}'
        )


    # Convert grounded answer into steps in a sequence
    try:
        extracted: list[Sequence] = extract_sequences(client=gemini, paragraph=grounded.text).parsed
    
        # iterate over parsed sequences and dump into dict
        # for passing back into model as json string
        sequences: str = json.dumps([sequence.model_dump() for sequence in extracted])
    
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
        flowchart: Graph = create_flowchart(client=gemini, sequences=sequences,
                                            techniques=techniques).parsed
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
    else:
        # Update the flowchart names to use the grounded solution
        # preserving more verbose content/clarity
        flowchart.name = grounded.name
    """

    # Return generated directed graph/flowchart to the user
    # FastAPI automatically dumps the model as JSON
    return flowchart


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)