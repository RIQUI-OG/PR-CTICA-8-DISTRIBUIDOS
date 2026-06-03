# Pérez Hernández Ricardo — Práctica 8: Contenedores y Microservicios
# ─────────────────────────────────────────────────────────────────────────────
# notes-api/main.py  —  Microservicio de Notas (FastAPI)
# Puerto: 8000
# ─────────────────────────────────────────────────────────────────────────────
from fastapi import FastAPI, HTTPException
from modelo import NoteIn, NoteOut, Notes
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Notes API", description="Microservicio de Notas — Práctica 8")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notes_db = Notes()


@app.get("/health")
def health():
    return {"status": "ok", "service": "notes-api"}


@app.post("/{user}", status_code=201)
def add_note(user: str, note: NoteIn):
    notes_db.add_note(user, note)
    return {"message": "Note added successfully"}


@app.get("/{user}", response_model=list[NoteOut], status_code=200)
def get_notes(user: str):
    return notes_db.get_notes(user)


@app.get("/{user}/{id}", response_model=NoteOut, status_code=200)
def get_note(user: str, id: int):
    note = notes_db.get_note(user, id)
    if note is not None:
        return note
    raise HTTPException(status_code=404, detail="Note not found")


@app.put("/{user}/{id}", status_code=200)
def modify_note(user: str, id: int, note: NoteIn):
    if notes_db.modify_note(user, id, note.title, note.note):
        return {"message": "Note modified successfully"}
    raise HTTPException(status_code=404, detail="Note not found")


@app.delete("/{user}/{id}", status_code=204)
def delete_note(user: str, id: int):
    if not notes_db.delete_note(user, id):
        raise HTTPException(status_code=404, detail="Note not found")
