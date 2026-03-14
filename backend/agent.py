import os
import json
from groq import Groq
from dotenv import load_dotenv
from monday_client import get_work_orders_data, get_deals_data, get_boards_summary

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a Business Intelligence Agent for Skylark Drones, a drone services company.
You have access to two data sources from monday.com:
1. Work_Order_Tracker_Data - Contains project execution data (work orders, clients, status, revenue, sectors)
2. Deal_Funnel_Data - Contains sales pipeline data (deals, stages, values, sectors, probabilities)

Your job is to answer founder-level business questions with meaningful insights, not just raw numbers.

Guidelines:
- Always fetch fresh data before answering
- Cross-reference both boards when needed
- Handle missing/null values gracefully - mention data gaps when relevant
- Provide context and trends, not just numbers
- If data is unclear or missing, say so honestly
- Format responses clearly with sections when needed
- When asked about pipeline, revenue, sectors - give actionable insights
- When asked cross-board questions, fetch work orders first, summarize key findings, then fetch deals. Keep responses concise.

You have these tools available:
- get_work_orders: Fetch all work order data
- get_deals: Fetch all deals/pipeline data  
- get_summary: Get high level overview of both boards
"""

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_work_orders",
            "description": "Fetch all work orders data from monday.com including project status, revenue, clients, sectors and operational metrics",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_deals",
            "description": "Fetch all deals and sales pipeline data from monday.com including deal stages, values, sectors, probability and client info",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_summary",
            "description": "Get a high level summary of both boards - total items, board names and IDs",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    }
]

def truncate_data(data: dict, max_items: int = 15) -> dict:
    """Limit items and columns sent to Groq to avoid token limits"""
    if "data" in data and isinstance(data["data"], list):
        items = data["data"][:max_items]
        # Keep only the most important columns
        key_columns = [
            "name", "Status", "Deal Status", "Deal Stage",
            "Sector/service", "Sector", "Masked Deal value",
            "Closure Probability", "Owner code", "Client Code",
            "Created Date", "Close Date (A)"
        ]
        slimmed = []
        for item in items:
            slim_item = {k: v for k, v in item.items() if k in key_columns}
            slimmed.append(slim_item)
        data["data"] = slimmed
        data["note"] = f"Showing {max_items} of {data.get('total_items', '?')} items"
    return data

def execute_tool(tool_name: str) -> str:
    """Execute a tool and return result as string"""
    try:
        if tool_name == "get_work_orders":
            data = get_work_orders_data()
            data = truncate_data(data, 15)
        elif tool_name == "get_deals":
            data = get_deals_data()
            data = truncate_data(data, 15)
        elif tool_name == "get_summary":
            data = get_boards_summary()
        else:
            return json.dumps({"error": f"Unknown tool: {tool_name}"})

        return json.dumps(data, default=str)
    except Exception as e:
        return json.dumps({"error": str(e)})

def chat(messages: list) -> dict:
    """
    Main chat function - takes conversation history,
    returns AI response with optional chart data
    """
    try:
        # First call to Groq with tools
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            tools=tools,
            tool_choice="auto",
            max_tokens=4096
        )

        message = response.choices[0].message

        # If no tool calls, return direct response
        if not message.tool_calls:
            return {
                "reply": message.content,
                "chartData": None
            }

        # Process tool calls
        tool_results = []
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            result = execute_tool(tool_name)
            tool_results.append({
                "tool_call_id": tool_call.id,
                "tool_name": tool_name,
                "result": result
            })

        # Build messages with tool results for second call
        extended_messages = (
            [{"role": "system", "content": SYSTEM_PROMPT}]
            + messages
            + [{"role": "assistant", "content": message.content or "", "tool_calls": message.tool_calls}]
            + [
                {
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": tr["result"]
                }
                for tr in tool_results
            ]
        )

        # Second call with tool results
        final_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=extended_messages,
            max_tokens=4096
        )

        final_text = final_response.choices[0].message.content

        # Try to extract chart data from tool results
        chart_data = extract_chart_data(tool_results)

        return {
            "reply": final_text,
            "chartData": chart_data
        }

    except Exception as e:
        return {
            "reply": f"Sorry, I encountered an error: {str(e)}",
            "chartData": None
        }

def extract_chart_data(tool_results: list) -> dict | None:
    """Extract structured chart data from tool results for frontend visualization"""
    try:
        for tr in tool_results:
            data = json.loads(tr["result"])
            
            if "error" in data:
                continue

            items = data.get("data", [])
            if not items:
                continue

            sector_counts = {}
            status_counts = {}
            
            for item in items:
                # Exact column names from your monday.com board
                sector = (
                    item.get("Sector/service") or
                    item.get("Sector") or
                    item.get("Industry") or
                    "Unknown"
                )
                if sector and sector not in ("N/A", "", "Unknown"):
                    sector_counts[sector] = sector_counts.get(sector, 0) + 1

                status = (
                    item.get("Deal Status") or
                    item.get("Deal Stage") or
                    item.get("Status") or
                    item.get("Stage") or
                    "Unknown"
                )
                if status and status not in ("N/A", "", "Unknown"):
                    status_counts[status] = status_counts.get(status, 0) + 1

            if sector_counts or status_counts:
                return {
                    "sectorData": [
                        {"name": k, "value": v}
                        for k, v in sorted(sector_counts.items(), key=lambda x: x[1], reverse=True)
                    ],
                    "statusData": [
                        {"name": k, "value": v}
                        for k, v in sorted(status_counts.items(), key=lambda x: x[1], reverse=True)
                    ]
                }

        return None

    except Exception:
        return None
    
