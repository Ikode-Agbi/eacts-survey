from database import db

class Section(db.Model):
    """
    A section is a group of related questions within a survey.
    
    For example:
    - Section 1: "Preoperative Assessment" (questions 1-5)
    - Section 2: "Intraoperative Management" (questions 6-10)
    
    Sections create "pages" in the survey.
    """
    
    __tablename__ = 'sections'
    
    # Columns
    id = db.Column(db.Integer, primary_key=True)
    survey_id = db.Column(db.Integer, db.ForeignKey('surveys.id'), nullable=False)
    section_number = db.Column(db.Integer, nullable=False)  # Order: 1, 2, 3...
    title = db.Column(db.String(200), nullable=False)  # e.g., "Preoperative Assessment"
    description = db.Column(db.Text)  # Optional instructions for this section
    
    # Relationships
    # This section has many questions
    questions = db.relationship('Question', backref='section', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Section {self.section_number}: {self.title}>'