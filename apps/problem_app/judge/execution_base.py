from dataclasses import dataclass, field
from typing import List, Any, Optional

@dataclass
class ExecutionResult:
    outputs: List[Any] = field(default_factory=list)
    runtimes: List[float] = field(default_factory=list)
    memory: float = 0.0
    stdout: str = ""
    error: Optional[str] = None
    error_type: Optional[str] = None 
