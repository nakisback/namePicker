"""
models.py

Plain data holders. Nothing in this file prints anything, reads a file, or
makes a decision about who gets called next — it's just the shape of the
data, plus a few tiny convenience lookups that operate only on that shape.
Keeping it this "dumb" is what lets every other module (storage, call
queue, ui, activities) depend on it without also dragging in file I/O or
terminal printing.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List, Optional


@dataclass
class Student:
    id: str
    number: str
    name: str
    gender: str
    group: str = ""
    # One dict for all "how many times called" counters instead of a
    # separate qCount/bCount/jCount attribute. Adding a new callable
    # category later (e.g. a "cCount" for cleanup duty) means adding one
    # line to config.CATEGORIES — nothing here has to change.
    counts: Dict[str, int] = field(default_factory=dict)
    # category -> ISO date string (e.g. "2026-09-12") of the last time this
    # student was called for that category. Empty string means never.
    last_called: Dict[str, str] = field(default_factory=dict)
    #increment: int = 0  # how many times this student has been called in the current session

    def count(self, category: str) -> int: 
        return int(self.counts.get(category, 0))

    # def increment(self, category: str) -> None:
    #     self.counts[category] = self.count(category) + 1

    def last_called_display(self, category: str) -> str:
        """Human-friendly version of last_called, e.g. 'today',
        '3 days ago', or 'never'."""
        raw = self.last_called.get(category, "")
        if not raw:
            return "never"
        try:
            called_on = date.fromisoformat(raw)
        except ValueError:
            return raw
        delta = (date.today() - called_on).days
        if delta == 0:
            return "today"
        if delta == 1:
            return "yesterday"
        if delta < 0:
            return raw  # a future date got in there somehow — just show it raw
        return f"{delta} days ago"

    
    # Added Oct 28, 2026 -- called_today() and record_call()
    def called_today(self, other_than: str = None) -> bool:
        today = date.today().isoformat()
        return any(day == today for cat, day in self.last_called.items()
                if cat != other_than)
  
    def record_call(self, category: str, times: int = 1) -> None:
        """Mirror what save_counts wrote to the CSV, in memory."""
        self.counts[category] = self.count(category) + times
        self.last_called[category] = date.today().isoformat()

    def __str__(self) -> str:
        return f"{self.name} (#{self.number})"

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass
class Group:
    name: str
    members: List[Student] = field(default_factory=list)

    def __str__(self) -> str:
        return f"{self.name} ({len(self.members)} ppl.)"


@dataclass
class Roster:
    room: str
    students: List[Student]

    def find(self, query: str) -> Optional[Student]:
        """Looks a student up by name. Exact match wins; if nothing matches
        exactly, falls back to a unique substring match (so a teacher can
        type 'choose ali' for 'Alice' without spelling the whole name)."""
        query = query.strip().lower()
        if not query:
            return None
        for s in self.students:
            if s.name.lower() == query:
                return s
        matches = [s for s in self.students if query in s.name.lower()]
        return matches[0] if len(matches) == 1 else None
