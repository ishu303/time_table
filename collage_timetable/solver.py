import logging
from typing import Dict, List, Tuple, Optional
from ortools.sat.python import cp_model
from app import db
from models import (Teacher, Course, Section, Room, TimeSlot, Offering, 
                   TimetableSlot, TeacherAvailability, RoomAvailability, 
                   TimetableGeneration)
from datetime import datetime

logger = logging.getLogger(__name__)

class TimetableSolver:
    """OR-Tools CP-SAT based timetable solver"""
    
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
            logger.info("Starting timetable generation...")
            
            # Clear existing timetable
            TimetableSlot.query.delete()
            db.session.commit()
            
            # Load data
            self._load_data()
            
            # Create variables
            self._create_variables()
            
            # Add constraints
            self._add_hard_constraints()
            self._add_soft_constraints()
            
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
        self.offerings = Offering.query.join(Course).join(Teacher).join(Section).filter(
            Course.is_active == True,
            Teacher.is_active == True,
            Section.is_active == True
        ).all()
        
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
    
    def _is_suitable_room(self, course: Course, room: Room) -> bool:
        """Check if room is suitable for course"""
        if course.is_lab and room.room_type != 'lab':
            return False
        if not course.is_lab and room.room_type == 'lab':
            # Allow theory classes in labs if no other option
            pass
        return True
    
    def _add_hard_constraints(self):
        """Add hard constraints that must be satisfied"""
        
        # Constraint 1: Each offering must be scheduled exactly sessions_per_week times
        for offering in self.offerings:
            sessions_needed = offering.course.sessions_per_week
            assignments = []
            
            for time_slot_id in self.variables[offering.id]:
                for room_id in self.variables[offering.id][time_slot_id]:
                    assignments.append(self.variables[offering.id][time_slot_id][room_id])
            
            if assignments:
                self.model.Add(sum(assignments) == sessions_needed)
        
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
        
        # Constraint 5: Teacher availability
        self._add_availability_constraints()
        
        # Constraint 6: Lab duration constraints (labs need consecutive slots)
        self._add_lab_duration_constraints()
    
    def _add_availability_constraints(self):
        """Add teacher and room availability constraints"""
        # Teacher availability
        teacher_unavailable = {}
        for availability in TeacherAvailability.query.filter_by(is_available=False).all():
            teacher_id = availability.teacher_id
            time_slot_id = availability.time_slot_id
            if teacher_id not in teacher_unavailable:
                teacher_unavailable[teacher_id] = set()
            teacher_unavailable[teacher_id].add(time_slot_id)
        
        for offering in self.offerings:
            teacher_id = offering.teacher_id
            if teacher_id in teacher_unavailable:
                for time_slot_id in teacher_unavailable[teacher_id]:
                    if time_slot_id in self.variables[offering.id]:
                        for room_id in self.variables[offering.id][time_slot_id]:
                            self.model.Add(self.variables[offering.id][time_slot_id][room_id] == 0)
        
        # Room availability
        room_unavailable = {}
        for availability in RoomAvailability.query.filter_by(is_available=False).all():
            room_id = availability.room_id
            time_slot_id = availability.time_slot_id
            if room_id not in room_unavailable:
                room_unavailable[room_id] = set()
            room_unavailable[room_id].add(time_slot_id)
        
        for offering in self.offerings:
            for time_slot_id in self.variables[offering.id]:
                for room_id in self.variables[offering.id][time_slot_id]:
                    if room_id in room_unavailable and time_slot_id in room_unavailable[room_id]:
                        self.model.Add(self.variables[offering.id][time_slot_id][room_id] == 0)
    
    def _add_lab_duration_constraints(self):
        """Ensure lab courses get consecutive time slots"""
        # Group time slots by day
        days_slots = {}
        for slot in self.time_slots:
            day = slot.day_of_week
            if day not in days_slots:
                days_slots[day] = []
            days_slots[day].append(slot)
        
        # Sort slots by period number for each day
        for day in days_slots:
            days_slots[day].sort(key=lambda x: x.period_number)
        
        # Add consecutive constraints for lab courses
        for offering in self.offerings:
            if offering.course.is_lab and offering.course.session_duration > 1:
                duration = offering.course.session_duration
                
                for day, day_slots in days_slots.items():
                    if len(day_slots) >= duration:
                        # For each possible starting position
                        for i in range(len(day_slots) - duration + 1):
                            consecutive_slots = day_slots[i:i + duration]
                            
                            # If any slot in the sequence is assigned, all must be assigned
                            for room_id in self.variables[offering.id].get(consecutive_slots[0].id, {}):
                                sequence_vars = []
                                for slot in consecutive_slots:
                                    if slot.id in self.variables[offering.id] and room_id in self.variables[offering.id][slot.id]:
                                        sequence_vars.append(self.variables[offering.id][slot.id][room_id])
                                
                                if len(sequence_vars) == duration:
                                    # All slots must have the same assignment value
                                    for j in range(1, len(sequence_vars)):
                                        self.model.Add(sequence_vars[0] == sequence_vars[j])
    
    def _add_soft_constraints(self):
        """Add soft constraints for optimization"""
        soft_constraints = []
        
        # Prefer even distribution of classes throughout the week
        self._add_distribution_preferences(soft_constraints)
        
        # Prefer certain time slots over others
        self._add_time_preferences(soft_constraints)
        
        # Add objective to maximize soft constraint satisfaction
        if soft_constraints:
            self.model.Maximize(sum(soft_constraints))
    
    def _add_distribution_preferences(self, soft_constraints: List):
        """Add preferences for even distribution of classes"""
        # Group time slots by day
        days = {}
        for slot in self.time_slots:
            day = slot.day_of_week
            if day not in days:
                days[day] = []
            days[day].append(slot.id)
        
        # For each section, prefer even distribution across days
        for section in self.sections:
            section_offerings = [o for o in self.offerings if o.section_id == section.id]
            
            daily_assignments = {}
            for day, day_slot_ids in days.items():
                daily_vars = []
                for offering in section_offerings:
                    for slot_id in day_slot_ids:
                        if slot_id in self.variables[offering.id]:
                            for room_id in self.variables[offering.id][slot_id]:
                                daily_vars.append(self.variables[offering.id][slot_id][room_id])
                
                if daily_vars:
                    daily_assignments[day] = self.model.NewIntVar(0, len(daily_vars), f'daily_{section.id}_{day}')
                    self.model.Add(daily_assignments[day] == sum(daily_vars))
            
            # Add preference for balanced daily distribution
            if len(daily_assignments) > 1:
                days_list = list(daily_assignments.keys())
                for i in range(len(days_list) - 1):
                    for j in range(i + 1, len(days_list)):
                        # Penalize large differences between days
                        diff_var = self.model.NewIntVar(-20, 20, f'diff_{section.id}_{days_list[i]}_{days_list[j]}')
                        self.model.Add(diff_var == daily_assignments[days_list[i]] - daily_assignments[days_list[j]])
                        
                        abs_diff = self.model.NewIntVar(0, 20, f'abs_diff_{section.id}_{days_list[i]}_{days_list[j]}')
                        self.model.AddAbsEquality(abs_diff, diff_var)
                        
                        # Preference for smaller differences (weight: -1 for each unit of difference)
                        balance_var = self.model.NewIntVar(-20, 0, f'balance_{section.id}_{days_list[i]}_{days_list[j]}')
                        self.model.Add(balance_var == -abs_diff)
                        soft_constraints.append(balance_var)
    
    def _add_time_preferences(self, soft_constraints: List):
        """Add preferences for certain time slots"""
        # Avoid first and last periods when possible (soft constraint)
        for offering in self.offerings:
            for time_slot in self.time_slots:
                if time_slot.period_number in [1, 8]:  # First and last periods
                    for room_id in self.variables[offering.id].get(time_slot.id, {}):
                        # Small penalty for using first/last slots
                        penalty_var = self.model.NewIntVar(-1, 0, f'penalty_{offering.id}_{time_slot.id}_{room_id}')
                        self.model.Add(penalty_var == -self.variables[offering.id][time_slot.id][room_id])
                        soft_constraints.append(penalty_var)
    
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
