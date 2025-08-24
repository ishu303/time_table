import os
import json
from io import BytesIO, StringIO
from flask import render_template, request, redirect, url_for, flash, jsonify, send_file, make_response
from sqlalchemy import func
from .app import app, db
from .models import (
    Teacher, Course, Section, Room, TimeSlot, Offering, TimetableSlot,
    TeacherAvailability, RoomAvailability, TimetableGeneration, UserConstraint, WorkloadFile
)
from .simple_solver import SimpleTimetableSolver
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import csv
from werkzeug.utils import secure_filename
from datetime import datetime

@app.route('/')
def index():
    """Dashboard home page"""
    stats = {
        'teachers': Teacher.query.filter_by(is_active=True).count(),
        'courses': Course.query.filter_by(is_active=True).count(),
        'sections': Section.query.filter_by(is_active=True).count(),
        'rooms': Room.query.filter_by(is_active=True).count(),
        'offerings': Offering.query.count(),
        'scheduled_slots': TimetableSlot.query.count()
    }
    
    # Get latest generation
    latest_generation = TimetableGeneration.query.order_by(TimetableGeneration.created_at.desc()).first()
    
    return render_template('index.html', stats=stats, latest_generation=latest_generation)

# Teacher Management Routes
@app.route('/teachers')
def teachers():
    """List all teachers"""
    teachers_list = Teacher.query.filter_by(is_active=True).all()
    return render_template('teachers.html', teachers=teachers_list)

@app.route('/teachers/add', methods=['GET', 'POST'])
def add_teacher():
    """Add new teacher"""
    if request.method == 'POST':
        teacher = Teacher(
            name=request.form['name'],
            code=request.form.get('code'),
            designation=request.form['designation'],
            max_weekly_load=int(request.form.get('max_weekly_load', 16))
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teachers'))
    
    return render_template('teachers.html', add_mode=True)

@app.route('/teachers/<int:teacher_id>/edit', methods=['POST'])
def edit_teacher(teacher_id):
    """Edit teacher"""
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.name = request.form['name']
    teacher.code = request.form.get('code')
    teacher.designation = request.form['designation']
    teacher.max_weekly_load = int(request.form.get('max_weekly_load', 16))
    db.session.commit()
    flash('Teacher updated successfully!', 'success')
    return redirect(url_for('teachers'))

@app.route('/teachers/<int:teacher_id>/delete', methods=['POST'])
def delete_teacher(teacher_id):
    """Delete teacher (soft delete)"""
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.is_active = False
    db.session.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('teachers'))

# Course Management Routes
@app.route('/courses')
def courses():
    """List all courses"""
    courses_list = Course.query.filter_by(is_active=True).all()
    return render_template('courses.html', courses=courses_list)

