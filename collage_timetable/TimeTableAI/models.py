from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

def create_models(db):
    """Create all models with the given database instance"""
    
    class Teacher(db.Model):
        """Faculty/Teacher model based on workload data"""
        __tablename__ = 'teachers'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        code = db.Column(db.String(20), unique=True)  # Optional faculty code
        designation = db.Column(db.String(50), nullable=False)  # Professor, AP Stage-I, etc.
        max_weekly_load = db.Column(db.Integer, default=16)  # Maximum weekly teaching hours
        is_active = db.Column(db.Boolean, default=True)
        
        # Relationships
        offerings = relationship("Offering", back_populates="teacher")
        availabilities = relationship("TeacherAvailability", back_populates="teacher", cascade="all, delete-orphan")
        
        def __repr__(self):
            return f'<Teacher {self.name}>'

    class Room(db.Model):
        """Room/Classroom model"""
        __tablename__ = 'rooms'
        
        id = db.Column(db.Integer, primary_key=True)
        number = db.Column(db.String(20), nullable=False, unique=True)
        name = db.Column(db.String(100))  # Optional room name
        room_type = db.Column(db.String(20), nullable=False)  # 'classroom', 'lab', 'auditorium'
        capacity = db.Column(db.Integer, default=60)
        is_active = db.Column(db.Boolean, default=True)
        
        # Relationships
        offerings = relationship("Offering", back_populates="room")
        availabilities = relationship("RoomAvailability", back_populates="room", cascade="all, delete-orphan")
        timetable_slots = relationship("TimetableSlot", back_populates="room")
        
        def __repr__(self):
            return f'<Room {self.number}>'

    class Course(db.Model):
        """Course/Subject model based on course codes from workload data"""
        __tablename__ = 'courses'
        
        id = db.Column(db.Integer, primary_key=True)
        code = db.Column(db.String(20), nullable=False, unique=True)  # e.g., BCOM-22-301
        name = db.Column(db.String(200), nullable=False)  # e.g., Company Law
        credit_hours = db.Column(db.Integer, default=4)
        sessions_per_week = db.Column(db.Integer, default=4)  # Number of sessions needed per week
        session_duration = db.Column(db.Integer, default=1)  # Duration in time slots (1 for theory, 2+ for labs)
        is_lab = db.Column(db.Boolean, default=False)
        is_online = db.Column(db.Boolean, default=False)
        program = db.Column(db.String(20), nullable=False)  # BCOM, BCA, MCA, MBA, BAHMC
        semester = db.Column(db.String(10), nullable=False)  # I, III, V
        is_active = db.Column(db.Boolean, default=True)
        
        # Relationships
        offerings = relationship("Offering", back_populates="course")
        
        def __repr__(self):
            return f'<Course {self.code}: {self.name}>'

    class Section(db.Model):
        """Section model for student groups"""
        __tablename__ = 'sections'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50), nullable=False)  # e.g., BCA-III-A, BCOM-V
        program = db.Column(db.String(20), nullable=False)  # BCOM, BCA, MCA, MBA, BAHMC
        semester = db.Column(db.String(10), nullable=False)  # I, III, V
        section_letter = db.Column(db.String(5))  # A, B, C, D (optional for single sections)
        student_count = db.Column(db.Integer, default=60)
        is_active = db.Column(db.Boolean, default=True)
        
        # Relationships
        offerings = relationship("Offering", back_populates="section")
        timetable_slots = relationship("TimetableSlot", back_populates="section")
        
        __table_args__ = (UniqueConstraint('program', 'semester', 'section_letter'),)
        
        def __repr__(self):
            return f'<Section {self.name}>'

    class TimeSlot(db.Model):
        """Time slot model for daily periods"""
        __tablename__ = 'time_slots'
        
        id = db.Column(db.Integer, primary_key=True)
        day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
        period_number = db.Column(db.Integer, nullable=False)  # 1-8 for daily periods
        start_time = db.Column(db.String(10), nullable=False)  # e.g., "09:00"
        end_time = db.Column(db.String(10), nullable=False)    # e.g., "09:50"
        is_break = db.Column(db.Boolean, default=False)
        is_active = db.Column(db.Boolean, default=True)
        
        # Relationships
        timetable_slots = relationship("TimetableSlot", back_populates="time_slot")
        teacher_availabilities = relationship("TeacherAvailability", back_populates="time_slot")
        room_availabilities = relationship("RoomAvailability", back_populates="time_slot")
        
        __table_args__ = (UniqueConstraint('day_of_week', 'period_number'),)
        
        def __repr__(self):
            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return f'<TimeSlot {days[self.day_of_week]} Period {self.period_number}>'

    class Offering(db.Model):
        """Junction table linking teachers, courses, and sections"""
        __tablename__ = 'offerings'
        
        id = db.Column(db.Integer, primary_key=True)
        teacher_id = db.Column(db.Integer, ForeignKey('teachers.id'), nullable=False)
        course_id = db.Column(db.Integer, ForeignKey('courses.id'), nullable=False)
        section_id = db.Column(db.Integer, ForeignKey('sections.id'), nullable=False)
        room_id = db.Column(db.Integer, ForeignKey('rooms.id'))  # Preferred room, can be overridden
        
        # Relationships
        teacher = relationship("Teacher", back_populates="offerings")
        course = relationship("Course", back_populates="offerings")
        section = relationship("Section", back_populates="offerings")
        room = relationship("Room", back_populates="offerings")
        timetable_slots = relationship("TimetableSlot", back_populates="offering")
        
        __table_args__ = (UniqueConstraint('teacher_id', 'course_id', 'section_id'),)
        
        def __repr__(self):
            return f'<Offering {self.teacher.name} - {self.course.code} - {self.section.name}>'

    class TimetableSlot(db.Model):
        """Generated timetable slots"""
        __tablename__ = 'timetable_slots'
        
        id = db.Column(db.Integer, primary_key=True)
        offering_id = db.Column(db.Integer, ForeignKey('offerings.id'), nullable=False)
        section_id = db.Column(db.Integer, ForeignKey('sections.id'), nullable=False)
        room_id = db.Column(db.Integer, ForeignKey('rooms.id'), nullable=False)
        time_slot_id = db.Column(db.Integer, ForeignKey('time_slots.id'), nullable=False)
        is_locked = db.Column(db.Boolean, default=False)  # For manual constraints
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Relationships
        offering = relationship("Offering", back_populates="timetable_slots")
        section = relationship("Section", back_populates="timetable_slots")
        room = relationship("Room", back_populates="timetable_slots")
        time_slot = relationship("TimeSlot", back_populates="timetable_slots")
        
        __table_args__ = (UniqueConstraint('section_id', 'time_slot_id'),
                          UniqueConstraint('room_id', 'time_slot_id'))
        
        def __repr__(self):
            return f'<TimetableSlot {self.offering.course.code} - {self.section.name}>'

    class TeacherAvailability(db.Model):
        """Teacher availability constraints"""
        __tablename__ = 'teacher_availabilities'
        
        id = db.Column(db.Integer, primary_key=True)
        teacher_id = db.Column(db.Integer, ForeignKey('teachers.id'), nullable=False)
        time_slot_id = db.Column(db.Integer, ForeignKey('time_slots.id'), nullable=False)
        is_available = db.Column(db.Boolean, default=True)
        
        # Relationships
        teacher = relationship("Teacher", back_populates="availabilities")
        time_slot = relationship("TimeSlot", back_populates="teacher_availabilities")
        
        __table_args__ = (UniqueConstraint('teacher_id', 'time_slot_id'),)

    class RoomAvailability(db.Model):
        """Room availability constraints"""
        __tablename__ = 'room_availabilities'
        
        id = db.Column(db.Integer, primary_key=True)
        room_id = db.Column(db.Integer, ForeignKey('rooms.id'), nullable=False)
        time_slot_id = db.Column(db.Integer, ForeignKey('time_slots.id'), nullable=False)
        is_available = db.Column(db.Boolean, default=True)
        
        # Relationships
        room = relationship("Room", back_populates="availabilities")
        time_slot = relationship("TimeSlot", back_populates="room_availabilities")
        
        __table_args__ = (UniqueConstraint('room_id', 'time_slot_id'),)

    class TimetableGeneration(db.Model):
        """Track timetable generation runs"""
        __tablename__ = 'timetable_generations'
        
        id = db.Column(db.Integer, primary_key=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        status = db.Column(db.String(20), default='pending')  # pending, success, failed
        solver_status = db.Column(db.String(50))
        total_slots = db.Column(db.Integer)
        constraints_satisfied = db.Column(db.Integer)
        solve_time_seconds = db.Column(db.Float)
        notes = db.Column(db.Text)
        
        def __repr__(self):
            return f'<TimetableGeneration {self.id}: {self.status}>'

    class UserConstraint(db.Model):
        """User-defined constraints for timetable generation"""
        __tablename__ = 'user_constraints'
        
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(100), nullable=False)
        constraint_type = db.Column(db.String(50), nullable=False)  # 'teacher_unavailable', 'room_unavailable', 'section_preference', 'time_preference'
        teacher_id = db.Column(db.Integer, ForeignKey('teachers.id'))
        room_id = db.Column(db.Integer, ForeignKey('rooms.id'))
        section_id = db.Column(db.Integer, ForeignKey('sections.id'))
        time_slot_id = db.Column(db.Integer, ForeignKey('time_slots.id'))
        day_of_week = db.Column(db.Integer)  # 0-6 for Monday-Sunday
        period_number = db.Column(db.Integer)  # 1-8 for periods
        is_active = db.Column(db.Boolean, default=True)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)
        
        # Relationships
        teacher = relationship("Teacher")
        room = relationship("Room")
        section = relationship("Section")
        time_slot = relationship("TimeSlot")
        
        def __repr__(self):
            return f'<UserConstraint {self.name}: {self.constraint_type}>'

    class WorkloadFile(db.Model):
        """Uploaded workload files"""
        __tablename__ = 'workload_files'
        
        id = db.Column(db.Integer, primary_key=True)
        filename = db.Column(db.String(255), nullable=False)
        original_filename = db.Column(db.String(255), nullable=False)
        file_path = db.Column(db.String(500), nullable=False)
        file_size = db.Column(db.Integer)
        uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
        processed = db.Column(db.Boolean, default=False)
        processing_status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
        processing_notes = db.Column(db.Text)
        
        def __repr__(self):
            return f'<WorkloadFile {self.original_filename}>'

    # Return all models as a dictionary
    return {
        'Teacher': Teacher,
        'Course': Course,
        'Section': Section,
        'Room': Room,
        'TimeSlot': TimeSlot,
        'Offering': Offering,
        'TimetableSlot': TimetableSlot,
        'TeacherAvailability': TeacherAvailability,
        'RoomAvailability': RoomAvailability,
        'TimetableGeneration': TimetableGeneration,
        'UserConstraint': UserConstraint,
        'WorkloadFile': WorkloadFile
    }
