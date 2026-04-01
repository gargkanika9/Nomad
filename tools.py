# tools.py
# These are the tools we give the agent.
# Claude reads these descriptions and decides WHEN and WHETHER to use each one.
# You are not telling Claude the steps — you are giving it capabilities.

TOOLS = [
    {
        "name": "read_document",
        "description": """Read a requirements document and return its raw text.
        Use this first whenever the user gives you a file or pastes text.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The raw text content of the document"
                }
            },
            "required": ["content"]
        }
    },
    {
        "name": "extract_requirements",
        "description": """Extract individual requirements from raw document text.
        Identify sentences that are actual requirements (contain shall/must/will/should).
        Ignore headings, rationale, and background text.
        Return each requirement with its type: functional, non-functional, or constraint.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id":   {"type": "string", "description": "e.g. REQ-001"},
                            "text": {"type": "string", "description": "The exact requirement text"},
                            "type": {"type": "string", "enum": ["functional", "non-functional", "constraint"]}
                        }
                    }
                }
            },
            "required": ["requirements"]
        }
    },
    {
        "name": "ask_user",
        "description": """Ask the user a clarifying question when something is ambiguous
        or you need more information to proceed. Do NOT guess — ask instead.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The specific question you need answered"
                }
            },
            "required": ["question"]
        }
    },
    {
        "name": "finish",
        "description": """Call this when you have completed the task.
        Provide a clear summary of what you found and did.""",
        "input_schema": {
            "type": "object",
            "properties": {
                "summary": {
                    "type": "string",
                    "description": "Summary of what was accomplished"
                },
                "requirements": {
                    "type": "array",
                    "description": "Final list of extracted requirements",
                    "items": {"type": "object"}
                }
            },
            "required": ["summary"]
        }
    }
]
