import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.application import JobApplication
from app.models.job import Job

class PersonalizationMemory:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def record_feedback(self, job_id: int, feedback_type: str) -> Dict[str, Any]:
        """
        Records user feedback: 'interested', 'not_interested', 'relevant', 'irrelevant'.
        Updates user preference memory accordingly.
        """
        app = self.db.query(JobApplication).filter(
            JobApplication.user_id == self.user_id,
            JobApplication.job_id == job_id
        ).first()

        if not app:
            app = JobApplication(
                user_id=self.user_id,
                job_id=job_id,
                status="saved" if feedback_type in ["interested", "relevant"] else "closed",
                feedback=feedback_type,
            )
            self.db.add(app)
        else:
            app.feedback = feedback_type

        # Update user profile preferences based on positive feedback
        if feedback_type in ["interested", "relevant"]:
            job = self.db.query(Job).filter(Job.id == job_id).first()
            user = self.db.query(User).filter(User.id == self.user_id).first()
            if job and user:
                prefs = json.loads(user.preferences_json) if user.preferences_json else {}
                target_skills = set(prefs.get("target_skills", []))
                job_skills = json.loads(job.skills_json) if job.skills_json else []
                target_skills.update(job_skills[:3])
                prefs["target_skills"] = list(target_skills)
                user.preferences_json = json.dumps(prefs)

        self.db.commit()
        return {"status": "success", "job_id": job_id, "feedback": feedback_type}

    def get_personalization_summary(self) -> Dict[str, Any]:
        apps = self.db.query(JobApplication).filter(JobApplication.user_id == self.user_id).all()
        interested_jobs = [a for a in apps if a.feedback in ["interested", "relevant"]]
        dismissed_jobs = [a for a in apps if a.feedback in ["not_interested", "irrelevant"]]
        return {
            "total_feedback_signals": len(apps),
            "interested_count": len(interested_jobs),
            "dismissed_count": len(dismissed_jobs),
            "actively_tracked": len([a for a in apps if a.status != "closed"]),
        }
