/**
 * Timetable JavaScript functionality
 * Handles drag-and-drop, AJAX operations, and UI interactions
 */

// Global variables
let draggedSlot = null;
let originalCell = null;

/**
 * Initialize drag and drop functionality for timetable
 */
function initializeTimetableDragDrop() {
    const timetableSlots = document.querySelectorAll('.timetable-slot');
    const timetableCells = document.querySelectorAll('.timetable-cell');
    
    // Make slots draggable
    timetableSlots.forEach(slot => {
        slot.addEventListener('dragstart', handleDragStart);
        slot.addEventListener('dragend', handleDragEnd);
    });
    
    // Make cells drop targets
    timetableCells.forEach(cell => {
        cell.addEventListener('dragover', handleDragOver);
        cell.addEventListener('dragenter', handleDragEnter);
        cell.addEventListener('dragleave', handleDragLeave);
        cell.addEventListener('drop', handleDrop);
    });
}

/**
 * Handle drag start event
 */
function handleDragStart(e) {
    draggedSlot = this;
    originalCell = this.parentElement;
    this.classList.add('dragging');
    
    // Store data for the drag operation
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.outerHTML);
}

/**
 * Handle drag end event
 */
function handleDragEnd(e) {
    this.classList.remove('dragging');
    
    // Clean up drag states
    const cells = document.querySelectorAll('.timetable-cell');
    cells.forEach(cell => {
        cell.classList.remove('drag-over', 'drag-invalid');
    });
}

/**
 * Handle drag over event
 */
function handleDragOver(e) {
    if (e.preventDefault) {
        e.preventDefault();
    }
    
    e.dataTransfer.dropEffect = 'move';
    return false;
}

/**
 * Handle drag enter event
 */
function handleDragEnter(e) {
    if (this === originalCell) {
        return;
    }
    
    // Check if drop is valid
    if (isValidDrop(this)) {
        this.classList.add('drag-over');
    } else {
        this.classList.add('drag-invalid');
    }
}

/**
 * Handle drag leave event
 */
function handleDragLeave(e) {
    this.classList.remove('drag-over', 'drag-invalid');
}

/**
 * Handle drop event
 */
function handleDrop(e) {
    if (e.stopPropagation) {
        e.stopPropagation();
    }
    
    const targetCell = this;
    
    if (!isValidDrop(targetCell) || targetCell === originalCell) {
        return false;
    }
    
    // Check if target cell already has a slot
    const existingSlot = targetCell.querySelector('.timetable-slot');
    if (existingSlot) {
        showNotification('Target slot is already occupied', 'error');
        return false;
    }
    
    // Perform the move
    const slotId = draggedSlot.getAttribute('data-slot-id');
    const newTimeSlotId = targetCell.getAttribute('data-timeslot-id');
    const newRoomId = getAvailableRoomForSlot(targetCell, draggedSlot);
    
    if (!newTimeSlotId) {
        showNotification('Invalid target time slot', 'error');
        return false;
    }
    
    // Send AJAX request to update the timetable
    updateTimetableSlot(slotId, newTimeSlotId, newRoomId, targetCell);
    
    return false;
}

/**
 * Check if a drop operation is valid
 */
function isValidDrop(targetCell) {
    if (!targetCell.classList.contains('timetable-cell')) {
        return false;
    }
    
    // Check if target cell is empty
    const existingSlot = targetCell.querySelector('.timetable-slot');
    if (existingSlot && existingSlot !== draggedSlot) {
        return false;
    }
    
    // Additional validation can be added here
    return true;
}

/**
 * Get available room for a time slot
 */
function getAvailableRoomForSlot(targetCell, slot) {
    // For now, use the same room as the original slot
    // In a more advanced implementation, this could check room availability
    return slot.getAttribute('data-room-id');
}

/**
 * Update timetable slot via AJAX
 */