@app.route('/courses/add', methods=['GET', 'POST'])
def add_course():
    """Add new course"""
    if request.method == 'POST':
        course = Course(
            code=request.form['code'],
            name=request.form['name'],
            credit_hours=int(request.form.get('credit_hours', 4)),
            sessions_per_week=int(request.form.get('sessions_per_week', 4)),
            session_duration=int(request.form.get('session_duration', 1)),
            is_lab=request.form.get('is_lab') == 'on',
            is_online=request.form.get('is_online') == 'on',
            program=request.form['program'],
            semester=request.form['semester']
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added successfully!', 'success')
        return redirect(url_for('courses'))
    
    return render_template('courses.html', add_mode=True)

@app.route('/courses/<int:course_id>/edit', methods=['POST'])
def edit_course(course_id):
    """Edit course"""
    course = Course.query.get_or_404(course_id)
    course.code = request.form['code']
    course.name = request.form['name']
    course.credit_hours = int(request.form.get('credit_hours', 4))
    course.sessions_per_week = int(request.form.get('sessions_per_week', 4))
    course.session_duration = int(request.form.get('session_duration', 1))
    course.is_lab = request.form.get('is_lab') == 'on'
    course.is_online = request.form.get('is_online') == 'on'
    course.program = request.form['program']
    course.semester = request.form['semester']
    db.session.commit()
    flash('Course updated successfully!', 'success')
    return redirect(url_for('courses'))

@app.route('/courses/<int:course_id>/delete', methods=['POST'])
def delete_course(course_id):
    """Delete course (soft delete)"""
    course = Course.query.get_or_404(course_id)
    course.is_active = False
    db.session.commit()
    flash('Course deleted successfully!', 'success')
    return redirect(url_for('courses'))

# Room Management Routes
@app.route('/rooms')
def rooms():
    """List all rooms"""
    rooms_list = Room.query.filter_by(is_active=True).all()
    return render_template('rooms.html', rooms=rooms_list)

@app.route('/rooms/add', methods=['GET', 'POST'])
def add_room():
    """Add new room"""
    if request.method == 'POST':
        room = Room(
            number=request.form['number'],
            name=request.form.get('name'),
            room_type=request.form['room_type'],
            capacity=int(request.form.get('capacity', 60))
        )
        db.session.add(room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('rooms'))
    
    return render_template('rooms.html', add_mode=True)

@app.route('/rooms/<int:room_id>/edit', methods=['POST'])
def edit_room(room_id):
    """Edit room"""
    room = Room.query.get_or_404(room_id)
    room.number = request.form['number']
    room.name = request.form.get('name')
    room.room_type = request.form['room_type']
    room.capacity = int(request.form.get('capacity', 60))
    db.session.commit()
    flash('Room updated successfully!', 'success')
    return redirect(url_for('rooms'))

@app.route('/rooms/<int:room_id>/delete', methods=['POST'])
def delete_room(room_id):
    """Delete room (soft delete)"""
    room = Room.query.get_or_404(room_id)
    room.is_active = False
    db.session.commit()
    flash('Room deleted successfully!', 'success')
    return redirect(url_for('rooms'))

# Section Management Routes
@app.route('/sections')
def sections():
    """List all sections"""
    sections_list = Section.query.filter_by(is_active=True).all()
    return render_template('sections.html', sections=sections_list)

@app.route('/sections/add', methods=['GET', 'POST'])
def add_section():
    """Add new section"""
    if request.method == 'POST':
        section = Section(
            name=request.form['name'],
            program=request.form['program'],
            semester=request.form['semester'],
            section_letter=request.form.get('section_letter'),
            student_count=int(request.form.get('student_count', 60))
        )
        db.session.add(section)
        db.session.commit()
        flash('Section added successfully!', 'success')
        return redirect(url_for('sections'))
    
    return render_template('sections.html', add_mode=True)

@app.route('/sections/<int:section_id>/edit', methods=['POST'])
def edit_section(section_id):
    """Edit section"""
    section = Section.query.get_or_404(section_id)
    section.name = request.form['name']
    section.program = request.form['program']
    section.semester = request.form['semester']
    section.section_letter = request.form.get('section_letter')
    section.student_count = int(request.form.get('student_count', 60))
    db.session.commit()
    flash('Section updated successfully!', 'success')
    return redirect(url_for('sections'))

@app.route('/sections/<int:section_id>/delete', methods=['POST'])
def delete_section(section_id):
    """Delete section (soft delete)"""
    section = Section.query.get_or_404(section_id)
    section.is_active = False
    db.session.commit()
    flash('Section deleted successfully!', 'success')
    return redirect(url_for('sections'))

# Timetable Generation and Viewing
@app.route('/generate')
def generate_page():
    """Timetable generation page"""
    offerings = Offering.query.join(Teacher).join(Course).join(Section).all()
    generations = TimetableGeneration.query.order_by(TimetableGeneration.created_at.desc()).limit(10).all()
    return render_template('generate.html', offerings=offerings, generations=generations)

@app.route('/generate/run', methods=['POST'])
def run_generation():
    """Run timetable generation"""
    try:
        solver = SimpleTimetableSolver()
        result = solver.generate_timetable()
        
        if result['status'] == 'success':
            flash(f'Timetable generated successfully! {result["total_slots"]} slots scheduled using simplified solver.', 'success')
        else:
            flash(f'Generation failed: {result.get("error", "Unknown error")}', 'error')
        
        return redirect(url_for('generate_page'))
    except Exception as e:
        flash(f'Generation error: {str(e)}', 'error')
        return redirect(url_for('generate_page'))

@app.route('/timetable')
def timetable():
    """View generated timetable"""
    filter_type = request.args.get('filter_type', 'section')
    filter_id = request.args.get('filter_id')
    
    # Get filter options
    sections = Section.query.filter_by(is_active=True).all()
    teachers = Teacher.query.filter_by(is_active=True).all()
    rooms = Room.query.filter_by(is_active=True).all()
    
    # Get timetable data with explicit join conditions
    query = (TimetableSlot.query
             .join(Offering, TimetableSlot.offering_id == Offering.id)
             .join(Course, Offering.course_id == Course.id)
             .join(Teacher, Offering.teacher_id == Teacher.id)
             .join(Section, Offering.section_id == Section.id)
             .join(Room, TimetableSlot.room_id == Room.id)
             .join(TimeSlot, TimetableSlot.time_slot_id == TimeSlot.id))
    
    if filter_type == 'section' and filter_id:
        query = query.filter(Section.id == filter_id)
    elif filter_type == 'teacher' and filter_id:
        query = query.filter(Teacher.id == filter_id)
    elif filter_type == 'room' and filter_id:
        query = query.filter(Room.id == filter_id)
    
    timetable_slots = query.all()
    
    # Get time slots for grid
    time_slots = TimeSlot.query.filter_by(is_active=True, is_break=False).order_by(
        TimeSlot.day_of_week, TimeSlot.period_number
    ).all()
    
    # Organize data for grid display
    grid_data = {}
    for slot in timetable_slots:
        day = slot.time_slot.day_of_week
        period = slot.time_slot.period_number
        
        if day not in grid_data:
            grid_data[day] = {}
        
        grid_data[day][period] = {
            'course': slot.offering.course,
            'teacher': slot.offering.teacher,
            'room': slot.room,
            'section': slot.section,
            'slot_id': slot.id
        }
    
    return render_template('timetable.html', 
                         grid_data=grid_data, 
                         time_slots=time_slots,
                         sections=sections,
                         teachers=teachers,
                         rooms=rooms,
                         filter_type=filter_type,
                         filter_id=int(filter_id) if filter_id else None)

@app.route('/timetable/move', methods=['POST'])
def move_timetable_slot():
    """Move a timetable slot (drag and drop)"""
    data = request.get_json()
    
    slot_id = data.get('slot_id')
    new_time_slot_id = data.get('new_time_slot_id')
    new_room_id = data.get('new_room_id')
    
    try:
        slot = TimetableSlot.query.get_or_404(slot_id)
        
        # Check for conflicts
        conflicts = TimetableSlot.query.filter(
            TimetableSlot.id != slot_id,
            TimetableSlot.time_slot_id == new_time_slot_id
        ).filter(
            (TimetableSlot.section_id == slot.section_id) |
            (TimetableSlot.room_id == new_room_id) |
            (TimetableSlot.offering.has(teacher_id=slot.offering.teacher_id))
        ).first()
        
        if conflicts:
            return jsonify({'success': False, 'error': 'Conflict detected'})
        
        # Update slot
        slot.time_slot_id = new_time_slot_id
        if new_room_id:
            slot.room_id = new_room_id
        
        db.session.commit()
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Export Functions
@app.route('/export/pdf')
def export_pdf():
    """Export timetable to PDF"""
    filter_type = request.args.get('filter_type', 'section')
    filter_id = request.args.get('filter_id')
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        alignment=1  # Center
    )
    story.append(Paragraph("College Timetable", title_style))
    story.append(Spacer(1, 12))
    
    # Get data with explicit join conditions
    query = (TimetableSlot.query
             .join(Offering, TimetableSlot.offering_id == Offering.id)
             .join(Course, Offering.course_id == Course.id)
             .join(Teacher, Offering.teacher_id == Teacher.id)
             .join(Section, Offering.section_id == Section.id)
             .join(Room, TimetableSlot.room_id == Room.id)
             .join(TimeSlot, TimetableSlot.time_slot_id == TimeSlot.id))
    
    if filter_type == 'section' and filter_id:
        query = query.filter(Section.id == filter_id)
        section = Section.query.get(filter_id)
        story.append(Paragraph(f"Section: {section.name}", styles['Heading2']))
    elif filter_type == 'teacher' and filter_id:
        query = query.filter(Teacher.id == filter_id)
        teacher = Teacher.query.get(filter_id)
        story.append(Paragraph(f"Teacher: {teacher.name}", styles['Heading2']))
    elif filter_type == 'room' and filter_id:
        query = query.filter(Room.id == filter_id)
        room = Room.query.get(filter_id)
        story.append(Paragraph(f"Room: {room.number}", styles['Heading2']))
    
    story.append(Spacer(1, 12))
    
    timetable_slots = query.order_by(TimeSlot.day_of_week, TimeSlot.period_number).all()
    
    # Create table data
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    periods = list(range(1, 9))  # Periods 1-8
    
    # Header row
    table_data = [['Period'] + days]
    
    # Build grid
    grid = {}
    for slot in timetable_slots:
        day = slot.time_slot.day_of_week
        period = slot.time_slot.period_number
        if period not in grid:
            grid[period] = {}
        
        course_info = f"{slot.offering.course.code}\n{slot.offering.teacher.name}\n{slot.room.number}"
        grid[period][day] = course_info
    
    # Fill table data
    for period in periods:
        row = [f"Period {period}"]
        for day in range(6):  # 0-5 for Mon-Sat
            cell_data = grid.get(period, {}).get(day, '')
            row.append(cell_data)
        table_data.append(row)
    
    # Create table
    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    story.append(table)
    doc.build(story)
    
    buffer.seek(0)
    return send_file(buffer, 
                     as_attachment=True, 
                     download_name='timetable.pdf', 
                     mimetype='application/pdf')

