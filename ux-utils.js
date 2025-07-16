// UX-утилиты для Aaadviser WebApp

// Toast notification system
function showToast(message, type = 'success', duration = 3000) {
    const container = document.getElementById('toastContainer') || createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        if (toast.parentElement) {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }
    }, duration);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container';
    container.id = 'toastContainer';
    document.body.appendChild(container);
    return container;
}

// Snackbar for undo functionality
let lastDeletedItem = null;
let undoTimeout = null;

function showSnackbar(message, undoCallback) {
    const snackbar = document.getElementById('snackbar') || createSnackbar();
    const messageEl = document.getElementById('snackbarMessage');
    const undoBtn = document.getElementById('snackbarUndo');
    
    messageEl.textContent = message;
    snackbar.style.display = 'flex';
    
    // Clear previous timeout
    if (undoTimeout) {
        clearTimeout(undoTimeout);
    }
    
    // Set new timeout
    undoTimeout = setTimeout(() => {
        snackbar.style.display = 'none';
        lastDeletedItem = null;
    }, 5000);
    
    // Set undo callback
    undoBtn.onclick = () => {
        if (undoCallback) {
            undoCallback();
        }
        snackbar.style.display = 'none';
        if (undoTimeout) {
            clearTimeout(undoTimeout);
        }
    };
}

function createSnackbar() {
    const snackbar = document.createElement('div');
    snackbar.id = 'snackbar';
    snackbar.className = 'snackbar';
    snackbar.style.display = 'none';
    snackbar.innerHTML = `
        <span id="snackbarMessage"></span>
        <button class="snackbar-undo" id="snackbarUndo">Отменить</button>
    `;
    document.body.appendChild(snackbar);
    return snackbar;
}

// Skeleton loading
function showSkeleton(containerId, skeletonClass = 'skeleton-card', count = 3) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = '';
    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = `skeleton ${skeletonClass}`;
        container.appendChild(skeleton);
    }
    container.style.display = '';
}

function hideSkeleton(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
    }
}

// Empty state
function showEmptyState(containerId, icon, title, description, actionText, actionCallback) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">${icon}</div>
            <div class="empty-state-title">${title}</div>
            <div class="empty-state-description">${description}</div>
            ${actionText ? `<button class="btn" onclick="${actionCallback}">${actionText}</button>` : ''}
        </div>
    `;
    container.style.display = '';
}

// Loading states
function showLoading(containerId, text = 'Загрузка...') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>${text}</p>
        </div>
    `;
    container.style.display = '';
}

function hideLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
        container.style.display = 'none';
    }
}

