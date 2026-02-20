from database import db


class Answer(db.Model):
    """
    one answer to one question which is linked to a survey
    """

    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    response_id = db.Column(db.Integer, db.ForeignKey('responses.id'), nullable=False)
    question_id= db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    choice = db.Column(db.String(10), nullable=False)  # 'Yes', 'No', or 'Abstain'
    elaboration = db.Column(db.Text)  # Optional explanation
    
    def __repr__(self):
        return f'<Answer: {self.choice} for Question {self.question_id}>'