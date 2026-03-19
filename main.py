from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
import uvicorn
import os

from database import engine, get_db, Base
import models
import schemas
import crud

# Create tables
Base.metadata.create_all(bind=engine)

# Create uploads directory
os.makedirs("uploads", exist_ok=True)

app = FastAPI(title="TaskJournal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# ─── TASKS ───────────────────────────────────────────────────────────────────

@app.get("/tasks", response_model=List[schemas.TaskOut])
def get_tasks(db: Session = Depends(get_db)):
    return crud.get_tasks(db)

@app.get("/tasks/by-deadline", response_model=List[schemas.TaskOut])
def get_tasks_by_deadline(db: Session = Depends(get_db)):
    return crud.get_tasks_sorted_by_deadline(db)

@app.get("/tasks/{task_id}", response_model=schemas.TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", response_model=schemas.TaskOut)
async def create_task(
    title: str = Form(...),
    description: str = Form(""),
    deadline: Optional[str] = Form(None),
    before_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    before_path = None
    if before_image and before_image.filename:
        before_path = await crud.save_upload(before_image, "before")
    return crud.create_task(db, title, description, deadline, before_path)

@app.patch("/tasks/{task_id}", response_model=schemas.TaskOut)
async def update_task(
    task_id: int,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    deadline: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    after_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    after_path = None
    if after_image and after_image.filename:
        after_path = await crud.save_upload(after_image, "after")
    return crud.update_task(db, task, title, description, deadline, status, after_path)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = crud.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, task)
    return {"message": "Task deleted"}


# ─── JOURNAL ─────────────────────────────────────────────────────────────────

@app.get("/journal", response_model=List[schemas.JournalOut])
def get_journal_entries(db: Session = Depends(get_db)):
    return crud.get_journal_entries(db)

@app.get("/journal/{entry_id}", response_model=schemas.JournalOut)
def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = crud.get_journal_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.post("/journal", response_model=schemas.JournalOut)
def create_journal_entry(entry: schemas.JournalCreate, db: Session = Depends(get_db)):
    return crud.create_journal_entry(db, entry)

@app.patch("/journal/{entry_id}", response_model=schemas.JournalOut)
def update_journal_entry(entry_id: int, entry: schemas.JournalUpdate, db: Session = Depends(get_db)):
    existing = crud.get_journal_entry(db, entry_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Entry not found")
    return crud.update_journal_entry(db, existing, entry)

@app.delete("/journal/{entry_id}")
def delete_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = crud.get_journal_entry(db, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    crud.delete_journal_entry(db, entry)
    return {"message": "Entry deleted"}


# ─── STATS ───────────────────────────────────────────────────────────────────

@app.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