// Modal utilities
function showModal(title, content, buttons = []) {
    let oldModal = document.getElementById('modal');
    if (oldModal) oldModal.remove();
    
    const modal = document.createElement('div');
    modal.id = 'modal';
    modal.className = 'modal';
    
    const buttonHtml = buttons.map(btn => 
        `<button class="btn ${btn.class || ''}" onclick="${btn.onclick}">${btn.text}</button>`
    ).join('');
    
    modal.innerHTML = `
        <div class="modal-content">
            <div class="title">${title}</div>
            <div class="content">${content}</div>
            <div class="buttons">
                ${buttonHtml}
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.getElementById('modal');
    if (modal) modal.remove();
}

// Confirmation dialog
function confirmAction(message, onConfirm, onCancel) {
    showModal(
        'Подтверждение',
        message,
        [
            {
                text: 'Отмена',
                class: 'btn-secondary',
                onclick: 'closeModal(); if (typeof onCancel === "function") onCancel();'
            },
            {
                text: 'Подтвердить',
                onclick: 'closeModal(); if (typeof onConfirm === "function") onConfirm();'
            }
        ]
    );
}

// Form utilities
function validateForm(formData) {
    const errors = [];
    
    for (const [key, value] of formData.entries()) {
        if (!value || value.trim() === '') {
            errors.push(`Поле ${key} обязательно для заполнения`);
        }
    }
    
    return errors;
}

function showFormErrors(errors) {
    if (errors.length > 0) {
        showToast(errors.join('\n'), 'error');
        return false;
    }
    return true;
}

// Animation utilities
function animateElement(element, animation, duration = 300) {
    element.style.animation = `${animation} ${duration}ms ease`;
    setTimeout(() => {
        element.style.animation = '';
    }, duration);
}

function fadeIn(element) {
    element.style.opacity = '0';
    element.style.transform = 'translateY(10px)';
    element.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0)';
    }, 50);
}

function fadeOut(element, callback) {
    element.style.opacity = '1';
    element.style.transform = 'translateY(0)';
    element.style.transition = 'all 0.3s ease';
    
    setTimeout(() => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(10px)';
        
        setTimeout(() => {
            if (callback) callback();
        }, 300);
    }, 50);
}

// Localization utilities
const locales = {
    'ru': {
        'loading': 'Загрузка...',
        'error': 'Ошибка',
        'success': 'Успешно',
        'warning': 'Предупреждение',
        'info': 'Информация',
        'confirm': 'Подтвердить',
        'cancel': 'Отмена',
        'close': 'Закрыть',
        'save': 'Сохранить',
        'delete': 'Удалить',
        'edit': 'Редактировать',
        'back': 'Назад',
        'next': 'Далее',
        'submit': 'Отправить',
        'required_field': 'Обязательное поле',
        'network_error': 'Ошибка сети. Проверьте соединение.',
        'server_error': 'Ошибка сервера. Попробуйте позже.',
        'validation_error': 'Ошибка валидации данных.',
        'success_saved': 'Данные успешно сохранены',
        'success_deleted': 'Элемент успешно удален',
        'success_updated': 'Данные успешно обновлены'
    },
    'en': {
        'loading': 'Loading...',
        'error': 'Error',
        'success': 'Success',
        'warning': 'Warning',
        'info': 'Information',
        'confirm': 'Confirm',
        'cancel': 'Cancel',
        'close': 'Close',
        'save': 'Save',
        'delete': 'Delete',
        'edit': 'Edit',
        'back': 'Back',
        'next': 'Next',
        'submit': 'Submit',
        'required_field': 'Required field',
        'network_error': 'Network error. Check your connection.',
        'server_error': 'Server error. Try again later.',
        'validation_error': 'Data validation error.',
        'success_saved': 'Data saved successfully',
        'success_deleted': 'Item deleted successfully',
        'success_updated': 'Data updated successfully'
    }
};

let currentLanguage = 'ru';

function setLanguage(lang) {
    currentLanguage = lang;
    updatePageText();
}

function getText(key) {
    const locale = locales[currentLanguage] || locales['ru'];
    return locale[key] || key;
}

function updatePageText() {
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        element.textContent = getText(key);
    });
}

// API utilities
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API Error');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message || getText('network_error'), 'error');
        throw error;
    }
}

// Debounce utility
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Throttle utility
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Storage utilities
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Storage set error:', error);
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (error) {
            console.error('Storage get error:', error);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (error) {
            console.error('Storage remove error:', error);
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
        } catch (error) {
            console.error('Storage clear error:', error);
        }
    }
};

// Device utilities
const device = {
    isMobile: () => window.innerWidth <= 768,
    isTablet: () => window.innerWidth > 768 && window.innerWidth <= 1024,
    isDesktop: () => window.innerWidth > 1024,
    isTouch: () => 'ontouchstart' in window || navigator.maxTouchPoints > 0
};

// Performance utilities
function measurePerformance(name, fn) {
    const start = performance.now();
    const result = fn();
    const end = performance.now();
    console.log(`${name} took ${end - start} milliseconds`);
    return result;
}

// Error handling
function handleError(error, context = '') {
    console.error(`Error in ${context}:`, error);
    
    let message = getText('server_error');
    
    if (error.name === 'NetworkError') {
        message = getText('network_error');
    } else if (error.message) {
        message = error.message;
    }
    
    showToast(message, 'error');
}

// Initialize UX utilities
function initUX() {
    // Create toast container if it doesn't exist
    if (!document.getElementById('toastContainer')) {
        createToastContainer();
    }
    
    // Create snackbar if it doesn't exist
    if (!document.getElementById('snackbar')) {
        createSnackbar();
    }
    
    // Add global error handler
    window.addEventListener('error', (event) => {
        handleError(event.error, 'Global');
    });
    
    // Add unhandled promise rejection handler
    window.addEventListener('unhandledrejection', (event) => {
        handleError(event.reason, 'Promise');
    });
}

// Export utilities for use in other files
window.UXUtils = {
    showToast,
    showSnackbar,
    showSkeleton,
    hideSkeleton,
    showEmptyState,
    showLoading,
    hideLoading,
    showModal,
    closeModal,
    confirmAction,
    validateForm,
    showFormErrors,
    animateElement,
    fadeIn,
    fadeOut,
    setLanguage,
    getText,
    updatePageText,
    apiRequest,
    debounce,
    throttle,
    storage,
    device,
    measurePerformance,
    handleError,
    initUX
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUX);
} else {
    initUX();
} 