from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import ActivityEvent, Comment, Project, Task, User
from app.schemas import ActivityEventRead, CommentCreate, CommentRead
from app.services.activity import record_activity

router = APIRouter(tags=["Comments & Activity"])


def get_task_for_user(
    task_id: int,
    current_user: User,
    db: Session,
) -> Task:
    task = (
        db.query(Task)
        .join(Project, Task.project_id == Project.id)
        .filter(Task.id == task_id, Project.owner_id == current_user.id)
        .first()
    )
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post(
    "/tasks/{task_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    task_id: int,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Comment:
    task = get_task_for_user(task_id, current_user, db)

    comment = Comment(
        task_id=task.id,
        author_id=current_user.id,
        body=comment_in.body,
    )
    db.add(comment)

    record_activity(
        db=db,
        task_id=task.id,
        actor=current_user,
        event_type="comment_added",
        payload={"comment_id": None, "preview": comment_in.body[:100]},
    )

    db.commit()
    db.refresh(comment)
    return comment


@router.get("/tasks/{task_id}/comments", response_model=list[CommentRead])
def list_comments(
    task_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Comment]:
    get_task_for_user(task_id, current_user, db)

    return (
        db.query(Comment)
        .filter(Comment.task_id == task_id)
        .order_by(Comment.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/tasks/{task_id}/activity", response_model=list[ActivityEventRead])
def list_activity(
    task_id: int,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ActivityEvent]:
    get_task_for_user(task_id, current_user, db)

    return (
        db.query(ActivityEvent)
        .filter(ActivityEvent.task_id == task_id)
        .order_by(ActivityEvent.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
