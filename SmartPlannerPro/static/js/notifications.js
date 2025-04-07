// Notifications system for real-time updates
let notificationsCount = 0;
let notificationsInterval;

function initializeNotifications() {
    // Check if user is logged in (notifications badge exists)
    const notificationsBadge = document.getElementById('notifications-badge');
    if (!notificationsBadge) return;

    // Initial load of notifications
    fetchNotifications();
    
    // Set interval to check for new notifications every 30 seconds
    notificationsInterval = setInterval(fetchNotifications, 30000);
    
    // Setup listener for notification dropdown to mark as read
    const notificationsDropdown = document.getElementById('notifications-dropdown');
    if (notificationsDropdown) {
        notificationsDropdown.addEventListener('click', handleNotificationClick);
    }
}

function fetchNotifications() {
    fetch('/notifications')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            updateNotificationsBadge(data.length);
            updateNotificationsDropdown(data);
        })
        .catch(error => {
            console.error('Error fetching notifications:', error);
        });
}

function updateNotificationsBadge(count) {
    const badge = document.getElementById('notifications-badge');
    if (!badge) return;
    
    notificationsCount = count;
    
    if (count > 0) {
        badge.textContent = count;
        badge.classList.remove('d-none');
    } else {
        badge.classList.add('d-none');
    }
}

function updateNotificationsDropdown(notifications) {
    const container = document.getElementById('notifications-list');
    if (!container) return;
    
    if (notifications.length === 0) {
        container.innerHTML = '<div class="dropdown-item text-center text-muted">No new notifications</div>';
        return;
    }
    
    // Clear current notifications
    container.innerHTML = '';
    
    // Add notifications
    notifications.forEach(notification => {
        const item = document.createElement('div');
        item.className = 'dropdown-item notification-item';
        item.dataset.id = notification.id;
        
        const time = new Date(notification.created_at).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        item.innerHTML = `
            <div class="d-flex justify-content-between align-items-center mb-1">
                <small class="text-muted">${time}</small>
                <button class="btn btn-sm btn-link p-0 mark-read" data-id="${notification.id}">
                    <i class="bi bi-check-circle"></i>
                </button>
            </div>
            <p class="mb-0">${notification.message}</p>
        `;
        
        container.appendChild(item);
    });
}

function handleNotificationClick(event) {
    // Check if clicked element is the "mark as read" button
    if (event.target.closest('.mark-read')) {
        const button = event.target.closest('.mark-read');
        const notificationId = button.dataset.id;
        
        if (notificationId) {
            markNotificationAsRead(notificationId);
            event.preventDefault();
            event.stopPropagation();
        }
    }
}

function markNotificationAsRead(notificationId) {
    fetch(`/notifications/mark_read/${notificationId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Remove the notification from the dropdown
            const notificationElement = document.querySelector(`.notification-item[data-id="${notificationId}"]`);
            if (notificationElement) {
                notificationElement.remove();
                
                // Update count
                updateNotificationsBadge(notificationsCount - 1);
                
                // If no more notifications, refresh the dropdown
                if (notificationsCount <= 0) {
                    updateNotificationsDropdown([]);
                }
            }
        }
    })
    .catch(error => {
        console.error('Error marking notification as read:', error);
    });
}

// Clean up when page is unloaded
window.addEventListener('beforeunload', function() {
    if (notificationsInterval) {
        clearInterval(notificationsInterval);
    }
});
