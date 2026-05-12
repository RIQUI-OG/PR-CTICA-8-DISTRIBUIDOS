# Pérez Hernández Ricardo — Práctica 8
# ─────────────────────────────────────────────────────────────────────────────
# notes-api/modelo.py  —  Modelos Pydantic y lógica de almacenamiento
# ─────────────────────────────────────────────────────────────────────────────
from pydantic import BaseModel


class NoteIn(BaseModel):
    title: str
    note: str


class NoteOut(BaseModel):
    id: int
    title: str
    note: str


class Notes:
    def __init__(self):
        self.notes: dict[str, list[NoteOut]] = {}
        self.last_id: dict[str, int] = {}

    def add_note(self, user: str, nota: NoteIn):
        if user not in self.notes:
            self.notes[user] = []
            self.last_id[user] = 0
        self.notes[user].insert(0, NoteOut(id=self.last_id[user], title=nota.title, note=nota.note))
        self.last_id[user] += 1

    def get_notes(self, user: str) -> list[NoteOut]:
        return [
            NoteOut(id=n.id, title=n.title, note=(n.note[:10] + '...' if len(n.note) > 10 else n.note))
            for n in self.notes.get(user, [])
        ]

    def get_note(self, user: str, id: int) -> NoteOut | None:
        for note in self.notes.get(user, []):
            if note.id == id:
                return note
        return None

    def modify_note(self, user: str, id: int, new_title: str, new_note: str) -> bool:
        for note in self.notes.get(user, []):
            if note.id == id:
                note.title = new_title
                note.note  = new_note
                return True
        return False

    def delete_note(self, user: str, id: int) -> bool:
        notes = self.notes.get(user, [])
        for i, note in enumerate(notes):
            if note.id == id:
                del notes[i]
                return True
        return False
