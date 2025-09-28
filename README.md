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

```
python3 -m venv .venv
```


### 2. Activate Environment
# Linux / macOS
```
source .venv/bin/activate
```

# Windows (PowerShell)
```
.venv\Scripts\Activate
```

###3. Install Dependencies
```pip install -r requirements.txt```

###4.Run Server
```uvicorn main:app --host 0.0.0.0 --port 8000```

## 📡 Using the RAG API  

### Example with `curl`:  
```
curl -X POST http://localhost:8000/rag \
    -H "Content-Type: application/json" \
    -d '{"question": "your-question"}
```
Example JSON body for Postman:
```
{
  "question": "your-question"
}
```

🧩 Run RAG Standalone

You can also run RAG without API calls:
```
python service/rag.py

```
