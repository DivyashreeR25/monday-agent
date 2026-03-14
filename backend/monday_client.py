import requests
import os
from dotenv import load_dotenv

load_dotenv()

MONDAY_API_TOKEN = os.getenv("MONDAY_API_TOKEN")
MONDAY_API_URL = "https://api.monday.com/v2"

headers = {
    "Authorization": MONDAY_API_TOKEN,
    "Content-Type": "application/json",
    "API-Version": "2024-01"
}

def run_query(query: str) -> dict:
    """Execute a GraphQL query against monday.com API"""
    try:
        response = requests.post(
            MONDAY_API_URL,
            json={"query": query},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def get_all_boards() -> list:
    """Get all boards and their IDs"""
    query = """
    {
        boards {
            id
            name
        }
    }
    """
    result = run_query(query)
    if "error" in result:
        return []
    return result.get("data", {}).get("boards", [])

def get_board_items(board_id: str) -> list:
    """Get all items and column values from a board"""
    query = f"""
    {{
        boards(ids: {board_id}) {{
            name
            items_page(limit: 200) {{
                items {{
                    id
                    name
                    column_values {{
                        column {{
                            title
                        }}
                        text
                        value
                    }}
                }}
            }}
        }}
    }}
    """
    result = run_query(query)
    if "error" in result:
        return []
    
    boards = result.get("data", {}).get("boards", [])
    if not boards:
        return []
    
    items = boards[0].get("items_page", {}).get("items", [])
    return items

def get_board_columns(board_id: str) -> list:
    """Get column structure of a board"""
    query = f"""
    {{
        boards(ids: {board_id}) {{
            columns {{
                id
                title
                type
            }}
        }}
    }}
    """
    result = run_query(query)
    if "error" in result:
        return []
    
    boards = result.get("data", {}).get("boards", [])
    if not boards:
        return []
    
    return boards[0].get("columns", [])

def format_items_as_dict(items: list) -> list:
    """Convert raw monday.com items into clean flat dictionaries"""
    formatted = []
    for item in items:
        row = {"name": item.get("name", "Unknown")}
        for col in item.get("column_values", []):
            col_title = col.get("column", {}).get("title", "unknown")
            col_text = col.get("text", "") or ""
            row[col_title] = col_text.strip() if col_text else "N/A"
        formatted.append(row)
    return formatted

def get_work_orders_data() -> dict:
    """Fetch and return all work orders data"""
    boards = get_all_boards()
    
    # Find work orders board (flexible name matching)
    work_order_board = None
    for board in boards:
        name_lower = board["name"].lower()
        if any(keyword in name_lower for keyword in ["work order", "workorder", "work_order", "project"]):
            work_order_board = board
            break
    
    if not work_order_board:
        # Fall back to first board
        if boards:
            work_order_board = boards[0]
        else:
            return {"error": "No boards found"}
    
    items = get_board_items(work_order_board["id"])
    formatted = format_items_as_dict(items)
    
    return {
        "board_name": work_order_board["name"],
        "board_id": work_order_board["id"],
        "total_items": len(formatted),
        "data": formatted
    }

def get_deals_data() -> dict:
    """Fetch and return all deals data"""
    boards = get_all_boards()
    
    # Find deals board (flexible name matching)
    deals_board = None
    for board in boards:
        name_lower = board["name"].lower()
        if any(keyword in name_lower for keyword in ["deal", "sales", "pipeline", "crm"]):
            deals_board = board
            break
    
    if not deals_board:
        # Fall back to second board if available
        if len(boards) > 1:
            deals_board = boards[1]
        elif boards:
            deals_board = boards[0]
        else:
            return {"error": "No boards found"}
    
    items = get_board_items(deals_board["id"])
    formatted = format_items_as_dict(items)
    
    return {
        "board_name": deals_board["name"],
        "board_id": deals_board["id"],
        "total_items": len(formatted),
        "data": formatted
    }

def get_boards_summary() -> dict:
    """Get a high level summary of both boards"""
    boards = get_all_boards()
    summary = []
    for board in boards:
        items = get_board_items(board["id"])
        summary.append({
            "board_id": board["id"],
            "board_name": board["name"],
            "total_items": len(items)
        })
    return {"boards": summary}
