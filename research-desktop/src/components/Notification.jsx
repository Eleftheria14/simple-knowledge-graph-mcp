import React, { useEffect, useState } from 'react';

const Notification = ({ notification, onClose }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLeaving, setIsLeaving] = useState(false);

  useEffect(() => {
    // Animate in
    const timer = setTimeout(() => setIsVisible(true), 100);
    
    // Auto-close after duration
    if (notification.duration !== 0) {
      const autoCloseTimer = setTimeout(() => {
        handleClose();
      }, notification.duration || 5000);
      
      return () => {
        clearTimeout(timer);
        clearTimeout(autoCloseTimer);
      };
    }
    
    return () => clearTimeout(timer);
  }, [notification.duration]);

  const handleClose = () => {
    setIsLeaving(true);
    setTimeout(() => {
      onClose();
    }, 300);
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success': return '✅';
      case 'error': return '❌';
      case 'warning': return '⚠️';
      case 'info': return 'ℹ️';
      default: return 'ℹ️';
    }
  };

  const getStyles = (type) => {
    const baseStyles = 'notification max-w-sm rounded-lg shadow-lg p-4 border transition-all duration-300 ease-out';
    
    const variants = {
      success: 'notification-success bg-green-900 bg-opacity-90 border-green-600 text-green-100',
      error: 'notification-error bg-red-900 bg-opacity-90 border-red-600 text-red-100',
      warning: 'notification-warning bg-yellow-900 bg-opacity-90 border-yellow-600 text-yellow-100',
      info: 'notification-info bg-blue-900 bg-opacity-90 border-blue-600 text-blue-100'
    };

    const animationStyles = isLeaving 
      ? 'transform translate-x-full opacity-0' 
      : isVisible 
        ? 'transform translate-x-0 opacity-100' 
        : 'transform translate-x-full opacity-0';

    return `${baseStyles} ${variants[type] || variants.info} ${animationStyles}`;
  };

  return (
    <div className={getStyles(notification.type)}>
      <div className="flex items-start space-x-3">
        <div className="text-lg flex-shrink-0 mt-0.5">
          {getIcon(notification.type)}
        </div>
        
        <div className="flex-1 min-w-0">
          {notification.title && (
            <h4 className="font-medium text-sm mb-1 truncate">
              {notification.title}
            </h4>
          )}
          
          {notification.message && (
            <p className="text-sm opacity-90 leading-relaxed">
              {notification.message}
            </p>
          )}
          
          {notification.action && (
            <button
              onClick={notification.action.handler}
              className="mt-2 text-xs underline hover:no-underline transition-all"
            >
              {notification.action.label}
            </button>
          )}
        </div>
        
        <button
          onClick={handleClose}
          className="flex-shrink-0 text-lg opacity-70 hover:opacity-100 transition-opacity"
          aria-label="Close notification"
        >
          ×
        </button>
      </div>
      
      {/* Progress bar for auto-close */}
      {notification.duration && notification.duration > 0 && (
        <div className="mt-3 bg-black bg-opacity-20 rounded-full h-1 overflow-hidden">
          <div 
            className="h-full bg-current opacity-50 transition-all ease-linear"
            style={{
              width: '100%',
              animation: `shrink ${notification.duration}ms linear`
            }}
          />
        </div>
      )}
      
      <style>{`
        @keyframes shrink {
          from { width: 100%; }
          to { width: 0%; }
        }
      `}</style>
    </div>
  );
};

export default Notification;