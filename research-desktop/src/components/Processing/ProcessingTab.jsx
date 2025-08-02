import React, { useEffect, useRef, useState, useCallback } from 'react';
import { HiClock, HiCheck, HiBan, HiChevronDown, HiChevronRight, HiDatabase, HiCog, HiDocumentText, HiLightBulb } from 'react-icons/hi';
import TokenStream from './TokenStream';

// Component for displaying LLM tokens in expandable section
const LLMTokensDisplay = ({ tokens, tokenCount }) => {
  const safeTokenCount = typeof tokenCount === 'number' && !isNaN(tokenCount) ? tokenCount : (tokens || '').length;
  const safeTokens = tokens || '';
  
  return (
    <div className="mt-3">
      <details className="group">
        <summary className="cursor-pointer text-xs text-blue-400 hover:text-blue-300 flex items-center">
          <span className="mr-1">📝</span>
          <span>View LLM Response ({safeTokenCount} chars)</span>
          <span className="ml-1 transform group-open:rotate-90 transition-transform">▶</span>
        </summary>
        <div className="mt-2 bg-black/50 rounded-lg p-3 max-h-64 overflow-y-auto border border-blue-600/30">
          <div className="font-mono text-xs text-blue-300 whitespace-pre-wrap leading-relaxed">
            {safeTokens}
          </div>
        </div>
      </details>
    </div>
  );
};