@app.route('/export/csv')
def export_csv():
    """Export timetable to CSV"""
    filter_type = request.args.get('filter_type', 'section')
    filter_id = request.args.get('filter_id')
    
    # Get data with explicit join conditions
    query = (TimetableSlot.query
             .join(Offering, TimetableSlot.offering_id == Offering.id)
             .join(Course, Offering.course_id == Course.id)
             .join(Teacher, Offering.teacher_id == Teacher.id)
             .join(Section, Offering.section_id == Section.id)
             .join(Room, TimetableSlot.room_id == Room.id)
             .join(TimeSlot, TimetableSlot.time_slot_id == TimeSlot.id))
    
    if filter_type == 'section' and filter_id:
        query = query.filter(Section.id == filter_id)
    elif filter_type == 'teacher' and filter_id:
        query = query.filter(Teacher.id == filter_id)
    elif filter_type == 'room' and filter_id:
        query = query.filter(Room.id == filter_id)
    
    timetable_slots = query.order_by(TimeSlot.day_of_week, TimeSlot.period_number).all()
    
    # Create CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['Day', 'Period', 'Start Time', 'End Time', 'Course Code', 'Course Name', 
                     'Teacher', 'Section', 'Room', 'Room Type'])
    
    # Write data
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for slot in timetable_slots:
        writer.writerow([
            days[slot.time_slot.day_of_week],
            slot.time_slot.period_number,
            slot.time_slot.start_time,
            slot.time_slot.end_time,
            slot.offering.course.code,
            slot.offering.course.name,
            slot.offering.teacher.name,
            slot.section.name,
            slot.room.number,
            slot.room.room_type
        ])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = 'attachment; filename=timetable.csv'
    return response

