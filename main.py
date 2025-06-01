# Fast API entry point
from fastapi import FastAPI

# Initialize fast APi
app = FastAPI()


# Placeholder endpoint for webservice root
@app.get('/')
async def root():
    return{"message": "Hello world"}


# TODO:
# Response model for the jitsujournal friendly
# directed graph/flowchart



# Actual endpoint for processing a given user problem
@app.get('/solve/{problem}')
def solve(problem: str):
    """
    Given a problem faced by the user in their jiu-jitsu practice,
    return a jitsu-journal friendly directed graph/flowchart.
    Passed into the app for creating initial nodes and edges.
    """
    print(problem)
    return{"problem": problem}