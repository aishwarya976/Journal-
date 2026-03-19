from sqlalchemy.orm import Session
from sqlalchemy import asc, nulls_last
from fastapi import UploadFile
from datetime import datetime
from typing import Optional
import uuid, os, shutil

import models, schemas


# ─── FILE UPLOAD ─────────────────────────────────────────────────────────────

async def save_upload(file: UploadFile, prefix: str) -> str:
    ext = os.path.splitext(file.filename)[1]
    filename = f"{prefix}_{uuid.uuid4().hex}{ext}"
    path = f"uploads/{filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return f"/uploads/{filename}"


# ─── TASKS ───────────────────────────────────────────────────────────────────

def get_tasks(db: Session):
    return db.query(models.Task).order_by(models.Task.created_at.desc()).all()

def get_tasks_sorted_by_deadline(db: Session):
    return db.query(models.Task).order_by(
        nulls_last(asc(models.Task.deadline))
    ).all()

def get_task(db: Session, task_id: int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def create_task(db: Session, title: str, description: str, deadline: Optional[str], before_image: Optional[str]):
    parsed_deadline = None
    if deadline:
        try:
            parsed_deadline = datetime.fromisoformat(deadline)
        except ValueError:
            pass

    task = models.Task(
        title=title,
        description=description,
        deadline=parsed_deadline,
        before_image=before_image,
        status="pending"
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

def update_task(db: Session, task: models.Task, title, description, deadline, status, after_image):
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if deadline is not None:
        try:
            task.deadline = datetime.fromisoformat(deadline)
        except ValueError:
            pass
    if status is not None:
        task.status = status
    if after_image is not None:
        task.after_image = after_image
    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)
    return task

def delete_task(db: Session, task: models.Task):
    db.delete(task)
    db.commit()


# ─── JOURNAL ─────────────────────────────────────────────────────────────────

def get_journal_entries(db: Session):
    return db.query(models.JournalEntry).order_by(models.JournalEntry.created_at.desc()).all()

def get_journal_entry(db: Session, entry_id: int):
    return db.query(models.JournalEntry).filter(models.JournalEntry.id == entry_id).first()

def create_journal_entry(db: Session, entry: schemas.JournalCreate):
    db_entry = models.JournalEntry(**entry.model_dump())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    return db_entry

def update_journal_entry(db: Session, existing: models.JournalEntry, entry: schemas.JournalUpdate):
    for field, value in entry.model_dump(exclude_unset=True).items():
        setattr(existing, field, value)
    existing.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(existing)
    return existing

def delete_journal_entry(db: Session, entry: models.JournalEntry):
    db.delete(entry)
    db.commit()


# ─── STATS ───────────────────────────────────────────────────────────────────

def get_stats(db: Session):
    total = db.query(models.Task).count()
    completed = db.query(models.Task).filter(models.Task.status == "completed").count()
    pending = db.query(models.Task).filter(models.Task.status == "pending").count()
    in_progress = db.query(models.Task).filter(models.Task.status == "in_progress").count()
    journal_count = db.query(models.JournalEntry).count()

    now = datetime.utcnow()
    overdue = db.query(models.Task).filter(
        models.Task.deadline < now,
        models.Task.status != "completed"
    ).count()

    return {
        "total_tasks": total,
        "completed": completed,
        "pending": pending,
        "in_progress": in_progress,
        "overdue": overdue,
        "journal_entries": journal_count,
        "completion_rate": round((completed / total * 100) if total > 0 else 0, 1)
    }
