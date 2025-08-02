import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';

const PDFDropZone = ({ onFilesSelected, isProcessing, disabled }) => {
  const [dragActive, setDragActive] = useState(false);

  const onDrop = useCallback((acceptedFiles) => {
    if (disabled || isProcessing) return;
    
    const pdfFiles = acceptedFiles.filter(file => 
      file.type === 'application/pdf' || file.name.toLowerCase().endsWith('.pdf')
    );
    
    if (pdfFiles.length > 0) {
      // In Electron, we need to get the full file path
      const filePaths = pdfFiles.map(file => {
        // Electron provides the full path in the file object
        return file.path || file.webkitRelativePath || file.name;
      });
      
      console.log('Dropped files:', filePaths); // Debug log
      onFilesSelected(filePaths);
    }
  }, [onFilesSelected, disabled, isProcessing]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    disabled: disabled || isProcessing,
    multiple: true
  });

  const handleBrowseClick = async () => {
    if (disabled || isProcessing) return;
    
    try {
      // Trigger the native file picker through Electron
      const result = await window.electronAPI.showOpenDialog({
        properties: ['openFile', 'multiSelections'],
        filters: [{ name: 'PDF Files', extensions: ['pdf'] }]
      });
      
      console.log('File dialog result:', result); // Debug log
      
      if (!result.canceled && result.filePaths && result.filePaths.length > 0) {
        onFilesSelected(result.filePaths);
      }
    } catch (error) {
      console.error('Error opening file dialog:', error);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-white mb-4">📄 Add Documents</h2>
      
      <div
        {...getRootProps()}
        className={`
          drop-zone cursor-pointer transition-all duration-200
          ${isDragActive ? 'drag-over' : ''}
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${isProcessing ? 'opacity-50 cursor-wait' : ''}
        `}
      >
        <input {...getInputProps()} />
        
        <div className="text-center py-8">
          <div className="text-4xl mb-4">
            {isProcessing ? '⏳' : isDragActive ? '📥' : '📄'}
          </div>
          
          <div className="space-y-2">
            {isProcessing ? (
              <>
                <p className="text-lg font-medium text-blue-400">Processing PDFs...</p>
                <div className="spinner mx-auto mt-2"></div>
              </>
            ) : isDragActive ? (
              <p className="text-lg font-medium text-blue-400">Drop PDFs here!</p>
            ) : (
              <>
                <p className="text-lg font-medium text-gray-300">
                  Drop PDFs here or{' '}
                  <button
                    onClick={handleBrowseClick}
                    className="text-blue-400 hover:text-blue-300 underline"
                    disabled={disabled}
                  >
                    browse files
                  </button>
                </p>
                <p className="text-sm text-gray-500">
                  Academic papers will be processed with GROBID
                </p>
              </>
            )}
          </div>
        </div>
      </div>
      
      {!disabled && (
        <div className="text-xs text-gray-500 space-y-1">
          <p>✅ Supports batch processing</p>
          <p>✅ Extracts entities & relationships</p>
          <p>✅ Processes citations & authors</p>
          <p>✅ Stores in knowledge graph</p>
        </div>
      )}
      
      {disabled && (
        <div className="text-sm text-red-400 bg-red-900 bg-opacity-20 p-3 rounded-lg border border-red-700">
          <p className="font-medium">⚠️ MCP Server Disconnected</p>
          <p className="text-xs mt-1">
            Please ensure the MCP server is running on port 3001
          </p>
        </div>
      )}
    </div>
  );
};

export default PDFDropZone;