# 🎓 Generic College Timetable Generator

A flexible, AI-powered timetable generation system that can be used by any educational institution. This system is completely independent of specific institutional data and can be customized for any college or university.

## 🚀 **Key Features**

### **🎯 Universal Design**
- **No Institutional Dependencies**: Works with any college/university structure
- **Flexible Data Models**: Adapts to different naming conventions
- **Customizable Constraints**: Set your own institutional rules
- **Generic Sample Data**: Ready-to-use example data

### **🤖 AI-Powered Generation**
- **OR-Tools Solver**: Advanced constraint satisfaction
- **Conflict-Free Scheduling**: Automatic conflict detection and resolution
- **Optimization**: Finds the best possible timetable
- **Flexible Constraints**: Hard and soft constraint support

### **📊 Data Management**
- **Teacher Management**: Add, edit, and manage faculty
- **Course Management**: Handle any course structure
- **Room Management**: Support any room types and capacities
- **Section Management**: Flexible section naming
- **Time Slot Management**: Customizable daily schedules

### **🔧 Advanced Features**
- **Constraint Management**: Set institutional and personal constraints
- **File Upload**: Import data from PDF, Excel, or CSV files
- **Interactive Editor**: Drag-and-drop timetable editing
- **Export Options**: PDF, CSV, and Excel exports
- **Conflict Detection**: Real-time conflict checking

## 🛠️ **Installation & Setup**

### **1. Prerequisites**
```bash
# Python 3.8+ required
python --version

# Install dependencies
pip install flask sqlalchemy ortools pandas PyPDF2 werkzeug
```

### **2. Quick Start**
```bash
# Clone or download the project
cd TimeTableAI

# Run the application
python app.py

# Access the application
# Open browser to: http://localhost:5000
```

### **3. Database Setup**
```bash
# The system will automatically create the database
# Sample data is included for immediate testing
```

## 📋 **How to Use**

### **Step 1: Explore Sample Data**
The system comes with generic sample data:
- **Teachers**: 19 faculty members across different departments
- **Courses**: 20 courses in Computer Science, Business, and Engineering
- **Sections**: 18 sections across 3 programs and 3 semesters
- **Rooms**: 15 rooms (classrooms, labs, auditorium)
- **Time Slots**: 48 time slots (Monday-Saturday, 8 periods)

### **Step 2: Generate Your First Timetable**
1. Go to "Generate" in the navigation
2. Click "Generate Timetable"
3. View the generated timetable
4. Check for any conflicts or issues

### **Step 3: Customize for Your Institution**

#### **A. Replace Sample Data**
```python
# Edit seed_generic.py to add your data
# Or use the web interface to add data manually
```

#### **B. Set Your Constraints**
1. Go to "Constraints" in the navigation
2. Add teacher unavailability
3. Set room restrictions
4. Define section preferences
5. Configure time preferences

#### **C. Upload Your Data**
1. Go to "Workload" in the navigation
2. Upload your institutional data files
3. Process and import the data
4. Review the extracted information

### **Step 4: Generate and Edit**
1. Generate timetables with your data
2. Use the interactive editor to make adjustments
3. Check for conflicts
4. Export final timetables

## 🎨 **Customization Guide**

### **Program Structure**
The system supports any program structure:
```python
# Examples of supported formats:
- CS (Computer Science)
- BUS (Business)
- ENG (Engineering)
- MATH (Mathematics)
- Any 2-4 letter program code
```

### **Course Codes**
Flexible course code patterns:
```python
# Supported formats:
- CS-22-301 (Program-Year-Course)
- CS301 (ProgramCourse)
- CS-301 (Program-Course)
- CS 301 (Program Course)
```

### **Section Names**
Any section naming convention:
```python
# Examples:
- CS-I-A (Program-Semester-Section)
- CS1A (ProgramSemesterSection)
- Computer Science 1A
- Any descriptive name
```

### **Room Types**
Support for any room classification:
```python
# Built-in types:
- classroom
- lab
- auditorium
- seminar
- workshop
- Any custom type
```

## 📊 **Data Models**

### **Teacher Model**
```python
class Teacher:
    name: str              # Full name
    code: str              # Short code (e.g., SJ, MC)
    designation: str       # Professor, AP, etc.
    max_weekly_load: int   # Maximum teaching hours
    is_active: bool        # Active status
```

### **Course Model**
```python
class Course:
    code: str              # Course code
    name: str              # Course name
    credit_hours: int      # Credit hours
    sessions_per_week: int # Required sessions
    is_lab: bool          # Lab course flag
    program: str          # Program (CS, BUS, etc.)
    semester: str         # Semester (I, III, V)
```

### **Section Model**
```python
class Section:
    name: str              # Section name
    program: str          # Program
    semester: str         # Semester
    section_letter: str   # Section letter (A, B, C)
    student_count: int    # Number of students
```

### **Room Model**
```python
class Room:
    number: str           # Room number
    name: str             # Room name
    room_type: str        # Type (classroom, lab, etc.)
    capacity: int         # Student capacity
```

## 🔧 **Advanced Configuration**

