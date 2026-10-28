"""
call_queue.py

This replaces getCallOrder() (helpers.py) plus the index-juggling that used
to live in responses.boxResponse() and callers.groupQuestions(). All the
"who's next / who's absent / teacher picked someone by name" logic lives
in one class with plain list operations (pop/insert) instead of hand-rolled
index math — which is what caused bugs like the IndexError risk in the
original `grp.callOrder[ind], grp.callOrder[ind+1] = ...` swap when `ind`
was the last index in the list.

Fairness rule (kept from the original): students who've been called the
fewest times for this category go first. Students tied on count are
shuffled among themselves so the order isn't predictable class to class.
"""

import random
from typing import List, Optional

from models import Roster, Student


class CallQueue:
    def __init__(self, students: List[Student], category: str, shuffle: bool = True):
        self.category = category
        self._queue: List[Student] = self._build_order(students, shuffle)
        self.called: List[Student] = []

    def _build_order(self, students: List[Student], shuffle: bool) -> List[Student]:
        buckets = {}
        for s in students:
            buckets.setdefault(s.count(self.category), []).append(s)
        order = []
        #print(f"Buckets for category '{self.category}': {buckets}")
        for count in sorted(buckets):
            group = buckets[count]
            if shuffle:
                random.shuffle(group)
            order.extend(group)
        return order

    def has_next(self) -> bool:
        return len(self._queue) > 0

    def peek(self) -> Optional[Student]:
        return self._queue[0] if self._queue else None

    def remaining(self) -> int:
        return len(self._queue)

    def call_next(self) -> Student:
        """Calls the student at the front of the queue: removes them and
        records them as called for this session."""
        if len(self._queue) == 0:
            self._queue = self.called.copy()
            #raise IndexError("No students left in the queue to call.")
        student = self._queue.pop(0)
        self._queue.append(student)  # put them at the end of the queue for next time
        self.called.append(student)
        return student

    def mark_absent(self) -> Optional[Student]:
        """The student at the front of the queue isn't here today — remove
        them from the queue without counting it as a call."""
        student = self.called.pop() if self.called else None
        self._queue.append(student)  # put them at the end of the queue for next time
        return student
        #return self._queue.pop(0) if self._queue else None 

    def defer(self) -> None:
        """The student at the front asked to go after the next person
        instead of right now."""
        if len(self._queue) >= 2:
            self._queue[0], self._queue[1] = self._queue[1], self._queue[0]

    def choose(self, name: str, roster: Roster) -> Optional[Student]:
        """Teacher wants a specific student called next, out of order.
        Returns the matched student, or None if not found / already
        called / not in this queue."""
        print(f"Choosing {name} from queue: {[s.name for s in self._queue]}")
        student = roster.find(name)
        if student is None or student not in self._queue:
            return None
        self._queue.remove(student)
        self._queue.insert(0, student)
        return student

    def remove(self, name: str, roster: Roster) -> Optional[Student]:
        """Teacher wants a specific student removed from called entirely
        (e.g. they left class). Returns the matched student, or None if not
        found / already called / not in this queue."""
        print(f"Removing {name} from queue: {[s.name for s in self._queue]}")
        student = roster.find(name)
        if student is None or student not in self._queue:
            return None
        self.called.remove(student)
        return student

    def count_increments(self) -> None:
        """Sorts the called list by student number, so the teacher can see
        at a glance who has been called this session. Does not change the
        order of the queue itself."""
        for s in self.called:
            s.increment += 1