# Offerings Management Routes
@app.route('/offerings')
def offerings():
    """List all offerings"""
    offerings_list = Offering.query.join(Teacher).join(Course).join(Section).all()
    teachers = Teacher.query.filter_by(is_active=True).all()
    courses = Course.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()
    rooms = Room.query.filter_by(is_active=True).all()
    return render_template('offerings.html', 
                         offerings=offerings_list,
                         teachers=teachers,
                         courses=courses,
                         sections=sections,
                         rooms=rooms)

@app.route('/offerings/add', methods=['GET', 'POST'])
def add_offering():
    """Add new offering"""
    if request.method == 'POST':
        # Check if this offering already exists
        existing = Offering.query.filter_by(
            teacher_id=request.form['teacher_id'],
            course_id=request.form['course_id'],
            section_id=request.form['section_id']
        ).first()
        
        if existing:
            flash('This offering already exists!', 'error')
            return redirect(url_for('offerings'))
        
        offering = Offering(
            teacher_id=request.form['teacher_id'],
            course_id=request.form['course_id'],
            section_id=request.form['section_id'],
            room_id=request.form.get('room_id') if request.form.get('room_id') else None
        )
        db.session.add(offering)
        db.session.commit()
        flash('Offering added successfully!', 'success')
        return redirect(url_for('offerings'))
    
    return redirect(url_for('offerings'))

