import React from 'react';
import { HiClipboardList, HiSearch, HiX, HiChevronDown, HiChevronRight, HiTrash } from 'react-icons/hi';

// ACS Citation formatting function
const formatACSCitation = (result) => {
  if (!result) return '';
  
  const authors = result.authors || [];
  const journal = result.metadata?.journal || result.journal || 'Unknown Journal';
  const year = result.timestamp ? new Date(result.timestamp).getFullYear() : new Date().getFullYear();
  const volume = result.metadata?.volume || result.volume || '';
  const pages = result.metadata?.pages || result.pages || '';
  
  // Format authors in ACS style (Last, F. M.)
  let authorString = '';
  if (authors.length === 0) {
    authorString = 'Unknown Author';
  } else if (authors.length === 1) {
    authorString = authors[0];
  } else if (authors.length <= 10) {
    authorString = authors.join('; ');
  } else {
    authorString = authors.slice(0, 10).join('; ') + '; et al.';
  }
  
  // ACS format: Author(s). Journal Year, volume(issue), pages.
  let citation = `${authorString}. ${journal} ${year}`;
  
  if (volume) {
    citation += `, ${volume}`;
    if (pages) {
      citation += `, ${pages}`;
    }
  }
  
  citation += '.';
  return citation;
};

const DocumentList = ({ 
  results, 
  filteredResults, 
  expandedResults, 
  toggleResultExpanded,
  resetFilters,
  onDeleteDocument
}) => {
  if (results.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-4">
          <HiClipboardList className="w-16 h-16 mx-auto" />
        </div>
        <p>No PDFs processed yet</p>
      </div>
    );
  }

  if (filteredResults.length === 0) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="text-4xl mb-4">
          <HiSearch className="w-16 h-16 mx-auto" />
        </div>
        <p>No documents match the current filters</p>
        <button
          onClick={resetFilters}
          className="mt-4 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm flex items-center space-x-2 mx-auto"
        >
          <HiX className="w-4 h-4" />
          <span>Clear Filters</span>
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {filteredResults.map((result) => {
        const isExpanded = expandedResults.has(result.id);
        return (
          <div key={result.id} className="bg-gray-800 rounded-lg border border-gray-700 overflow-hidden hover:border-gray-600 transition-colors">
            {/* Compact Header - Always Visible */}
            <div 
              className="p-4 cursor-pointer hover:bg-gray-750 transition-colors"
              onClick={() => toggleResultExpanded(result.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${
                      result.success ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium truncate">
                        {result.title || 'Untitled Document'}
                      </h3>
                      <div className="text-xs text-gray-400 mt-1 space-y-1">
                        {/* ACS Citation */}
                        <div className="truncate">
                          {formatACSCitation(result)}
                        </div>
                        {/* Metadata */}
                        <div className="flex items-center space-x-3">
                          <span>{new Date(result.timestamp).toLocaleDateString()}</span>
                          <span>{(result.content_length || result.fullText?.length || 0).toLocaleString()} chars</span>
                          {result.references && result.references.length > 0 && (
                            <span>{result.references.length} refs</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-2 ml-4">
                  {result.success && (
                    <div className="flex items-center space-x-2 text-xs">
                      <span className="bg-green-900 text-green-300 px-2 py-1 rounded">
                        ✓ Parsed
                      </span>
                    </div>
                  )}
                  
                  {/* Delete button */}
                  {onDeleteDocument && (
                    <button 
                      onClick={(e) => {
                        e.stopPropagation(); // Prevent triggering the expand/collapse
                        onDeleteDocument(result.id);
                      }}
                      className="p-1 hover:bg-red-600 rounded transition-colors text-gray-400 hover:text-red-300"
                      title="Delete document"
                    >
                      <HiTrash className="w-4 h-4" />
                    </button>
                  )}
                  
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
              <div className="border-t border-gray-700 bg-gray-900">
                <div className="p-4 space-y-4">
                  {/* Error State */}
                  {!result.success ? (
                    <div className="text-red-300">
                      <strong>Error:</strong> {result.error || 'Unknown error'}
                    </div>
                  ) : (
                    <>
                      {/* Abstract */}
                      {result.abstract && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Abstract</h4>
                          <p className="text-sm text-gray-400 leading-relaxed">
                            {result.abstract}
                          </p>
                        </div>
                      )}

                      {/* Authors */}
                      {result.authors && result.authors.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Authors</h4>
                          <div className="flex flex-wrap gap-2">
                            {result.authors.map((author, index) => (
                              <span 
                                key={index}
                                className="bg-purple-900/30 text-purple-300 px-2 py-1 rounded-full text-xs"
                              >
                                {author}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Keywords */}
                      {result.keywords && result.keywords.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Keywords</h4>
                          <div className="flex flex-wrap gap-2">
                            {result.keywords.map((keyword, index) => (
                              <span 
                                key={index}
                                className="bg-blue-900/30 text-blue-300 px-2 py-1 rounded-full text-xs"
                              >
                                {keyword}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Complete Document Text */}
                      {(result.fullText || result.content || result.full_text) && (
                        <div>
                          {(() => {
                            const fullText = result.fullText || result.content || result.full_text || '';
                            return (
                              <>
                                <h4 className="text-sm font-medium text-gray-300 mb-2">
                                  Complete Document Text ({fullText.length.toLocaleString()} characters)
                                  <span className="text-xs text-gray-500 ml-2">- Full paper content from GROBID</span>
                                </h4>
                                <div className="bg-gray-800 p-4 rounded max-h-[600px] overflow-y-auto">
                                  <pre className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed font-mono">
                                    {fullText}
                                  </pre>
                                </div>
                                <div className="mt-2 text-xs text-gray-500 flex items-center space-x-1">
                                  <span>This is the complete structured text extracted by GROBID from the PDF - all {fullText.length.toLocaleString()} characters</span>
                                </div>
                              </>
                            );
                          })()}
                        </div>
                      )}

                      {/* Complete References List */}
                      {result.references && result.references.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Complete References List ({result.references.length})</h4>
                          <div className="bg-gray-800 p-4 rounded max-h-96 overflow-y-auto space-y-2">
                            {result.references.map((ref, idx) => (
                              <div key={idx} className="text-xs text-gray-300 border-l-2 border-blue-500 pl-3 pb-2">
                                <div className="font-medium text-blue-300 mb-1">
                                  [{idx + 1}] {ref.title || 'Untitled Reference'}
                                </div>
                                {ref.authors && ref.authors.length > 0 && (
                                  <div className="text-gray-400 mb-1">
                                    <span className="font-medium">Authors:</span> {ref.authors.join(', ')}
                                  </div>
                                )}
                                <div className="text-gray-400">
                                  {ref.journal && (
                                    <span>
                                      <span className="font-medium">Journal:</span> <span className="italic">{ref.journal}</span>
                                    </span>
                                  )}
                                  {ref.year && (
                                    <span className="ml-3">
                                      <span className="font-medium">Year:</span> {ref.year}
                                    </span>
                                  )}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Figures and Tables */}
                      {((result.figures && result.figures.length > 0) || (result.tables && result.tables.length > 0)) && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2">Document Structure</h4>
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Figures */}
                            {result.figures && result.figures.length > 0 && (
                              <div>
                                <h5 className="font-medium mb-2 text-red-300">Figures ({result.figures.length})</h5>
                                <div className="bg-gray-800 p-3 rounded max-h-64 overflow-y-auto space-y-3">
                                  {result.figures.map((figure, idx) => (
                                    <div key={idx} className="text-xs text-gray-300 border-l-2 border-red-500 pl-2">
                                      <div className="font-medium text-red-300 mb-1">Figure {idx + 1}</div>
                                      {figure.caption && (
                                        <div className="text-gray-400 leading-relaxed">{figure.caption}</div>
                                      )}
                                      {figure.type && (
                                        <div className="text-gray-500 mt-1">Type: {figure.type}</div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Tables */}
                            {result.tables && result.tables.length > 0 && (
                              <div>
                                <h5 className="font-medium mb-2 text-green-300">Tables ({result.tables.length})</h5>
                                <div className="bg-gray-800 p-3 rounded max-h-64 overflow-y-auto space-y-3">
                                  {result.tables.map((table, idx) => (
                                    <div key={idx} className="text-xs text-gray-300 border-l-2 border-green-500 pl-2">
                                      <div className="font-medium text-green-300 mb-1">Table {idx + 1}</div>
                                      {table.caption && (
                                        <div className="text-gray-400 mb-2 leading-relaxed">{table.caption}</div>
                                      )}
                                      {table.content && (
                                        <div className="text-gray-300 mt-2 p-2 bg-gray-900 rounded font-mono text-xs leading-relaxed">
                                          {table.content}
                                        </div>
                                      )}
                                      {table.type && (
                                        <div className="text-gray-500 mt-1">Type: {table.type}</div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      )}
                    </>
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

export default DocumentList;