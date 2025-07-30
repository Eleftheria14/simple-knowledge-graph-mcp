/**
 * Knowledge Graph Batch Processor
 * 
 * Adapted from DocsGPT's BatchProcessor for direct integration with
 * our n8n + MCP knowledge graph system.
 */
import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';

interface ProcessingResult {
  filename: string;
  success: boolean;
  entities_count?: number;
  relationships_count?: number;
  chunks_count?: number;
  processing_time?: number;
  error?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  document_id?: string;
  neo4j_entities?: number;
  chromadb_vectors?: number;
}

interface BatchProcessorProps {
  onClose?: () => void;
  onBatchComplete?: (results: ProcessingResult[]) => void;
  webhookUrl?: string; // Allow custom webhook URL
  maxFiles?: number;
}

export const KnowledgeGraphBatchProcessor: React.FC<BatchProcessorProps> = ({ 
  onClose, 
  onBatchComplete,
  webhookUrl = 'http://localhost:5678/webhook/docsgpt-document-upload',
  maxFiles = 10
}) => {
  const [files, setFiles] = useState<File[]>([]);
  const [processing, setProcessing] = useState(false);
  const [results, setResults] = useState<ProcessingResult[]>([]);
  const [currentlyProcessing, setCurrentlyProcessing] = useState<string | null>(null);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Filter for supported file types
    const supportedFiles = acceptedFiles.filter(file => {
      const extension = file.name.toLowerCase().split('.').pop();
      return ['pdf', 'docx', 'txt', 'md', 'doc'].includes(extension || '');
    });
    
    // Limit total files
    const availableSlots = maxFiles - files.length;
    const filesToAdd = supportedFiles.slice(0, availableSlots);
    
    setFiles(prev => [...prev, ...filesToAdd]);
    
    // Initialize results for new files
    const newResults: ProcessingResult[] = filesToAdd.map(file => ({
      filename: file.name,
      success: false,
      status: 'pending'
    }));
    
    setResults(prev => [...prev, ...newResults]);
  }, [files.length, maxFiles]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'application/msword': ['.doc'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md']
    },
    multiple: true,
    maxFiles: maxFiles
  });

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
    setResults(prev => prev.filter((_, i) => i !== index));
  };

  const processDocument = async (file: File, index: number): Promise<ProcessingResult> => {
    const startTime = Date.now();
    
    try {
      const formData = new FormData();
      formData.append('document', file);
      formData.append('payload', JSON.stringify({
        filename: file.name,
        batch_processing: true,
        batch_index: index + 1,
        batch_total: files.length,
        user_id: 'knowledge_graph_batch',
        metadata: {
          upload_date: new Date().toISOString(),
          source: 'knowledge_graph_batch_processor',
          original_name: file.name,
          processor_version: '2.0'
        }
      }));

      const response = await fetch(webhookUrl, {
        method: 'POST',
        body: formData,
        headers: {
          // Remove Content-Type to let browser set it with boundary for FormData
        }
      });

      const processingTime = Date.now() - startTime;

      if (response.ok) {
        const result = await response.json();
        
        return {
          filename: file.name,
          success: true,
          status: 'completed',
          entities_count: result.entities_count || 0,
          relationships_count: result.relationships_count || 0,
          chunks_count: result.chunks_count || 0,
          processing_time: processingTime,
          document_id: result.document_id,
          neo4j_entities: result.neo4j_entities,
          chromadb_vectors: result.chromadb_vectors
        };
      } else {
        const errorText = await response.text();
        return {
          filename: file.name,
          success: false,
          status: 'failed',
          error: `HTTP ${response.status}: ${errorText}`,
          processing_time: processingTime
        };
      }
    } catch (error) {
      return {
        filename: file.name,
        success: false,
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown error',
        processing_time: Date.now() - startTime
      };
    }
  };

  const processBatch = async () => {
    if (files.length === 0) return;
    
    setProcessing(true);
    const updatedResults: ProcessingResult[] = [...results];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      setCurrentlyProcessing(file.name);
      
      // Update status to processing
      updatedResults[i] = { ...updatedResults[i], status: 'processing' };
      setResults([...updatedResults]);

      // Process the document
      const result = await processDocument(file, i);
      updatedResults[i] = result;
      setResults([...updatedResults]);
      
      // Add a small delay between files to prevent overwhelming the server
      if (i < files.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    setCurrentlyProcessing(null);
    setProcessing(false);
    
    // Callback with results
    if (onBatchComplete) {
      onBatchComplete(updatedResults);
    }
  };

  const clearAll = () => {
    setFiles([]);
    setResults([]);
  };

  const getStatusIcon = (status: ProcessingResult['status']) => {
    switch (status) {
      case 'pending':
        return '⏳';
      case 'processing':
        return '🔄';
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      default:
        return '❓';
    }
  };

  const getStatusColor = (status: ProcessingResult['status']) => {
    switch (status) {
      case 'pending':
        return 'text-gray-500';
      case 'processing':
        return 'text-blue-500';
      case 'completed':
        return 'text-green-500';
      case 'failed':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const completedCount = results.filter(r => r.status === 'completed').length;
  const failedCount = results.filter(r => r.status === 'failed').length;
  const totalEntities = results.reduce((sum, r) => sum + (r.entities_count || 0), 0);
  const totalRelationships = results.reduce((sum, r) => sum + (r.relationships_count || 0), 0);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
          🧠 Knowledge Graph Batch Processor
        </h2>
        {onClose && (
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ✕
          </button>
        )}
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50 dark:bg-blue-900/20'
            : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
        }`}
      >
        <input {...getInputProps()} />
        <div className="text-gray-600 dark:text-gray-300">
          {isDragActive ? (
            <p>📁 Drop the files here...</p>
          ) : (
            <div>
              <p className="text-lg mb-2">📄 Drag & drop documents here, or click to select</p>
              <p className="text-sm text-gray-500">
                Supports PDF, DOCX, TXT, MD files • Max {maxFiles} files
              </p>
            </div>
          )}
        </div>
      </div>

      {/* File List */}
      {files.length > 0 && (
        <div className="mt-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Files to Process ({files.length})
            </h3>
            <div className="flex gap-2">
              <button
                onClick={clearAll}
                disabled={processing}
                className="px-3 py-1 text-sm text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 disabled:opacity-50"
              >
                Clear All
              </button>
              <button
                onClick={processBatch}
                disabled={processing || files.length === 0}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {processing ? '🔄 Processing...' : '🚀 Start Processing'}
              </button>
            </div>
          </div>

          {/* Results Summary */}
          {results.some(r => r.status !== 'pending') && (
            <div className="mb-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-green-600 font-medium">✅ Completed: {completedCount}</span>
                </div>
                <div>
                  <span className="text-red-600 font-medium">❌ Failed: {failedCount}</span>
                </div>
                <div>
                  <span className="text-blue-600 font-medium">🏷️ Entities: {totalEntities}</span>
                </div>
                <div>
                  <span className="text-purple-600 font-medium">🔗 Relations: {totalRelationships}</span>
                </div>
              </div>
            </div>
          )}

          {/* File List */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {files.map((file, index) => {
              const result = results[index];
              const isCurrentlyProcessing = currentlyProcessing === file.name;
              
              return (
                <div
                  key={`${file.name}-${index}`}
                  className={`flex items-center justify-between p-3 rounded-lg border ${
                    isCurrentlyProcessing 
                      ? 'border-blue-300 bg-blue-50 dark:bg-blue-900/20' 
                      : 'border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-700'
                  }`}
                >
                  <div className="flex items-center gap-3 flex-1">
                    <span className="text-lg">
                      {result ? getStatusIcon(result.status) : '⏳'}
                    </span>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900 dark:text-white truncate">
                        {file.name}
                      </p>
                      <div className="flex gap-4 text-xs text-gray-500 dark:text-gray-400">
                        <span>{(file.size / 1024).toFixed(1)} KB</span>
                        {result?.entities_count !== undefined && (
                          <span>🏷️ {result.entities_count} entities</span>
                        )}
                        {result?.relationships_count !== undefined && (
                          <span>🔗 {result.relationships_count} relations</span>
                        )}
                        {result?.processing_time && (
                          <span>⏱️ {(result.processing_time / 1000).toFixed(1)}s</span>
                        )}
                      </div>
                      {result?.error && (
                        <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                          {result.error}
                        </p>
                      )}
                    </div>
                  </div>
                  
                  {!processing && (
                    <button
                      onClick={() => removeFile(index)}
                      className="text-gray-400 hover:text-red-500 ml-2"
                    >
                      🗑️
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Processing Status */}
      {currentlyProcessing && (
        <div className="mt-4 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
          <p className="text-blue-800 dark:text-blue-200">
            🔄 Currently processing: <span className="font-medium">{currentlyProcessing}</span>
          </p>
        </div>
      )}
    </div>
  );
};