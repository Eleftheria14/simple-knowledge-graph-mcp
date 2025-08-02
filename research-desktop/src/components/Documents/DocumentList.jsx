import React from 'react';
import { 
  HiClipboardList, 
  HiSearch, 
  HiX, 
  HiChevronDown, 
  HiChevronRight, 
  HiTrash,
  HiDocumentText,
  HiUsers,
  HiTag,
  HiBookOpen,
  HiPhotograph,
  HiTable,
  HiCalendar,
  HiClock,
  HiFolder,
  HiAcademicCap,
  HiInformationCircle,
  HiDocument
} from 'react-icons/hi';

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
                      {/* Publication Metadata */}
                      <div className="bg-gray-800 p-4 rounded-lg">
                        <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
                          <HiAcademicCap className="w-4 h-4 mr-2" />
                          Publication Information
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs">
                          {result.journal && (
                            <div>
                              <span className="text-gray-400">Journal:</span>
                              <span className="ml-2 text-blue-300 font-medium">{result.journal}</span>
                            </div>
                          )}
                          {result.timestamp && (
                            <div>
                              <span className="text-gray-400">Processed:</span>
                              <span className="ml-2 text-green-300">{new Date(result.timestamp).toLocaleString()}</span>
                            </div>
                          )}
                          {result.content_length && (
                            <div>
                              <span className="text-gray-400">Content Length:</span>
                              <span className="ml-2 text-yellow-300">{result.content_length.toLocaleString()} characters</span>
                            </div>
                          )}
                          {(result.references_count || (result.references && result.references.length > 0)) && (
                            <div>
                              <span className="text-gray-400">References:</span>
                              <span className="ml-2 text-blue-300">{result.references_count || result.references.length} citations</span>
                            </div>
                          )}
                          {(result.figures_count || (result.figures && result.figures.length > 0)) && (
                            <div>
                              <span className="text-gray-400">Figures:</span>
                              <span className="ml-2 text-red-300">{result.figures_count || result.figures.length} figures</span>
                            </div>
                          )}
                          {(result.tables_count || (result.tables && result.tables.length > 0)) && (
                            <div>
                              <span className="text-gray-400">Tables:</span>
                              <span className="ml-2 text-green-300">{result.tables_count || result.tables.length} tables</span>
                            </div>
                          )}
                          {result.fileName && (
                            <div>
                              <span className="text-gray-400">File:</span>
                              <span className="ml-2 text-gray-300 font-mono">{result.fileName}</span>
                            </div>
                          )}
                          {result.originalFileName && result.fileRenamed && (
                            <div>
                              <span className="text-gray-400">Original:</span>
                              <span className="ml-2 text-gray-400 font-mono text-xs">{result.originalFileName}</span>
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Abstract */}
                      {result.abstract && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                            <HiDocumentText className="w-4 h-4 mr-2" />
                            Abstract
                          </h4>
                          <div className="bg-gray-800 p-4 rounded-lg">
                            <p className="text-sm text-gray-300 leading-relaxed">
                              {result.abstract}
                            </p>
                          </div>
                        </div>
                      )}

                      {/* Authors */}
                      {result.authors && result.authors.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                            <HiUsers className="w-4 h-4 mr-2" />
                            Authors ({result.authors.length})
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {result.authors.map((author, index) => (
                              <span 
                                key={index}
                                className="bg-purple-900/30 text-purple-300 px-3 py-1 rounded-full text-xs font-medium"
                              >
                                {typeof author === 'object' ? (author.name || author) : author}
                                {typeof author === 'object' && author.affiliation && (
                                  <span className="text-purple-400 ml-1">({author.affiliation})</span>
                                )}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Keywords */}
                      {result.keywords && result.keywords.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                            <HiTag className="w-4 h-4 mr-2" />
                            Keywords ({result.keywords.length})
                          </h4>
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
                            const wordCount = fullText.split(/\s+/).filter(word => word.length > 0).length;
                            const avgWordsPerPage = 500; // Academic paper average
                            const estimatedPages = Math.ceil(wordCount / avgWordsPerPage);
                            
                            return (
                              <>
                                <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
                                  <HiDocument className="w-4 h-4 mr-2" />
                                  Complete Document Text
                                </h4>
                                
                                {/* Text Statistics */}
                                <div className="bg-gray-800 p-3 rounded-lg mb-3">
                                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                                    <div>
                                      <span className="text-gray-400">Characters:</span>
                                      <span className="ml-2 text-yellow-300 font-medium">{fullText.length.toLocaleString()}</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-400">Words:</span>
                                      <span className="ml-2 text-blue-300 font-medium">{wordCount.toLocaleString()}</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-400">Est. Pages:</span>
                                      <span className="ml-2 text-green-300 font-medium">~{estimatedPages}</span>
                                    </div>
                                    <div>
                                      <span className="text-gray-400">Source:</span>
                                      <span className="ml-2 text-purple-300 font-medium">GROBID</span>
                                    </div>
                                  </div>
                                </div>
                                
                                {/* Full Text Content */}
                                <div className="bg-gray-800 p-4 rounded-lg max-h-[600px] overflow-y-auto border border-gray-700">
                                  <div className="text-xs text-gray-400 mb-2 sticky top-0 bg-gray-800 pb-2 border-b border-gray-700 flex items-center">
                                    <HiBookOpen className="w-3 h-3 mr-1" />
                                    Structured Academic Text (Extracted from PDF)
                                  </div>
                                  <pre className="text-xs text-gray-300 whitespace-pre-wrap leading-relaxed font-mono">
                                    {fullText}
                                  </pre>
                                </div>
                                
                                <div className="mt-2 text-xs text-gray-500 bg-gray-900 p-2 rounded flex items-start">
                                  <HiInformationCircle className="w-3 h-3 mr-1 mt-0.5 flex-shrink-0" />
                                  <span>
                                    <strong>About this text:</strong> This is the complete structured content extracted by GROBID 
                                    from the original PDF, preserving academic formatting, sections, and citations.
                                  </span>
                                </div>
                              </>
                            );
                          })()}
                        </div>
                      )}

                      {/* Complete References List */}
                      {result.references && result.references.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                            <HiBookOpen className="w-4 h-4 mr-2" />
                            Bibliography & References ({result.references.length})
                          </h4>
                          <div className="bg-gray-800 p-4 rounded-lg max-h-96 overflow-y-auto space-y-3">
                            {result.references.map((ref, idx) => (
                              <div key={idx} className="text-xs text-gray-300 border-l-4 border-blue-500 pl-4 pb-3 bg-gray-900/50 rounded-r p-3">
                                <div className="font-medium text-blue-300 mb-2 text-sm">
                                  <span className="bg-blue-900/30 px-2 py-1 rounded mr-2">[{idx + 1}]</span>
                                  {ref.title || 'Untitled Reference'}
                                </div>
                                
                                {ref.authors && ref.authors.length > 0 && (
                                  <div className="text-gray-300 mb-2 flex flex-wrap gap-1">
                                    <span className="font-medium text-purple-400">Authors:</span>
                                    <div className="flex flex-wrap gap-1">
                                      {ref.authors.map((author, authIdx) => (
                                        <span key={authIdx} className="bg-purple-900/30 text-purple-300 px-2 py-1 rounded text-xs">
                                          {author}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}
                                
                                <div className="text-gray-400 space-y-1">
                                  {ref.journal && (
                                    <div>
                                      <span className="font-medium text-blue-400">Journal:</span> 
                                      <span className="italic ml-1 text-blue-300">{ref.journal}</span>
                                    </div>
                                  )}
                                  
                                  <div className="flex flex-wrap gap-4 text-xs">
                                    {ref.year && (
                                      <span>
                                        <span className="font-medium text-green-400">Year:</span> 
                                        <span className="ml-1 text-green-300">{ref.year}</span>
                                      </span>
                                    )}
                                    {ref.volume && (
                                      <span>
                                        <span className="font-medium text-yellow-400">Vol:</span> 
                                        <span className="ml-1 text-yellow-300">{ref.volume}</span>
                                      </span>
                                    )}
                                    {ref.pages && (
                                      <span>
                                        <span className="font-medium text-red-400">Pages:</span> 
                                        <span className="ml-1 text-red-300">{ref.pages}</span>
                                      </span>
                                    )}
                                    {ref.doi && (
                                      <span>
                                        <span className="font-medium text-indigo-400">DOI:</span> 
                                        <span className="ml-1 text-indigo-300 font-mono">{ref.doi}</span>
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Figures and Tables */}
                      {((result.figures && result.figures.length > 0) || (result.tables && result.tables.length > 0)) && (
                        <div>
                          <h4 className="text-sm font-medium text-gray-300 mb-2 flex items-center">
                            <HiPhotograph className="w-4 h-4 mr-2" />
                            Document Structure
                          </h4>
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {/* Figures */}
                            {result.figures && result.figures.length > 0 && (
                              <div>
                                <h5 className="font-medium mb-3 text-red-300 flex items-center">
                                  <HiPhotograph className="w-4 h-4 mr-2" />
                                  Figures ({result.figures.length})
                                </h5>
                                <div className="bg-gray-800 p-4 rounded-lg max-h-80 overflow-y-auto space-y-4">
                                  {result.figures.map((figure, idx) => (
                                    <div key={idx} className="text-xs text-gray-300 border-l-4 border-red-500 pl-4 pb-3">
                                      <div className="font-medium text-red-300 mb-2 text-sm">Figure {idx + 1}</div>
                                      {figure.caption && (
                                        <div className="text-gray-300 leading-relaxed mb-2 bg-gray-900 p-2 rounded">
                                          {figure.caption}
                                        </div>
                                      )}
                                      {figure.type && (
                                        <div className="text-gray-500 text-xs">
                                          <span className="bg-red-900/30 px-2 py-1 rounded">Type: {figure.type}</span>
                                        </div>
                                      )}
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                            
                            {/* Tables */}
                            {result.tables && result.tables.length > 0 && (
                              <div>
                                <h5 className="font-medium mb-3 text-green-300 flex items-center">
                                  <HiTable className="w-4 h-4 mr-2" />
                                  Tables ({result.tables.length})
                                </h5>
                                <div className="bg-gray-800 p-4 rounded-lg max-h-80 overflow-y-auto space-y-4">
                                  {result.tables.map((table, idx) => (
                                    <div key={idx} className="text-xs text-gray-300 border-l-4 border-green-500 pl-4 pb-3">
                                      <div className="font-medium text-green-300 mb-2 text-sm">Table {idx + 1}</div>
                                      {table.caption && (
                                        <div className="text-gray-300 mb-3 leading-relaxed bg-gray-900 p-2 rounded">
                                          {table.caption}
                                        </div>
                                      )}
                                      {table.content && (
                                        <div className="text-gray-300 mt-2 p-3 bg-gray-900 rounded font-mono text-xs leading-relaxed border border-gray-700">
                                          <div className="text-green-400 mb-1 font-sans">Table Content:</div>
                                          <pre className="whitespace-pre-wrap">{table.content}</pre>
                                        </div>
                                      )}
                                      {table.type && (
                                        <div className="text-gray-500 text-xs mt-2">
                                          <span className="bg-green-900/30 px-2 py-1 rounded">Type: {table.type}</span>
                                        </div>
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