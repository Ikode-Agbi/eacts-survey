from database import db
"""
this is for one question of one survey and its linked its responses (yes/no.abstain) 

"""
class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    question_number = db.Column(db.Integer, nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    # each question is connected to answers from responders  
    answers = db.relationship('Answer', backref='question', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Question: {self.question_number}: {self.question_text[:50]}...'
    
    def calculate_statistics(self):

        """
        to calculate the statistics i need to know the number of people that said:
        - yes
        - no 
        - abstain

        then calculate the percentage 

        """

        total_answers = len(self.answers)

        if total_answers == 0:
            return {
                'question_number': self.question_number,
                'question_text': self.question_text,
                'total_responses': 0,
                'yes_count': 0,
                'no_count': 0,
                'abstain_count': 0,
                'yes_percentage': 0,
                'meets_threshold': False
            }

        sum_of_yes = 0
        sum_of_no = 0
        sum_of_abstain = 0
        

        for answer in self.answers:
            if answer.choice == 'Yes':
                sum_of_yes +=1
            elif answer.choice == 'No':
                sum_of_no += 1
            elif answer.choice == 'Abstain':
                sum_of_abstain += 1

        total_yes_no = sum_of_yes + sum_of_no

        # Avoid division by zero when everyone abstained
        if total_yes_no == 0:
            yes_percentage = 0.0
        else:
            yes_percentage = round((sum_of_yes / total_yes_no) * 100, 1)

        if yes_percentage >= 75.0:
            meets_threshold = True
        else:
            meets_threshold = False

        return {
             'question_number': self.question_number,
                'question_text': self.question_text,
                'total_responses': total_answers,
                'yes_count': sum_of_yes,
                'no_count': sum_of_no,
                'abstain_count': sum_of_abstain,
                'yes_percentage': yes_percentage,
                'meets_threshold': meets_threshold
        }

    def __repr__(self):
        return f'<Question {self.question_number}: {self.question_text[:50]}...'

        

        


        