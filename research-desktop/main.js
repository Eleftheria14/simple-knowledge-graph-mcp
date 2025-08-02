const { app, BrowserWindow, Menu, dialog, ipcMain, shell } = require('electron');
const path = require('path');
const { execSync } = require('child_process');
const http = require('http');

// Keep a global reference of the window object
let mainWindow;
let settingsWindow;

function createWindow() {
  // Create the browser window
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 700,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset', // Native macOS title bar
    vibrancy: 'under-window', // Modern macOS glass effect
    show: false // Don't show until ready
  });

  // Load the app
  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile('dist/index.html');
  }

  // Show window when ready to prevent visual flash
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Handle external links
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url);
    return { action: 'deny' };
  });
}

function createSettingsWindow() {
  if (settingsWindow) {
    settingsWindow.focus();
    return;
  }

  settingsWindow = new BrowserWindow({
    width: 600,
    height: 700,
    resizable: false,
    minimizable: false,
    maximizable: false,
    parent: mainWindow,
    modal: true,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset'
  });

  const isDev = process.env.NODE_ENV === 'development' || !app.isPackaged;
  if (isDev) {
    settingsWindow.loadURL('http://localhost:5173#/settings');
  } else {
    settingsWindow.loadFile('dist/index.html', { hash: 'settings' });
  }

  settingsWindow.on('closed', () => {
    settingsWindow = null;
  });
}

