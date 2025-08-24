#!/usr/bin/env python3
"""
Generic seed script to populate database with sample data
This script creates generic data that can be used by any institution
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
# Import models after app is initialized
from app import Teacher, Course, Section, Room, TimeSlot, Offering, TimetableSlot

def create_time_slots():
    """Create standard time slots for any college"""
    time_slots_data = [
        # Monday to Friday (0-4), Saturday (5)
        # Period 1-8 with standard timings
        {'day': 0, 'period': 1, 'start': '09:00', 'end': '09:50'},
        {'day': 0, 'period': 2, 'start': '09:50', 'end': '10:40'},
        {'day': 0, 'period': 3, 'start': '10:40', 'end': '11:30'},
        {'day': 0, 'period': 4, 'start': '11:45', 'end': '12:35'},  # After break
        {'day': 0, 'period': 5, 'start': '12:35', 'end': '13:25'},
        {'day': 0, 'period': 6, 'start': '14:10', 'end': '15:00'},  # After lunch
        {'day': 0, 'period': 7, 'start': '15:00', 'end': '15:50'},
        {'day': 0, 'period': 8, 'start': '15:50', 'end': '16:40'},
    ]
    
    # Replicate for all weekdays
    all_slots = []
    for day in range(6):  # Monday to Saturday
        for slot_template in time_slots_data:
            time_slot = TimeSlot(
                day_of_week=day,
                period_number=slot_template['period'],
                start_time=slot_template['start'],
                end_time=slot_template['end'],
                is_break=False,
                is_active=True
            )
            all_slots.append(time_slot)
    
    db.session.add_all(all_slots)
    print(f"Created {len(all_slots)} time slots")

def create_teachers():
    """Create generic teachers"""
    teachers_data = [
        # Computer Science Faculty
        {'name': 'Dr. Sarah Johnson', 'code': 'SJ', 'designation': 'Professor', 'load': 12},
        {'name': 'Dr. Michael Chen', 'code': 'MC', 'designation': 'Professor', 'load': 12},
        {'name': 'Dr. Emily Rodriguez', 'code': 'ER', 'designation': 'Associate Professor', 'load': 14},
        {'name': 'Prof. David Kim', 'code': 'DK', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Dr. Lisa Wang', 'code': 'LW', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Prof. James Wilson', 'code': 'JW', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Dr. Maria Garcia', 'code': 'MG', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Prof. Robert Brown', 'code': 'RB', 'designation': 'Assistant Professor', 'load': 16},
        
        # Business Faculty
        {'name': 'Dr. Jennifer Smith', 'code': 'JS', 'designation': 'Professor', 'load': 12},
        {'name': 'Dr. Thomas Anderson', 'code': 'TA', 'designation': 'Associate Professor', 'load': 14},
        {'name': 'Prof. Amanda Davis', 'code': 'AD', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Dr. Christopher Lee', 'code': 'CL', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Prof. Jessica Taylor', 'code': 'JT', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Dr. Daniel Martinez', 'code': 'DM', 'designation': 'Assistant Professor', 'load': 16},
        
        # Engineering Faculty
        {'name': 'Dr. Kevin Thompson', 'code': 'KT', 'designation': 'Professor', 'load': 12},
        {'name': 'Dr. Rachel White', 'code': 'RW', 'designation': 'Associate Professor', 'load': 14},
        {'name': 'Prof. Steven Clark', 'code': 'SC', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Dr. Nicole Lewis', 'code': 'NL', 'designation': 'Assistant Professor', 'load': 16},
        {'name': 'Prof. Andrew Hall', 'code': 'AH', 'designation': 'Assistant Professor', 'load': 16},
    ]
    
    teachers = []
    for teacher_data in teachers_data:
        teacher = Teacher(
            name=teacher_data['name'],
            code=teacher_data['code'],
            designation=teacher_data['designation'],
            max_weekly_load=teacher_data['load']
        )
        teachers.append(teacher)
    
    db.session.add_all(teachers)
    print(f"Created {len(teachers)} teachers")

def create_courses():
    """Create generic courses"""
    courses_data = [
        # Computer Science Courses
        {'code': 'CS101', 'name': 'Introduction to Computer Science', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'CS', 'semester': 'I'},
        {'code': 'CS102', 'name': 'Programming Fundamentals', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'CS', 'semester': 'I'},
        {'code': 'CS103', 'name': 'Programming Lab', 'credits': 2, 'sessions': 2, 'is_lab': True, 'program': 'CS', 'semester': 'I'},
        {'code': 'CS201', 'name': 'Data Structures', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'CS', 'semester': 'III'},
        {'code': 'CS202', 'name': 'Algorithms', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'CS', 'semester': 'III'},
        {'code': 'CS203', 'name': 'Data Structures Lab', 'credits': 2, 'sessions': 2, 'is_lab': True, 'program': 'CS', 'semester': 'III'},
        {'code': 'CS301', 'name': 'Database Systems', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'CS', 'semester': 'V'},
        {'code': 'CS302', 'name': 'Database Lab', 'credits': 2, 'sessions': 2, 'is_lab': True, 'program': 'CS', 'semester': 'V'},
        
        # Business Courses
        {'code': 'BUS101', 'name': 'Introduction to Business', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'BUS', 'semester': 'I'},
        {'code': 'BUS102', 'name': 'Business Communication', 'credits': 3, 'sessions': 3, 'is_lab': False, 'program': 'BUS', 'semester': 'I'},
        {'code': 'BUS201', 'name': 'Marketing Principles', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'BUS', 'semester': 'III'},
        {'code': 'BUS202', 'name': 'Financial Accounting', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'BUS', 'semester': 'III'},
        {'code': 'BUS301', 'name': 'Strategic Management', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'BUS', 'semester': 'V'},
        {'code': 'BUS302', 'name': 'Business Ethics', 'credits': 3, 'sessions': 3, 'is_lab': False, 'program': 'BUS', 'semester': 'V'},
        
        # Engineering Courses
        {'code': 'ENG101', 'name': 'Engineering Mathematics', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'ENG', 'semester': 'I'},
        {'code': 'ENG102', 'name': 'Engineering Physics', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'ENG', 'semester': 'I'},
        {'code': 'ENG103', 'name': 'Physics Lab', 'credits': 2, 'sessions': 2, 'is_lab': True, 'program': 'ENG', 'semester': 'I'},
        {'code': 'ENG201', 'name': 'Engineering Mechanics', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'ENG', 'semester': 'III'},
        {'code': 'ENG202', 'name': 'Mechanics Lab', 'credits': 2, 'sessions': 2, 'is_lab': True, 'program': 'ENG', 'semester': 'III'},
        {'code': 'ENG301', 'name': 'Advanced Engineering', 'credits': 4, 'sessions': 4, 'is_lab': False, 'program': 'ENG', 'semester': 'V'},
    ]
    
    courses = []
    for course_data in courses_data:
        course = Course(
            code=course_data['code'],
            name=course_data['name'],
            credit_hours=course_data['credits'],
            sessions_per_week=course_data['sessions'],
            session_duration=1,
            is_lab=course_data['is_lab'],
            is_online=False,
            program=course_data['program'],
            semester=course_data['semester']
        )
        courses.append(course)
    
    db.session.add_all(courses)
    print(f"Created {len(courses)} courses")

def create_sections():
    """Create generic sections"""
    sections_data = [
        # Computer Science Sections
        {'name': 'CS-I-A', 'program': 'CS', 'semester': 'I', 'section_letter': 'A', 'students': 30},
        {'name': 'CS-I-B', 'program': 'CS', 'semester': 'I', 'section_letter': 'B', 'students': 30},
        {'name': 'CS-III-A', 'program': 'CS', 'semester': 'III', 'section_letter': 'A', 'students': 30},
        {'name': 'CS-III-B', 'program': 'CS', 'semester': 'III', 'section_letter': 'B', 'students': 30},
        {'name': 'CS-V-A', 'program': 'CS', 'semester': 'V', 'section_letter': 'A', 'students': 30},
        {'name': 'CS-V-B', 'program': 'CS', 'semester': 'V', 'section_letter': 'B', 'students': 30},
        
        # Business Sections
        {'name': 'BUS-I-A', 'program': 'BUS', 'semester': 'I', 'section_letter': 'A', 'students': 35},
        {'name': 'BUS-I-B', 'program': 'BUS', 'semester': 'I', 'section_letter': 'B', 'students': 35},
        {'name': 'BUS-III-A', 'program': 'BUS', 'semester': 'III', 'section_letter': 'A', 'students': 35},
        {'name': 'BUS-III-B', 'program': 'BUS', 'semester': 'III', 'section_letter': 'B', 'students': 35},
        {'name': 'BUS-V-A', 'program': 'BUS', 'semester': 'V', 'section_letter': 'A', 'students': 35},
        {'name': 'BUS-V-B', 'program': 'BUS', 'semester': 'V', 'section_letter': 'B', 'students': 35},
        
        # Engineering Sections
        {'name': 'ENG-I-A', 'program': 'ENG', 'semester': 'I', 'section_letter': 'A', 'students': 25},
        {'name': 'ENG-I-B', 'program': 'ENG', 'semester': 'I', 'section_letter': 'B', 'students': 25},
        {'name': 'ENG-III-A', 'program': 'ENG', 'semester': 'III', 'section_letter': 'A', 'students': 25},
        {'name': 'ENG-III-B', 'program': 'ENG', 'semester': 'III', 'section_letter': 'B', 'students': 25},
        {'name': 'ENG-V-A', 'program': 'ENG', 'semester': 'V', 'section_letter': 'A', 'students': 25},
        {'name': 'ENG-V-B', 'program': 'ENG', 'semester': 'V', 'section_letter': 'B', 'students': 25},
    ]
    
    sections = []
    for section_data in sections_data:
        section = Section(
            name=section_data['name'],
            program=section_data['program'],
            semester=section_data['semester'],
            section_letter=section_data['section_letter'],
            student_count=section_data['students']
        )
        sections.append(section)
    
    db.session.add_all(sections)
    print(f"Created {len(sections)} sections")

def create_rooms():
    """Create generic rooms"""
    rooms_data = [
        # Classrooms
        {'number': '101', 'name': 'Classroom 101', 'type': 'classroom', 'capacity': 40},
        {'number': '102', 'name': 'Classroom 102', 'type': 'classroom', 'capacity': 40},
        {'number': '103', 'name': 'Classroom 103', 'type': 'classroom', 'capacity': 40},
        {'number': '201', 'name': 'Classroom 201', 'type': 'classroom', 'capacity': 40},
        {'number': '202', 'name': 'Classroom 202', 'type': 'classroom', 'capacity': 40},
        {'number': '203', 'name': 'Classroom 203', 'type': 'classroom', 'capacity': 40},
        {'number': '301', 'name': 'Classroom 301', 'type': 'classroom', 'capacity': 40},
        {'number': '302', 'name': 'Classroom 302', 'type': 'classroom', 'capacity': 40},
        {'number': '303', 'name': 'Classroom 303', 'type': 'classroom', 'capacity': 40},
        
        # Computer Labs
        {'number': 'LAB1', 'name': 'Computer Lab 1', 'type': 'lab', 'capacity': 30},
        {'number': 'LAB2', 'name': 'Computer Lab 2', 'type': 'lab', 'capacity': 30},
        {'number': 'LAB3', 'name': 'Computer Lab 3', 'type': 'lab', 'capacity': 30},
        
        # Science Labs
        {'number': 'SLAB1', 'name': 'Science Lab 1', 'type': 'lab', 'capacity': 25},
        {'number': 'SLAB2', 'name': 'Science Lab 2', 'type': 'lab', 'capacity': 25},
        
        # Auditorium
        {'number': 'AUD', 'name': 'Main Auditorium', 'type': 'auditorium', 'capacity': 200},
    ]
    
    rooms = []
    for room_data in rooms_data:
        room = Room(
            number=room_data['number'],
            name=room_data['name'],
            room_type=room_data['type'],
            capacity=room_data['capacity']
        )
        rooms.append(room)
    
    db.session.add_all(rooms)
    print(f"Created {len(rooms)} rooms")

def create_offerings():
    """Create generic course offerings"""
    offerings_data = [
        # CS-I Offerings
        {'teacher_name': 'Dr. Sarah Johnson', 'course_code': 'CS101', 'section_name': 'CS-I-A'},
        {'teacher_name': 'Dr. Michael Chen', 'course_code': 'CS101', 'section_name': 'CS-I-B'},
        {'teacher_name': 'Dr. Emily Rodriguez', 'course_code': 'CS102', 'section_name': 'CS-I-A'},
        {'teacher_name': 'Prof. David Kim', 'course_code': 'CS102', 'section_name': 'CS-I-B'},
        {'teacher_name': 'Dr. Lisa Wang', 'course_code': 'CS103', 'section_name': 'CS-I-A'},
        {'teacher_name': 'Prof. James Wilson', 'course_code': 'CS103', 'section_name': 'CS-I-B'},
        
        # CS-III Offerings
        {'teacher_name': 'Dr. Sarah Johnson', 'course_code': 'CS201', 'section_name': 'CS-III-A'},
        {'teacher_name': 'Dr. Michael Chen', 'course_code': 'CS201', 'section_name': 'CS-III-B'},
        {'teacher_name': 'Dr. Emily Rodriguez', 'course_code': 'CS202', 'section_name': 'CS-III-A'},
        {'teacher_name': 'Prof. David Kim', 'course_code': 'CS202', 'section_name': 'CS-III-B'},
        {'teacher_name': 'Dr. Lisa Wang', 'course_code': 'CS203', 'section_name': 'CS-III-A'},
        {'teacher_name': 'Prof. James Wilson', 'course_code': 'CS203', 'section_name': 'CS-III-B'},
        
        # CS-V Offerings
        {'teacher_name': 'Dr. Sarah Johnson', 'course_code': 'CS301', 'section_name': 'CS-V-A'},
        {'teacher_name': 'Dr. Michael Chen', 'course_code': 'CS301', 'section_name': 'CS-V-B'},
        {'teacher_name': 'Dr. Emily Rodriguez', 'course_code': 'CS302', 'section_name': 'CS-V-A'},
        {'teacher_name': 'Prof. David Kim', 'course_code': 'CS302', 'section_name': 'CS-V-B'},
        
        # BUS-I Offerings
        {'teacher_name': 'Dr. Jennifer Smith', 'course_code': 'BUS101', 'section_name': 'BUS-I-A'},
        {'teacher_name': 'Dr. Thomas Anderson', 'course_code': 'BUS101', 'section_name': 'BUS-I-B'},
        {'teacher_name': 'Prof. Amanda Davis', 'course_code': 'BUS102', 'section_name': 'BUS-I-A'},
        {'teacher_name': 'Dr. Christopher Lee', 'course_code': 'BUS102', 'section_name': 'BUS-I-B'},
        
        # BUS-III Offerings
        {'teacher_name': 'Dr. Jennifer Smith', 'course_code': 'BUS201', 'section_name': 'BUS-III-A'},
        {'teacher_name': 'Dr. Thomas Anderson', 'course_code': 'BUS201', 'section_name': 'BUS-III-B'},
        {'teacher_name': 'Prof. Amanda Davis', 'course_code': 'BUS202', 'section_name': 'BUS-III-A'},
        {'teacher_name': 'Dr. Christopher Lee', 'course_code': 'BUS202', 'section_name': 'BUS-III-B'},
        
        # BUS-V Offerings
        {'teacher_name': 'Dr. Jennifer Smith', 'course_code': 'BUS301', 'section_name': 'BUS-V-A'},
        {'teacher_name': 'Dr. Thomas Anderson', 'course_code': 'BUS301', 'section_name': 'BUS-V-B'},
        {'teacher_name': 'Prof. Amanda Davis', 'course_code': 'BUS302', 'section_name': 'BUS-V-A'},
        {'teacher_name': 'Dr. Christopher Lee', 'course_code': 'BUS302', 'section_name': 'BUS-V-B'},
        
        # ENG-I Offerings
        {'teacher_name': 'Dr. Kevin Thompson', 'course_code': 'ENG101', 'section_name': 'ENG-I-A'},
        {'teacher_name': 'Dr. Rachel White', 'course_code': 'ENG101', 'section_name': 'ENG-I-B'},
        {'teacher_name': 'Prof. Steven Clark', 'course_code': 'ENG102', 'section_name': 'ENG-I-A'},
        {'teacher_name': 'Dr. Nicole Lewis', 'course_code': 'ENG102', 'section_name': 'ENG-I-B'},
        {'teacher_name': 'Prof. Andrew Hall', 'course_code': 'ENG103', 'section_name': 'ENG-I-A'},
        {'teacher_name': 'Dr. Kevin Thompson', 'course_code': 'ENG103', 'section_name': 'ENG-I-B'},
        
        # ENG-III Offerings
        {'teacher_name': 'Dr. Rachel White', 'course_code': 'ENG201', 'section_name': 'ENG-III-A'},
        {'teacher_name': 'Prof. Steven Clark', 'course_code': 'ENG201', 'section_name': 'ENG-III-B'},
        {'teacher_name': 'Dr. Nicole Lewis', 'course_code': 'ENG202', 'section_name': 'ENG-III-A'},
        {'teacher_name': 'Prof. Andrew Hall', 'course_code': 'ENG202', 'section_name': 'ENG-III-B'},
        
        # ENG-V Offerings
        {'teacher_name': 'Dr. Kevin Thompson', 'course_code': 'ENG301', 'section_name': 'ENG-V-A'},
        {'teacher_name': 'Dr. Rachel White', 'course_code': 'ENG301', 'section_name': 'ENG-V-B'},
    ]
    
    offerings = []
    for offering_data in offerings_data:
        teacher = Teacher.query.filter_by(name=offering_data['teacher_name']).first()
        course = Course.query.filter_by(code=offering_data['course_code']).first()
        section = Section.query.filter_by(name=offering_data['section_name']).first()
        
        if teacher and course and section:
            offering = Offering(
                teacher_id=teacher.id,
                course_id=course.id,
                section_id=section.id
            )
            offerings.append(offering)
        else:
            print(f"Warning: Could not create offering for {offering_data}")
    
    db.session.add_all(offerings)
    print(f"Created {len(offerings)} offerings")

def main():
    """Run the generic seed script"""
    with app.app_context():
        print("Starting generic database seeding...")
        
        # Clear existing data
        print("Clearing existing data...")
        TimetableSlot.query.delete()
        Offering.query.delete()
        Teacher.query.delete()
        Course.query.delete()
        Section.query.delete()
        Room.query.delete()
        TimeSlot.query.delete()
        db.session.commit()
        
        # Create new data
        create_time_slots()
        create_teachers()
        create_courses()
        create_sections()
        create_rooms()
        
        # Commit before creating offerings (need IDs)
        db.session.commit()
        
        create_offerings()
        
        # Final commit
        db.session.commit()
        
        print("Generic database seeding completed successfully!")
        print("\nSummary:")
        print(f"Teachers: {Teacher.query.count()}")
        print(f"Courses: {Course.query.count()}")
        print(f"Sections: {Section.query.count()}")
        print(f"Rooms: {Room.query.count()}")
        print(f"Time Slots: {TimeSlot.query.count()}")
        print(f"Offerings: {Offering.query.count()}")
        print("\nThis is a generic dataset that can be customized for any institution.")

if __name__ == "__main__":
    main() 