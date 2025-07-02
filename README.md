# JitsuJournal API
LLM based API for generating jiu-jitsu sequences given a users problem. Built with FastAPI and Gemini, this repository powers JitsuJournal's "Ask AI" feature.

# AI/LLM Pipeline
## Diagram
Sample image showing an illustration of the models, db store, log flow, and other info.
## Summary
- Generate a jiu-jitsu sequence as the solution to a users problem/prompt [1]
- Use the generated sequence to perform a similarity search and retrieve sequences from real youtube tutorials [2]
- Use the retrieved sequences to ground the generated solution, increasing correctness [3]
- Breakdown grounded sequence into steps and convert into a react-flow like direct-graph data-structure
- Rename sequence and recreate notes using the directed-graph and retrieved/generated sequences.

[1] Link/Paper in MLA
[2] Link/Paper in MLA
[3] Link/Paper in MLA

# Architecture
## Database
Supabase[link] and PostgreSQL[link] is being used as the primary persistent data store. In addition to maintaing a table with the techniques, PostgreSQL's vector store mode is also used for storing the embededed youtube tutorials sequences and perform similarity search.

## AI
Structured outputs
Model choices

## API
Implemented the API/HTTP layer using Fast API. It's simple interface makes it the best option for minimizing boiler plate code. The Supabase and Gemini clients are injected as dependencies to the endpoint responsible of solving users jiu-jitsu problem. Response models and request body parameters are type safed using PyDantic models.

## Auth
To facilitate rate limiting for API endpoints, we use UUID's generated when users sign up on JitsuJournal and keep track of their usage. When a new request is received, we check if the sum of their usage is within their assigned limit for a period (e.x. 50 per month).

UUID's are not required for contributing to the LLM pipeline, read setup instruction below.

# Sample
## API Request
### Input
```
// API request from client-side/front-end 
// you can also use tools like postman for sending a request
```
### Output
## LLM Service


# Contribution Guide
## Setup Dev. Env.
## Open Pull Request
When you are done with your fork or branch and pushed any commits and changes, you an open a pull request to fork
## Contact
- Discord
- Email