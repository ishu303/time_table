# Overview

This is an AI-powered college timetable generator built with Flask that uses Google's OR-Tools CP-SAT constraint solver to automatically generate clash-free academic schedules. The system manages complex institutional data including teachers, courses, sections, rooms, and time slots, then applies sophisticated constraint solving to create optimized timetables. It features a web-based interface for data management, interactive timetable visualization with drag-and-drop editing, and export capabilities to PDF and CSV formats.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Backend Architecture
- **Framework**: Flask with SQLAlchemy ORM for database operations
- **Database**: SQLite for development with configurable PostgreSQL support via environment variables
- **Constraint Solver**: Google OR-Tools CP-SAT solver for automated timetable generation
- **Session Management**: Flask sessions with configurable secret keys
- **Model Layer**: SQLAlchemy models with relationships for Teachers, Courses, Sections, Rooms, TimeSlots, Offerings, and TimetableSlots

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap for responsive UI
- **Styling**: Bootstrap with dark theme and custom CSS for timetable grids
- **Interactivity**: Vanilla JavaScript with drag-and-drop functionality for manual timetable editing
- **Icons**: Feather icons for consistent visual elements
- **Layout**: Base template with navigation and modular content blocks

## Data Model Design
The system uses a relational model with core entities:
- **Teacher**: Faculty members with designations, codes, and maximum weekly loads
- **Course**: Academic subjects with codes, names, and credit hours  
- **Section**: Student groups organized by program and semester
- **Room**: Physical spaces with types (classroom, lab) and capacities
- **TimeSlot**: Scheduled periods with day, time, and break information
- **Offering**: Course assignments linking teachers, sections, and requirements
- **TimetableSlot**: Generated schedule entries with conflict resolution

## Constraint Solving Engine
- **Hard Constraints**: No teacher/room/section conflicts, availability respect, lab duration requirements
- **Soft Constraints**: Even distribution preferences, avoiding first/last slots
- **Optimization**: CP-SAT model with decision variables for each possible assignment
- **Solution Processing**: Converts solver output to database records with conflict validation

## Export and Reporting
- **PDF Generation**: ReportLab integration for formatted timetable documents
- **CSV Export**: Structured data export for external processing
- **Filtering**: Section, teacher, and room-specific views
- **Real-time Updates**: AJAX-based interactions for dynamic content

# External Dependencies

## Core Framework Dependencies
- **Flask**: Web application framework
- **SQLAlchemy**: Database ORM and query builder
- **Werkzeug**: WSGI utilities and middleware for proxy handling

## Constraint Solving
- **OR-Tools**: Google's optimization and constraint programming library for CP-SAT solver

## Document Generation
- **ReportLab**: PDF generation library for timetable exports with table formatting and styling

## Frontend Libraries
- **Bootstrap**: CSS framework via CDN for responsive design and dark theme
- **Feather Icons**: Icon library via CDN for consistent UI elements
- **Dragula**: Drag-and-drop library via CDN for manual timetable editing

## Development Tools
- **Python Logging**: Built-in logging for debugging and monitoring
- **CSV Module**: Standard library for data export functionality
- **DateTime**: Standard library for time-based operations and scheduling

## Infrastructure
- **SQLite**: Default development database with PostgreSQL migration path
- **Environment Variables**: Configuration for database URLs and session secrets
- **WSGI ProxyFix**: Middleware for proper header handling in deployment environments