from langchain.schema import HumanMessage, AIMessage
import json
from langchain.agents import Tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_community.chat_models import ChatOpenAI
import os
async def callmcp(question):
    client = MultiServerMCPClient({
        "cmkl": {
            "url": "https://mcp-hackathon.cmkl.ai/mcp",
            "transport": "streamable_http"
        }
    })
    tools = await client.get_tools()
    print("Discovered tools:", [tool.name for tool in tools])

    llm = ChatOpenAI(model= "typhoon2-8b-instruct",api_key="dummy", base_url="http://localhost:5555/v1")
     # Create system message with tools information
    tool_descriptions = []
    for tool in tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}")
    tool_descriptions = []
    for tool in tools:
        tool_descriptions.append(f"- {tool.name}: {tool.description}")

    system_message = f"""ท่านมีหน้าที่เลือกคำตอบที่ถูกต้องและเหมาะสมที่สุดจากบริบทที่ได้รับ โดยพิจารณาจากข้อมูลที่ปรากฏในบริบทดังกล่าว

ข้อกำหนดในการให้คำตอบ:

หากในบริบทมีการใช้คำที่เป็นการทับศัพท์ (transliteration) เช่น "ออร์โธปิดิกส์" ท่านสามารถใช้คำภาษาอังกฤษดั้งเดิม เช่น "Orthopedics" แทนได้

ให้เลือกคำตอบที่ถูกต้องเพียงข้อเดียวจากตัวเลือกที่ให้มา

การตอบกลับต้องอยู่ในรูปแบบของตัวเลือกตัวอักษรที่ถูกต้องที่สุด เช่น "ก" หรือ "ข" หรือ "ค" หรือ "ง" โดยต้องใส่เครื่องหมายคำพูดครอบตัวอักษรไว้เสมอ

ห้ามแสดงคำอธิบาย ข้อมูลเพิ่มเติม หรือข้อความอื่นใดนอกเหนือจากตัวเลือกที่เลือกแล้ว

ตัวอย่างรูปแบบที่ถูกต้อง: "ข"
{chr(10).join(tool_descriptions)}
"""
    # Initialize conversation
    messages = [{"role": "system", "content": system_message}]
    
    # Example user message
    user_message = question
    messages.append({"role": "user", "content": user_message})
    
    # Get response from LLM
    response = await llm.ainvoke([HumanMessage(content=user_message)])
    
    # Check if response contains tool call
    response_content = response.content
    
    try:
        # Try to parse as JSON (tool call)
        tool_call = json.loads(response_content)
        if "tool" in tool_call and "arguments" in tool_call:
            # Find the tool
            tool_name = tool_call["tool"]
            tool_args = tool_call["arguments"]
            
            # Find the tool in our tools list
            selected_tool = None
            for tool in tools:
                if tool.name == tool_name:
                    selected_tool = tool
                    break
            
            if selected_tool:
                print(f"Using tool: {tool_name}")
                print(f"Arguments: {tool_args}")
                
                # Execute the tool
                result = await client.call_tool(tool_name, tool_args)
                print(f"Tool result: {result}")
                
                # Add tool result to conversation and get final response
                messages.append({"role": "assistant", "content": response_content})
                messages.append({"role": "user", "content": f"Tool result: {result}"})
                
                final_response = await llm.ainvoke([HumanMessage(content=f"Tool result: {result}")])
                return final_response.content
            else:
                return f"Tool {tool_name} not found"
        else:
            return response_content
    except json.JSONDecodeError:
        # Not a tool call, just a regular response
        return response_content
