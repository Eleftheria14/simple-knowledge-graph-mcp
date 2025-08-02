import React, { useState, useRef, useEffect } from 'react';

const SearchInterface = ({ onSearch, onResultSelect }) => {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState('both'); // both, entities, text, citations
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTab, setSelectedTab] = useState('all');
  const searchInputRef = useRef(null);

  // Sample results for demonstration
  const sampleResults = {
    entities: [
      {
        id: 'transformer-arch',
        type: 'entity',
        name: 'Transformer Architecture',
        entityType: 'concept',
        confidence: 0.95,
        documents: ['Attention Is All You Need', 'BERT Paper'],
        relationships: ['uses Attention Mechanism', 'enables BERT']
      },
      {
        id: 'vaswani-author',
        type: 'entity',
        name: 'Ashish Vaswani',
        entityType: 'author',
        confidence: 1.0,
        documents: ['Attention Is All You Need'],
        relationships: ['authored Transformer', 'works at Google']
      }
    ],
    text: [
      {
        id: 'passage-1',
        type: 'text',
        content: 'The Transformer architecture relies entirely on attention mechanisms to draw global dependencies between input and output...',
        document: 'Attention Is All You Need',
        page: 3,
        confidence: 0.89,
        context: 'Abstract and Introduction'
      },
      {
        id: 'passage-2',
        type: 'text',
        content: 'Self-attention, sometimes called intra-attention, is an attention mechanism relating different positions...',
        document: 'Attention Is All You Need',
        page: 4,
        confidence: 0.92,
        context: 'Model Architecture'
      }
    ],
    citations: [
      {
        id: 'citation-1',
        type: 'citation',
        title: 'Attention Is All You Need',
        authors: ['Vaswani, A.', 'Shazeer, N.', 'Parmar, N.'],
        year: 2017,
        venue: 'NIPS',
        citedBy: 85432,
        confidence: 1.0,
        relevance: 0.95
      },
      {
        id: 'citation-2',
        type: 'citation',
        title: 'BERT: Pre-training of Deep Bidirectional Transformers',
        authors: ['Devlin, J.', 'Chang, M.', 'Lee, K.'],
        year: 2018,
        venue: 'arXiv',
        citedBy: 64821,
        confidence: 1.0,
        relevance: 0.88
      }
    ]
  };

  // Focus search input when component mounts or when triggered from menu
  useEffect(() => {
    const handleFocusSearch = () => {
      if (searchInputRef.current) {
        searchInputRef.current.focus();
      }
    };

    if (window.electronAPI) {
      window.electronAPI.onFocusSearch(handleFocusSearch);
    }

    return () => {
      if (window.electronAPI) {
        window.electronAPI.removeAllListeners('focus-search');
      }
    };
  }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    try {
      // TODO: Replace with actual MCP API call
      if (window.electronAPI?.mcpAPI) {
        const mcpResults = await window.electronAPI.mcpAPI.queryKnowledgeGraph(query, {
          includeEntities: searchType === 'both' || searchType === 'entities',
          includeText: searchType === 'both' || searchType === 'text',
          limit: 20
        });
        
        setResults(mcpResults);
      } else {
        // Use sample data for demo
        await new Promise(resolve => setTimeout(resolve, 1000));
        setResults(sampleResults);
      }

      if (onSearch) {
        onSearch(query, { searchType });
      }
    } catch (error) {
      console.error('Search failed:', error);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const getAllResults = () => {
    const allResults = [];
    if (results.entities) allResults.push(...results.entities);
    if (results.text) allResults.push(...results.text);
    if (results.citations) allResults.push(...results.citations);
    return allResults;
  };

  const getFilteredResults = () => {
    switch (selectedTab) {
      case 'entities':
        return results.entities || [];
      case 'text':
        return results.text || [];
      case 'citations':
        return results.citations || [];
      default:
        return getAllResults();
    }
  };

  const getResultIcon = (type) => {
    switch (type) {
      case 'entity': return '🔗';
      case 'text': return '📄';
      case 'citation': return '📚';
      default: return '🔍';
    }
  };

  const getEntityTypeIcon = (entityType) => {
    switch (entityType) {
      case 'concept': return '💡';
      case 'author': return '👤';
      case 'model': return '🤖';
      case 'field': return '🎓';
      default: return '🔗';
    }
  };

  const filteredResults = getFilteredResults();
  const hasResults = getAllResults().length > 0;

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Search Header */}
      <div className="p-6 bg-slate-800 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">🔍 Search Knowledge Graph</h2>
        
        {/* Search Input */}
        <div className="flex space-x-4 mb-4">
          <div className="flex-1">
            <input
              ref={searchInputRef}
              type="text"
              placeholder="Search entities, relationships, or document content..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="input w-full text-lg"
              disabled={isLoading}
            />
          </div>
          
          <select
            value={searchType}
            onChange={(e) => setSearchType(e.target.value)}
            className="input"
            disabled={isLoading}
          >
            <option value="both">All Content</option>
            <option value="entities">Entities Only</option>
            <option value="text">Text Only</option>
            <option value="citations">Citations Only</option>
          </select>
          
          <button
            onClick={handleSearch}
            disabled={isLoading || !query.trim()}
            className="btn btn-primary px-6"
          >
            {isLoading ? <div className="spinner" /> : 'Search'}
          </button>
        </div>
        
        {/* Search Tips */}
        {!hasResults && !isLoading && (
          <div className="text-sm text-gray-400 space-y-1">
            <p>💡 Try searching for: "transformer architecture", "attention mechanism", or author names</p>
            <p>🔗 Results include related entities, text passages, and citation networks</p>
          </div>
        )}
      </div>

      {/* Results Area */}
      <div className="flex-1 overflow-hidden">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="spinner mb-4"></div>
              <p className="text-gray-400">Searching knowledge graph...</p>
            </div>
          </div>
        ) : hasResults ? (
          <div className="flex flex-col h-full">
            {/* Results Tabs */}
            <div className="flex border-b border-slate-700 bg-slate-800">
              {[
                { key: 'all', label: 'All Results', count: getAllResults().length },
                { key: 'entities', label: 'Entities', count: (results.entities || []).length },
                { key: 'text', label: 'Text', count: (results.text || []).length },
                { key: 'citations', label: 'Citations', count: (results.citations || []).length }
              ].map(({ key, label, count }) => (
                <button
                  key={key}
                  onClick={() => setSelectedTab(key)}
                  className={`px-4 py-3 text-sm font-medium transition-colors ${
                    selectedTab === key
                      ? 'text-blue-400 border-b-2 border-blue-400'
                      : 'text-gray-400 hover:text-gray-300'
                  }`}
                >
                  {label} ({count})
                </button>
              ))}
            </div>

            {/* Results List */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {filteredResults.map((result) => (
                <div
                  key={result.id}
                  onClick={() => onResultSelect && onResultSelect(result)}
                  className="card hover:bg-slate-700 cursor-pointer transition-colors"
                >
                  <div className="card-body">
                    <div className="flex items-start space-x-3">
                      <div className="text-2xl">
                        {result.type === 'entity' 
                          ? getEntityTypeIcon(result.entityType)
                          : getResultIcon(result.type)
                        }
                      </div>
                      
                      <div className="flex-1 min-w-0">
                        {result.type === 'entity' && (
                          <div>
                            <h3 className="font-semibold text-white text-lg">{result.name}</h3>
                            <p className="text-sm text-gray-400 capitalize mb-2">
                              {result.entityType} • Confidence: {(result.confidence * 100).toFixed(0)}%
                            </p>
                            {result.relationships && (
                              <div className="mb-2">
                                <p className="text-sm text-gray-300">Relationships:</p>
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {result.relationships.slice(0, 3).map((rel, idx) => (
                                    <span key={idx} className="status-indicator bg-blue-900 text-blue-300 text-xs">
                                      {rel}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            )}
                            <p className="text-xs text-gray-500">
                              Found in: {result.documents.join(', ')}
                            </p>
                          </div>
                        )}
                        
                        {result.type === 'text' && (
                          <div>
                            <p className="text-white mb-2 leading-relaxed">{result.content}</p>
                            <div className="flex items-center space-x-4 text-sm text-gray-400">
                              <span>📄 {result.document}</span>
                              <span>📖 Page {result.page}</span>
                              <span>🎯 {(result.confidence * 100).toFixed(0)}% relevant</span>
                            </div>
                            {result.context && (
                              <p className="text-xs text-gray-500 mt-1">Section: {result.context}</p>
                            )}
                          </div>
                        )}
                        
                        {result.type === 'citation' && (
                          <div>
                            <h3 className="font-semibold text-white text-lg mb-1">{result.title}</h3>
                            <p className="text-gray-300 mb-2">
                              {result.authors.slice(0, 3).join(', ')}
                              {result.authors.length > 3 && ` +${result.authors.length - 3} more`}
                            </p>
                            <div className="flex items-center space-x-4 text-sm text-gray-400">
                              <span>📅 {result.year}</span>
                              <span>📚 {result.venue}</span>
                              <span>📊 {result.citedBy.toLocaleString()} citations</span>
                              <span>🎯 {(result.relevance * 100).toFixed(0)}% relevant</span>
                            </div>
                          </div>
                        )}
                      </div>
                      
                      <div className="text-right">
                        <div className={`status-indicator ${
                          result.confidence > 0.9 ? 'status-success' :
                          result.confidence > 0.7 ? 'status-warning' : 'status-error'
                        }`}>
                          {(result.confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : query && !isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-2">No Results Found</h3>
              <p>Try different keywords or check your search filters</p>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">🔍</div>
              <h3 className="text-xl font-semibold mb-2">Search Your Knowledge Graph</h3>
              <p>Enter keywords to find entities, relationships, and content</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchInterface;