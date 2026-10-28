from sqlalchemy.orm import Session

from app.models import ActivityEvent, User


def record_activity(
    db: Session,
    task_id: int,
    actor: User,
    event_type: str,
    payload: dict | None = None,
) -> ActivityEvent:
    event = ActivityEvent(
        task_id=task_id,
        actor_id=actor.id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    return event
