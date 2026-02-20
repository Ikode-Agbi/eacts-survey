from database import db
from datetime import datetime

class Survey(db.Model):
    """
    This shows an individual survey and its connections:
        - each survey is connected to many sections
        - each section has many questions
        - each survey is connected to many responses
    """
    
    __tablename__ = 'surveys'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    sections = db.relationship('Section', backref='survey', lazy=True, cascade='all, delete-orphan')
    responses = db.relationship('Response', backref='survey', lazy=True, cascade='all, delete-orphan')
    
    def get_all_questions(self):
        """Get all questions across all sections in order."""
        all_questions = []
        
        ordered_sections = sorted(self.sections, key=lambda s: s.section_number)
        
        for section in ordered_sections:
            section_questions = sorted(section.questions, key=lambda q: q.question_number)
            all_questions.extend(section_questions)
        
        return all_questions
    
    def get_all_statistics(self):
        """Get statistics for all questions in this survey."""
        all_stats = []
        
        # FIXED: Use get_all_questions() instead of self.questions
        for question in self.get_all_questions():
            question_stats = question.calculate_statistics()
            all_stats.append(question_stats)
        
        return all_stats
    
    def __repr__(self):
        return f'<Survey: {self.title}>'