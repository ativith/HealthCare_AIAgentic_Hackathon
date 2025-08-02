import chromadb
from chromadb.utils.embedding_functions import EmbeddingFunction
from openai import OpenAI
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.chat_models import ChatOpenAI
from huggingface_hub import InferenceClient
import os
import hashlib
import time
import json
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# LLM
llm = ChatOpenAI(model="typhoon2-8b-instruct", api_key="dummy", base_url="http://localhost:5555/v1")

# HuggingFace Embedding Client
hf_client = InferenceClient(
    provider="hf-inference",
    api_key="your_huggingface_api_key",
)

class E5EmbeddingFunction:
    def __init__(self, hf_client):
        self.client = hf_client

    def __call__(self, input):
        inputs = [f"passage: {text}" for text in input]
        return self.client.feature_extraction(inputs, model="intfloat/multilingual-e5-large")

    def name(self):
        return "e5-huggingface-inference"

# Paths
DATA_PATH = r"data"
CHROMA_PATH = r"chroma_db"

print(f"Using data path: {DATA_PATH}")
print("Loading documents from PDF files...")
loader = PyPDFDirectoryLoader(DATA_PATH)
documents = loader.load()
print(f"Loaded {len(documents)} documents")
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separators=["\n\n", "\n", " ", ""])
chunks = splitter.split_documents(documents)

# Setup ChromaDB
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
embedding_fn = E5EmbeddingFunction(hf_client=hf_client)
collection = chroma_client.get_or_create_collection(name="contextual_chunks", embedding_function=embedding_fn)

# Prompts
DOCUMENT_CONTEXT_PROMPT = """
<document>
{doc_content}
</document>
"""
CHUNK_CONTEXT_PROMPT = """
ตอบคำถามนี้โดยใช้เฉพาะบริบทด้านล่างนี้
<chunk>
{doc_content}
</chunk>

กรุณาให้บริบทโดยย่อและกระชับ เพื่ออธิบายว่าส่วนนี้เกี่ยวข้องกับเอกสารฉบับเต็มอย่างไร
จุดประสงค์คือเพื่อช่วยให้การค้นหาเนื้อหา (search retrieval) มีประสิทธิภาพยิ่งขึ้น
โปรดตอบเฉพาะบริบทโดยย่อเท่านั้น และอย่าตอบข้อความอื่นใด
"""

def situate_context(doc: str, chunk: str) -> str:
    prompt = DOCUMENT_CONTEXT_PROMPT.format(doc_content=doc) + "\n\n" + CHUNK_CONTEXT_PROMPT.format(doc_content=chunk)
    response = llm.invoke(prompt, max_tokens=200, temperature=0.1)
    return response.content

# Index new chunks into Chroma
full_doc_text = "\n\n".join([d.page_content for d in documents])
existing_ids = set(collection.get()["ids"])

for idx, doc_chunk in enumerate(chunks):
    chunk_text = doc_chunk.page_content
    uid = f"pdf_{idx}_" + hashlib.md5(chunk_text.encode("utf-8")).hexdigest()

    if uid in existing_ids:
        print(f"[!] Skipping chunk {idx} (already exists)")
        continue

    try:
        context = situate_context(chunk_text[:1500], chunk_text)
        full_chunk = context.strip() + "\n\n" + chunk_text
        collection.upsert(
            ids=[uid],
            documents=[full_chunk],
            metadatas=[{"chunk_index": idx, "context": context}]
        )
        print(f"[✓] Added chunk {idx}")
    except Exception as e:
        print(f"[✗] Failed to add chunk {idx}: {e}")

# Util
def ask_llm(messages) -> dict:
    response = llm.invoke(messages, max_tokens=300, temperature=0.1)
    try:
        return json.loads(response.content)
    except json.JSONDecodeError:
        return {"answer": "", "reason": "ไม่สามารถแปลงคำตอบเป็น JSON ได้"}

def search_chunks(query, top_k=3):
    query_embedding = "query: " + query
    results = collection.query(query_texts=[query_embedding], n_results=top_k)
    return results['documents'][0]

def generate_answer_with_feedback(query) -> dict:
    chunks = search_chunks(query)
    context = "\n\n".join(chunks)
    
    messages = [
        {"role": "system", "content": """คุณมีหน้าที่เลือกคำตอบที่ถูกต้องที่สุดจากบริบท และอธิบายเหตุผลประกอบ

คำตอบต้องอยู่ในรูปแบบ JSON ดังนี้:
{
  "answer": "ตัวเลือกที่ถูกต้อง เช่น ก",
  "reason": "คำอธิบายเหตุผล"
}

ห้ามตอบนอกเหนือจาก JSON นี้โดยเด็ดขาด
"""}, 
        {"role": "user", "content": f"""กรุณาตอบคำถามนี้โดยอิงจากบริบทที่ให้ไว้ด้านล่างเท่านั้น:

Context:
---------
{context}

Question:
{query}
"""}
    ]
    initial_answer = ask_llm(messages)

    # ตรวจสอบความเพียงพอของคำตอบ
    feedback_prompt = [
        {"role": "system", "content": "คุณคือผู้ช่วยด้าน meta-reasoning"},
        {"role": "user", "content": f"""
คำถาม: "{query}"

คำตอบที่ได้รับ:
"{initial_answer['answer']}"

โปรดตรวจสอบว่า คำตอบนี้ได้รับการสนับสนุนอย่างเพียงพอจากบริบทที่ให้ไว้หรือไม่:
- ถ้า "ใช่" ให้ตอบเพียงว่า: คำตอบเพียงพอและได้รับการสนับสนุนอย่างดี
- ถ้า "ไม่ใช่" ให้เสนอ query ที่ควรใช้แทน โดยตอบในรูปแบบ:
query: [ข้อความค้นหาใหม่]
**ห้ามตอบคำอธิบายอื่น**
"""}
    ]
    feedback_result = llm.invoke(feedback_prompt, max_tokens=200).content.strip()

    if feedback_result.lower().startswith("query:"):
        refined_query = feedback_result.split("query:")[-1].strip(":.\n\" ")
        new_chunks = search_chunks(refined_query)
        new_context = "\n\n".join(new_chunks)

        new_prompt = [
            {"role": "system", "content": """คุณมีหน้าที่เลือกคำตอบที่ถูกต้องที่สุดจากบริบท และอธิบายเหตุผลประกอบ

คำตอบต้องอยู่ในรูปแบบ JSON ดังนี้:
{
  "answer": "ตัวเลือกที่ถูกต้อง เช่น ก",
  "reason": "คำอธิบายเหตุผล"
}

ห้ามตอบนอกเหนือจาก JSON นี้โดยเด็ดขาด
"""}, 
            {"role": "user", "content": f"""Context:
---------
{new_context}

Original Question:
{query}
"""}
        ]
        final_answer = ask_llm(new_prompt)
        return final_answer
    else:
        return initial_answer