# JitsuJournal API
LLM pipeline for generating jiu-jitsu sequences given a users problem (i.e. problem/query). Built with FastAPI and Gemini, this repository powers JitsuJournal's "Ask AI" feature.

## LLM Pipeline Overview
### Diagram
### Steps
- Generate a jiu-jitsu sequence as the solution to a users problem/prompt
- Use the generated sequence to perform a similarity search and retrieve sequences from real youtube tutorials
- Use the retrieved sequences to ground the generated solution, increasing correctness
- Breakdown gronuded sequence into steps and convert into a react-flow like data-structure
- 