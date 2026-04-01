# agent.py
# The requirements specialist agent — Stage 1
#
# HOW TO RUN:
#   pip install anthropic
#   set ANTHROPIC_API_KEY=your-key-here   (Windows)
#   export ANTHROPIC_API_KEY=your-key     (Mac/Linux)
#   python agent.py

import os
import json
import anthropic

from tools import TOOLS
from system_prompt import SYSTEM_PROMPT

# ─────────────────────────────────────────────
# SET YOUR API KEY HERE if not using environment
# ─────────────────────────────────────────────
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "YOUR_API_KEY_HERE")
client  = anthropic.Anthropic(api_key=API_KEY)


def handle_tool_call(tool_name, tool_input):
    """
    Execute whatever tool Claude decided to call.
    Returns a string result that Claude will read and reason about.

    This is the key concept: Claude decides WHAT to call,
    Python decides HOW to execute it.
    """

    if tool_name == "read_document":
        content    = tool_input["content"]
        word_count = len(content.split())
        return (
            f"Document read. {word_count} words loaded. "
            f"Content is ready for analysis."
        )

    elif tool_name == "extract_requirements":
        reqs  = tool_input["requirements"]
        lines = [f"  {r['id']} [{r['type']}]: {r['text']}" for r in reqs]
        return f"Stored {len(reqs)} requirements:\n" + "\n".join(lines)

    elif tool_name == "ask_user":
        # The agent is unsure — it pauses and asks you
        question = tool_input["question"]
        print(f"\n  Agent needs your input:")
        print(f"  {question}")
        answer = input("  Your answer: ")
        return f"User answered: {answer}"

    elif tool_name == "finish":
        # Signal to stop the loop
        return "DONE"

    else:
        return f"Unknown tool: {tool_name}"


def run_agent(user_message):
    """
    The agent loop.

    This is a ReAct loop:
      1. Claude reasons about what to do
      2. Claude calls a tool
      3. We run the tool and return the result
      4. Claude reads the result and reasons again
      5. Repeat until Claude calls finish()
    """

    print(f"\nUser: {user_message}")
    print("=" * 60)

    # Full conversation history — grows each iteration
    messages = [{"role": "user", "content": user_message}]

    max_iterations = 10  # safety net — prevents infinite loops

    for iteration in range(max_iterations):

        print(f"\n[Iteration {iteration + 1}] Asking Claude what to do next...")

        # ── Ask Claude what to do ──────────────────────────────
        response = client.messages.create(
            model       = "claude-sonnet-4-20250514",
            max_tokens  = 2000,
            system      = SYSTEM_PROMPT,
            tools       = TOOLS,
            messages    = messages
        )

        # ── Did Claude want to call a tool? ───────────────────
        if response.stop_reason == "tool_use":

            # Add Claude's response to conversation history
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []

            for block in response.content:

                # Print any reasoning Claude shared
                if hasattr(block, "text") and block.text:
                    print(f"\n  Claude thinks: {block.text}")

                # Process tool calls
                if block.type == "tool_use":
                    print(f"\n  Claude calls: {block.name}()")

                    # Execute the tool
                    result = handle_tool_call(block.name, block.input)

                    # Check if agent is done
                    if result == "DONE":
                        print("\n" + "=" * 60)
                        print("AGENT FINISHED")
                        print("=" * 60)

                        summary      = block.input.get("summary", "")
                        requirements = block.input.get("requirements", [])

                        print(f"\nSummary: {summary}")
                        print(f"\nRequirements found: {len(requirements)}")
                        for r in requirements:
                            print(f"  {r.get('id','?')} [{r.get('type','?')}]: {r.get('text','')}")

                        return summary, requirements

                    print(f"  Result: {result}")

                    # Collect result to send back to Claude
                    tool_results.append({
                        "type":        "tool_result",
                        "tool_use_id": block.id,
                        "content":     result
                    })

            # Add tool results to history — Claude reads these in the next iteration
            messages.append({"role": "user", "content": tool_results})

        # ── Claude gave a plain text answer (no tool) ─────────
        elif response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(f"\nClaude: {block.text}")
            break

    print("Max iterations reached.")
    return "", []


# ─────────────────────────────────────────────
# RUN THE AGENT
# ─────────────────────────────────────────────
if __name__ == "__main__":

    # Sample requirements document — replace with your own text
    sample_doc = """
    Section 3.2 — User Authentication

    This section describes authentication requirements for the system.
    Authentication is critical for security in healthcare applications.

    The system shall authenticate users before granting access to any feature.
    Login attempts must be limited to 5 before the account is temporarily locked.
    The system shall support multi-factor authentication via SMS or email.
    Passwords must be at least 12 characters long and contain one special character.
    Session tokens should expire after 30 minutes of inactivity.

    Note: See Appendix A for the full security policy.
    """

    run_agent(f"Extract all requirements from this document:\n\n{sample_doc}")
