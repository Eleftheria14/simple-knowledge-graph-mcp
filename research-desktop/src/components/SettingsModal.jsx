import React, { useState, useEffect } from 'react';

const SettingsModal = ({ settings, onClose, onSave }) => {
  const [formData, setFormData] = useState({
    neo4j: {
      uri: 'bolt://localhost:7687',
      username: 'neo4j',
      password: '',
      testConnection: false
    },
    ai: {
      groqApiKey: '',
      model: 'llama-3.1-70b-versatile',
      confidenceThreshold: 0.7
    },
    processing: {
      autoProcess: true,
      extractFigures: true,
      maxConcurrentFiles: 3
    },
    display: {
      theme: 'dark',
      graphLayout: 'fcose',
      showConfidenceScores: true
    }
  });

  const [connectionStatus, setConnectionStatus] = useState(null);
  const [testingConnection, setTestingConnection] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  useEffect(() => {
    if (settings) {
      setFormData({ ...formData, ...settings });
    }
  }, [settings]);

  const handleInputChange = (section, field, value) => {
    setFormData(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
    setHasChanges(true);
  };

  const testDatabaseConnection = async () => {
    setTestingConnection(true);
    setConnectionStatus(null);

    try {
      // TODO: Implement actual connection test through MCP API
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate connection test
      if (formData.neo4j.uri && formData.neo4j.username && formData.neo4j.password) {
        setConnectionStatus({ success: true, message: 'Connection successful!' });
      } else {
        setConnectionStatus({ success: false, message: 'Missing required fields' });
      }
    } catch (error) {
      setConnectionStatus({ 
        success: false, 
        message: `Connection failed: ${error.message}` 
      });
    } finally {
      setTestingConnection(false);
    }
  };

  const handleSave = () => {
    onSave(formData);
    setHasChanges(false);
  };

  const handleClose = () => {
    if (hasChanges) {
      const confirmClose = window.confirm('You have unsaved changes. Are you sure you want to close?');
      if (!confirmClose) return;
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-slate-800 rounded-lg shadow-xl w-full max-w-2xl max-h-[80vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-slate-700">
          <h2 className="text-xl font-semibold text-white">⚙️ Settings</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            ✕
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[60vh]">
          <div className="p-6 space-y-8">
            {/* Database Settings */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                🗄️ Database Settings
              </h3>
              
              <div className="grid grid-cols-1 gap-4">
                <div className="input-group">
                  <label className="input-label">Neo4j URI</label>
                  <input
                    type="text"
                    value={formData.neo4j.uri}
                    onChange={(e) => handleInputChange('neo4j', 'uri', e.target.value)}
                    placeholder="bolt://localhost:7687"
                    className="input"
                  />
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="input-group">
                    <label className="input-label">Username</label>
                    <input
                      type="text"
                      value={formData.neo4j.username}
                      onChange={(e) => handleInputChange('neo4j', 'username', e.target.value)}
                      placeholder="neo4j"
                      className="input"
                    />
                  </div>
                  
                  <div className="input-group">
                    <label className="input-label">Password</label>
                    <input
                      type="password"
                      value={formData.neo4j.password}
                      onChange={(e) => handleInputChange('neo4j', 'password', e.target.value)}
                      placeholder="Enter password"
                      className="input"
                    />
                  </div>
                </div>
                
                <div className="flex items-center space-x-3">
                  <button
                    onClick={testDatabaseConnection}
                    disabled={testingConnection}
                    className="btn btn-secondary"
                  >
                    {testingConnection ? (
                      <>
                        <div className="spinner mr-2" />
                        Testing...
                      </>
                    ) : (
                      'Test Connection'
                    )}
                  </button>
                  
                  {connectionStatus && (
                    <div className={`text-sm ${
                      connectionStatus.success ? 'text-green-400' : 'text-red-400'
                    }`}>
                      {connectionStatus.success ? '✅' : '❌'} {connectionStatus.message}
                    </div>
                  )}
                </div>
              </div>
            </section>

            {/* AI Settings */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                🤖 AI Settings
              </h3>
              
              <div className="grid grid-cols-1 gap-4">
                <div className="input-group">
                  <label className="input-label">Groq API Key</label>
                  <input
                    type="password"
                    value={formData.ai.groqApiKey}
                    onChange={(e) => handleInputChange('ai', 'groqApiKey', e.target.value)}
                    placeholder="Enter your Groq API key"
                    className="input"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Get your API key from <a href="https://console.groq.com" className="text-blue-400 hover:text-blue-300">console.groq.com</a>
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="input-group">
                    <label className="input-label">Model</label>
                    <select
                      value={formData.ai.model}
                      onChange={(e) => handleInputChange('ai', 'model', e.target.value)}
                      className="input"
                    >
                      <option value="llama-3.1-70b-versatile">Llama 3.1 70B</option>
                      <option value="llama-3.1-8b-instant">Llama 3.1 8B</option>
                      <option value="mixtral-8x7b-32768">Mixtral 8x7B</option>
                    </select>
                  </div>
                  
                  <div className="input-group">
                    <label className="input-label">Confidence Threshold</label>
                    <input
                      type="number"
                      min="0"
                      max="1"
                      step="0.1"
                      value={formData.ai.confidenceThreshold}
                      onChange={(e) => handleInputChange('ai', 'confidenceThreshold', parseFloat(e.target.value))}
                      className="input"
                    />
                  </div>
                </div>
              </div>
            </section>

            {/* Processing Options */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                📊 Processing Options
              </h3>
              
              <div className="space-y-3">
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={formData.processing.autoProcess}
                    onChange={(e) => handleInputChange('processing', 'autoProcess', e.target.checked)}
                    className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-300">Auto-process new PDFs when added</span>
                </label>
                
                <label className="flex items-center space-x-3">
                  <input
                    type="checkbox"
                    checked={formData.processing.extractFigures}
                    onChange={(e) => handleInputChange('processing', 'extractFigures', e.target.checked)}
                    className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-300">Extract figures and tables</span>
                </label>
                
                <div className="input-group">
                  <label className="input-label">Max Concurrent Files</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.processing.maxConcurrentFiles}
                    onChange={(e) => handleInputChange('processing', 'maxConcurrentFiles', parseInt(e.target.value))}
                    className="input w-24"
                  />
                </div>
              </div>
            </section>

            {/* Display Options */}
            <section className="space-y-4">
              <h3 className="text-lg font-semibold text-white flex items-center">
                🎨 Display Options
              </h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="input-group">
                  <label className="input-label">Theme</label>
                  <select
                    value={formData.display.theme}
                    onChange={(e) => handleInputChange('display', 'theme', e.target.value)}
                    className="input"
                  >
                    <option value="dark">Dark</option>
                    <option value="light">Light</option>
                    <option value="auto">Auto</option>
                  </select>
                </div>
                
                <div className="input-group">
                  <label className="input-label">Default Graph Layout</label>
                  <select
                    value={formData.display.graphLayout}
                    onChange={(e) => handleInputChange('display', 'graphLayout', e.target.value)}
                    className="input"
                  >
                    <option value="fcose">Force Layout</option>
                    <option value="dagre">Hierarchical</option>
                    <option value="circle">Circular</option>
                    <option value="cose">Spring</option>
                  </select>
                </div>
              </div>
              
              <label className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  checked={formData.display.showConfidenceScores}
                  onChange={(e) => handleInputChange('display', 'showConfidenceScores', e.target.checked)}
                  className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-300">Show confidence scores</span>
              </label>
            </section>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-slate-700 bg-slate-750">
          <div className="text-sm text-gray-400">
            {hasChanges && '● Unsaved changes'}
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={handleClose}
              className="btn btn-ghost"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!hasChanges}
              className="btn btn-primary"
            >
              Save Settings
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsModal;