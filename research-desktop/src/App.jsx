import React, { useState, useEffect, useCallback, useRef } from 'react';

// Component imports
import Sidebar from './components/Layout/Sidebar';
import TabNavigation from './components/Layout/TabNavigation';
import UploadTab from './components/Upload/UploadTab';
import EntityExtractionTab from './components/EntityExtraction/EntityExtractionTab';
import KnowledgeGraphTab from './components/KnowledgeGraph/KnowledgeGraphTab';
import PromptTemplateEditor from './components/Settings/PromptTemplateEditor';

function App() {
  // === Core State ===
  const [results, setResults] = useState([]);
  const [currentTab, setCurrentTab] = useState('upload');
  
  // === Sidebar State ===
  const [showSidebar, setShowSidebar] = useState(true);
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [newSessionName, setNewSessionName] = useState('');
  const [creatingSession, setCreatingSession] = useState(false);
  const [deletingSessionId, setDeletingSessionId] = useState(null);

  // === Upload State ===
  const [dragActive, setDragActive] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [grobidConnected, setGrobidConnected] = useState(false);
  const processingQueueRef = useRef([]);
  const [processingSteps, setProcessingSteps] = useState([
    { id: 1, label: 'Reading file', status: 'pending' },
    { id: 2, label: 'Connecting to GROBID', status: 'pending' },
    { id: 3, label: 'Processing with GROBID', status: 'pending' },
    { id: 4, label: 'Parsing results', status: 'pending' },
    { id: 5, label: 'Saving to database', status: 'pending' }
  ]);
  const [processingStep, setProcessingStep] = useState('');
  const [processingProgress, setProcessingProgress] = useState(0);
  const [batchQueue, setBatchQueue] = useState([]);
  const [currentFileIndex, setCurrentFileIndex] = useState(0);
  const [batchProgress, setBatchProgress] = useState({ completed: 0, total: 0 });

  // === Results State ===
  const [expandedResults, setExpandedResults] = useState(new Set());
  const [filteredResults, setFilteredResults] = useState([]);

  // === Entity Extraction State ===
  const [extractingEntities, setExtractingEntities] = useState(false);
  const [entityResults, setEntityResults] = useState([]);
  const [extractionConfig, setExtractionConfig] = useState('academic');
  const [selectedDocuments, setSelectedDocuments] = useState(new Set());
  const [currentExtractionDoc, setCurrentExtractionDoc] = useState('');
  const [extractionLogs, setExtractionLogs] = useState([]);
  const [chunkingStrategy, setChunkingStrategy] = useState('hierarchical');

  // === Prompt Template State ===
  const [promptTemplates, setPromptTemplates] = useState({
    academic: {
      name: 'Academic Research',
      systemPrompt: `You are an expert entity extraction agent specialized in analyzing academic document content.
Your task is to identify and extract structured knowledge from research papers with high accuracy.

Extraction Mode: academic
Domain Context: Academic research paper analysis

Focus on precision and relevance. Only extract entities you are confident about.`,
      
      instructionTemplate: `Analyze the following document content and extract entities and relationships.

TARGET ENTITY TYPES: person, organization, concept, technology, publication
TARGET RELATIONSHIP TYPES: AUTHORED, WORKS_AT, USES, CITES, RELATED_TO, DEVELOPED

EXTRACTION GUIDELINES:
- PERSON: Extract authors, researchers, historical figures. Include affiliation when available.
- ORGANIZATION: Extract companies, universities, institutions. Specify organization type.
- CONCEPT: Extract key technical terms, theories, methodologies. Focus on domain-specific concepts.
- TECHNOLOGY: Extract tools, frameworks, systems, algorithms. Include version info when relevant.
- PUBLICATION: Extract papers, books, journals. Include publication year and venue when available.

RELATIONSHIP GUIDELINES:
- AUTHORED: Person -> Publication (authored/wrote)
- WORKS_AT: Person -> Organization (employment/affiliation)
- USES: Entity -> Technology (utilizes/implements)
- CITES: Publication -> Publication (references/cites)
- RELATED_TO: General conceptual relationship
- DEVELOPED: Person/Organization -> Technology (created/built)

QUALITY REQUIREMENTS:
- Only extract entities with confidence >= 0.8
- Provide clear, standardized entity names
- Include relevant properties for context
- Ensure relationships are meaningful and accurate

ADDITIONAL INSTRUCTIONS:
- Prioritize author names and institutional affiliations
- Extract research methodologies and experimental approaches
- Identify key contributions and novel concepts
- Map citation relationships between publications
- Focus on technical terminology and domain concepts

IMPORTANT: Return ONLY valid JSON format with no additional text, explanations, or markdown formatting. Do not use backticks or code blocks. Start directly with { and end with }.

{
  "entities": [
    {
      "id": "unique_entity_id",
      "name": "Standardized Entity Name", 
      "type": "entity_type",
      "properties": {"key": "value"},
      "confidence": 0.0-1.0
    }
  ],
  "relationships": [
    {
      "source": "source_entity_id",
      "target": "target_entity_id", 
      "type": "RELATIONSHIP_TYPE",
      "context": "Brief explanation of relationship",
      "confidence": 0.0-1.0
    }
  ],
  "metadata": {
    "total_entities": 0,
    "total_relationships": 0,
    "extraction_mode": "academic",
    "confidence_threshold": 0.8
  }
}

Document content:
{content}`,
      
      confidenceThreshold: 0.8,
      temperature: 0.05,
      maxTokens: 4096
    },
    
    business: {
      name: 'Business Analysis',
      systemPrompt: `You are an expert entity extraction agent specialized in analyzing business document content.
Your task is to identify and extract structured knowledge from business documents with high accuracy.

Extraction Mode: business
Domain Context: Business and organizational document analysis

Focus on organizations, people, and business relationships.`,
      
      instructionTemplate: `Analyze the following document content and extract entities and relationships.

TARGET ENTITY TYPES: person, organization, technology, event, metric, location
TARGET RELATIONSHIP TYPES: WORKS_AT, USES, DEVELOPED, PARTICIPATED_IN, LOCATED_AT

EXTRACTION GUIDELINES:
- PERSON: Extract executives, employees, stakeholders. Include role/title when available.
- ORGANIZATION: Extract companies, departments, divisions. Specify organization type and industry.
- TECHNOLOGY: Extract business tools, software, platforms used.
- EVENT: Extract meetings, conferences, product launches, milestones.
- METRIC: Extract KPIs, financial figures, performance indicators.
- LOCATION: Extract offices, markets, regions.

Return ONLY valid JSON format:

{
  "entities": [...],
  "relationships": [...],
  "metadata": {...}
}

Document content:
{content}`,
      
      confidenceThreshold: 0.7,
      temperature: 0.1,
      maxTokens: 4096
    },
    
    technical: {
      name: 'Technical Documentation',
      systemPrompt: `You are an expert entity extraction agent specialized in analyzing technical document content.
Your task is to identify and extract structured knowledge from technical documents with high accuracy.

Extraction Mode: technical
Domain Context: Technical documentation and implementation guides

Focus on technologies, methods, and technical relationships.`,
      
      instructionTemplate: `Analyze the following document content and extract entities and relationships.

TARGET ENTITY TYPES: technology, methodology, concept, person, organization
TARGET RELATIONSHIP TYPES: USES, DEVELOPED, BASED_ON, IMPLEMENTED_WITH

EXTRACTION GUIDELINES:
- TECHNOLOGY: Extract programming languages, frameworks, tools, APIs, databases.
- METHODOLOGY: Extract development practices, algorithms, design patterns.
- CONCEPT: Extract technical concepts, principles, architectural patterns.

Return ONLY valid JSON format:

{
  "entities": [...],
  "relationships": [...],
  "metadata": {...}
}

Document content:
{content}`,
      
      confidenceThreshold: 0.75,
      temperature: 0.1,
      maxTokens: 4096
    }
  });

  // === Effects ===
  useEffect(() => {
    // Wait a moment for backend to be ready, then load sessions
    const initializeApp = async () => {
      // Check if backend is ready
      try {
        const response = await fetch('http://localhost:8001/health');
        if (response.ok) {
          loadSessions();
        } else {
          // If health check fails, still try loading sessions with retries
          setTimeout(() => loadSessions(), 1000);
        }
      } catch (error) {
        console.log('Backend not ready, will retry loading sessions...');
        setTimeout(() => loadSessions(), 1000);
      }
      
      checkGrobidConnection();
    };
    
    initializeApp();
  }, []);

  useEffect(() => {
    if (currentSession) {
      loadSessionDocuments(currentSession.id);
    }
  }, [currentSession]);

  useEffect(() => {
    setFilteredResults(results);
  }, [results]);

  // === Session Management ===
  const loadSessions = async (retryCount = 0, maxRetries = 3) => {
    try {
      const sessionList = await window.electronAPI.api.getSessions();
      setSessions(sessionList || []);
      
      if (sessionList && sessionList.length > 0 && !currentSession) {
        setCurrentSession(sessionList[0]);
      }
    } catch (error) {
      console.error(`Failed to load sessions (attempt ${retryCount + 1}):`, error);
      
      // Retry with exponential backoff if we haven't exceeded max retries
      if (retryCount < maxRetries) {
        const delay = Math.pow(2, retryCount) * 1000; // 1s, 2s, 4s
        console.log(`Retrying in ${delay}ms...`);
        setTimeout(() => loadSessions(retryCount + 1, maxRetries), delay);
      }
    }
  };

  const createNewSession = async (sessionName) => {
    setCreatingSession(true);
    try {
      const result = await window.electronAPI.api.createSession(sessionName);
      if (result.success) {
        await loadSessions();
        setNewSessionName('');
        
        const newSession = { 
          id: result.session?.id || result.session_id, 
          name: result.session?.name || result.name 
        };
        setCurrentSession(newSession);
      }
    } catch (error) {
      console.error('Failed to create session:', error);
    } finally {
      setCreatingSession(false);
    }
  };

  const deleteSession = async (sessionId, deleteDocuments = false) => {
    setDeletingSessionId(sessionId);
    try {
      await window.electronAPI.api.deleteSession(sessionId, deleteDocuments);
      await loadSessions();
      
      if (currentSession?.id === sessionId) {
        const remainingSessions = sessions.filter(s => s.id !== sessionId);
        setCurrentSession(remainingSessions.length > 0 ? remainingSessions[0] : null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
    } finally {
      setDeletingSessionId(null);
    }
  };

  const loadSessionDocuments = async (sessionId) => {
    try {
      console.log('Loading documents for session:', sessionId);
      const documents = await window.electronAPI.api.getSessionDocuments(sessionId);
      console.log('Loaded documents:', documents?.length || 0);
      
      if (documents) {
        setResults(documents);
      } else {
        console.warn('No documents returned for session:', sessionId);
        // Don't clear existing results if API returns null/undefined
        // setResults([]);
      }
    } catch (error) {
      console.error('Failed to load session documents:', error);
      // Don't clear existing results on API failure - keep current state
      // setResults([]);
    }
  };

  // === Upload Handlers ===
  const checkGrobidConnection = async () => {
    try {
      const connected = await window.electronAPI.api.checkGrobidHealth();
      setGrobidConnected(connected);
    } catch (error) {
      setGrobidConnected(false);
    }
  };

  const processFiles = useCallback(async (files, sessionId = null) => {
    // Add files to the queue
    processingQueueRef.current.push(...files);
    
    // Update UI state
    setBatchQueue([...processingQueueRef.current]);
    setBatchProgress(prev => ({ 
      completed: prev.completed, 
      total: prev.completed + processingQueueRef.current.length 
    }));
    
    // If already processing, just return (files are added to queue)
    if (isProcessing) {
      return;
    }
    
    // Start processing
    setIsProcessing(true);
    
    // Initialize progress for the first batch
    setBatchProgress({ 
      completed: 0, 
      total: processingQueueRef.current.length 
    });
    
    // Process all files in queue (including any added while processing)
    let processed = 0;
    while (processingQueueRef.current.length > 0) {
      const fileToProcess = processingQueueRef.current.shift();
      
      // Update UI state
      setBatchQueue([...processingQueueRef.current]);
      setCurrentFileIndex(processed);
      
      // Process the file
      await processFile(fileToProcess.path, sessionId);
      
      processed++;
      setBatchProgress(prev => ({ 
        completed: processed, 
        total: Math.max(prev.total, processed + processingQueueRef.current.length)
      }));
    }
    
    // Reset state when done
    setIsProcessing(false);
    setBatchQueue([]);
    setBatchProgress({ completed: 0, total: 0 });
    setCurrentFileIndex(0);
  }, [isProcessing]);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (!grobidConnected) return;
    
    const files = Array.from(e.dataTransfer.files).filter(
      file => file.type === 'application/pdf'
    );
    
    if (files.length > 0) {
      processFiles(files, currentSession?.id);
    }
  }, [grobidConnected, processFiles, currentSession?.id]);

  const handleDragOver = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragEnter = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);
  
  const handleDragEnd = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  }, []);

  const handleFileSelect = async () => {
    if (!grobidConnected) return;
    
    try {
      const result = await window.electronAPI.showOpenDialog({
        properties: ['openFile', 'multiSelections'],
        filters: [{ name: 'PDF Files', extensions: ['pdf'] }]
      });
      
      if (!result.canceled && result.filePaths.length > 0) {
        const files = result.filePaths.map(path => ({ path }));
        processFiles(files, currentSession?.id);
      }
    } catch (error) {
      console.error('File selection failed:', error);
    }
  };

  const processFile = async (filePath, sessionId = null) => {
    resetProcessingSteps();
    setProcessingProgress(0);
    
    try {
      // Step 1: Reading file
      updateProcessingStep(1, 'in_progress');
      setProcessingStep(`Reading ${filePath.split('/').pop()}...`);
      await new Promise(resolve => setTimeout(resolve, 100));
      updateProcessingStep(1, 'completed');
      
      // Step 2: Connecting to GROBID
      updateProcessingStep(2, 'in_progress');
      setProcessingStep('Connecting to GROBID server...');
      await new Promise(resolve => setTimeout(resolve, 100));
      updateProcessingStep(2, 'completed');
      
      // Step 3: Processing with GROBID (main processing step)
      updateProcessingStep(3, 'in_progress');
      setProcessingStep('Processing with GROBID (this may take a while)...');
      setProcessingProgress(0);
      
      // Simulate GROBID progress
      const progressInterval = setInterval(() => {
        setProcessingProgress(prev => {
          if (prev >= 95) return prev;
          return prev + Math.random() * 5;
        });
      }, 500);
      
      const grobidResult = await window.electronAPI.api.processWithGrobid(filePath);
      
      clearInterval(progressInterval);
      setProcessingProgress(100);
      
      if (!grobidResult.success) {
        updateProcessingStep(3, 'failed');
        throw new Error(grobidResult.error);
      }
      
      updateProcessingStep(3, 'completed');
      updateProcessingStep(4, 'in_progress');
      setProcessingStep('Parsing academic content...');
      await new Promise(resolve => setTimeout(resolve, 200));
      updateProcessingStep(4, 'completed');
      
      // Step 5: Save to database
      updateProcessingStep(5, 'in_progress');
      setProcessingStep('Saving to database...');
      const storeResult = await window.electronAPI.api.savePDFResult(
        grobidResult, 
        sessionId
      );
      
      if (storeResult.success) {
        updateProcessingStep(5, 'completed');
        setProcessingStep('Processing complete!');
        
        // Optimistically add the processed document to current results
        const processedDoc = {
          id: storeResult.document_id,
          fileName: filePath.split('/').pop() || 'Unknown File',
          filePath: filePath,
          title: grobidResult.metadata?.title || 'Untitled Document',
          authors: grobidResult.metadata?.authors?.map(a => a.name || a) || [],
          abstract: grobidResult.metadata?.abstract || '',
          references: grobidResult.metadata?.references || [],
          entities: 0,
          success: true,
          error: '',
          timestamp: new Date().toISOString(),
          fullText: grobidResult.content || '',
          citations: grobidResult.metadata?.references || [],
          figures: grobidResult.metadata?.figures || [],
          tables: grobidResult.metadata?.tables || [],
          keywords: grobidResult.metadata?.keywords || [],
          entityList: []
        };
        
        // Add to current results immediately for better UX
        setResults(prevResults => [processedDoc, ...prevResults]);
        
      } else {
        updateProcessingStep(5, 'failed');
        console.error('Failed to store document:', storeResult.error);
      }
      
    } catch (error) {
      console.error('Processing failed:', error);
    }
  };

  const resetProcessingSteps = () => {
    setProcessingSteps(steps => 
      steps.map(step => ({ ...step, status: 'pending' }))
    );
  };

  const updateProcessingStep = (stepId, status) => {
    setProcessingSteps(steps => 
      steps.map(step => 
        step.id === stepId ? { ...step, status } : step
      )
    );
  };

  // === Entity Extraction Handlers ===
  const selectAllDocuments = () => {
    const successfulDocs = results.filter(doc => doc.success);
    setSelectedDocuments(new Set(successfulDocs.map(doc => doc.id)));
  };

  const clearDocumentSelection = () => {
    setSelectedDocuments(new Set());
  };

  const toggleDocumentSelection = (docId) => {
    setSelectedDocuments(prev => {
      const newSet = new Set(prev);
      if (newSet.has(docId)) {
        newSet.delete(docId);
      } else {
        newSet.add(docId);
      }
      return newSet;
    });
  };

  const startEntityExtraction = async () => {
    console.log('🚀 startEntityExtraction called');
    console.log('📊 selectedDocuments:', selectedDocuments);
    console.log('📋 extractionConfig:', extractionConfig);
    console.log('🔧 promptTemplates:', promptTemplates);
    
    setExtractingEntities(true);
    setEntityResults([]);
    setExtractionLogs([]);
    
    const documentsToProcess = Array.from(selectedDocuments);
    const selectedTemplate = promptTemplates[extractionConfig];
    
    console.log('📄 documentsToProcess:', documentsToProcess);
    console.log('📝 selectedTemplate:', selectedTemplate);
    
    try {
      for (const docId of documentsToProcess) {
        const doc = results.find(r => r.id === docId);
        if (doc) {
          console.log('🔍 Processing document:', doc.title);
          setCurrentExtractionDoc(doc.title || 'Unknown Document');
          
          // Pass the complete template configuration and chunking strategy to the backend
          console.log('📞 Calling electronAPI.api.extractEntities with chunking:', chunkingStrategy);
          const result = await window.electronAPI.api.extractEntities(docId, {
            mode: extractionConfig,
            template: selectedTemplate,
            chunking_strategy: chunkingStrategy
          });
          
          console.log('📥 Received result:', result);
          
          if (result.success) {
            setEntityResults(prev => [...prev, result]);
            console.log('✅ Added result to entityResults');
          } else {
            console.error('❌ Extraction failed:', result.error);
          }
        }
      }
    } catch (error) {
      console.error('Entity extraction failed:', error);
    } finally {
      setExtractingEntities(false);
      setCurrentExtractionDoc('');
    }
  };

  // === Other Handlers ===
  const toggleResultExpanded = (id) => {
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const resetFilters = () => {
    setFilteredResults(results);
  };

  const handleClearAllData = async () => {
    try {
      await window.electronAPI.api.clearAllPDFResults();
      setResults([]);
      setEntityResults([]);
      setSelectedDocuments(new Set());
    } catch (error) {
      console.error('Failed to clear data:', error);
    }
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      // Remove from frontend state immediately for better UX (optimistic update)
      setResults(prev => prev.filter(doc => doc.id !== documentId));
      
      // Remove from selected documents if it was selected
      setSelectedDocuments(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
      
      // Remove from expanded results
      setExpandedResults(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
      
      // Actually delete from backend permanently
      const result = await window.electronAPI.api.deleteDocument(documentId);
      
      if (!result.success) {
        console.error('Backend deletion failed:', result.error);
        // Reload documents on failure to sync state
        if (currentSession) {
          loadSessionDocuments(currentSession.id);
        }
      } else {
        console.log('Document permanently deleted from database:', documentId);
      }
      
    } catch (error) {
      console.error('Failed to delete document:', error);
      // Reload documents on error to sync state
      if (currentSession) {
        loadSessionDocuments(currentSession.id);
      }
    }
  };

  // === Render ===
  return (
    <div className="min-h-screen max-h-screen bg-gray-900 text-white flex">
      {/* Sidebar */}
      <Sidebar
        showSidebar={showSidebar}
        setShowSidebar={setShowSidebar}
        sessions={sessions}
        currentSession={currentSession}
        setCurrentSession={setCurrentSession}
        newSessionName={newSessionName}
        setNewSessionName={setNewSessionName}
        creatingSession={creatingSession}
        createNewSession={createNewSession}
        deletingSessionId={deletingSessionId}
        deleteSession={deleteSession}
      />

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        <div className="p-8">
          {/* Tab Navigation */}
          <TabNavigation
            currentTab={currentTab}
            setCurrentTab={setCurrentTab}
            results={results}
            entityResults={entityResults}
          />

          {/* Tab Content */}
          {currentTab === 'upload' && (
            <UploadTab
              grobidConnected={grobidConnected}
              dragActive={dragActive}
              isProcessing={isProcessing}
              handleDrop={handleDrop}
              handleDragOver={handleDragOver}
              handleDragEnter={handleDragEnter}
              handleDragLeave={handleDragLeave}
              handleDragEnd={handleDragEnd}
              handleFileSelect={handleFileSelect}
              batchProgress={batchProgress}
              currentFileIndex={currentFileIndex}
              batchQueue={batchQueue}
              processingSteps={processingSteps}
              processingStep={processingStep}
              processingProgress={processingProgress}
              results={results}
              filteredResults={filteredResults}
              expandedResults={expandedResults}
              toggleResultExpanded={toggleResultExpanded}
              resetFilters={resetFilters}
              onDeleteDocument={handleDeleteDocument}
            />
          )}

          {currentTab === 'extraction' && (
            <EntityExtractionTab
              extractingEntities={extractingEntities}
              entityResults={entityResults}
              extractionConfig={extractionConfig}
              setExtractionConfig={setExtractionConfig}
              selectedDocuments={selectedDocuments}
              results={results}
              selectAllDocuments={selectAllDocuments}
              clearDocumentSelection={clearDocumentSelection}
              startEntityExtraction={startEntityExtraction}
              toggleDocumentSelection={toggleDocumentSelection}
              currentExtractionDoc={currentExtractionDoc}
              extractionLogs={extractionLogs}
              promptTemplates={promptTemplates}
              chunkingStrategy={chunkingStrategy}
              setChunkingStrategy={setChunkingStrategy}
            />
          )}

          {currentTab === 'knowledge-graph' && (
            <KnowledgeGraphTab />
          )}

          {currentTab === 'settings' && (
            <PromptTemplateEditor 
              templates={promptTemplates}
              setTemplates={setPromptTemplates}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default App;