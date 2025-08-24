#!/usr/bin/env python3
"""
Workload file processor for handling different file formats
"""

import os
import pandas as pd
import PyPDF2
import logging
from typing import Dict, List, Optional
from app import app, db
from models import Teacher, Course, Section, Room, Offering, WorkloadFile

logger = logging.getLogger(__name__)

class WorkloadProcessor:
    """Process uploaded workload files"""
    
    def __init__(self, file_id: int):
        self.file_id = file_id
        self.file = WorkloadFile.query.get(file_id)
        self.file_path = self.file.file_path
        self.file_type = self.file.original_filename.split('.')[-1].lower()
        
    def process(self) -> Dict:
        """Process the workload file"""
        try:
            # Update status to processing
            self.file.processing_status = 'processing'
            db.session.commit()
            
            # Process based on file type
            if self.file_type == 'pdf':
                result = self._process_pdf()
            elif self.file_type in ['xlsx', 'xls']:
                result = self._process_excel()
            elif self.file_type == 'csv':
                result = self._process_csv()
            else:
                raise ValueError(f"Unsupported file type: {self.file_type}")
            
            # Update file status
            self.file.processing_status = 'completed'
            self.file.processing_notes = result.get('notes', 'Processing completed successfully')
            db.session.commit()
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing file {self.file_id}: {str(e)}")
            self.file.processing_status = 'failed'
            self.file.processing_notes = f"Processing failed: {str(e)}"
            db.session.commit()
            return {'success': False, 'error': str(e)}
    
    def _process_pdf(self) -> Dict:
        """Process PDF files"""
        try:
            with open(self.file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = ""
                
                for page in pdf_reader.pages:
                    text_content += page.extract_text()
                
                # Extract data from text content
                extracted_data = self._extract_data_from_text(text_content)
                
                return {
                    'success': True,
                    'data': extracted_data,
                    'notes': f'Processed {len(pdf_reader.pages)} pages from PDF'
                }
                
        except Exception as e:
            return {'success': False, 'error': f'PDF processing error: {str(e)}'}
    
    def _process_excel(self) -> Dict:
        """Process Excel files"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(self.file_path)
            extracted_data = {}
            
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(self.file_path, sheet_name=sheet_name)
                extracted_data[sheet_name] = self._extract_data_from_dataframe(df)
            
            return {
                'success': True,
                'data': extracted_data,
                'notes': f'Processed {len(excel_file.sheet_names)} sheets from Excel file'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Excel processing error: {str(e)}'}
    
    def _process_csv(self) -> Dict:
        """Process CSV files"""
        try:
            df = pd.read_csv(self.file_path)
            extracted_data = self._extract_data_from_dataframe(df)
            
            return {
                'success': True,
                'data': extracted_data,
                'notes': f'Processed CSV file with {len(df)} rows'
            }
            
        except Exception as e:
            return {'success': False, 'error': f'CSV processing error: {str(e)}'}
    
    def _extract_data_from_text(self, text: str) -> Dict:
        """Extract structured data from text content"""
        data = {
            'teachers': [],
            'courses': [],
            'sections': [],
            'offerings': []
        }
        
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Look for teacher patterns
            if any(title in line.lower() for title in ['dr.', 'professor', 'assistant professor', 'ap']):
                teacher_data = self._extract_teacher_from_text(line)
                if teacher_data:
                    data['teachers'].append(teacher_data)
            
            # Look for course patterns
            if any(code in line.upper() for code in ['BCOM', 'BCA', 'MCA', 'MBA']):
                course_data = self._extract_course_from_text(line)
                if course_data:
                    data['courses'].append(course_data)
        
        return data
    
    def _extract_data_from_dataframe(self, df: pd.DataFrame) -> Dict:
        """Extract structured data from DataFrame"""
        data = {
            'teachers': [],
            'courses': [],
            'sections': [],
            'offerings': []
        }
        
        # Look for teacher columns
        teacher_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['teacher', 'faculty', 'instructor', 'name'])]
        if teacher_columns:
            for _, row in df.iterrows():
                teacher_name = row[teacher_columns[0]]
                if pd.notna(teacher_name) and str(teacher_name).strip():
                    data['teachers'].append({
                        'name': str(teacher_name).strip(),
                        'code': self._generate_teacher_code(str(teacher_name)),
                        'designation': 'AP (Stage-I)'
                    })
        
        # Look for course columns
        course_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['course', 'subject', 'code'])]
        if course_columns:
            for _, row in df.iterrows():
                course_code = row[course_columns[0]]
                if pd.notna(course_code) and str(course_code).strip():
                    data['courses'].append({
                        'code': str(course_code).strip(),
                        'name': self._extract_course_name(row),
                        'program': self._extract_program_from_code(str(course_code)),
                        'semester': self._extract_semester_from_code(str(course_code))
                    })
        
        return data
    
    def _extract_teacher_from_text(self, text: str) -> Optional[Dict]:
        """Extract teacher information from text line"""
        # Simple pattern matching for teacher names
        words = text.split()
        if len(words) >= 2:
            # Look for titles
            titles = ['Dr.', 'Professor', 'Prof.', 'Assistant', 'AP']
            name_start = 0
            for i, word in enumerate(words):
                if any(title in word for title in titles):
                    name_start = i + 1
                    break
            
            if name_start < len(words):
                name = ' '.join(words[name_start:name_start+3])  # Take up to 3 words for name
                return {
                    'name': name,
                    'code': self._generate_teacher_code(name),
                    'designation': 'AP (Stage-I)'
                }
        
        return None
    
    def _extract_course_from_text(self, text: str) -> Optional[Dict]:
        """Extract course information from text line"""
        # Look for course code patterns - more flexible
        import re
        
        # Multiple course code patterns
        course_patterns = [
            r'([A-Z]{2,4}-\d{2}-\d{3})',      # CS-22-301, BUS-22-301
            r'([A-Z]{2,4}\d{3})',             # CS301, BUS301
            r'([A-Z]{2,4}-\d{3})',            # CS-301, BUS-301
            r'([A-Z]{2,4}\s+\d{3})',          # CS 301, BUS 301
        ]
        
        for pattern in course_patterns:
            match = re.search(pattern, text)
            if match:
                code = match.group(1).replace(' ', '')  # Remove spaces
                return {
                    'code': code,
                    'name': self._extract_course_name_from_text(text),
                    'program': self._extract_program_from_code(code),
                    'semester': self._extract_semester_from_code(code)
                }
        
        return None
    
    def _extract_course_name(self, row: pd.Series) -> str:
        """Extract course name from DataFrame row"""
        name_columns = [col for col in row.index if any(keyword in col.lower() for keyword in ['name', 'title', 'subject'])]
        if name_columns:
            for col in name_columns:
                if pd.notna(row[col]) and str(row[col]).strip():
                    return str(row[col]).strip()
        return "Unknown Course"
    
    def _extract_course_name_from_text(self, text: str) -> str:
        """Extract course name from text"""
        # Simple extraction - take text after course code
        import re
        course_pattern = r'([A-Z]{3,4}-\d{2}-\d{3})'
        match = re.search(course_pattern, text)
        
        if match:
            code_end = match.end()
            name_part = text[code_end:].strip()
            # Clean up the name
            name_part = re.sub(r'[^\w\s-]', '', name_part)
            return name_part[:50] if name_part else "Unknown Course"
        
        return "Unknown Course"
    
    def _extract_program_from_code(self, code: str) -> str:
        """Extract program from course code"""
        # Generic program extraction - look for common patterns
        import re
        
        # Common program patterns
        program_patterns = {
            r'^CS': 'CS',      # Computer Science
            r'^BUS': 'BUS',    # Business
            r'^ENG': 'ENG',    # Engineering
            r'^MATH': 'MATH',  # Mathematics
            r'^PHY': 'PHY',    # Physics
            r'^CHEM': 'CHEM',  # Chemistry
            r'^BIO': 'BIO',    # Biology
            r'^ECON': 'ECON',  # Economics
            r'^PSY': 'PSY',    # Psychology
            r'^HIST': 'HIST',  # History
            r'^LIT': 'LIT',    # Literature
            r'^ART': 'ART',    # Arts
            r'^MUS': 'MUS',    # Music
            r'^PE': 'PE',      # Physical Education
        }
        
        for pattern, program in program_patterns.items():
            if re.match(pattern, code):
                return program
        
        # If no pattern matches, try to extract from the code
        if len(code) >= 2:
            return code[:3].upper()
        
        return 'GEN'  # Generic
    
    def _extract_semester_from_code(self, code: str) -> str:
        """Extract semester from course code"""
        import re
        semester_pattern = r'-(\d{2})-\d{3}'
        match = re.search(semester_pattern, code)
        
        if match:
            semester_num = int(match.group(1))
            if semester_num <= 2:
                return 'I'
            elif semester_num <= 4:
                return 'III'
            elif semester_num <= 6:
                return 'V'
            else:
                return 'VII'
        
        return 'I'
    
    def _generate_teacher_code(self, name: str) -> str:
        """Generate teacher code from name"""
        words = name.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        elif len(words) == 1:
            return words[0][:2].upper()
        else:
            return "UN"

def process_workload_file(file_id: int):
    """Process a workload file"""
    with app.app_context():
        processor = WorkloadProcessor(file_id)
        return processor.process() 