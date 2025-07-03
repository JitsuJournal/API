# JitsuJournal API

LLM RAG based API for generating jiu-jitsu sequences given a users problem. Built with FastAPI and Gemini, this repository powers JitsuJournal's "Ask AI" feature.

## AI/LLM Pipeline

- Step 1: Generate a jiu-jitsu sequence in text as the solution to a users problem/prompt [\[1\]](https://arxiv.org/abs/2212.10496).
- Step 2: Use the generated sequence to perform a similarity search and retrieve sequences extracted from real youtube tutorials [\[2\]](https://arxiv.org/abs/2005.11401).
- Step 3: Use the retrieved sequences to ground the generated solution, increasing overall correctness.
- Step 4: Breakdown grounded sequence into steps and convert them into a react-flow like light-weight directed-graph data-structure.
- Step 5: Rename sequence and recreate notes using the directed-graph and retrieved/generated sequences as inputs.

[1] [Gao, Luyu, et al. &#34;Precise zero-shot dense retrieval without relevance labels.&#34; Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers). 2023.](https://arxiv.org/abs/2212.10496)

[2] [Lewis, Patrick, et al. &#34;Retrieval-augmented generation for knowledge-intensive nlp tasks.&#34; Advances in neural information processing systems 33 (2020): 9459-9474.](https://arxiv.org/abs/2005.11401)

# Architecture

## Database

[Supabase](https://supabase.com/database) and [PostgreSQL](https://www.postgresql.org/) are being used as the primary persistent data store. In addition to maintaing a table with 100+ techniques, PostgreSQL's [pgector](https://github.com/pgvector/pgvector/) implementation is being used for storing the embededed youtube tutorials sequences and facilitating similarity searches.

## AI

Google's [Gemini models](https://ai.google.dev/gemini-api/docs/models) are being used throughout the LLM service functions for their low-to-free costs and large input/output token limits. Additionally, their [Gen AI library](https://github.com/googleapis/python-genai) for developers has a interface that makes it really easy to generate structured outputs with the help of [PyDantic models](https://docs.pydantic.dev/latest/).

As shown in the diagram above, we use the following models:

- [Gemini-2.0-flash-lite](https://ai.google.dev/gemini-api/docs/models#gemini-2.0-flash-lite): Used in step 1 to 5 (except 2). This model was chosen for it's fast response and high input token limit.
- [Gemini-2.5-flash-preview-05-20](https://ai.google.dev/gemini-api/docs/models#gemini-2.5-flash): Smartest free model (outdated). Although it can be used in replacement of Gemini-2.0-flash-lite, we've currently commented it out since it has lower free rate limits.
- [text-embedding-004](https://ai.google.dev/gemini-api/docs/models#text-embedding): Used for creating embeddings of tutorials and generated solutions to facilitate RAG.

## API

Implemented the API/HTTP layer using [Fast API](https://fastapi.tiangolo.com/). It's simple interface makes it the best option for minimizing boiler plate code. Supabase and Gemini clients are injected as dependencies to the endpoint responsible of solving users jiu-jitsu problem by calling LLM service functions. Response models and request body parameters are type safed using PyDantic models.

[Render&#39;s platform](https://render.com/) and tooling for web services are currently being used for hosting this repo with auto-deployments configured for the main branch.

## Auth

To facilitate usage thresholds, we create a new record in the database with UUID's from JitsuJournal whenever a user tries to call a specific API endpoint. When a new request is received, we check if the sum of a users usage records is within their assigned limit for a set period (e.x. 50 per month).

Note: UUID's are not required for contributing to the LLM pipeline. Read contribution guide for more info.

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

Note: Send a GET request to https://api-g5to.onrender.com/sample for quickly getting sample data when building UI and other downstream applications.

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

## LLM Service

### Input

```
# .env file
GEMINI = 'YOUR_GEMINI_KEY'
```

```
from src.services.llm import conn_gemini, create_paragraph

# After setting gemini key in .env
gemini = conn_gemini()

problem: str = "Show me different ways to break an opponents closed guard when i'm on top and pass it to end up in side control or mount."
response: str = create_paragraph(gemini, problem).text

print(response)
```

### Output

```
Alright, let's break down the closed guard and get you into dominant positions. This is a fundamental skill in Jiu-Jitsu, and we'll cover both gi and no-gi approaches. Remember, the key is to be patient, persistent, and understand the principles of leverage and control.\n\n**The Problem:** You're on top, your opponent has a tight closed guard. You want to pass and establish side control or mount.\n\n**The Goal:** Break the guard, pass, and secure a dominant position (side control or mount).\n\n**The Principles:**\n\n*   **Posture:** Maintain good posture to prevent submissions and create space.\n*   **Base:** Keep your weight distributed and your base wide to avoid being swept.\n*   **Patience:** Don't rush. Break the guard systematically.\n*   **Control:** Control your opponent's limbs to limit their options.\n*   **Pressure:** Apply consistent pressure to break the guard and wear your opponent down.\n*   **Angles:** Use angles to create openings and avoid being caught in submissions.\n\n**The Sequence....
```

# Contribution Guide

## Setup

Follow the instructions below to setup your development envoirnment:

- Step 1: Download or clone the repository
  ```
  git clone https://github.com/JitsuJournal/API.git
  ```
- Step 2: Activate a virtual envoirnment
  ```
  # Mac unix/linux
  source ./venv/bin/activate

  # Windows
  .\venv\Scripts\activate
  ```
- Step 3: Install dependencies from PyPi
  ```
  pip install requirements.txt
  ```
- Step 4: Setup envoirnment variables
  ```
  GEMINI='YOUR_GEMINI_KEY'
  # Supabase keys (optional)
  SUPABASE_URL='YOUR_SUPABASE_URL'
  SUPABASE_KEY='YOUR_SUPABASE_URL'
  ```
Congratulations! You're now ready to start contributing to JitsuJournal's API!

## Pull Requests
When you are done making changes on your fork (or branch), you an open a pull request to merge changes with the main branch.

Follow [PEP 8](https://peps.python.org/pep-0008/) for making your code easy to review and merge:
- Cammel case for variables
- Underscore notation for functions and classes
- Uppercase names for constants
- Pop off with comments!

Note: No PR template at the moment!

## Contact
- Email: harrisiva6@gmail.com (or team@jitsujournal.com)
