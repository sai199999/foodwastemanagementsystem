document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    const popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Form validation - add Bootstrap validation classes
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Add animation to status cards
    const statCards = document.querySelectorAll('.stats-card');
    if (statCards.length > 0) {
        statCards.forEach(card => {
            animateCounter(card.querySelector('.stats-value'));
        });
    }

    // Show loading spinner when submitting forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(button => {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                showSpinner();
            }
        });
    });

    // Format all datetime fields on the page
    const datetimeElements = document.querySelectorAll('.format-datetime');
    if (datetimeElements.length > 0) {
        datetimeElements.forEach(element => {
            const timestamp = element.textContent;
            element.textContent = formatDateTime(timestamp);
        });
    }

    // Initialize notifications system
    initializeNotifications();
});

// Animate counter for dashboard statistics
function animateCounter(element) {
    if (!element) return;
    
    const target = parseInt(element.textContent);
    const duration = 1500;
    const step = Math.max(1, Math.floor(target / (duration / 30)));
    let current = 0;
    
    const timer = setInterval(function() {
        current += step;
        if (current >= target) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = current;
        }
    }, 30);
}

// Format date and time
function formatDateTime(timestamp) {
    if (!timestamp) return '';
    
    const date = new Date(timestamp);
    
    if (isNaN(date.getTime())) {
        return timestamp; // Return original if invalid
    }
    
    // Format: July 10, 2023 at 14:30
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    
    return date.toLocaleDateString('en-US', options).replace(' at', ',');
}

// Show spinner overlay
function showSpinner() {
    const spinner = document.createElement('div');
    spinner.className = 'spinner-overlay';
    spinner.innerHTML = `
        <div class="spinner-border text-light" role="status">
            <span class="visually-hidden">Loading...</span>
        </div>
    `;
    document.body.appendChild(spinner);
    
    // Remove spinner if page load takes too long
    setTimeout(() => {
        if (document.querySelector('.spinner-overlay')) {
            document.querySelector('.spinner-overlay').remove();
        }
    }, 8000);
}

// Hide spinner overlay
function hideSpinner() {
    const spinner = document.querySelector('.spinner-overlay');
    if (spinner) {
        spinner.remove();
    }
}

// Toggle password visibility
function togglePassword(inputId, iconId) {
    const passwordInput = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    
    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        icon.className = 'bi bi-eye-slash';
    } else {
        passwordInput.type = 'password';
        icon.className = 'bi bi-eye';
    }
}
