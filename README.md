🏥 Healthcare AI Agent Chatbot

An AI-powered healthcare assistant that helps patients and staff access reliable information about health insurance, state welfare, and hospital services.
This project integrates Retrieval-Augmented Generation (RAG) for policy-related queries and an MCP server for hospital-specific data (e.g., doctor schedules, appointments, patient history).

🚀 Features

Health Insurance & Welfare Support

-Answers questions about national/state welfare programs.

-Provides information about insurance policies and coverage.

-Powered by RAG with policy datasets.

Hospital Information Access

-Check doctor work schedules.

-Manage and query patient appointment history.

-Access patient records securely via MCP server.

AI Chat Interface

-Natural conversation powered by LLMs.

-Context-aware responses (public info + hospital data).


GET STARTED
Create Virture environtment

python3 -m venv .venv
Activate Environtment

source venv/bin/activate
Install Dependencies

```pip install -r requirments.txt```
if this have issue you can install

pip install chromadb
pip install langchain-community
pip install openai
pip install pypdf
pip install python-dotenv
pip install pydantic
Run server

uvicorn main:app --host 0.0.0.0 --port 8000
Server will run on port 8000 and you can use RAG API with this request

curl -X POST http://localhost:5000/rag \
    -H "Content-Type: application/json" \
    -d '{"question": "your-question"}'
or using Postman you can sent JSON like this

{
    "question" : "your-quesion"
}
you can run rag alone without api call by

python service/rag.py
