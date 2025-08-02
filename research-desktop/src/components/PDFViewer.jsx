import React, { useState, useEffect } from 'react';

const PDFViewer = ({ document, onClose }) => {
  const [pdfUrl, setPdfUrl] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [scale, setScale] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (document?.path) {
      loadPDF();
    }
  }, [document]);

  const loadPDF = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // In Electron, we can access local files directly
      // Convert file path to file:// URL for display
      const fileUrl = `file://${document.path}`;
      setPdfUrl(fileUrl);
      
      // For now, we'll simulate page count - in a real implementation,
      // you'd use PDF.js to get actual page information
      setTotalPages(Math.floor(Math.random() * 20) + 5); // Simulate 5-25 pages
      
    } catch (err) {
      setError(`Failed to load PDF: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleZoomIn = () => {
    setScale(prev => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setScale(prev => Math.max(prev - 0.25, 0.5));
  };

  const handleResetZoom = () => {
    setScale(1);
  };

  const handlePrevPage = () => {
    setCurrentPage(prev => Math.max(prev - 1, 1));
  };

  const handleNextPage = () => {
    setCurrentPage(prev => Math.min(prev + 1, totalPages));
  };

  const handleKeyDown = (e) => {
    switch (e.key) {
      case 'Escape':
        onClose();
        break;
      case 'ArrowLeft':
        handlePrevPage();
        break;
      case 'ArrowRight':
        handleNextPage();
        break;
      case '+':
      case '=':
        handleZoomIn();
        break;
      case '-':
        handleZoomOut();
        break;
      case '0':
        handleResetZoom();
        break;
    }
  };

  useEffect(() => {
    const handleKeyDownWrapper = (e) => handleKeyDown(e);
    window.addEventListener('keydown', handleKeyDownWrapper);
    return () => window.removeEventListener('keydown', handleKeyDownWrapper);
  }, []);

  if (!document) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex flex-col z-50">
      {/* Header */}
      <div className="bg-slate-800 p-4 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-white">
            📄 {document.name || document.title}
          </h2>
          {document.authors && (
            <span className="text-sm text-gray-400">
              by {document.authors.slice(0, 2).join(', ')}
              {document.authors.length > 2 && ` +${document.authors.length - 2} more`}
            </span>
          )}
        </div>
        
        <div className="flex items-center space-x-2">
          <span className="text-sm text-gray-400">
            {document.entities || 0} entities • {document.citations || 0} citations
          </span>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors p-2"
            title="Close (Esc)"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Toolbar */}
      <div className="bg-slate-800 p-3 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          {/* Page Navigation */}
          <div className="flex items-center space-x-2">
            <button
              onClick={handlePrevPage}
              disabled={currentPage <= 1}
              className="btn btn-ghost text-sm disabled:opacity-50"
              title="Previous Page (←)"
            >
              ←
            </button>
            <span className="text-sm text-gray-300">
              Page {currentPage} of {totalPages}
            </span>
            <button
              onClick={handleNextPage}
              disabled={currentPage >= totalPages}
              className="btn btn-ghost text-sm disabled:opacity-50"
              title="Next Page (→)"
            >
              →
            </button>
          </div>
          
          {/* Zoom Controls */}
          <div className="flex items-center space-x-2 border-l border-slate-600 pl-4">
            <button
              onClick={handleZoomOut}
              disabled={scale <= 0.5}
              className="btn btn-ghost text-sm disabled:opacity-50"
              title="Zoom Out (-)"
            >
              🔍−
            </button>
            <span className="text-sm text-gray-300 min-w-16 text-center">
              {Math.round(scale * 100)}%
            </span>
            <button
              onClick={handleZoomIn}
              disabled={scale >= 3}
              className="btn btn-ghost text-sm disabled:opacity-50"
              title="Zoom In (+)"
            >
              🔍+
            </button>
            <button
              onClick={handleResetZoom}
              className="btn btn-ghost text-sm"
              title="Reset Zoom (0)"
            >
              Reset
            </button>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => window.electronAPI?.showSaveDialog({
              filters: [{ name: 'PDF', extensions: ['pdf'] }]
            })}
            className="btn btn-secondary text-sm"
            title="Save As"
          >
            💾 Save As
          </button>
          <button
            onClick={async () => {
              if (window.electronAPI) {
                try {
                  await window.electronAPI.openPath(document.path);
                } catch (error) {
                  console.error('Failed to open PDF:', error);
                }
              }
            }}
            className="btn btn-secondary text-sm"
            title="Open in System Viewer"
          >
            🔗 Open External
          </button>
        </div>
      </div>

      {/* PDF Content */}
      <div className="flex-1 overflow-auto bg-gray-900 p-4">
        {loading && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="spinner mb-4"></div>
              <p className="text-gray-400">Loading PDF...</p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-red-400">
              <div className="text-6xl mb-4">⚠️</div>
              <h3 className="text-xl font-semibold mb-2">Cannot Preview PDF</h3>
              <p className="mb-4">{error}</p>
              <div className="space-x-2">
                <button 
                  onClick={loadPDF}
                  className="btn btn-secondary"
                >
                  Retry
                </button>
                <button 
                  onClick={async () => {
                    // Try to open with system default
                    if (window.electronAPI) {
                      try {
                        await window.electronAPI.openPath(document.path);
                      } catch (error) {
                        console.error('Failed to open PDF:', error);
                      }
                    }
                  }}
                  className="btn btn-primary"
                >
                  Open in System Viewer
                </button>
              </div>
            </div>
          </div>
        )}
        
        {pdfUrl && !loading && !error && (
          <div className="flex justify-center">
            <div 
              className="bg-white shadow-lg"
              style={{ 
                transform: `scale(${scale})`,
                transformOrigin: 'top center',
                minHeight: '800px',
                width: '612px' // Standard letter width in pixels
              }}
            >
              {/* Simple PDF placeholder - in production, use PDF.js */}
              <div className="w-full h-full border border-gray-300 bg-white p-8">
                <div className="text-black text-sm mb-4">
                  <strong>{document.name}</strong>
                </div>
                <div className="text-gray-600 text-xs mb-6">
                  Page {currentPage} of {totalPages}
                </div>
                <div className="text-gray-800 text-sm leading-relaxed">
                  <p className="mb-4">
                    <strong>Note:</strong> This is a placeholder PDF viewer. 
                    In a production app, you would integrate PDF.js or a similar 
                    library to render the actual PDF content.
                  </p>
                  <p className="mb-4">
                    <strong>Document Info:</strong>
                  </p>
                  <ul className="list-disc list-inside space-y-1 text-xs">
                    <li>File: {document.path}</li>
                    <li>Processed: {document.processedAt ? new Date(document.processedAt).toLocaleString() : 'Not processed'}</li>
                    <li>Entities: {document.entities || 0}</li>
                    <li>Citations: {document.citations || 0}</li>
                    <li>Status: {document.status}</li>
                  </ul>
                  <p className="mt-6 text-xs text-gray-500">
                    Use the toolbar above to navigate pages and zoom. 
                    Press Esc to close, arrow keys to navigate, +/- to zoom.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
      
      {/* Footer */}
      <div className="bg-slate-800 p-3 border-t border-slate-700 text-center">
        <div className="text-xs text-gray-500">
          Use arrow keys to navigate • +/- to zoom • Esc to close • Click "Open External" for full PDF viewer
        </div>
      </div>
    </div>
  );
};

export default PDFViewer;