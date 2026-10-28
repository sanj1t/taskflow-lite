from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models import Project, Task, User
from app.routers.projects import get_owned_project
from app.schemas import TaskCreate, TaskPriority, TaskRead, TaskStatus, TaskUpdate
from app.services.activity import record_activity

router = APIRouter(tags=["Tasks"])

@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskRead,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    project_id: int,
    task_in: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Task:
    get_owned_project(project_id, current_user, db)

    task = Task(
        project_id=project_id,
        title=task_in.title,
        description=task_in.description,
        status=task_in.status.value,
        priority=task_in.priority.value,
        assignee_id=task_in.assignee_id,
        due_date=task_in.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    record_activity(
        db=db,
        task_id=task.id,
        actor=current_user,
        event_type="task_created",
        payload={"title": task.title},
    )
    db.commit()
    db.refresh(task)
    return task

@router.get("/projects/{project_id}/tasks", response_model=list[TaskRead])
def list_tasks(
    project_id: int,
    status_filter: TaskStatus | None = Query(default=None, alias="status"),
    priority: TaskPriority | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Task]:
    get_owned_project(project_id, current_user, db)

    query = db.query(Task).filter(Task.project_id == project_id)

    if status_filter is not None:
        query = query.filter(Task.status == status_filter.value)
    if priority is not None:
        query = query.filter(Task.priority == priority.value)

    return (
        query.order_by(Task.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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


@router.patch("/tasks/{task_id}", response_model=TaskRead)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
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

    update_data = task_in.model_dump(exclude_unset=True)
    changes: dict[str, dict] = {}

    for field, value in update_data.items():
        if field in {"status", "priority"} and value is not None:
            value = value.value

        old_value = getattr(task, field)
        if value != old_value:
            changes[field] = {"old": old_value, "new": value}

        setattr(task, field, value)

    for field, change in changes.items():
        if field == "status":
            event_type = "task_status_changed"
        elif field == "priority":
            event_type = "task_priority_changed"
        elif field == "assignee_id":
            event_type = "task_assigned"
        else:
            continue

        record_activity(
            db=db,
            task_id=task.id,
            actor=current_user,
            event_type=event_type,
            payload=change,
        )

    db.commit()
    db.refresh(task)
    return task
