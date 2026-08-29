// ================================================================
//  ALERT SYSTEM – Toast notifications for any JS file
// ================================================================

(function() {
    'use strict';

    // ---------- CONFIG ----------
    const DEFAULT_DURATION = 3500;          // ms before auto-close
    const MAX_VISIBLE = 5;                 // max visible at once (older ones stack)

    // ---------- STYLES (injected only once) ----------
    const styles = `
        .alert-container {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 99999;
            display: flex;
            flex-direction: column;
            align-items: flex-end;
            gap: 12px;
            max-width: 420px;
            width: 100%;
            pointer-events: none;
        }
        .alert-toast {
            pointer-events: auto;
            background: var(--bg-card, #152615);
            color: var(--text-light, #eef6ee);
            border: 1px solid rgba(255,255,255,0.06);
            border-radius: 16px;
            padding: 1rem 1.2rem;
            box-shadow: 0 20px 60px rgba(0,0,0,0.6);
            display: flex;
            align-items: flex-start;
            gap: 0.8rem;
            width: 100%;
            box-sizing: border-box;
            transform: translateX(120%);
            opacity: 0;
            transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1),
                        opacity 0.3s ease;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            font-family: 'Space Grotesk', sans-serif;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        .alert-toast.show {
            transform: translateX(0);
            opacity: 1;
        }
        .alert-toast.hide {
            transform: translateX(120%);
            opacity: 0;
        }
        .alert-toast .alert-icon {
            flex-shrink: 0;
            font-size: 1.4rem;
            margin-top: 0.1rem;
        }
        .alert-toast .alert-content {
            flex: 1;
            word-break: break-word;
        }
        .alert-toast .alert-close {
            background: none;
            border: none;
            color: var(--text-muted, #8da68d);
            font-size: 1.2rem;
            cursor: pointer;
            padding: 0 0.2rem;
            transition: color 0.2s;
            flex-shrink: 0;
            margin-top: -0.1rem;
        }
        .alert-toast .alert-close:hover {
            color: var(--text-light, #eef6ee);
        }

        /* ---------- TYPES ---------- */
        .alert-toast.alert-info {
            border-left: 4px solid var(--accent-amber, #f59e0b);
        }
        .alert-toast.alert-info .alert-icon {
            color: var(--accent-amber, #f59e0b);
        }

        .alert-toast.alert-success {
            border-left: 4px solid var(--accent-emerald, #34d399);
        }
        .alert-toast.alert-success .alert-icon {
            color: var(--accent-emerald, #34d399);
        }

        .alert-toast.alert-warning {
            border-left: 4px solid #f59e0b;
        }
        .alert-toast.alert-warning .alert-icon {
            color: #f59e0b;
        }

        .alert-toast.alert-error {
            border-left: 4px solid #ef4444;
        }
        .alert-toast.alert-error .alert-icon {
            color: #ef4444;
        }

        .alert-toast.alert-neutral {
            border-left: 4px solid rgba(255,255,255,0.2);
        }
        .alert-toast.alert-neutral .alert-icon {
            color: var(--text-muted, #8da68d);
        }

        /* Mobile tweaks */
        @media (max-width: 480px) {
            .alert-container {
                top: 12px;
                right: 12px;
                left: 12px;
                max-width: 100%;
                width: auto;
            }
            .alert-toast {
                padding: 0.8rem 1rem;
                font-size: 0.85rem;
            }
        }
    `;

    // ---------- INJECT STYLES (once) ----------
    let stylesInjected = false;
    function injectStyles() {
        if (stylesInjected) return;
        const styleEl = document.createElement('style');
        styleEl.textContent = styles;
        document.head.appendChild(styleEl);
        stylesInjected = true;
    }

    // ---------- CONTAINER ----------
    let container = null;
    function getContainer() {
        if (!container) {
            container = document.createElement('div');
            container.className = 'alert-container';
            document.body.appendChild(container);
        }
        return container;
    }

    // ---------- ICON MAP ----------
    const iconMap = {
        info:    'fa-info-circle',
        success: 'fa-check-circle',
        warning: 'fa-exclamation-triangle',
        error:   'fa-times-circle',
        neutral: 'fa-bell'
    };

    // ---------- CREATE TOAST ----------
    function createToast(message, type = 'info', duration = DEFAULT_DURATION) {
        const containerEl = getContainer();

        // Limit visible toasts (remove oldest if too many)
        while (containerEl.children.length >= MAX_VISIBLE) {
            const first = containerEl.firstChild;
            if (first) {
                first.classList.add('hide');
                setTimeout(() => first.remove(), 400);
            }
        }

        const toast = document.createElement('div');
        toast.className = `alert-toast alert-${type}`;

        // Icon
        const iconClass = iconMap[type] || iconMap.info;
        const iconEl = document.createElement('span');
        iconEl.className = `alert-icon fas ${iconClass}`;
        toast.appendChild(iconEl);

        // Content
        const contentEl = document.createElement('span');
        contentEl.className = 'alert-content';
        contentEl.textContent = message;
        toast.appendChild(contentEl);

        // Close button
        const closeBtn = document.createElement('button');
        closeBtn.className = 'alert-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Close alert');
        closeBtn.addEventListener('click', () => {
            closeToast(toast);
        });
        toast.appendChild(closeBtn);

        // Append and trigger show
        containerEl.appendChild(toast);
        // Force reflow then add show class
        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        // Auto-dismiss
        let timer = null;
        if (duration > 0) {
            timer = setTimeout(() => {
                closeToast(toast);
            }, duration);
        }

        // Store timer for possible early cancellation
        toast._timer = timer;

        return toast;
    }

    // ---------- CLOSE TOAST ----------
    function closeToast(toast) {
        if (toast._closed) return;
        toast._closed = true;
        if (toast._timer) {
            clearTimeout(toast._timer);
            toast._timer = null;
        }
        toast.classList.remove('show');
        toast.classList.add('hide');
        // Remove after animation
        setTimeout(() => {
            if (toast.parentNode) toast.remove();
        }, 400);
    }

    // ---------- PUBLIC API ----------
    window.showAlert = function(message, type = 'info', duration = DEFAULT_DURATION) {
        injectStyles();
        return createToast(message, type, duration);
    };

    // ---------- SHORTCUTS ----------
    window.alertInfo    = (msg, dur) => showAlert(msg, 'info', dur);
    window.alertSuccess = (msg, dur) => showAlert(msg, 'success', dur);
    window.alertWarning = (msg, dur) => showAlert(msg, 'warning', dur);
    window.alertError   = (msg, dur) => showAlert(msg, 'error', dur);
    window.alertNeutral = (msg, dur) => showAlert(msg, 'neutral', dur);

    // ---------- CLOSE ALL ----------
    window.clearAlerts = function() {
        const containerEl = getContainer();
        while (containerEl.firstChild) {
            closeToast(containerEl.firstChild);
        }
    };

})();