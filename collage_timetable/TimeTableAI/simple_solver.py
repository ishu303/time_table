#!/usr/bin/env python3
"""
Simplified timetable solver that's more flexible
"""

import logging
from typing import Dict, List, Tuple, Optional
from ortools.sat.python import cp_model
from .app import db
from .models import (
    Teacher, Course, Section, Room, TimeSlot, Offering, TimetableSlot,
    TeacherAvailability, RoomAvailability, TimetableGeneration, UserConstraint
)
from datetime import datetime

logger = logging.getLogger(__name__)

class SimpleTimetableSolver:
    """Simplified OR-Tools CP-SAT based timetable solver"""
    
    def __init__(self):
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        self.variables = {}
        self.offerings = []
        self.time_slots = []
        self.rooms = []
        self.sections = []
        
    def generate_timetable(self) -> Dict:
        """Main method to generate timetable"""
        try:
            logger.info("Starting simplified timetable generation...")
            
            # Clear existing timetable
            TimetableSlot.query.delete()
            db.session.commit()
            
            # Load data
            self._load_data()
            
            # Create variables
            self._create_variables()
            
            # Add constraints
            self._add_hard_constraints()
            
            # Solve
            start_time = datetime.now()
            status = self.solver.Solve(self.model)
            solve_time = (datetime.now() - start_time).total_seconds()
            
            result = self._process_solution(status, solve_time)
            
            # Save generation record
            generation = TimetableGeneration(
                status=result['status'],
                solver_status=result['solver_status'],
                total_slots=result.get('total_slots', 0),
                solve_time_seconds=solve_time,
                notes=result.get('notes', '')
            )
            db.session.add(generation)
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in timetable generation: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e),
                'solver_status': 'error'
            }
    
    def _load_data(self):
        """Load all necessary data from database"""
        # NOTE: The solver is simplified and has hardcoded limits for performance.
        # It only considers the first 20 offerings. This should be adjusted for real-world use.
        self.offerings = Offering.query.join(Course).join(Teacher).join(Section).filter(
            Course.is_active == True,
            Teacher.is_active == True,
            Section.is_active == True
        ).limit(20).all()
        
        self.time_slots = TimeSlot.query.filter(
            TimeSlot.is_active == True,
            TimeSlot.is_break == False
        ).order_by(TimeSlot.day_of_week, TimeSlot.period_number).all()
        
        self.rooms = Room.query.filter(Room.is_active == True).all()
        self.sections = Section.query.filter(Section.is_active == True).all()
        
        logger.info(f"Loaded {len(self.offerings)} offerings, {len(self.time_slots)} time slots, "
                   f"{len(self.rooms)} rooms, {len(self.sections)} sections")
    
    def _create_variables(self):
        """Create decision variables for the solver"""
        # Variable: assignment[offering_id][time_slot_id][room_id] = 0/1
        self.variables = {}
        
        for offering in self.offerings:
            self.variables[offering.id] = {}
            for time_slot in self.time_slots:
                self.variables[offering.id][time_slot.id] = {}
                for room in self.rooms:
                    # Only consider suitable rooms (labs for lab courses, etc.)
                    if self._is_suitable_room(offering.course, room):
                        var_name = f'assign_{offering.id}_{time_slot.id}_{room.id}'
                        self.variables[offering.id][time_slot.id][room.id] = self.model.NewBoolVar(var_name)
    
    def _is_suitable_room(self, course, room) -> bool:
        """Check if room is suitable for course"""
        if course.is_lab and room.room_type != 'lab':
            return False
        if not course.is_lab and room.room_type == 'lab':
            # Allow theory classes in labs if no other option
            pass
        return True
    
    def _add_user_constraints(self):
        """Add user-defined constraints"""
        user_constraints = UserConstraint.query.filter_by(is_active=True).all()
        
        for constraint in user_constraints:
            if constraint.constraint_type == 'teacher_unavailable':
                # Teacher unavailable at specific time
                if constraint.teacher_id:
                    for offering in self.offerings:
                        if offering.teacher_id == constraint.teacher_id:
                            time_slot_id = self._get_time_slot_id(constraint.day_of_week, constraint.period_number)
                            if time_slot_id and time_slot_id in self.variables[offering.id]:
                                for room_id in self.variables[offering.id][time_slot_id]:
                                    self.model.Add(self.variables[offering.id][time_slot_id][room_id] == 0)
            
            elif constraint.constraint_type == 'room_unavailable':
                # Room unavailable at specific time
                if constraint.room_id:
                    time_slot_id = self._get_time_slot_id(constraint.day_of_week, constraint.period_number)
                    for offering in self.offerings:
                        if time_slot_id in self.variables[offering.id]:
                            if constraint.room_id in self.variables[offering.id][time_slot_id]:
                                self.model.Add(self.variables[offering.id][time_slot_id][constraint.room_id] == 0)
            
            elif constraint.constraint_type == 'section_preference':
                # Section preference (avoid specific time)
                if constraint.section_id:
                    time_slot_id = self._get_time_slot_id(constraint.day_of_week, constraint.period_number)
                    for offering in self.offerings:
                        if offering.section_id == constraint.section_id:
                            if time_slot_id in self.variables[offering.id]:
                                for room_id in self.variables[offering.id][time_slot_id]:
                                    self.model.Add(self.variables[offering.id][time_slot_id][room_id] == 0)
    
    def _get_time_slot_id(self, day_of_week: int, period_number: int) -> Optional[int]:
        """Get time slot ID from day and period"""
        for time_slot in self.time_slots:
            if time_slot.day_of_week == day_of_week and time_slot.period_number == period_number:
                return time_slot.id
        return None
    
    def _add_hard_constraints(self):
        """Add hard constraints that must be satisfied"""
        
        # Constraint 1: Each offering must be scheduled at least once (relaxed from exactly sessions_per_week)
        for offering in self.offerings:
            # NOTE: The number of sessions is limited to a maximum of 3 for simplicity.
            sessions_needed = min(offering.course.sessions_per_week, 3)  # Limit to 3 sessions max
            assignments = []
            
            for time_slot_id in self.variables[offering.id]:
                for room_id in self.variables[offering.id][time_slot_id]:
                    assignments.append(self.variables[offering.id][time_slot_id][room_id])
            
            if assignments:
                # At least 1 session, at most sessions_needed
                self.model.Add(sum(assignments) >= 1)
                self.model.Add(sum(assignments) <= sessions_needed)
        
        # Constraint 2: No teacher conflicts (teacher can't be in two places at once)
        teacher_slots = {}
        for offering in self.offerings:
            teacher_id = offering.teacher_id
            if teacher_id not in teacher_slots:
                teacher_slots[teacher_id] = {}
            
            for time_slot_id in self.variables[offering.id]:
                if time_slot_id not in teacher_slots[teacher_id]:
                    teacher_slots[teacher_id][time_slot_id] = []
                
                for room_id in self.variables[offering.id][time_slot_id]:
                    teacher_slots[teacher_id][time_slot_id].append(
                        self.variables[offering.id][time_slot_id][room_id]
                    )
        
        for teacher_id, slots in teacher_slots.items():
            for time_slot_id, assignments in slots.items():
                if len(assignments) > 1:
                    self.model.Add(sum(assignments) <= 1)
        
        # Constraint 3: No room conflicts (room can't host two classes at once)
        room_slots = {}
        for offering in self.offerings:
            for time_slot_id in self.variables[offering.id]:
                for room_id in self.variables[offering.id][time_slot_id]:
                    if room_id not in room_slots:
                        room_slots[room_id] = {}
                    if time_slot_id not in room_slots[room_id]:
                        room_slots[room_id][time_slot_id] = []
                    
                    room_slots[room_id][time_slot_id].append(
                        self.variables[offering.id][time_slot_id][room_id]
                    )
        
        for room_id, slots in room_slots.items():
            for time_slot_id, assignments in slots.items():
                if len(assignments) > 1:
                    self.model.Add(sum(assignments) <= 1)
        
        # Constraint 4: No section conflicts (section can't have two classes at once)
        section_slots = {}
        for offering in self.offerings:
            section_id = offering.section_id
            if section_id not in section_slots:
                section_slots[section_id] = {}
            
            for time_slot_id in self.variables[offering.id]:
                if time_slot_id not in section_slots[section_id]:
                    section_slots[section_id][time_slot_id] = []
                
                for room_id in self.variables[offering.id][time_slot_id]:
                    section_slots[section_id][time_slot_id].append(
                        self.variables[offering.id][time_slot_id][room_id]
                    )
        
        for section_id, slots in section_slots.items():
            for time_slot_id, assignments in slots.items():
                if len(assignments) > 1:
                    self.model.Add(sum(assignments) <= 1)
        
        # Constraint 5: User-defined constraints
        self._add_user_constraints()
    
    def _process_solution(self, status, solve_time: float) -> Dict:
        """Process the solver solution and save to database"""
        if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
            logger.info(f"Solution found! Status: {self.solver.StatusName(status)}")
            
            # Extract solution
            scheduled_slots = []
            total_scheduled = 0
            
            for offering in self.offerings:
                for time_slot_id in self.variables[offering.id]:
                    for room_id in self.variables[offering.id][time_slot_id]:
                        if self.solver.Value(self.variables[offering.id][time_slot_id][room_id]) == 1:
                            # Create timetable slot
                            timetable_slot = TimetableSlot(
                                offering_id=offering.id,
                                section_id=offering.section_id,
                                room_id=room_id,
                                time_slot_id=time_slot_id
                            )
                            scheduled_slots.append(timetable_slot)
                            total_scheduled += 1
            
            # Save to database
            db.session.add_all(scheduled_slots)
            db.session.commit()
            
            return {
                'status': 'success',
                'solver_status': self.solver.StatusName(status),
                'total_slots': total_scheduled,
                'solve_time': solve_time,
                'statistics': {
                    'branches': self.solver.NumBranches(),
                    'conflicts': self.solver.NumConflicts(),
                    'wall_time': self.solver.WallTime()
                }
            }
        else:
            logger.error(f"No solution found. Status: {self.solver.StatusName(status)}")
            return {
                'status': 'failed',
                'solver_status': self.solver.StatusName(status),
                'solve_time': solve_time,
                'error': 'No feasible solution found'
            } 