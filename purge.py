from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import and_, or_
from datetime import datetime, timezone

from .db import SessionLocal
from .models import AppointmentRecord, EventRegistration

def schedule_purge(app):
    scheduler = AsyncIOScheduler()

    @scheduler.scheduled_job("interval", hours=1)
    def purge_expired():
        now = datetime.now(timezone.utc)
        db = SessionLocal()
        try:
            # Delete all expired appointment records and used ones
            db.query(AppointmentRecord).filter(
                or_(AppointmentRecord.expiration_time < now, AppointmentRecord.is_used == True)
            ).delete(synchronize_session=False)
            # Delete expired event registrations
            db.query(EventRegistration).filter(
                EventRegistration.expiration_time < now
            ).delete(synchronize_session=False)
            db.commit()
        finally:
            db.close()

    scheduler.start()
    app.state.scheduler = scheduler