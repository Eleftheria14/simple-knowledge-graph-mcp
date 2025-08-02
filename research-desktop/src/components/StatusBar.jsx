import React, { useState, useEffect } from 'react';

const StatusBar = ({ mcpConnected, documentsCount, isProcessing }) => {
  const [memoryUsage, setMemoryUsage] = useState(null);
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    // Update time every second
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);

    // Update memory usage periodically (if available)
    const memoryInterval = setInterval(() => {
      if (window.performance && window.performance.memory) {
        setMemoryUsage({
          used: Math.round(window.performance.memory.usedJSHeapSize / 1024 / 1024),
          total: Math.round(window.performance.memory.totalJSHeapSize / 1024 / 1024)
        });
      }
    }, 5000);

    return () => {
      clearInterval(timeInterval);
      clearInterval(memoryInterval);
    };
  }, []);

  const formatTime = (date) => {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-t border-slate-700 text-xs text-gray-400">
      {/* Left side - Connection and processing status */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            mcpConnected ? 'bg-green-500 animate-pulse' : 'bg-red-500'
          }`} />
          <span>{mcpConnected ? 'MCP Connected' : 'MCP Disconnected'}</span>
        </div>
        
        {isProcessing && (
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 border border-blue-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-blue-400">Processing PDFs...</span>
          </div>
        )}
        
        <div className="flex items-center space-x-2">
          <span>📚</span>
          <span>{documentsCount} documents</span>
        </div>
      </div>

      {/* Right side - System info and time */}
      <div className="flex items-center space-x-4">
        {memoryUsage && (
          <div className="flex items-center space-x-2">
            <span>🧠</span>
            <span>{memoryUsage.used}MB / {memoryUsage.total}MB</span>
          </div>
        )}
        
        <div className="flex items-center space-x-2">
          <span>🕐</span>
          <span>{formatTime(currentTime)}</span>
        </div>
      </div>
    </div>
  );
};

export default StatusBar;