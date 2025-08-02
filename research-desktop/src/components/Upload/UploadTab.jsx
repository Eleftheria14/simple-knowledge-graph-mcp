import React, { useState, useEffect } from 'react';
import { HiSearch, HiFilter, HiX } from 'react-icons/hi';
import UploadArea from './UploadArea';
import ProcessingProgress from './ProcessingProgress';
import DocumentList from '../Documents/DocumentList';

const UploadTab = ({
  // Connection & Status
  grobidConnected,
  
  // Upload Area Props
  dragActive,
  isProcessing,
  handleDrop,
  handleDragOver,
  handleDragEnter,
  handleDragLeave,
  handleDragEnd,
  handleFileSelect,
  
  // Processing Props
  batchProgress,
  currentFileIndex,
  batchQueue,
  processingSteps,
  processingStep,
  processingProgress,
  
  // Results & Actions
  results,
  filteredResults,
  expandedResults,
  toggleResultExpanded,
  resetFilters,
  onDeleteDocument
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // all, success, error
  const [sortBy, setSortBy] = useState('newest'); // newest, oldest, title, authors
  const [showAdvancedFilters, setShowAdvancedFilters] = useState(false);
  const [citationFilters, setCitationFilters] = useState({
    author: '',
    journal: '',
    yearFrom: '',
    yearTo: '',
    hasReferences: 'all' // all, yes, no
  });
  const [localFilteredResults, setLocalFilteredResults] = useState(filteredResults);

  // Update local filtered results when filteredResults change
  useEffect(() => {
    let filtered = [...filteredResults];

    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(doc => 
        doc.title?.toLowerCase().includes(query) ||
        doc.authors?.some(author => author.toLowerCase().includes(query)) ||
        doc.abstract?.toLowerCase().includes(query) ||
        doc.keywords?.some(keyword => keyword.toLowerCase().includes(query))
      );
    }

    // Apply citation-based filters
    if (citationFilters.author.trim()) {
      const authorQuery = citationFilters.author.toLowerCase();
      filtered = filtered.filter(doc => 
        doc.authors?.some(author => author.toLowerCase().includes(authorQuery))
      );
    }

    if (citationFilters.journal.trim()) {
      const journalQuery = citationFilters.journal.toLowerCase();
      filtered = filtered.filter(doc => 
        doc.metadata?.journal?.toLowerCase().includes(journalQuery) ||
        doc.journal?.toLowerCase().includes(journalQuery)
      );
    }

    if (citationFilters.yearFrom || citationFilters.yearTo) {
      filtered = filtered.filter(doc => {
        const docYear = doc.timestamp ? new Date(doc.timestamp).getFullYear() : null;
        if (!docYear) return false;
        
        const yearFrom = citationFilters.yearFrom ? parseInt(citationFilters.yearFrom) : 0;
        const yearTo = citationFilters.yearTo ? parseInt(citationFilters.yearTo) : 9999;
        
        return docYear >= yearFrom && docYear <= yearTo;
      });
    }

    if (citationFilters.hasReferences !== 'all') {
      filtered = filtered.filter(doc => {
        const hasRefs = doc.references && doc.references.length > 0;
        return citationFilters.hasReferences === 'yes' ? hasRefs : !hasRefs;
      });
    }

    // Apply status filter
    if (filterStatus !== 'all') {
      filtered = filtered.filter(doc => 
        filterStatus === 'success' ? doc.success : !doc.success
      );
    }

    // Apply sorting
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'oldest':
          return new Date(a.timestamp) - new Date(b.timestamp);
        case 'title':
          return (a.title || '').localeCompare(b.title || '');
        case 'authors':
          const aAuthor = a.authors?.[0] || '';
          const bAuthor = b.authors?.[0] || '';
          return aAuthor.localeCompare(bAuthor);
        case 'newest':
        default:
          return new Date(b.timestamp) - new Date(a.timestamp);
      }
    });

    setLocalFilteredResults(filtered);
  }, [filteredResults, searchQuery, filterStatus, sortBy, citationFilters]);

  const clearFilters = () => {
    setSearchQuery('');
    setFilterStatus('all');
    setSortBy('newest');
    setCitationFilters({
      author: '',
      journal: '',
      yearFrom: '',
      yearTo: '',
      hasReferences: 'all'
    });
    setShowAdvancedFilters(false);
    resetFilters();
  };

  const hasFilters = searchQuery.trim() || filterStatus !== 'all' || sortBy !== 'newest' ||
    citationFilters.author.trim() || citationFilters.journal.trim() || 
    citationFilters.yearFrom || citationFilters.yearTo || citationFilters.hasReferences !== 'all';

  const hasCitationFilters = citationFilters.author.trim() || citationFilters.journal.trim() || 
    citationFilters.yearFrom || citationFilters.yearTo || citationFilters.hasReferences !== 'all';

  return (
    <div className="p-8">
      {/* Upload Area with Beautiful Centered Processing */}
      <UploadArea
        dragActive={dragActive}
        grobidConnected={grobidConnected}
        isProcessing={isProcessing}
        handleDrop={handleDrop}
        handleDragOver={handleDragOver}
        handleDragEnter={handleDragEnter}
        handleDragLeave={handleDragLeave}
        handleDragEnd={handleDragEnd}
        handleFileSelect={handleFileSelect}
        results={results}
        // Processing props for beautiful centered display
        batchProgress={batchProgress}
        currentFileIndex={currentFileIndex}
        batchQueue={batchQueue}
        processingSteps={processingSteps}
        processingStep={processingStep}
        processingProgress={processingProgress}
      />

      {/* Processing Progress - Full Screen Display */}
      <ProcessingProgress
        isProcessing={isProcessing}
        batchProgress={batchProgress}
        currentFileIndex={currentFileIndex}
        batchQueue={batchQueue}
        processingSteps={processingSteps}
        processingStep={processingStep}
      />

      {/* Document Filtering */}
      {results.length > 0 && (
        <div className="max-w-4xl mx-auto mb-6">
          <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
              {/* Search Bar */}
              <div className="flex-1 relative">
                <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search by title, authors, abstract, or keywords..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                />
              </div>

              {/* Status Filter */}
              <div className="flex items-center space-x-2">
                <HiFilter className="w-4 h-4 text-gray-400" />
                <select
                  value={filterStatus}
                  onChange={(e) => setFilterStatus(e.target.value)}
                  className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                >
                  <option value="all">All Documents</option>
                  <option value="success">Successfully Parsed</option>
                  <option value="error">Processing Errors</option>
                </select>
              </div>

              {/* Sort Options */}
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-400">Sort:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                >
                  <option value="newest">Newest First</option>
                  <option value="oldest">Oldest First</option>
                  <option value="title">Title A-Z</option>
                  <option value="authors">Author A-Z</option>
                </select>
              </div>

              {/* Advanced Filters Toggle */}
              <button
                onClick={() => setShowAdvancedFilters(!showAdvancedFilters)}
                className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                  showAdvancedFilters || hasCitationFilters
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
                }`}
              >
                <HiFilter className="w-4 h-4" />
                <span>Citation Filters</span>
                {hasCitationFilters && (
                  <span className="bg-blue-400 text-white rounded-full px-1.5 py-0.5 text-xs font-bold">●</span>
                )}
              </button>

              {/* Clear Filters */}
              {hasFilters && (
                <button
                  onClick={clearFilters}
                  className="flex items-center space-x-1 px-3 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm transition-colors"
                >
                  <HiX className="w-4 h-4" />
                  <span>Clear</span>
                </button>
              )}
            </div>

            {/* Advanced Citation Filters */}
            {showAdvancedFilters && (
              <div className="mt-4 pt-4 border-t border-gray-600">
                <h4 className="text-sm font-medium text-gray-300 mb-3">Citation-Based Filters</h4>
                <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-4 gap-4">
                  {/* Author Filter */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Author</label>
                    <input
                      type="text"
                      placeholder="Search by author name..."
                      value={citationFilters.author}
                      onChange={(e) => setCitationFilters(prev => ({ ...prev, author: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                  </div>

                  {/* Journal Filter */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Journal/Venue</label>
                    <input
                      type="text"
                      placeholder="Search by journal name..."
                      value={citationFilters.journal}
                      onChange={(e) => setCitationFilters(prev => ({ ...prev, journal: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                    />
                  </div>

                  {/* Year Range */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">Year Range</label>
                    <div className="flex space-x-2">
                      <input
                        type="number"
                        placeholder="From"
                        value={citationFilters.yearFrom}
                        onChange={(e) => setCitationFilters(prev => ({ ...prev, yearFrom: e.target.value }))}
                        className="w-full px-2 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                        min="1900"
                        max="2030"
                      />
                      <input
                        type="number"
                        placeholder="To"
                        value={citationFilters.yearTo}
                        onChange={(e) => setCitationFilters(prev => ({ ...prev, yearTo: e.target.value }))}
                        className="w-full px-2 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                        min="1900"
                        max="2030"
                      />
                    </div>
                  </div>

                  {/* References Filter */}
                  <div>
                    <label className="block text-xs text-gray-400 mb-1">References</label>
                    <select
                      value={citationFilters.hasReferences}
                      onChange={(e) => setCitationFilters(prev => ({ ...prev, hasReferences: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 text-sm"
                    >
                      <option value="all">All Documents</option>
                      <option value="yes">With References</option>
                      <option value="no">No References</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {/* Results Summary */}
            <div className="mt-3 flex items-center justify-between text-sm text-gray-400">
              <span>
                Showing {localFilteredResults.length} of {results.length} documents
              </span>
              {hasFilters && (
                <div className="flex items-center space-x-3">
                  {hasCitationFilters && (
                    <span className="text-purple-400 text-xs">
                      Citation filters active
                    </span>
                  )}
                  <span className="text-blue-400">
                    {localFilteredResults.length !== filteredResults.length ? 'Filtered' : 'Active filters'}
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Document List */}
      <DocumentList
        results={results}
        filteredResults={localFilteredResults}
        expandedResults={expandedResults}
        toggleResultExpanded={toggleResultExpanded}
        resetFilters={clearFilters}
        onDeleteDocument={onDeleteDocument}
      />
    </div>
  );
};

export default UploadTab;