### **Time Slot Configuration**
```python
# Default schedule (can be customized):
Period 1: 09:00-09:50
Period 2: 09:50-10:40
Period 3: 10:40-11:30
Break: 11:30-11:45
Period 4: 11:45-12:35
Period 5: 12:35-13:25
Lunch: 13:25-14:10
Period 6: 14:10-15:00
Period 7: 15:00-15:50
Period 8: 15:50-16:40
```

### **Constraint Types**
```python
# Available constraint types:
1. teacher_unavailable - Teacher can't teach at specific time
2. room_unavailable - Room not available at specific time
3. section_preference - Section preference for time slots
4. time_preference - General time-based preferences
```

### **Solver Configuration**
```python
# Solver settings (in simple_solver.py):
- Maximum offerings: 20 (can be increased)
- Session limits: 1-3 per course (customizable)
- Time limit: No limit (can be set)
- Optimization: Balance workload distribution
```

## 📁 **File Structure**

```
TimeTableAI/
├── app.py                 # Main Flask application
├── models.py              # Database models
├── routes.py              # Route handlers
├── simple_solver.py       # Constraint solver
├── workload_processor.py  # File processing
├── seed_generic.py        # Generic sample data
├── templates/             # HTML templates
├── static/                # CSS, JS, images
├── uploads/               # File upload directory
└── instance/              # Database files
```

## 🎯 **Use Cases**

### **For Different Institution Types**

#### **Universities**
- Multiple programs and departments
- Complex course structures
- Large faculty and student bodies
- Research and teaching balance

#### **Colleges**
- Focused program offerings
- Smaller class sizes
- Flexible scheduling needs
- Practical course emphasis

#### **Schools**
- Class-based scheduling
- Teacher availability focus
- Simple room requirements
- Regular schedule patterns

#### **Training Centers**
- Course-based scheduling
- Flexible time slots
- Resource allocation
- Short-term programs

## 🔒 **Security & Best Practices**

### **Data Security**
- Input validation on all forms
- Secure file upload handling
- SQL injection prevention
- XSS protection

### **Performance**
- Database indexing
- Efficient queries
- Background processing
- Caching strategies

### **Backup & Recovery**
- Regular database backups
- Export functionality
- Version control
- Error logging

## 🚀 **Deployment Options**

### **Local Development**
```bash
python app.py
# Access: http://localhost:5000
```

### **Production Deployment**
```bash
# Using Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Using Docker
docker build -t timetable-generator .
docker run -p 5000:5000 timetable-generator
```

### **Cloud Deployment**
- **Heroku**: Easy deployment with Procfile
- **AWS**: EC2 or Elastic Beanstalk
- **Google Cloud**: App Engine or Compute Engine
- **Azure**: App Service or Virtual Machines

## 📈 **Scaling Considerations**

### **Database Scaling**
- SQLite for development
- PostgreSQL for production
- MySQL for enterprise
- Cloud databases (AWS RDS, etc.)

### **Application Scaling**
- Load balancing
- Multiple instances
- Caching layers
- CDN for static files

### **Performance Optimization**
- Database query optimization
- Background job processing
- File upload optimization
- Memory management

## 🐛 **Troubleshooting**

### **Common Issues**

#### **Timetable Generation Fails**
```bash
# Check constraints
- Too many constraints may make it infeasible
- Reduce constraint complexity
- Increase solver time limit

# Check data
- Ensure all required data is present
- Verify relationships between entities
- Check for data inconsistencies
```

#### **File Upload Issues**
```bash
# Check file format
- Supported: PDF, Excel (.xlsx, .xls), CSV
- File size limits
- Upload directory permissions

# Check processing
- Review error logs
- Verify file content
- Check database connections
```

#### **Database Issues**
```bash
# Check database
- Verify database file exists
- Check file permissions
- Review SQLite version

# Check models
- Verify model relationships
- Check foreign key constraints
- Review data types
```

### **Performance Issues**
```bash
# Database optimization
- Add indexes to frequently queried columns
- Optimize complex queries
- Regular database maintenance

# Application optimization
- Enable caching
- Optimize file processing
- Background job processing
```

## 🔮 **Future Enhancements**

### **Planned Features**
- **Machine Learning**: Predictive scheduling
- **Mobile App**: Native mobile application
- **API Integration**: RESTful API
- **Advanced Analytics**: Scheduling insights
- **Multi-language**: Internationalization
- **Real-time Collaboration**: Live editing

### **Technical Improvements**
- **Performance**: Faster generation
- **Scalability**: Handle larger datasets
- **User Experience**: Enhanced interfaces
- **Integration**: Third-party systems
- **Automation**: Advanced workflows

## 📞 **Support & Documentation**

### **Getting Help**
- Review this README
- Check the code comments
- Examine the sample data
- Test with different scenarios

### **Customization Support**
- Modify seed_generic.py for your data
- Adjust constraint types as needed
- Customize time slots for your schedule
- Adapt room types for your facilities

### **Community**
- Share your customizations
- Report issues and bugs
- Suggest new features
- Contribute improvements

---

**🎉 Ready to Use**: This system is designed to work out-of-the-box with any educational institution. Simply run the application and start generating timetables!

**📝 License**: MIT License - Free to use and modify

**🔄 Version**: 2.0 Generic - Independent of institutional constraints 