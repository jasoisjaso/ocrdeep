from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from models import User, Job
from forms import LoginForm, UploadForm
from app import db
import os
import uuid
import magic
# from worker.tasks import process_pdf

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=True)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = UploadForm()
    if form.validate_on_submit():
        f = form.file.data
        filename = secure_filename(f.filename)
        
        # Security checks
        if not filename.lower().endswith('.pdf'):
            flash('Invalid file type. Only PDFs are allowed.')
            return redirect(url_for('main.index'))

        # MIME type validation
        file_mime_type = magic.from_buffer(f.read(2048), mime=True)
        f.seek(0)
        if file_mime_type != 'application/pdf':
            flash('Invalid file content. Only PDFs are allowed.')
            return redirect(url_for('main.index'))

        # Generate unique filename
        unique_filename = str(uuid.uuid4()) + '_' + filename
        upload_path = os.path.join('/app/data/uploads', unique_filename)
        os.makedirs(os.path.dirname(upload_path), exist_ok=True)
        f.save(upload_path)

        new_job = Job(user_id=current_user.id, filename=unique_filename)
        db.session.add(new_job)
        db.session.commit()

        # Dispatch Celery task
        # process_pdf.delay(new_job.id, upload_path)

        flash('File uploaded successfully and processing has started.')
        return redirect(url_for('main.index'))

    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('index.html', title='Home', form=form, jobs=jobs)

@main.route('/job/<int:id>')
@login_required
def job_status(id):
    job = Job.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('job_status.html', job=job)

@main.route('/api/job_status/<int:id>')
@login_required
def api_job_status(id):
    job = Job.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return jsonify({
        'id': job.id,
        'status': job.status.value,
        'error_message': job.error_message,
        'output_zip_path': job.output_zip_path
    })

@main.route('/download/<int:id>')
@login_required
def download(id):
    job = Job.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if job.status != 'COMPLETE' or not job.output_zip_path:
        flash('Download not available yet.')
        return redirect(url_for('main.job_status', id=id))

    if not os.path.exists(job.output_zip_path):
        flash('File not found.')
        return redirect(url_for('main.job_status', id=id))

    return send_from_directory(os.path.dirname(job.output_zip_path),
                               os.path.basename(job.output_zip_path),
                               as_attachment=True)
