from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class LoadNode:
    filename: str


@dataclass
class FilterNode:
    column: str
    operator: str
    value: Any


@dataclass
class AggregateNode:
    function: str
    column: Optional[str] = None
    group_by: Optional[str] = None


@dataclass
class PlotNode:
    plot_type: str


@dataclass
class ExportNode:
    filename: str


@dataclass
class CommandNode:
    load: LoadNode
    actions: List[object] = field(default_factory=list)