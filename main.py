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
from fastapi import FastAPI, Depends
from google.genai import Client as LlmClient
from supabase import Client as DbClient

# Initialize fast APi
app = FastAPI()

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

    # Create a hypothetical solution paragraph using the users problem
    hypothetical: Solution = create_paragraph(gemini, problem).parsed

    # Create embedding using the hypothetical solution
    # Used for searching tutorials with similar content
    embedding = create_embedding(gemini, paragraph=hypothetical.paragraph)
    vector: list[float] = embedding.embeddings[0].values

    # Retrive similar records to the generated solution from Supabase
    # NOTE: Using default match threshold and count for searching
    similar = similarity_search(client=supabase, vector=vector)

    paragraphs: list[str] = [data['content'] for data in similar.data]

    # Use top-k records in similar
    # to gound the hypothetical result
    grounded: Solution = ground(client=gemini, problem=problem, 
                      paragraphs=paragraphs, solution=hypothetical.paragraph).parsed

    # Convert grounded answer into steps in a sequence
    sequence: Sequence = extract_sequences(client=gemini, paragraph=grounded.paragraph, single=True).parsed

    # Load techniques into memory for passing as context in next stage
    # Using the DB service to fetch from Supabase (w/ joins for tags and cat IDs)
    techniques = get_techniques(client=supabase)

    # Use grounded steps with retrieved techniques
    # and create a basic lightweight directed graph
    flowchart: Graph = create_flowchart(client=gemini, steps=sequence.steps, techniques=techniques).parsed

    # Parse nodes and edges into react-flow friendly shapes
    # Swap ID's to UUID's and maintain a map to preserve relations
    idMap, reshapedNodes = shape_nodes(flowchart.nodes)
    reshapedEdges = shape_edges(idMap, flowchart.edges)

    # Pack response into ReactFlow model, ensuring type safety
    # use the sequences name as the graph name
    jitsujournal = Reactflow(name=sequence.name, 
                             initialNodes=reshapedNodes, initialEdges=reshapedEdges)

    # Return jitsujournal friendly graph to the user
    # FastAPI automatically dumps the model as JSON
    return jitsujournal


if __name__=="__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)