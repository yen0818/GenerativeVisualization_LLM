from typing import Any, Dict, List, Tuple

def prepare_chat_history(chat_history: List[Tuple[str, Any]], k: int) -> str:
    """
    Format last `k` chat histories in tuple (human, ai) into string.
    
    Output:
        Human:
        AI:
        Human:
        AI:
        ...

    """
    history = ""

    for human, ai in chat_history[-k:]:
        format_human = f"Human: {human}\n"
        format_ai = f"AI: {ai}\n"
        history += format_human + format_ai

    return history