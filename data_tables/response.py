from database import db
from datetime import datetime
import secrets

class Response(db.Model):
    """
    one persons completed survey containing all the questions and answers 

    """

    __tablename__ = 'responses'

    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)

    # Email for save & resume
    email = db.Column(db.String(200))

    # Participant name (collected on section 1, stored separately from answers)
    participant_name = db.Column(db.String(200))

    # Unique token for resuming
    resume_token = db.Column(db.String(36), unique=True)

    # Status tracking
    is_complete = db.Column(db.Boolean, default=False)

    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    answers = db.relationship('Answer', backref='response', lazy=True, cascade='all, delete-orphan')

    def generate_resume_token(self):
        """Generate unique token for resuming."""
        self.resume_token = secrets.token_urlsafe(32)
        return self.resume_token
    

    def __repr__(self):
        return f'<Response {self.id} for Survey {self.survey_id}>'