@app.route('/offerings/<int:offering_id>/edit', methods=['POST'])
def edit_offering(offering_id):
    """Edit offering"""
    offering = Offering.query.get_or_404(offering_id)
    
    # Check if this combination would create a duplicate
    existing = Offering.query.filter(
        Offering.id != offering_id,
        Offering.teacher_id == request.form['teacher_id'],
        Offering.course_id == request.form['course_id'],
        Offering.section_id == request.form['section_id']
    ).first()
    
    if existing:
        flash('This offering combination already exists!', 'error')
        return redirect(url_for('offerings'))
    
    offering.teacher_id = request.form['teacher_id']
    offering.course_id = request.form['course_id']
    offering.section_id = request.form['section_id']
    offering.room_id = request.form.get('room_id') if request.form.get('room_id') else None
    db.session.commit()
    flash('Offering updated successfully!', 'success')
    return redirect(url_for('offerings'))

@app.route('/offerings/<int:offering_id>/delete', methods=['POST'])
def delete_offering(offering_id):
    """Delete offering"""
    offering = Offering.query.get_or_404(offering_id)
    
    # Check if offering has timetable slots
    if offering.timetable_slots:
        flash('Cannot delete offering that has scheduled timetable slots!', 'error')
        return redirect(url_for('offerings'))
    
    db.session.delete(offering)
    db.session.commit()
    flash('Offering deleted successfully!', 'success')
    return redirect(url_for('offerings'))

# API Routes for AJAX
@app.route('/api/offerings')
def api_offerings():
    """Get offerings for AJAX"""
    offerings = Offering.query.join(Teacher).join(Course).join(Section).all()
    data = []
    for offering in offerings:
        data.append({
            'id': offering.id,
            'teacher': offering.teacher.name,
            'course': f"{offering.course.code} - {offering.course.name}",
            'section': offering.section.name,
            'sessions_per_week': offering.course.sessions_per_week
        })
    return jsonify(data)