function updateTimetableSlot(slotId, newTimeSlotId, newRoomId, targetCell) {
    const data = {
        slot_id: parseInt(slotId),
        new_time_slot_id: parseInt(newTimeSlotId),
        new_room_id: newRoomId ? parseInt(newRoomId) : null
    };
    
    fetch('/timetable/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Move the slot element to the new cell
            targetCell.appendChild(draggedSlot);
            
            // Update the cell's data attributes
            updateSlotDisplay(draggedSlot, targetCell);
            
            showNotification('Timetable updated successfully', 'success');
        } else {
            showNotification(`Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to update timetable', 'error');
    });
}

/**
 * Update slot display after successful move
 */
function updateSlotDisplay(slot, newCell) {
    // Update any necessary display attributes
    const day = newCell.getAttribute('data-day');
    const period = newCell.getAttribute('data-period');
    
    // Add any visual feedback for the successful move
    slot.style.animation = 'fadeIn 0.3s ease-out';
    
    // Re-initialize feather icons if needed
    feather.replace();
}

/**
 * Show notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
    `;
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 5000);
}

/**
 * Initialize tooltips
 */
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

/**
 * Handle offering management AJAX
 */
function loadOfferings() {
    fetch('/api/offerings')
        .then(response => response.json())
        .then(data => {
            updateOfferingsTable(data);
        })
        .catch(error => {
            console.error('Error loading offerings:', error);
        });
}

/**
 * Update offerings table
 */
function updateOfferingsTable(offerings) {
    // Implementation depends on if there's an offerings table on the page
    const tableBody = document.querySelector('#offeringsTableBody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    offerings.forEach(offering => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${offering.teacher}</td>
            <td>${offering.course}</td>
            <td>${offering.section}</td>
            <td><span class="badge bg-info">${offering.sessions_per_week}</span></td>
            <td>
                <button class="btn btn-sm btn-outline-danger" onclick="deleteOffering(${offering.id})">
                    <i data-feather="trash-2"></i>
                </button>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    // Re-initialize feather icons
    feather.replace();
}

/**
 * Delete offering
 */
function deleteOffering(offeringId) {
    if (!confirm('Are you sure you want to delete this offering?')) {
        return;
    }
    
    fetch(`/api/offerings/${offeringId}/delete`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Offering deleted successfully', 'success');
            loadOfferings(); // Reload the table
        } else {
            showNotification(`Error: ${data.error}`, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Failed to delete offering', 'error');
    });
}

/**
 * Handle form submissions with loading states
 */
function handleFormSubmission(formId, loadingText = 'Processing...') {
    const form = document.getElementById(formId);
    if (!form) return;
    
    form.addEventListener('submit', function(e) {
        const submitBtn = this.querySelector('button[type="submit"]');
        if (submitBtn) {
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = `<i data-feather="loader" class="me-2 spinner"></i>${loadingText}`;
            submitBtn.disabled = true;
            
            // Add spinner CSS if not exists
            if (!document.getElementById('spinner-style')) {
                const style = document.createElement('style');
                style.id = 'spinner-style';
                style.textContent = `
                    .spinner {
                        animation: spin 1s linear infinite;
                    }
                    @keyframes spin {
                        from { transform: rotate(0deg); }
                        to { transform: rotate(360deg); }
                    }
                `;
                document.head.appendChild(style);
            }
            
            feather.replace();
        }
    });
}

/**
 * Initialize search functionality
 */
function initializeSearch(inputId, tableId) {
    const searchInput = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!searchInput || !table) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) { // Skip header row
            const row = rows[i];
            const text = row.textContent.toLowerCase();
            
            if (text.includes(searchTerm)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }
    });
}

/**
 * Initialize all functionality when DOM is loaded
 */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize drag and drop if on timetable page
    if (document.querySelector('.timetable-grid')) {
        initializeTimetableDragDrop();
    }
    
    // Initialize form loading states
    handleFormSubmission('generateForm', 'Generating...');
    handleFormSubmission('addTeacherForm', 'Adding...');
    handleFormSubmission('addCourseForm', 'Adding...');
    handleFormSubmission('addRoomForm', 'Adding...');
    handleFormSubmission('addSectionForm', 'Adding...');
    
    // Initialize search functionality
    initializeSearch('teacherSearch', 'teachersTable');
    initializeSearch('courseSearch', 'coursesTable');
    initializeSearch('roomSearch', 'roomsTable');
    initializeSearch('sectionSearch', 'sectionsTable');
});

/**
 * Utility function to format time
 */
function formatTime(timeString) {
    const time = new Date(`2000-01-01T${timeString}`);
    return time.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
    });
}

/**
 * Utility function to get day name
 */
function getDayName(dayIndex) {
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    return days[dayIndex] || 'Unknown';
}

/**
 * Export functions for global access
 */
window.TimetableJS = {
    initializeTimetableDragDrop,
    showNotification,
    loadOfferings,
    deleteOffering,
    formatTime,
    getDayName
};
