import React from 'react';
import { HiLightBulb, HiCheck, HiClock } from 'react-icons/hi';

const EntityExtractionTab = ({
  extractingEntities,
  entityResults,
  extractionConfig,
  setExtractionConfig,
  selectedDocuments,
  results,
  selectAllDocuments,
  clearDocumentSelection,
  startEntityExtraction,
  toggleDocumentSelection,
  currentExtractionDoc,
  extractionLogs,
  promptTemplates,
  chunkingStrategy,
  setChunkingStrategy
}) => {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
          <HiLightBulb className="w-6 h-6 text-green-400" />
          <span>Entity Extraction</span>
        </h2>

        {/* Extraction Configuration */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Prompt Template</label>
              <select 
                value={extractionConfig}
                onChange={(e) => setExtractionConfig(e.target.value)}
                className="w-full max-w-md px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-green-500"
              >
                {Object.entries(promptTemplates).map(([key, template]) => (
                  <option key={key} value={key}>
                    {template.name}
                  </option>
                ))}
              </select>
              
              {/* Template Preview */}
              {promptTemplates[extractionConfig] && (
                <div className="mt-3 p-3 bg-gray-800 rounded border border-gray-700">
                  <div className="text-xs text-gray-400 mb-2">Template Preview:</div>
                  <div className="text-sm text-gray-300">
                    <div><strong>Confidence Threshold:</strong> {promptTemplates[extractionConfig].confidenceThreshold}</div>
                    <div><strong>Temperature:</strong> {promptTemplates[extractionConfig].temperature}</div>
                    <div className="mt-2 text-xs text-gray-400 line-clamp-3">
                      {promptTemplates[extractionConfig].systemPrompt.substring(0, 200)}...
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Chunking Strategy */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Document Chunking Strategy</label>
              <select 
                value={chunkingStrategy}
                onChange={(e) => setChunkingStrategy(e.target.value)}
                className="w-full max-w-md px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-green-500"
              >
                <option value="no_chunking">No Chunking - Process entire document (large context models)</option>
                <option value="simple_truncate">Simple Truncate - Take first 4000 characters (fastest)</option>
                <option value="recursive_character">Recursive Character - Smart paragraph and sentence splits</option>
                <option value="token_aware">Token Aware - Precise token control for LLM processing</option>
                <option value="sentence_aware">Sentence Aware - Never break sentences (NLTK)</option>
                <option value="hierarchical">Hierarchical - Respect paper sections (recommended for academic papers)</option>
                <option value="sliding_window">Sliding Window - Overlapping chunks, no lost content</option>
                <option value="semantic_topic">Semantic Topic - Split on topic changes</option>
                <option value="multi_level">Multi-Level - Maximum coverage (comprehensive analysis)</option>
                <option value="paragraph_based">Paragraph Based - Preserve paragraph structure</option>
                <option value="content_aware">Content Aware - Preserve figures, tables, and equations</option>
              </select>
              
              {/* Chunking Strategy Info */}
              <div className="mt-3 p-3 bg-gray-800 rounded border border-gray-700">
                <div className="text-xs text-gray-400 mb-2">Strategy Info:</div>
                <div className="text-sm text-gray-300">
                  {chunkingStrategy === 'no_chunking' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-purple-400">Variable</span></div>
                      <div><strong>Coverage:</strong> <span className="text-green-400">Complete</span></div>
                      <div className="text-xs text-green-400 mt-1">Best for large context models (32k+ tokens) - processes entire document at once</div>
                    </div>
                  )}
                  {chunkingStrategy === 'simple_truncate' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-green-400">High Speed</span></div>
                      <div><strong>Coverage:</strong> <span className="text-yellow-400">Limited</span></div>
                      <div className="text-xs text-yellow-400 mt-1">Note: Only processes first 4000 characters - may miss important content</div>
                    </div>
                  )}
                  {chunkingStrategy === 'recursive_character' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-green-400">Fast</span></div>
                      <div><strong>Coverage:</strong> <span className="text-blue-400">Good</span></div>
                      <div className="text-xs text-green-400 mt-1">Balanced approach - processes paragraphs, then sentences, then words</div>
                    </div>
                  )}
                  {chunkingStrategy === 'hierarchical' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-blue-400">Moderate</span></div>
                      <div><strong>Coverage:</strong> <span className="text-green-400">Excellent</span></div>
                      <div className="text-xs text-green-400 mt-1">Recommended: Respects Abstract, Methods, Results, Discussion sections</div>
                    </div>
                  )}
                  {chunkingStrategy === 'multi_level' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-red-400">Comprehensive</span></div>
                      <div><strong>Coverage:</strong> <span className="text-green-400">Maximum</span></div>
                      <div className="text-xs text-blue-400 mt-1">Processes at multiple granularities - most comprehensive analysis</div>
                    </div>
                  )}
                  {chunkingStrategy === 'content_aware' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-blue-400">Moderate</span></div>
                      <div><strong>Coverage:</strong> <span className="text-green-400">Excellent</span></div>
                      <div className="text-xs text-blue-400 mt-1">Preserves figures, tables, equations - optimal for technical papers</div>
                    </div>
                  )}
                  {chunkingStrategy === 'token_aware' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-green-400">Fast</span></div>
                      <div><strong>Coverage:</strong> <span className="text-blue-400">Good</span></div>
                      <div className="text-xs text-blue-400 mt-1">Precise token control for optimal LLM processing</div>
                    </div>
                  )}
                  {chunkingStrategy === 'sentence_aware' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-blue-400">Moderate</span></div>
                      <div><strong>Coverage:</strong> <span className="text-blue-400">Good</span></div>
                      <div className="text-xs text-green-400 mt-1">Uses NLTK to ensure sentences are never broken</div>
                    </div>
                  )}
                  {chunkingStrategy === 'sliding_window' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-blue-400">Moderate</span></div>
                      <div><strong>Coverage:</strong> <span className="text-green-400">Excellent</span></div>
                      <div className="text-xs text-green-400 mt-1">Overlapping chunks ensure no content is lost</div>
                    </div>
                  )}
                  {chunkingStrategy === 'semantic_topic' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-blue-400">Moderate</span></div>
                      <div><strong>Coverage:</strong> <span className="text-blue-400">Good</span></div>
                      <div className="text-xs text-blue-400 mt-1">Intelligently splits on topic boundaries</div>
                    </div>
                  )}
                  {chunkingStrategy === 'paragraph_based' && (
                    <div>
                      <div><strong>Performance:</strong> <span className="text-green-400">Fast</span></div>
                      <div><strong>Coverage:</strong> <span className="text-blue-400">Good</span></div>
                      <div className="text-xs text-green-400 mt-1">Maintains natural paragraph structure and flow</div>
                    </div>
                  )}
                  {!['no_chunking', 'simple_truncate', 'recursive_character', 'hierarchical', 'multi_level', 'content_aware', 'token_aware', 'sentence_aware', 'sliding_window', 'semantic_topic', 'paragraph_based'].includes(chunkingStrategy) && (
                    <div className="text-xs text-gray-400">
                      Advanced chunking strategy selected
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Document Selection Controls */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-300">
                  {selectedDocuments.size} of {results.filter(doc => doc.success).length} documents selected
                </span>
                <button 
                  onClick={selectAllDocuments}
                  className="text-sm px-3 py-1 bg-blue-600 rounded hover:bg-blue-700"
                >
                  Select All
                </button>
                <button 
                  onClick={clearDocumentSelection}
                  className="text-sm px-3 py-1 bg-gray-600 rounded hover:bg-gray-700"
                >
                  Clear All
                </button>
              </div>
              <button 
                onClick={startEntityExtraction}
                disabled={selectedDocuments.size === 0}
                className={`px-6 py-3 rounded-lg font-medium flex items-center space-x-2 ${
                  selectedDocuments.size === 0 
                    ? 'bg-gray-600 cursor-not-allowed' 
                    : 'bg-green-600 hover:bg-green-700'
                }`}
              >
                <HiLightBulb className="w-5 h-5" />
                <span>Start Extraction</span>
              </button>
            </div>

            {/* Document List */}
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {results.filter(doc => doc.success).map((doc) => (
                <div 
                  key={doc.id}
                  className={`p-3 border rounded cursor-pointer transition-colors ${
                    selectedDocuments.has(doc.id)
                      ? 'border-green-500 bg-green-900/20'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                  onClick={() => toggleDocumentSelection(doc.id)}
                >
                  <div className="flex items-start space-x-3">
                    <div className={`w-5 h-5 rounded border-2 flex items-center justify-center mt-0.5 ${
                      selectedDocuments.has(doc.id)
                        ? 'border-green-500 bg-green-500'
                        : 'border-gray-400'
                    }`}>
                      {selectedDocuments.has(doc.id) && (
                        <HiCheck className="w-3 h-3 text-white" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium truncate">{doc.title}</h3>
                      <div className="flex items-center space-x-3 text-xs text-gray-400 mt-1">
                        {doc.authors && doc.authors.length > 0 && (
                          <span className="truncate">
                            {doc.authors.slice(0, 2).join(', ')}
                            {doc.authors.length > 2 && ` et al.`}
                          </span>
                        )}
                        {(doc.metadata?.journal || doc.journal || doc.venue || doc.publication || doc.source) && (
                          <span className="truncate text-gray-400">
                            {doc.metadata?.journal || doc.journal || doc.venue || doc.publication || doc.source}
                          </span>
                        )}
                        <span>{doc.timestamp ? new Date(doc.timestamp).getFullYear() : new Date().getFullYear()}</span>
                        <span>{(doc.content_length || doc.fullText?.length || doc.content?.length || doc.full_text?.length || 0).toLocaleString()} chars</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
      </div>
    </div>
  );
};

export default EntityExtractionTab;