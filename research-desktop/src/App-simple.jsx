import React, { useState, useEffect } from 'react';

function App() {
  const [mcpConnected, setMcpConnected] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [processing, setProcessing] = useState(false);
  const [processedResults, setProcessedResults] = useState([]);

  // Test MCP connection without crashing
  useEffect(() => {
    const testConnection = async () => {
      try {
        // Simple connection test with no-cors mode
        const response = await fetch('http://localhost:3001/', { 
          method: 'GET',
          mode: 'no-cors'
        });
        setMcpConnected(true);
        console.log('MCP server is reachable');
      } catch (error) {
        console.log('MCP connection test failed:', error);
        setMcpConnected(false);
      }
    };

    testConnection();
  }, []);

  // Simple file handler
  const handleFileSelect = async () => {
    try {
      const result = await window.electronAPI.showOpenDialog({
        properties: ['openFile', 'multiSelections'],
        filters: [{ name: 'PDF Files', extensions: ['pdf'] }]
      });
      
      if (!result.canceled && result.filePaths) {
        setSelectedFiles(result.filePaths);
      }
    } catch (error) {
      console.error('File selection error:', error);
    }
  };

  // Simple drag and drop
  const handleDrop = (e) => {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files)
      .filter(file => file.name.toLowerCase().endsWith('.pdf'))
      .map(file => file.path || file.name);
    
    if (files.length > 0) {
      setSelectedFiles(files);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  // Process selected files
  const processFiles = async () => {
    if (selectedFiles.length === 0) return;
    
    setProcessing(true);
    setProcessedResults([]);
    
    try {
      for (const filePath of selectedFiles) {
        console.log(`Processing: ${filePath}`);
        
        // Simulate processing with GROBID (you can replace this with actual MCP calls)
        const result = {
          fileName: filePath.split('/').pop(),
          filePath: filePath,
          status: 'processed',
          entities: Math.floor(Math.random() * 50) + 10,
          citations: Math.floor(Math.random() * 20) + 5,
          processedAt: new Date().toISOString()
        };
        
        // Add a delay to simulate processing
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setProcessedResults(prev => [...prev, result]);
        console.log(`✅ Processed: ${result.fileName}`);
      }
      
      console.log('🎉 All files processed successfully!');
    } catch (error) {
      console.error('❌ Processing failed:', error);
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <h1 className="text-xl font-bold">Academic Research Assistant</h1>
        <div className="flex items-center mt-2">
          <div className={`w-3 h-3 rounded-full mr-2 ${mcpConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm">{mcpConnected ? 'MCP Connected' : 'MCP Disconnected'}</span>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-lg font-semibold mb-4">📄 PDF File Processor</h2>
          
          {/* File Drop Zone */}
          <div 
            className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center mb-6
                       hover:border-blue-500 transition-colors cursor-pointer"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onClick={handleFileSelect}
          >
            <div className="text-4xl mb-4">📄</div>
            <p className="text-lg mb-2">Drop PDFs here or click to browse</p>
            <p className="text-sm text-gray-400">Supports multiple files</p>
          </div>

          {/* Selected Files */}
          {selectedFiles.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4">
              <h3 className="font-semibold mb-3">Selected Files:</h3>
              <ul className="space-y-2">
                {selectedFiles.map((file, index) => (
                  <li key={index} className="text-sm text-gray-300 bg-gray-700 p-2 rounded">
                    📄 {file.split('/').pop()}
                    <div className="text-xs text-gray-500 mt-1">{file}</div>
                  </li>
                ))}
              </ul>
              <button 
                className="mt-4 bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                onClick={processFiles}
                disabled={processing}
              >
                {processing ? 'Processing...' : `Process Files (${selectedFiles.length})`}
              </button>
            </div>
          )}

          {/* Processed Results */}
          {processedResults.length > 0 && (
            <div className="bg-gray-800 rounded-lg p-4 mt-6">
              <h3 className="font-semibold mb-3">🎉 Processed Documents:</h3>
              <div className="space-y-3">
                {processedResults.map((result, index) => (
                  <div key={index} className="bg-gray-700 p-3 rounded">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-green-400">📄 {result.fileName}</h4>
                        <p className="text-sm text-gray-400 mt-1">
                          📊 {result.entities} entities • 📚 {result.citations} citations
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          Processed: {new Date(result.processedAt).toLocaleString()}
                        </p>
                      </div>
                      <div className="text-green-500">✅</div>
                    </div>
                  </div>
                ))}
              </div>
              <button 
                className="mt-4 bg-gray-600 hover:bg-gray-500 px-4 py-2 rounded transition-colors text-sm"
                onClick={() => {
                  setProcessedResults([]);
                  setSelectedFiles([]);
                }}
              >
                Clear Results
              </button>
            </div>
          )}

          {/* Status */}
          <div className="mt-6 text-sm text-gray-400">
            <p>✅ File browsing and drag-and-drop ready</p>
            <p>⚡ Processing simulation ready</p>
            <p>🔧 MCP connection: {mcpConnected ? 'Working' : 'Not connected'}</p>
            {processing && <p className="text-blue-400">⏳ Processing files...</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;