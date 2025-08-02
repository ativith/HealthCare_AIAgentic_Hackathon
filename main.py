import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from mcptools import callmcp
from rag import generate_answer_with_feedback

app = FastAPI()

class QuestionInput(BaseModel):
    question: str

class AnswerOutput(BaseModel):
    answer: str = Field(description="The answer to the question.")
    reason: str = Field(description="The reason for the answer.")

@app.post("/eval", response_model=AnswerOutput)
async def eval_question(payload: QuestionInput):
    question = payload.question.strip()

    try:
        # เรียก MCP ก่อน
        respond = await callmcp(question)
        prompt = question + " นี้คือข้อมูลจาก mcp " + respond + " พร้อมเหตุผล"
        
        result = generate_answer_with_feedback(prompt)  # return dict: {"answer": ..., "reason": ...}
        result["reason"] += " (ใช้ MCP + RAG)"
        return result

    except Exception as e:
        try:
            # fallback ใช้เฉพาะ RAG
            result = generate_answer_with_feedback(question)
            result["reason"] += " (ใช้เฉพาะ RAG เพราะ MCP ล้มเหลว)"
            return result

        except Exception as inner_e:
            # ทั้งคู่ล้มเหลว
            return {
                "answer": "❌ ERROR",
                "reason": f"ทั้ง MCP และ RAG ล้มเหลว: {str(inner_e)}"
            }