function createMenu() {
  const template = [
    {
      label: 'Academic Research Assistant',
      submenu: [
        { label: 'About Academic Research Assistant', role: 'about' },
        { type: 'separator' },
        { 
          label: 'Preferences...', 
          accelerator: 'Cmd+,',
          click: () => createSettingsWindow()
        },
        { type: 'separator' },
        { label: 'Hide Academic Research Assistant', accelerator: 'Cmd+H', role: 'hide' },
        { label: 'Hide Others', accelerator: 'Cmd+Alt+H', role: 'hideothers' },
        { label: 'Show All', role: 'unhide' },
        { type: 'separator' },
        { label: 'Quit', accelerator: 'Cmd+Q', role: 'quit' }
      ]
    },
    {
      label: 'File',
      submenu: [
        { 
          label: 'Add PDFs...', 
          accelerator: 'Cmd+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow, {
              properties: ['openFile', 'multiSelections'],
              filters: [
                { name: 'PDF Files', extensions: ['pdf'] }
              ]
            });
            
            if (!result.canceled) {
              mainWindow.webContents.send('files-selected', result.filePaths);
            }
          }
        },
        { type: 'separator' },
        { 
          label: 'Export Graph...', 
          accelerator: 'Cmd+E',
          click: () => mainWindow.webContents.send('export-graph')
        },
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { label: 'Undo', accelerator: 'Cmd+Z', role: 'undo' },
        { label: 'Redo', accelerator: 'Shift+Cmd+Z', role: 'redo' },
        { type: 'separator' },
        { label: 'Cut', accelerator: 'Cmd+X', role: 'cut' },
        { label: 'Copy', accelerator: 'Cmd+C', role: 'copy' },
        { label: 'Paste', accelerator: 'Cmd+V', role: 'paste' }
      ]
    },
    {
      label: 'View',
      submenu: [
        { label: 'Reload', accelerator: 'Cmd+R', role: 'reload' },
        { label: 'Force Reload', accelerator: 'Cmd+Shift+R', role: 'forceReload' },
        { label: 'Toggle Developer Tools', accelerator: 'F12', role: 'toggleDevTools' },
        { type: 'separator' },
        { label: 'Actual Size', accelerator: 'Cmd+0', role: 'resetZoom' },
        { label: 'Zoom In', accelerator: 'Cmd+Plus', role: 'zoomIn' },
        { label: 'Zoom Out', accelerator: 'Cmd+-', role: 'zoomOut' },
        { type: 'separator' },
        { label: 'Toggle Fullscreen', accelerator: 'Ctrl+Cmd+F', role: 'togglefullscreen' }
      ]
    },
    {
      label: 'Research',
      submenu: [
        { 
          label: 'Search Knowledge Graph', 
          accelerator: 'Cmd+F',
          click: () => mainWindow.webContents.send('focus-search')
        },
        { type: 'separator' },
        { 
          label: 'Clear All Data', 
          click: async () => {
            const result = await dialog.showMessageBox(mainWindow, {
              type: 'warning',
              buttons: ['Cancel', 'Clear All Data'],
              defaultId: 0,
              cancelId: 0,
              title: 'Clear All Data',
              message: 'This will permanently delete all documents, entities, and relationships from your knowledge graph.',
              detail: 'This action cannot be undone.'
            });
            
            if (result.response === 1) {
              mainWindow.webContents.send('clear-all-data');
            }
          }
        }
      ]
    },
    {
      label: 'Window',
      submenu: [
        { label: 'Minimize', accelerator: 'Cmd+M', role: 'minimize' },
        { label: 'Close', accelerator: 'Cmd+W', role: 'close' }
      ]
    },
    {
      label: 'Help',
      submenu: [
        { 
          label: 'Academic Research Assistant Help',
          click: () => shell.openExternal('https://github.com/your-repo/academic-research-assistant#readme')
        },
        { type: 'separator' },
        { 
          label: 'Report Issue',
          click: () => shell.openExternal('https://github.com/your-repo/academic-research-assistant/issues')
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

// IPC handlers
ipcMain.handle('get-app-version', () => {
  return app.getVersion();
});

ipcMain.handle('show-open-dialog', async (event, options) => {
  const result = await dialog.showOpenDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-save-dialog', async (event, options) => {
  const result = await dialog.showSaveDialog(mainWindow, options);
  return result;
});

ipcMain.handle('show-error-dialog', async (event, title, content) => {
  dialog.showErrorBox(title, content);
});

ipcMain.handle('show-message-dialog', async (event, options) => {
  const result = await dialog.showMessageBox(mainWindow, options);
  return result;
});

ipcMain.handle('open-path', async (event, path) => {
  const { shell } = require('electron');
  return await shell.openPath(path);
});

ipcMain.handle('read-file', async (event, filePath) => {
  const fs = require('fs').promises;
  return await fs.readFile(filePath);
});

ipcMain.handle('store-grobid-result', async (event, grobidResult, filePath, sessionId = null) => {
  try {
    const response = await fetch('http://localhost:8001/api/documents', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        grobid_result: grobidResult,
        file_path: filePath,
        session_id: sessionId
      })
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Backend API error: ${response.status} ${response.statusText}`
      };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: `Failed to store document: ${error.message}`
    };
  }
});

ipcMain.handle('load-grobid-documents', async (event) => {
  try {
    const response = await fetch('http://localhost:8001/api/documents', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      console.error(`Backend API error: ${response.status} ${response.statusText}`);
      return [];
    }

    const documents = await response.json();
    return documents;
  } catch (error) {
    console.error(`Failed to load documents: ${error.message}`);
    return [];
  }
});

ipcMain.handle('clear-grobid-documents', async (event) => {
  try {
    const response = await fetch('http://localhost:8001/api/documents', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Backend API error: ${response.status} ${response.statusText}`
      };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: `Failed to clear documents: ${error.message}`
    };
  }
});

// Session management handlers
ipcMain.handle('create-session', async (event, sessionName) => {
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
      return {
        success: false,
        error: `Backend API error: ${response.status} ${response.statusText}`
      };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: `Failed to create session: ${error.message}`
    };
  }
});

ipcMain.handle('get-sessions', async (event) => {
  try {
    const response = await fetch('http://localhost:8001/api/sessions', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      console.error(`Backend API error: ${response.status} ${response.statusText}`);
      return [];
    }

    const sessions = await response.json();
    return sessions;
  } catch (error) {
    console.error(`Failed to load sessions: ${error.message}`);
    return [];
  }
});

