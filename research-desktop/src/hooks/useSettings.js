import { useState, useEffect } from 'react';

const DEFAULT_SETTINGS = {
  neo4j: {
    uri: 'bolt://localhost:7687',
    username: 'neo4j',
    password: ''
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
};

export const useSettings = () => {
  const [settings, setSettings] = useState(DEFAULT_SETTINGS);
  const [showSettings, setShowSettings] = useState(false);

  // Load settings from localStorage on mount
  useEffect(() => {
    try {
      const savedSettings = localStorage.getItem('academic-research-settings');
      if (savedSettings) {
        const parsed = JSON.parse(savedSettings);
        setSettings({ ...DEFAULT_SETTINGS, ...parsed });
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  }, []);

  // Save settings to localStorage
  const saveSettings = (newSettings) => {
    try {
      localStorage.setItem('academic-research-settings', JSON.stringify(newSettings));
      setSettings(newSettings);
      
      // Apply theme changes immediately
      if (newSettings.display?.theme) {
        applyTheme(newSettings.display.theme);
      }
      
      return true;
    } catch (error) {
      console.error('Failed to save settings:', error);
      return false;
    }
  };

  // Apply theme to document
  const applyTheme = (theme) => {
    const root = document.documentElement;
    
    if (theme === 'light') {
      root.classList.add('light-theme');
      root.classList.remove('dark-theme');
    } else if (theme === 'dark') {
      root.classList.add('dark-theme');
      root.classList.remove('light-theme');
    } else if (theme === 'auto') {
      // Use system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      if (prefersDark) {
        root.classList.add('dark-theme');
        root.classList.remove('light-theme');
      } else {
        root.classList.add('light-theme');
        root.classList.remove('dark-theme');
      }
    }
  };

  // Get a specific setting value
  const getSetting = (path) => {
    const keys = path.split('.');
    let value = settings;
    
    for (const key of keys) {
      value = value?.[key];
      if (value === undefined) break;
    }
    
    return value;
  };

  // Update a specific setting
  const updateSetting = (path, value) => {
    const keys = path.split('.');
    const newSettings = { ...settings };
    let current = newSettings;
    
    for (let i = 0; i < keys.length - 1; i++) {
      const key = keys[i];
      if (!current[key]) current[key] = {};
      current = current[key];
    }
    
    current[keys[keys.length - 1]] = value;
    return saveSettings(newSettings);
  };

  // Reset to defaults
  const resetSettings = () => {
    return saveSettings(DEFAULT_SETTINGS);
  };

  // Check if settings are valid for MCP connection
  const isConfigurationValid = () => {
    const neo4j = settings.neo4j;
    return neo4j.uri && neo4j.username && neo4j.password;
  };

  // Export settings for backup
  const exportSettings = () => {
    try {
      const dataStr = JSON.stringify(settings, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'academic-research-settings.json';
      link.click();
      
      URL.revokeObjectURL(url);
      return true;
    } catch (error) {
      console.error('Failed to export settings:', error);
      return false;
    }
  };

  // Import settings from file
  const importSettings = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const imported = JSON.parse(e.target.result);
          const merged = { ...DEFAULT_SETTINGS, ...imported };
          
          if (saveSettings(merged)) {
            resolve(merged);
          } else {
            reject(new Error('Failed to save imported settings'));
          }
        } catch (error) {
          reject(new Error('Invalid settings file format'));
        }
      };
      
      reader.onerror = () => reject(new Error('Failed to read settings file'));
      reader.readAsText(file);
    });
  };

  return {
    settings,
    saveSettings,
    getSetting,
    updateSetting,
    resetSettings,
    isConfigurationValid,
    exportSettings,
    importSettings,
    showSettings,
    setShowSettings
  };
};