// Clean document results list
const ExtractionResultsList = ({ results }) => {
  const [expandedResults, setExpandedResults] = useState(new Set());
  const [documentEntities, setDocumentEntities] = useState(new Map());
  const [loadingEntities, setLoadingEntities] = useState(new Set());

  // Debug logging
  console.log('🔍 ExtractionResultsList received results:', results.map(r => ({
    title: r.document_title,
    has_tokens: !!r.llm_tokens,
    token_count: r.token_count,
    entities: r.entities_found,
    relationships: r.relationships_found
  })));

  const toggleResultExpanded = async (index) => {
    const result = results[index];
    
    setExpandedResults(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
        // Fetch entities when expanding
        if (result.document_id && !documentEntities.has(result.document_id)) {
          fetchDocumentEntities(result.document_id);
        }
      }
      return newSet;
    });
  };

  const fetchDocumentEntities = async (documentId) => {
    if (loadingEntities.has(documentId)) return;
    
    setLoadingEntities(prev => new Set([...prev, documentId]));
    
    try {
      const response = await fetch(`http://localhost:8001/api/documents/${documentId}/entities`);
      const data = await response.json();
      
      if (data.success) {
        setDocumentEntities(prev => new Map([...prev, [documentId, data]]));
      } else {
        console.error('Failed to fetch entities:', data);
      }
    } catch (error) {
      console.error('Error fetching document entities:', error);
    } finally {
      setLoadingEntities(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
    }
  };

  return (
    <div className="space-y-3">
      {results.map((result, index) => {
        const isExpanded = expandedResults.has(index);
        return (
          <div key={index} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors">
            {/* Header - Always Visible */}
            <div 
              className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
              onClick={() => toggleResultExpanded(index)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      result.success ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium truncate">
                        {result.document_title || 'Unknown Document'}
                      </h3>
                      <div className="text-xs text-gray-400 mt-1">
                        <span className="mr-4">{result.entities_found || 0} entities</span>
                        <span className="mr-4">{result.relationships_found || 0} relationships</span>
                        <span>{result.extraction_mode || 'unknown'} mode</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  <span className="bg-green-900 text-green-300 px-2 py-1 rounded text-xs">
                    ✓ Extracted
                  </span>
                  
                  <button className="p-1 hover:bg-gray-600 rounded transition-colors">
                    {isExpanded ? (
                      <HiChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <HiChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                  </button>
                </div>
              </div>
            </div>

            {/* Expanded Details */}
            {isExpanded && (
              <div className="border-t border-gray-700 bg-gray-850 p-6 space-y-6">
                
                {/* LLM Response - Primary section */}
                {result.llm_tokens ? (
                  <div className="bg-gray-800 p-4 rounded-lg border border-blue-600/20">
                    <h4 className="text-sm font-medium text-blue-300 mb-3 flex items-center">
                      <HiLightBulb className="w-4 h-4 mr-2" />
                      LLM Response ({result.token_count || result.llm_tokens.length} characters)
                    </h4>
                    <div className="bg-black/50 rounded-lg p-4 max-h-64 overflow-y-auto border border-blue-600/30">
                      <div className="font-mono text-xs text-blue-300 whitespace-pre-wrap leading-relaxed">
                        {result.llm_tokens}
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="bg-gray-800 p-4 rounded-lg border border-yellow-600/20">
                    <h4 className="text-sm font-medium text-yellow-300 mb-2 flex items-center">
                      <HiLightBulb className="w-4 h-4 mr-2" />
                      LLM Response
                    </h4>
                    <div className="text-xs text-gray-400">
                      No LLM response captured. This may be from an older extraction before token streaming was implemented.
                    </div>
                  </div>
                )}

                {/* Extracted Knowledge */}
                <div className="bg-gray-800 p-4 rounded-lg border border-green-600/20">
                  <h4 className="text-sm font-medium text-green-300 mb-3 flex items-center">
                    <HiDatabase className="w-4 h-4 mr-2" />
                    Extracted Knowledge
                  </h4>
                  
                  {loadingEntities.has(result.document_id) ? (
                    <div className="flex items-center text-xs text-gray-400">
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-green-400 mr-2"></div>
                      Loading entities from Neo4j...
                    </div>
                  ) : documentEntities.has(result.document_id) ? (
                    <div className="space-y-4">
                      {(() => {
                        const entityData = documentEntities.get(result.document_id);
                        const entities = entityData?.entities || [];
                        const relationships = entityData?.relationships || [];
                        
                        return (
                          <>
                            {/* Summary Stats */}
                            <div className="grid grid-cols-2 gap-4 text-xs">
                              <div className="bg-gray-700 p-2 rounded">
                                <span className="text-gray-400">Entities:</span>
                                <span className="ml-2 text-blue-300 font-medium">{entities.length}</span>
                              </div>
                              <div className="bg-gray-700 p-2 rounded">
                                <span className="text-gray-400">Relationships:</span>
                                <span className="ml-2 text-purple-300 font-medium">{relationships.length}</span>
                              </div>
                            </div>

                            {/* Entities */}
                            {entities.length > 0 && (
                              <div>
                                <h5 className="text-xs font-medium text-blue-300 mb-2">
                                  Entities (showing top {Math.min(entities.length, 8)})
                                </h5>
                                <div className="space-y-1 max-h-48 overflow-y-auto">
                                  {entities.slice(0, 8).map((entity, idx) => (
                                    <div key={idx} className="flex items-center justify-between text-xs bg-gray-700 p-2 rounded">
                                      <div className="flex-1 min-w-0">
                                        <div className="font-medium text-blue-300 truncate">
                                          {entity.name}
                                        </div>
                                        <div className="text-gray-400 text-xs">
                                          {entity.type}
                                        </div>
                                      </div>
                                      <div className="ml-2 flex-shrink-0">
                                        <span className="bg-green-900 text-green-300 px-2 py-1 rounded text-xs">
                                          {Math.round((entity.confidence || 0) * 100)}%
                                        </span>
                                      </div>
                                    </div>
                                  ))}
                                  {entities.length > 8 && (
                                    <div className="text-xs text-gray-500 text-center py-2 bg-gray-700 rounded">
                                      ... and {entities.length - 8} more entities
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}
                            
                            {/* Relationships */}
                            {relationships.length > 0 && (
                              <div>
                                <h5 className="text-xs font-medium text-purple-300 mb-2">
                                  Relationships (showing top {Math.min(relationships.length, 4)})
                                </h5>
                                <div className="space-y-1 max-h-32 overflow-y-auto">
                                  {relationships.slice(0, 4).map((rel, idx) => (
                                    <div key={idx} className="text-xs bg-gray-700 p-2 rounded">
                                      <div className="flex items-center space-x-2 mb-1">
                                        <span className="text-blue-300 truncate font-medium">
                                          {rel.source_name || 'Unknown'}
                                        </span>
                                        <span className="text-gray-400">→</span>
                                        <span className="text-purple-300 font-medium">
                                          {rel.relationship_type}
                                        </span>
                                        <span className="text-gray-400">→</span>
                                        <span className="text-green-300 truncate font-medium">
                                          {rel.target_name || 'Unknown'}
                                        </span>
                                      </div>
                                      {rel.context && (
                                        <div className="text-gray-500 text-xs truncate">
                                          Context: {rel.context}
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                  {relationships.length > 4 && (
                                    <div className="text-xs text-gray-500 text-center py-1 bg-gray-700 rounded">
                                      ... and {relationships.length - 4} more relationships
                                    </div>
                                  )}
                                </div>
                              </div>
                            )}

                            {entities.length === 0 && relationships.length === 0 && (
                              <div className="text-xs text-gray-500 text-center py-4">
                                No entities or relationships found in Neo4j for this document
                              </div>
                            )}
                          </>
                        );
                      })()}
                    </div>
                  ) : (
                    <div className="text-xs text-gray-400 bg-gray-700 p-3 rounded">
                      Expand this card to load extracted entities and relationships from Neo4j
                    </div>
                  )}
                </div>

                {/* Processing Details */}
                <div className="bg-gray-800 p-4 rounded-lg border border-gray-600/20">
                  <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
                    <HiCog className="w-4 h-4 mr-2" />
                    Processing Details
                  </h4>
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div className="bg-gray-700 p-2 rounded">
                      <span className="text-gray-400">Mode:</span>
                      <span className="ml-2 text-green-300 font-medium">{result.extraction_mode || 'Unknown'}</span>
                    </div>
                    <div className="bg-gray-700 p-2 rounded">
                      <span className="text-gray-400">Chunking:</span>
                      <span className="ml-2 text-yellow-300 font-medium">{result.chunking_strategy || 'Unknown'}</span>
                    </div>
                  </div>
                  {result.message && (
                    <div className="mt-3 p-3 bg-gray-700 rounded text-xs text-gray-300">
                      <strong>Result:</strong> {result.message}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

const ProcessingTab = ({
  extractingEntities,
  entityResults,
  currentExtractionDoc,
  extractionLogs,
  chunkingStrategy,
  llmTokens,
  llmStreaming
}) => {
  const tokenStreamRef = useRef(null);
  const [forceUpdate, setForceUpdate] = useState(0);
  
  // Force re-render when tokens change
  const forceRerender = useCallback(() => {
    setForceUpdate(prev => prev + 1);
  }, []);
  
  // Auto-scroll token stream to bottom when new tokens arrive
  useEffect(() => {
    if (tokenStreamRef.current && llmStreaming) {
      tokenStreamRef.current.scrollTop = tokenStreamRef.current.scrollHeight;
    }
  }, [llmTokens, llmStreaming, forceUpdate]);
  
  // Set up a polling mechanism to force re-renders during streaming
  useEffect(() => {
    let interval;
    if (llmStreaming || extractingEntities) {
      interval = setInterval(() => {
        forceRerender();
      }, 100); // Force re-render every 100ms during streaming
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [llmStreaming, extractingEntities, forceRerender]);
  
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
          <HiClock className="w-6 h-6 text-yellow-400" />
          <span>Entity Extraction Processing</span>
        </h2>

        {!extractingEntities && entityResults.length === 0 && (
          <div className="text-center py-12 text-gray-400">
            <div className="text-4xl mb-4">
              <HiBan className="w-16 h-16 mx-auto" />
            </div>
            <p className="text-lg mb-2">No extraction in progress</p>
            <p className="text-sm">Go to "Extract Entities" to start processing documents</p>
          </div>
        )}

        {/* Live Processing (only during extraction) */}
        {extractingEntities && (
          <div className="bg-gray-800 rounded-lg p-6 border border-gray-700 mb-6">
            <div className="flex items-center space-x-3 mb-4">
              <HiClock className="w-6 h-6 text-blue-400 animate-spin" />
              <h3 className="text-lg font-medium">Extracting Entities...</h3>
            </div>
            
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-sm">
                <span>Processing documents with Groq LLM</span>
                <span className="text-blue-400">Please wait...</span>
              </div>
              
              <div className="bg-gray-700 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full w-1/3 animate-pulse"></div>
              </div>
            </div>

            {currentExtractionDoc && (
              <div className="mb-4 p-3 bg-gray-900 rounded">
                <p className="text-sm text-gray-300">
                  <strong>Current:</strong> {currentExtractionDoc}
                </p>
              </div>
            )}

            {/* Live Token Stream */}
            <TokenStream 
              isActive={true} 
              persistedTokens={llmTokens}
              isStreaming={llmStreaming}
            />
          </div>
        )}

        {/* Results (after extraction) */}
        {entityResults.length > 0 && !extractingEntities && (
          <div className="space-y-4">
            <h3 className="text-lg font-medium flex items-center space-x-2">
              <HiCheck className="w-5 h-5 text-green-400" />
              <span>Extraction Results</span>
              <span className="text-sm text-gray-400">({entityResults.length} documents processed)</span>
            </h3>
            
            <ExtractionResultsList 
              results={entityResults}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default ProcessingTab;