ipcMain.handle('get-session-documents', async (event, sessionId) => {
  try {
    const response = await fetch(`http://localhost:8001/api/sessions/${sessionId}/documents`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      console.error(`Backend API error: ${response.status} ${response.statusText}`);
      return [];
    }

    const documents = await response.json();
    return documents;
  } catch (error) {
    console.error(`Failed to load session documents: ${error.message}`);
    return [];
  }
});

ipcMain.handle('delete-session', async (event, sessionId, deleteDocuments = false) => {
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
      return {
        success: false,
        error: `Backend API error: ${response.status} ${response.statusText}`
      };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: `Failed to delete session: ${error.message}`
    };
  }
});

// Document details handler
ipcMain.handle('get-document-details', async (event, documentId) => {
  try {
    const response = await fetch(`http://localhost:8001/api/documents/${documentId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (!response.ok) {
      return {
        success: false,
        error: `Backend API error: ${response.status} ${response.statusText}`
      };
    }

    const result = await response.json();
    return result;
  } catch (error) {
    return {
      success: false,
      error: `Failed to get document details: ${error.message}`
    };
  }
});

// Entity extraction handler
ipcMain.handle('extract-entities', async (event, documentId, extractionConfig = 'academic') => {
  console.log('🔧 Entity extraction API call for:', documentId, extractionConfig);
  
  try {
    // Determine extraction mode and chunking strategy
    let extractionMode = 'academic';
    let chunkingStrategy = 'hierarchical';
    
    if (typeof extractionConfig === 'object') {
      extractionMode = extractionConfig.mode || 'academic';
      chunkingStrategy = extractionConfig.chunking_strategy || 'hierarchical';
    } else {
      extractionMode = extractionConfig;
    }

    const postData = JSON.stringify({
      extraction_mode: extractionMode,
      chunking_strategy: chunkingStrategy,
      template: extractionConfig.template || null
    });

    const options = {
      hostname: '127.0.0.1',  // Use IPv4 explicitly instead of localhost
      port: 8001,
      path: `/api/documents/${documentId}/extract-entities`,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const result = await new Promise((resolve, reject) => {
      const req = http.request(options, (res) => {
        let data = '';
        
        res.on('data', (chunk) => {
          data += chunk;
        });
        
        res.on('end', () => {
          try {
            if (res.statusCode !== 200) {
              reject(new Error(`API request failed: ${res.statusCode} ${res.statusMessage}`));
              return;
            }
            
            const response = JSON.parse(data);
            console.log('✅ Entity extraction API response:', response);
            resolve(response);
          } catch (parseError) {
            reject(new Error(`Failed to parse API response: ${parseError.message}`));
          }
        });
      });
      
      req.on('error', (error) => {
        reject(new Error(`HTTP request failed: ${error.message}`));
      });
      
      req.write(postData);
      req.end();
    });

    return result;

  } catch (error) {
    console.error('❌ Entity extraction API error:', error);
    return {
      success: false,
      error: `Failed to extract entities: ${error.message}`
    };
  }
});

ipcMain.handle('process-grobid', async (event, filePath) => {
  try {
    console.log('Main process: Starting GROBID API call for:', filePath);
    
    const response = await fetch('http://localhost:8001/api/process-grobid', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        file_path: filePath
      })
    });

    console.log('Main process: Response status:', response.status);

    if (!response.ok) {
      return {
        success: false,
        error: `Backend API error: ${response.status} ${response.statusText}`
      };
    }

    const result = await response.json();
    console.log('Main process: GROBID processing successful');
    return result;
  } catch (error) {
    console.error('Main process: GROBID processing error:', error);
    return {
      success: false,
      error: `Failed to process with GROBID: ${error.message}`
    };
  }
});


// App event handlers
app.whenReady().then(() => {
  createWindow();
  createMenu();
  
  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

// Security: Prevent new window creation
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event, navigationUrl) => {
    event.preventDefault();
    shell.openExternal(navigationUrl);
  });
});