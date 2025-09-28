# 🏥 Healthcare AI Agent Chatbot  

An AI-powered healthcare assistant that helps patients and staff access reliable information about **health insurance, state welfare, and hospital services**.  
This project integrates **Retrieval-Augmented Generation (RAG)** for policy-related queries and an **MCP server** for hospital-specific data (e.g., doctor schedules, appointments, patient history).  

---

## 🚀 Features  

### 🔹 Health Insurance & Welfare Support  
- Answers questions about national/state welfare programs.  
- Provides information about insurance policies and coverage.  
- Powered by **RAG** with policy datasets.  

### 🔹 Hospital Information Access  
- Check **doctor work schedules**.  
- Manage and query **patient appointment history**.  
- Access patient records securely via **MCP server**.  

### 🔹 AI Chat Interface  
- Natural conversation powered by **LLMs**.  
- Context-aware responses (public info + hospital data).  

---

## ⚙️ Get Started  

### 1. Create Virtual Environment  
```bash
python3 -m venv .venv
2. Activate Environment
bash
Copy code
# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate
3. Install Dependencies
bash
Copy code
pip install -r requirements.txt
If this has issues, install manually:

bash
Copy code
pip install chromadb
pip install langchain-community
pip install openai
pip install pypdf
pip install python-dotenv
pip install pydantic
4. Run Server
bash
Copy code
uvicorn main:app --host 0.0.0.0 --port 8000
The server will run on port 8000.

📡 Using the RAG API
Example with curl:
bash
Copy code
curl -X POST http://localhost:8000/rag \
    -H "Content-Type: application/json" \
    -d '{"question": "your-question"}'
Example JSON body for Postman:
json
Copy code
{
  "question": "your-question"
}
🧩 Run RAG Standalone
You can also run RAG without API calls:

bash
Copy code
python service/rag.py
⚠️ Disclaimer
This project is for informational and administrative purposes only.
It does not provide medical diagnoses or professional healthcare advice.
Always consult a licensed healthcare provider for medical concerns.

yaml
Copy code

---
