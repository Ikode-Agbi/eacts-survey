from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import db
from data_tables.survey import Survey
from data_tables.response import Response
from data_tables.answer import Answer

survey_bp = Blueprint('survey', __name__, url_prefix='/survey')


@survey_bp.route('/<int:survey_id>')
def take_survey(survey_id):
    """Show survey - redirects to the correct section."""

    survey = Survey.query.get_or_404(survey_id)

    # Allow admins to preview inactive surveys
    if not survey.is_active and not session.get('admin_logged_in'):
        flash('This survey is no longer active', 'error')
        return redirect(url_for('home'))

    # Check if resuming via token link
    resume_token = request.args.get('token')

    if resume_token:
        existing_response = Response.query.filter_by(
            resume_token=resume_token,
            survey_id=survey_id,
            is_complete=False
        ).first()

        if existing_response:
            session['resume_token'] = resume_token
            session['resume_email'] = existing_response.email

    # Land on the section they saved at (default 1 for fresh starts)
    target_section = request.args.get('section', 1, type=int)
    return redirect(url_for('survey.show_section', survey_id=survey_id, section_num=target_section))


@survey_bp.route('/<int:survey_id>/section/<int:section_num>', methods=['GET', 'POST'])
def show_section(survey_id, section_num):
    """Show one section at a time."""

    survey = Survey.query.get_or_404(survey_id)

    if not survey.is_active and not session.get('admin_logged_in'):
        flash('This survey is no longer active', 'error')
        return redirect(url_for('home'))

    sections = sorted(survey.sections, key=lambda s: s.section_number)
    total_sections = len(sections)

    if section_num < 1 or section_num > total_sections:
        flash('Invalid section', 'error')
        return redirect(url_for('survey.take_survey', survey_id=survey_id))

    current_section = sections[section_num - 1]

    # Get existing response if resuming
    existing_response = None
    resume_token = session.get('resume_token')

    if resume_token:
        existing_response = Response.query.filter_by(resume_token=resume_token).first()

    # ── POST ──────────────────────────────────────────────────────────────────
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'save':
            email = request.form.get('email', '').strip()

            if not email:
                # Re-render same section with an error (no redirect — preserves form state)
                return render_template('take_survey_section.html',
                                       survey=survey,
                                       section=current_section,
                                       section_num=section_num,
                                       total_sections=total_sections,
                                       existing_response=existing_response,
                                       saved_email='',
                                       save_error='Please enter your email address to save your progress.')

            # Create or update the response record
            if not existing_response:
                existing_response = Response(survey_id=survey.id, email=email)
                existing_response.generate_resume_token()
                db.session.add(existing_response)
                db.session.commit()
                session['resume_token'] = existing_response.resume_token
                session['resume_email'] = email
            else:
                existing_response.email = email
                session['resume_email'] = email
                db.session.commit()

            # Save whatever answers were filled in on this section
            save_section_answers(survey, current_section, existing_response)

            # Resume link — encodes the current section so they land here when they return
            resume_link = url_for('survey.take_survey',
                                  survey_id=survey_id,
                                  token=existing_response.resume_token,
                                  section=section_num,
                                  _external=True)

            # Try to send email; returns True if it actually sent
            email_sent = send_resume_email(email, survey.title, resume_link, section_num, total_sections)

            # Refresh so existing_response.answers reflects the just-saved answers
            db.session.refresh(existing_response)

            # Re-render the SAME section with the save confirmation box
            return render_template('take_survey_section.html',
                                   survey=survey,
                                   section=current_section,
                                   section_num=section_num,
                                   total_sections=total_sections,
                                   existing_response=existing_response,
                                   saved_email=email,
                                   resume_link=resume_link,
                                   saved_to_email=email if email_sent else None)

        else:
            # next / previous / submit — save answers first, then navigate
            save_section_answers(survey, current_section, existing_response)

            if action == 'next':
                return redirect(url_for('survey.show_section',
                                        survey_id=survey_id,
                                        section_num=section_num + 1))

            elif action == 'previous':
                return redirect(url_for('survey.show_section',
                                        survey_id=survey_id,
                                        section_num=section_num - 1))

            elif action == 'submit':
                if not existing_response:
                    existing_response = Response(survey_id=survey.id, is_complete=True)
                    db.session.add(existing_response)
                else:
                    existing_response.is_complete = True

                db.session.commit()

                session.pop('resume_token', None)
                session.pop('resume_email', None)

                return redirect(url_for('survey.thank_you'))

    # ── GET ───────────────────────────────────────────────────────────────────
    return render_template('take_survey_section.html',
                           survey=survey,
                           section=current_section,
                           section_num=section_num,
                           total_sections=total_sections,
                           existing_response=existing_response,
                           saved_email=session.get('resume_email', ''))


def save_section_answers(survey, section, existing_response):
    """Save answers for the current section."""

    if not existing_response:
        existing_response = Response(survey_id=survey.id)
        existing_response.generate_resume_token()
        db.session.add(existing_response)
        db.session.flush()
        session['resume_token'] = existing_response.resume_token

    # Delete old answers for this section so we can replace them
    question_ids = [q.id for q in section.questions]
    Answer.query.filter(
        Answer.response_id == existing_response.id,
        Answer.question_id.in_(question_ids)
    ).delete(synchronize_session=False)

    # Save new answers
    for question in section.questions:
        choice = request.form.get(f'question_{question.id}')
        elaboration = request.form.get(f'elaboration_{question.id}', '').strip()

        if choice:
            answer = Answer(
                response_id=existing_response.id,
                question_id=question.id,
                choice=choice,
                elaboration=elaboration if elaboration else None
            )
            db.session.add(answer)

    db.session.commit()


@survey_bp.route('/thank-you')
def thank_you():
    """Thank you page."""
    return render_template('thank_you.html')


def send_resume_email(to_email, survey_title, resume_link, current_section, total_sections):
    """Send resume link via email. Returns True if sent, False if not configured or failed."""

    from flask import current_app

    # Don't even try if credentials aren't configured
    if not current_app.config.get('MAIL_USERNAME') or not current_app.config.get('MAIL_PASSWORD'):
        print("Email not configured: set MAIL_USERNAME and MAIL_PASSWORD environment variables.")
        return False

    try:
        from flask_mail import Mail, Message
        mail = Mail(current_app)

        msg = Message(
            subject=f'Resume Your Survey: {survey_title}',
            recipients=[to_email],
            body=f'''Hello,

You have saved your progress on: {survey_title}

Progress: Section {current_section} of {total_sections}

Click the link below to continue where you left off:
{resume_link}

This link is unique to you and can be used at any time to resume the survey.

Best regards,
EACTS Survey System
'''
        )
        mail.send(msg)
        return True

    except Exception as e:
        print(f"Email send failed: {e}")
        return False
