const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // App info
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // Dialog handlers
  showOpenDialog: (options) => ipcRenderer.invoke('show-open-dialog', options),
  showSaveDialog: (options) => ipcRenderer.invoke('show-save-dialog', options),
  showErrorDialog: (title, content) => ipcRenderer.invoke('show-error-dialog', title, content),
  showMessageDialog: (options) => ipcRenderer.invoke('show-message-dialog', options),
  
  // Menu actions - receive from main process
  onFilesSelected: (callback) => ipcRenderer.on('files-selected', callback),
  onExportGraph: (callback) => ipcRenderer.on('export-graph', callback),
  onExportReview: (callback) => ipcRenderer.on('export-review', callback),
  onFocusSearch: (callback) => ipcRenderer.on('focus-search', callback),
  onOpenLiteratureReview: (callback) => ipcRenderer.on('open-literature-review', callback),
  onClearAllData: (callback) => ipcRenderer.on('clear-all-data', callback),
  
  // Remove listeners
  removeAllListeners: (channel) => ipcRenderer.removeAllListeners(channel),
  
  // Platform info
  platform: process.platform,
  
  // File operations
  openPath: (path) => ipcRenderer.invoke('open-path', path),
  
  // Direct API calls - no MCP dependency
  api: {
    // Call backend GROBID processor
    async processWithGrobid(filePath) {
      try {
        console.log('Starting GROBID processing for:', filePath);
        
        if (!filePath) {
          throw new Error('No file path provided');
        }
        
        // Direct HTTP call to backend API server
        const response = await fetch('http://localhost:8001/api/process-grobid', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            file_path: filePath
          })
        });

        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        
        if (!result) {
          throw new Error('No result from backend GROBID processor');
        }
        
        if (!result.success) {
          throw new Error(result.error || 'Backend GROBID processing failed');
        }
        
        // Transform backend response to frontend format
        const referencesArray = result.metadata?.references || [];
        const transformedResult = {
          success: true,
          title: result.metadata?.title || 'Untitled Document',
          authors: result.metadata?.authors?.map(a => a.name || a) || [],
          abstract: result.metadata?.abstract || '',
          references: referencesArray, // Array of reference objects for display
          entities: 0, // Will be extracted by LLM later
          entityList: [], // Will be populated by LLM entity extraction
          content: result.content || '',
          fullText: result.content || '',
          metadata: result.metadata || {},
          citations: referencesArray, // Same data, different field name for compatibility
          figures: result.metadata?.figures || [],
          tables: result.metadata?.tables || [],
          keywords: result.metadata?.keywords || [],
          filePath
        };
        
        console.log('Backend GROBID processing successful:', {
          title: transformedResult.title.substring(0, 50),
          authors: transformedResult.authors.length,
          references: transformedResult.references.length,
          entities: transformedResult.entities
        });
        
        return transformedResult;
        
      } catch (error) {
        console.error('GROBID processing error:', error);
        return {
          success: false,
          error: error.message,
          title: 'Processing Error',
          authors: [],
          abstract: '',
          references: 0,
          entities: 0,
          entityList: [],
          filePath
        };
      }
    },
    
    
    
    // Check if GROBID is running
    async checkGrobidHealth() {
      try {
        const response = await fetch('http://localhost:8070/api/isalive');
        const result = await response.text();
        return result.trim() === 'true';
      } catch (error) {
        return false;
      }
    },
    
    // Backend storage functions - no direct database calls in frontend
    async savePDFResult(result, sessionId = null) {
      try {
        // Direct HTTP call to backend API server
        const response = await fetch('http://localhost:8001/api/documents', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            grobid_result: result,
            file_path: result.filePath,
            session_id: sessionId
          })
        });

        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const storageResult = await response.json();
        console.log('Storage result:', storageResult);
        return storageResult;
      } catch (error) {
        console.error('Error saving to backend storage:', error);
        return { success: false, error: error.message };
      }
    },
    
    async loadPDFResults() {
      try {
        const documents = await ipcRenderer.invoke('load-grobid-documents');
        
        // Transform backend format to frontend format for compatibility
        return documents.map(doc => ({
          id: doc.id,
          fileName: doc.file_name,
          filePath: doc.path,
          originalPath: doc.original_path,
          originalFileName: doc.original_filename,
          fileRenamed: doc.file_renamed,
          title: doc.title,
          authors: doc.authors,
          abstract: doc.abstract,
          references: doc.references || [], // Array of reference objects for display
          entities: 0, // Entities would be extracted by LLM separately
          success: doc.success,
          error: doc.error,
          timestamp: doc.created,
          fullText: doc.full_text,
          citations: doc.references || [], // Same data, different field name for compatibility
          figures: doc.figures || [],
          tables: doc.tables || [],
          keywords: doc.keywords || [],
          entityList: []
        }));
      } catch (error) {
        console.error('Error loading from backend storage:', error);
        return [];
      }
    },
    
    async clearAllPDFResults() {
      try {
        const result = await ipcRenderer.invoke('clear-grobid-documents');
        console.log('Clear operation result:', result);
        return result;
      } catch (error) {
        console.error('Error clearing backend data:', error);
        return { success: false, error: error.message };
      }
    },

    // Session management functions
    async createSession(sessionName = null) {
      try {
        const response = await fetch('http://localhost:8001/api/sessions', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: sessionName
          })
        });

        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        return result;
      } catch (error) {
        console.error('Error creating session:', error);
        return { success: false, error: error.message };
      }
    },

    async getSessions() {
      try {
        const response = await fetch('http://localhost:8001/api/sessions');
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const sessions = await response.json();
        return sessions;
      } catch (error) {
        console.error('Error loading sessions:', error);
        return [];
      }
    },

    async getSessionDocuments(sessionId) {
      try {
        const response = await fetch(`http://localhost:8001/api/sessions/${sessionId}/documents`);
        
        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const documents = await response.json();
        
        // Transform backend format to frontend format for compatibility
        return documents.map(doc => ({
          id: doc.id,
          fileName: doc.file_name,
          filePath: doc.path,
          originalPath: doc.original_path,
          originalFileName: doc.original_filename,
          fileRenamed: doc.file_renamed,
          title: doc.title,
          authors: doc.authors,
          abstract: doc.abstract,
          references: doc.references || [], // Array of reference objects for display
          entities: 0, // Entities would be extracted by LLM separately
          success: doc.success,
          error: doc.error,
          timestamp: doc.created,
          fullText: doc.full_text,
          citations: doc.references || [], // Same data, different field name for compatibility
          figures: doc.figures || [],
          tables: doc.tables || [],
          keywords: doc.keywords || [],
          entityList: []
        }));
      } catch (error) {
        console.error('Error loading session documents:', error);
        return [];
      }
    },

    async deleteSession(sessionId, deleteDocuments = false) {
      try {
        const response = await fetch(`http://localhost:8001/api/sessions/${sessionId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            delete_documents: deleteDocuments
          })
        });

        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        return result;
      } catch (error) {
        console.error('Error deleting session:', error);
        return { success: false, error: error.message };
      }
    },

    async getDocumentDetails(documentId) {
      try {
        const result = await ipcRenderer.invoke('get-document-details', documentId);
        return result;
      } catch (error) {
        console.error('Error loading document details:', error);
        return { success: false, error: error.message };
      }
    },

    async extractEntities(documentId, extractionConfig = 'academic') {
      try {
        const result = await ipcRenderer.invoke('extract-entities', documentId, extractionConfig);
        return result;
      } catch (error) {
        console.error('Error extracting entities:', error);
        return { success: false, error: error.message };
      }
    },

    async deleteDocument(documentId) {
      try {
        const response = await fetch(`http://localhost:8001/api/documents/${documentId}`, {
          method: 'DELETE',
          headers: {
            'Content-Type': 'application/json',
          }
        });

        if (!response.ok) {
          throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
        }

        const result = await response.json();
        return result;
      } catch (error) {
        console.error('Error deleting document:', error);
        return { success: false, error: error.message };
      }
    }
  }
});

// DOM content loaded helper
contextBridge.exposeInMainWorld('domReady', () => {
  return new Promise(resolve => {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', resolve);
    } else {
      resolve();
    }
  });
});