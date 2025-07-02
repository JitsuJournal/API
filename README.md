# JitsuJournal API
LLM pipeline for generating jiu-jitsu sequences given a users problem (i.e. problem/query). Built with FastAPI and Gemini, this repository powers JitsuJournal's "Ask AI" feature.

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

## Auth 
Go over loguse and alternatives to use without that when dev, setup of dev env is expanded on more below

## AI
Structured outputs
Model choices

## API
Fast API endpoints and setup with PyDantic models for type safe


# Sample
## Input
## Output


# Contribution Guide
## Setup Dev. Env.
## Open Pull Request
When you are done with your fork or branch and pushed any commits and changes, you an open a pull request to fork
## Contact
- Discord
- Email