@app.route('/api/offerings/add', methods=['POST'])
def api_add_offering():
    """Add offering via AJAX"""
    try:
        data = request.get_json()
        offering = Offering(
            teacher_id=data['teacher_id'],
            course_id=data['course_id'],
            section_id=data['section_id'],
            room_id=data.get('room_id')
        )
        db.session.add(offering)
        db.session.commit()
        return jsonify({'success': True, 'id': offering.id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/offerings/<int:offering_id>/delete', methods=['DELETE'])
def api_delete_offering(offering_id):
    """Delete offering via AJAX"""
    try:
        offering = Offering.query.get_or_404(offering_id)
        db.session.delete(offering)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Constraint Management Routes
@app.route('/constraints')
def constraints():
    """Manage user constraints"""
    constraints_list = UserConstraint.query.filter_by(is_active=True).order_by(UserConstraint.created_at.desc()).all()
    teachers = Teacher.query.filter_by(is_active=True).all()
    rooms = Room.query.filter_by(is_active=True).all()
    sections = Section.query.filter_by(is_active=True).all()
    
    return render_template('constraints.html', 
                         constraints=constraints_list,
                         teachers=teachers,
                         rooms=rooms,
                         sections=sections)

@app.route('/constraints/add', methods=['POST'])
def add_constraint():
    """Add new constraint"""
    try:
        constraint = UserConstraint(
            name=request.form['name'],
            constraint_type=request.form['constraint_type'],
            teacher_id=request.form.get('teacher_id'),
            room_id=request.form.get('room_id'),
            section_id=request.form.get('section_id'),
            day_of_week=int(request.form['day_of_week']),
            period_number=int(request.form['period_number'])
        )
        db.session.add(constraint)
        db.session.commit()
        flash('Constraint added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding constraint: {str(e)}', 'error')
    
    return redirect(url_for('constraints'))

@app.route('/constraints/<int:constraint_id>/delete', methods=['POST'])
def delete_constraint(constraint_id):
    """Delete constraint"""
    try:
        constraint = UserConstraint.query.get_or_404(constraint_id)
        constraint.is_active = False
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Workload Upload Routes
@app.route('/workload')
def workload_upload():
    """Workload upload page"""
    workload_files = WorkloadFile.query.order_by(WorkloadFile.uploaded_at.desc()).all()
    return render_template('workload_upload.html', workload_files=workload_files)

@app.route('/workload/upload', methods=['POST'])
def upload_workload():
    """Handle workload file upload"""
    try:
        if 'workload_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('workload_upload'))
        
        file = request.files['workload_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('workload_upload'))
        
        if file:
            # Save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            
            # Ensure upload directory exists
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(file_path)
            
            # Create database record
            workload_file = WorkloadFile(
                filename=unique_filename,
                original_filename=filename,
                file_path=file_path,
                file_size=os.path.getsize(file_path),
                processing_status='pending'
            )
            db.session.add(workload_file)
            db.session.commit()
            
            # NOTE: This is a synchronous call. For a production environment,
            # this should be moved to a background worker (e.g., Celery) to avoid blocking the server.
            from .workload_processor import process_workload_file
            process_workload_file(workload_file.id)
            
            flash('File uploaded successfully! Processing started.', 'success')
            
    except Exception as e:
        flash(f'Error uploading file: {str(e)}', 'error')
    
    return redirect(url_for('workload_upload'))

@app.route('/workload/<int:file_id>/results')
def workload_results(file_id):
    """Get processing results for a workload file"""
    try:
        file = WorkloadFile.query.get_or_404(file_id)
        
        if file.processing_status != 'completed':
            return jsonify({'success': False, 'error': 'File not yet processed'})
        
        # Generate results HTML
        html = f"""
        <div class="row">
            <div class="col-12">
                <h6>Processing Results for {file.original_filename}</h6>
                <p><strong>Status:</strong> {file.processing_status}</p>
                <p><strong>Notes:</strong> {file.processing_notes or 'No notes available'}</p>
            </div>
        </div>
        """
        
        return jsonify({'success': True, 'html': html})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/workload/<int:file_id>/delete', methods=['POST'])
def delete_workload_file(file_id):
    """Delete workload file"""
    try:
        file = WorkloadFile.query.get_or_404(file_id)
        
        # Delete physical file
        if os.path.exists(file.file_path):
            os.remove(file.file_path)
        
        # Delete database record
        db.session.delete(file)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Enhanced Timetable Routes
@app.route('/timetable/edit')
def timetable_edit():
    """Enhanced timetable editing page"""
    filter_type = request.args.get('filter_type', 'section')
    filter_id = request.args.get('filter_id')
    
    # Get filter options
    sections = Section.query.filter_by(is_active=True).all()
    teachers = Teacher.query.filter_by(is_active=True).all()
    rooms = Room.query.filter_by(is_active=True).all()
    offerings = Offering.query.join(Course).join(Teacher).join(Section).all()
    
    # Get timetable data
    query = (TimetableSlot.query
             .join(Offering, TimetableSlot.offering_id == Offering.id)
             .join(Course, Offering.course_id == Course.id)
             .join(Teacher, Offering.teacher_id == Teacher.id)
             .join(Section, Offering.section_id == Section.id)
             .join(Room, TimetableSlot.room_id == Room.id)
             .join(TimeSlot, TimetableSlot.time_slot_id == TimeSlot.id))
    
    if filter_type == 'section' and filter_id:
        query = query.filter(Section.id == filter_id)
    elif filter_type == 'teacher' and filter_id:
        query = query.filter(Teacher.id == filter_id)
    elif filter_type == 'room' and filter_id:
        query = query.filter(Room.id == filter_id)
    
    timetable_slots = query.all()
    
    # Get time slots for grid
    time_slots = TimeSlot.query.filter_by(is_active=True, is_break=False).order_by(
        TimeSlot.day_of_week, TimeSlot.period_number
    ).all()
    
    # Organize data for grid display
    grid_data = {}
    for slot in timetable_slots:
        day = slot.time_slot.day_of_week
        period = slot.time_slot.period_number
        
        if day not in grid_data:
            grid_data[day] = {}
        
        grid_data[day][period] = {
            'course': slot.offering.course,
            'teacher': slot.offering.teacher,
            'room': slot.room,
            'section': slot.section,
            'slot_id': slot.id
        }
    
    return render_template('timetable_edit.html', 
                         grid_data=grid_data, 
                         time_slots=time_slots,
                         sections=sections,
                         teachers=teachers,
                         rooms=rooms,
                         offerings=offerings,
                         filter_type=filter_type,
                         filter_id=int(filter_id) if filter_id else None)

@app.route('/timetable/slot/<int:slot_id>')
def get_slot(slot_id):
    """Get slot details for editing"""
    try:
        slot = TimetableSlot.query.get_or_404(slot_id)
        return jsonify({
            'success': True,
            'slot': {
                'id': slot.id,
                'offering_id': slot.offering_id,
                'room_id': slot.room_id,
                'time_slot_id': slot.time_slot_id
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/timetable/slot/add', methods=['POST'])
def add_slot():
    """Add new timetable slot"""
    try:
        slot = TimetableSlot(
            offering_id=int(request.form['offering_id']),
            section_id=Offering.query.get(int(request.form['offering_id'])).section_id,
            room_id=int(request.form['room_id']),
            time_slot_id=int(request.form['time_slot_id'])
        )
        db.session.add(slot)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/timetable/slot/<int:slot_id>/update', methods=['POST'])
def update_slot(slot_id):
    """Update timetable slot"""
    try:
        slot = TimetableSlot.query.get_or_404(slot_id)
        slot.offering_id = int(request.form['offering_id'])
        slot.section_id = Offering.query.get(int(request.form['offering_id'])).section_id
        slot.room_id = int(request.form['room_id'])
        slot.time_slot_id = int(request.form['time_slot_id'])
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/timetable/slot/<int:slot_id>/delete', methods=['POST'])
def delete_slot(slot_id):
    """Delete timetable slot"""
    try:
        slot = TimetableSlot.query.get_or_404(slot_id)
        db.session.delete(slot)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/timetable/check-conflicts')
def check_conflicts():
    """Check for timetable conflicts"""
    try:
        conflicts = []
        
        # Check for teacher conflicts
        teacher_conflicts = db.session.query(TimetableSlot).join(Offering).join(TimeSlot).group_by(
            Offering.teacher_id, TimeSlot.day_of_week, TimeSlot.period_number
        ).having(func.count(TimetableSlot.id) > 1).all()
        
        for conflict in teacher_conflicts:
            conflicts.append({
                'type': 'teacher_conflict',
                'message': f'Teacher {conflict.offering.teacher.name} has multiple classes at the same time'
            })
        
        # Check for room conflicts
        room_conflicts = db.session.query(TimetableSlot).join(Room).join(TimeSlot).group_by(
            TimetableSlot.room_id, TimeSlot.day_of_week, TimeSlot.period_number
        ).having(func.count(TimetableSlot.id) > 1).all()
        
        for conflict in room_conflicts:
            conflicts.append({
                'type': 'room_conflict',
                'message': f'Room {conflict.room.number} has multiple classes at the same time'
            })
        
        # Check for section conflicts
        section_conflicts = db.session.query(TimetableSlot).join(Section).join(TimeSlot).group_by(
            TimetableSlot.section_id, TimeSlot.day_of_week, TimeSlot.period_number
        ).having(func.count(TimetableSlot.id) > 1).all()
        
        for conflict in section_conflicts:
            conflicts.append({
                'type': 'section_conflict',
                'message': f'Section {conflict.section.name} has multiple classes at the same time'
            })
        
        # Generate HTML for conflicts
        if conflicts:
            html = '<ul class="list-unstyled">'
            for conflict in conflicts:
                html += f'<li><i class="text-danger me-2">⚠</i>{conflict["message"]}</li>'
            html += '</ul>'
        else:
            html = '<p class="text-success">No conflicts detected!</p>'
        
        return jsonify({
            'success': True,
            'conflicts': conflicts,
            'html': html
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})