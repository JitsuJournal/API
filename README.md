# JitsuJournal API

LLM based API for generating jiu-jitsu sequences given a users problem. Built with FastAPI and Gemini, this repository powers JitsuJournal's "Ask AI" feature.

# AI/LLM Pipeline

## Diagram

Sample image showing an illustration of the models, db store, log flow, and other info.

## Summary

- Step 1: Generate a jiu-jitsu sequence as the solution to a users problem/prompt [1]
- Step 2: Use the generated sequence to perform a similarity search and retrieve sequences from real youtube tutorials [2]
- Step 3: Use the retrieved sequences to ground the generated solution, increasing correctness
- Step 4: Breakdown grounded sequence into steps and convert into a react-flow like direct-graph data-structure
- Step 5: Rename sequence and recreate notes using the directed-graph and retrieved/generated sequences.

[1] [Gao, Luyu, et al. "Precise zero-shot dense retrieval without relevance labels." Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2023.](https://arxiv.org/abs/2212.10496)
[2] [Lewis, Patrick, et al. "Retrieval-augmented generation for knowledge-intensive nlp tasks." Advances in neural information processing systems 33 (2020): 9459-9474.](https://arxiv.org/abs/2005.11401)

# Architecture

## Database

Supabase[link] and PostgreSQL[link] are being used as the primary persistent data store. In addition to maintaing a table with the techniques, PostgreSQL's vector store mode is also used for storing the embededed youtube tutorials sequences and perform similarity search.

## AI
Google's Gemini models are being used throughout the LLM service functions for their low to free costs, large input and output token limits, and generous rate limits. The Gen AI library provided by Google for developers has a really beautiful interface, making it really easy to generate structured output with the help of PyDantic models.

As shown in the diagram above, we use different Gemini models:
- Gemini-2.0-flash-lite: Used in steps 1, 3, 4, and 5. This model was chosen for it's fast response and high input token limit.
- Gemini-2.5-flash-preview-05-20: Was the smartest model that was free. Although it can be used in replacement of Gemini-2.0-flash-lite, we've currently commented it out since it has lower rate limits.
- text-embedding-004: Used for creating embeddings of tutorials and hyde doc for RAG.

## API

Implemented the API/HTTP layer using Fast API. It's simple interface makes it the best option for minimizing boiler plate code. The Supabase and Gemini clients are injected as dependencies to the endpoint responsible of solving users jiu-jitsu problem. Response models and request body parameters are type safed using PyDantic models.

Render's platform and tooling for web services is being used for hosting.

## Auth

To facilitate rate limiting for API endpoints, we use UUID's generated when users sign up on JitsuJournal and keep track of their usage. When a new request is received, we check if the sum of their usage is within their assigned limit for a period (e.x. 50 per month).

UUID's are not required for contributing to the LLM pipeline, read setup instruction below.

# Sample

## API Request

### Input
```
// API request from client-side/front-end 
// you can also use tools like postman for sending a request

import axios from 'axios';

const response = await axios.post(
    `https://api-g5to.onrender.com/solve/`,
    {user_id, problem}
);
```

### Output
```
// Recommened: Implement your own error handling logic
// If no errors, print results
console.log(response.data);
```
```
{
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
```
Note: Send a GET request to https://api-g5to.onrender.com/sample for quickly getting sample data when building UI and other downstream applications.

## LLM Service
### Input
```
# .env file
GEMINI_CLIENT = 'YOUR_KEY'
```
```
from Gemini import conn_gemini, generate_hypothetical, 
from Models import Solution

# After setting gemini key in .env
client = conn_gemini()

problem: str = ""
response: Solution = generate_hypothetical(
    client=client,
    problem=problem
)

print(response)
```
### Output
```
# Pull from the logged responses
# Don't even need to regenerate
```

# Contribution Guide

## Setup Dev. Env.

## Open Pull Request

When you are done with your fork or branch and pushed any commits and changes, you an open a pull request to fork

## Contact

- Discord
- Email
