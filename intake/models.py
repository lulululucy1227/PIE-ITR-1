from dataclasses import dataclass, field

@dataclass
class NormalizedCase:
    source_type: str
    source_reference: str = ""
    conversation_title: str = ""
    normalized_messages: list[dict] = field(default_factory=list)
    current_message: str = ""
    quoted_history: str = ""
    needs_human_check: bool = False
