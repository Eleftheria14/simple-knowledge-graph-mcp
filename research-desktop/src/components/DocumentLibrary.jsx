import React, { useState, useMemo } from 'react';
import PDFViewer from './PDFViewer';

const DocumentLibrary = ({ documents, onDocumentSelect, onDocumentDelete }) => {
  const [sortBy, setSortBy] = useState('processedAt');
  const [sortOrder, setSortOrder] = useState('desc');
  const [filterStatus, setFilterStatus] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDocs, setSelectedDocs] = useState(new Set());
  const [previewDocument, setPreviewDocument] = useState(null);

  const filteredAndSortedDocs = useMemo(() => {
    let filtered = documents;

    // Filter by search term
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filtered = filtered.filter(doc => 
        doc.name.toLowerCase().includes(term) ||
        (doc.authors && doc.authors.some(author => author.toLowerCase().includes(term))) ||
        (doc.title && doc.title.toLowerCase().includes(term))
      );
    }

    // Filter by status
    if (filterStatus !== 'all') {
      filtered = filtered.filter(doc => doc.status === filterStatus);
    }

    // Sort
    filtered.sort((a, b) => {
      let aVal = a[sortBy];
      let bVal = b[sortBy];

      if (sortBy === 'processedAt') {
        aVal = new Date(aVal);
        bVal = new Date(bVal);
      }

      if (sortBy === 'name' || sortBy === 'title') {
        aVal = aVal?.toString().toLowerCase() || '';
        bVal = bVal?.toString().toLowerCase() || '';
      }

      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [documents, searchTerm, filterStatus, sortBy, sortOrder]);

  const handleSort = (field) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const handleSelectDoc = (docId) => {
    const newSelected = new Set(selectedDocs);
    if (newSelected.has(docId)) {
      newSelected.delete(docId);
    } else {
      newSelected.add(docId);
    }
    setSelectedDocs(newSelected);
  };

  const handleSelectAll = () => {
    if (selectedDocs.size === filteredAndSortedDocs.length) {
      setSelectedDocs(new Set());
    } else {
      setSelectedDocs(new Set(filteredAndSortedDocs.map(doc => doc.id)));
    }
  };

  const handleBulkDelete = () => {
    if (selectedDocs.size === 0) return;
    
    const confirmDelete = window.confirm(
      `Are you sure you want to delete ${selectedDocs.size} document(s)? This will also remove all associated entities and relationships.`
    );
    
    if (confirmDelete) {
      selectedDocs.forEach(docId => onDocumentDelete(docId));
      setSelectedDocs(new Set());
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'processed': return '✅';
      case 'processing': return '⏳';
      case 'failed': return '❌';
      case 'pending': return '⏸️';
      default: return '❓';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'processed': return 'status-success';
      case 'processing': return 'status-processing';
      case 'failed': return 'status-error';
      case 'pending': return 'status-warning';
      default: return 'bg-gray-900 text-gray-300';
    }
  };

  const getSortIcon = (field) => {
    if (sortBy !== field) return '↕️';
    return sortOrder === 'asc' ? '↑' : '↓';
  };

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Header */}
      <div className="p-6 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">📚 Document Library</h2>
          
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-400">
              {filteredAndSortedDocs.length} of {documents.length} documents
            </span>
            
            {selectedDocs.size > 0 && (
              <button
                onClick={handleBulkDelete}
                className="btn btn-danger text-sm"
              >
                🗑️ Delete ({selectedDocs.size})
              </button>
            )}
          </div>
        </div>
        
        {/* Filters and Search */}
        <div className="flex items-center space-x-4">
          <div className="flex-1">
            <input
              type="text"
              placeholder="Search documents, authors, titles..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input w-full"
            />
          </div>
          
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="input"
          >
            <option value="all">All Status</option>
            <option value="processed">Processed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
            <option value="pending">Pending</option>
          </select>
        </div>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-hidden">
        {filteredAndSortedDocs.length > 0 ? (
          <div className="overflow-auto h-full">
            <table className="w-full">
              <thead className="sticky top-0 bg-slate-800 border-b border-slate-700">
                <tr className="text-left">
                  <th className="p-4 w-12">
                    <input
                      type="checkbox"
                      checked={selectedDocs.size === filteredAndSortedDocs.length && filteredAndSortedDocs.length > 0}
                      onChange={handleSelectAll}
                      className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                    />
                  </th>
                  
                  <th className="p-4 w-12">Status</th>
                  
                  <th 
                    className="p-4 cursor-pointer hover:bg-slate-700 transition-colors"
                    onClick={() => handleSort('name')}
                  >
                    <div className="flex items-center space-x-2">
                      <span>Document</span>
                      <span className="text-xs">{getSortIcon('name')}</span>
                    </div>
                  </th>
                  
                  <th 
                    className="p-4 cursor-pointer hover:bg-slate-700 transition-colors"
                    onClick={() => handleSort('processedAt')}
                  >
                    <div className="flex items-center space-x-2">
                      <span>Processed</span>
                      <span className="text-xs">{getSortIcon('processedAt')}</span>
                    </div>
                  </th>
                  
                  <th className="p-4">Entities</th>
                  <th className="p-4">Citations</th>
                  <th className="p-4 w-12">Actions</th>
                </tr>
              </thead>
              
              <tbody>
                {filteredAndSortedDocs.map((doc) => (
                  <tr 
                    key={doc.id}
                    className={`border-b border-slate-700 hover:bg-slate-800 transition-colors ${
                      selectedDocs.has(doc.id) ? 'bg-slate-800' : ''
                    }`}
                  >
                    <td className="p-4">
                      <input
                        type="checkbox"
                        checked={selectedDocs.has(doc.id)}
                        onChange={() => handleSelectDoc(doc.id)}
                        className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                      />
                    </td>
                    
                    <td className="p-4">
                      <div className={`status-indicator ${getStatusColor(doc.status)}`}>
                        {getStatusIcon(doc.status)}
                      </div>
                    </td>
                    
                    <td className="p-4">
                      <div className="cursor-pointer" onClick={() => setPreviewDocument(doc)}>
                        <div className="font-medium text-white hover:text-blue-400 transition-colors">
                          {doc.title || doc.name}
                        </div>
                        {doc.authors && (
                          <div className="text-sm text-gray-400 mt-1">
                            {doc.authors.slice(0, 3).join(', ')}
                            {doc.authors.length > 3 && ` +${doc.authors.length - 3} more`}
                          </div>
                        )}
                        <div className="text-xs text-gray-500 mt-1">
                          {doc.path.split('/').pop()}
                        </div>
                        {doc.processingMethod && (
                          <div className={`text-xs mt-1 ${
                            doc.processingMethod.includes('GROBID') 
                              ? 'text-green-400' 
                              : 'text-yellow-400'
                          }`}>
                            Method: {doc.processingMethod}
                          </div>
                        )}
                      </div>
                    </td>
                    
                    <td className="p-4 text-gray-300">
                      {doc.processedAt ? new Date(doc.processedAt).toLocaleDateString() : '-'}
                    </td>
                    
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-blue-400 font-medium">{doc.entities || 0}</span>
                        <span className="text-xs text-gray-500">entities</span>
                      </div>
                    </td>
                    
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-green-400 font-medium">{doc.citations || 0}</span>
                        <span className="text-xs text-gray-500">citations</span>
                      </div>
                    </td>
                    
                    <td className="p-4">
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => setPreviewDocument(doc)}
                          className="text-green-400 hover:text-green-300 transition-colors"
                          title="Preview PDF"
                        >
                          📄
                        </button>
                        <button
                          onClick={() => onDocumentSelect(doc)}
                          className="text-blue-400 hover:text-blue-300 transition-colors"
                          title="View details"
                        >
                          👁️
                        </button>
                        <button
                          onClick={() => onDocumentDelete(doc.id)}
                          className="text-red-400 hover:text-red-300 transition-colors"
                          title="Delete document"
                        >
                          🗑️
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              {documents.length === 0 ? (
                <>
                  <div className="text-6xl mb-4">📚</div>
                  <h3 className="text-xl font-semibold mb-2">No Documents Yet</h3>
                  <p>Upload some PDFs to start building your document library</p>
                </>
              ) : (
                <>
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold mb-2">No Matching Documents</h3>
                  <p>Try adjusting your search or filter criteria</p>
                </>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer Summary */}
      {documents.length > 0 && (
        <div className="p-4 bg-slate-800 border-t border-slate-700">
          <div className="flex items-center justify-between text-sm text-gray-400">
            <div className="flex items-center space-x-6">
              <span>Total: {documents.length} documents</span>
              <span>Processed: {documents.filter(d => d.status === 'processed').length}</span>
              <span>Failed: {documents.filter(d => d.status === 'failed').length}</span>
            </div>
            
            <div className="flex items-center space-x-6">
              <span>Total Entities: {documents.reduce((sum, d) => sum + (d.entities || 0), 0)}</span>
              <span>Total Citations: {documents.reduce((sum, d) => sum + (d.citations || 0), 0)}</span>
            </div>
          </div>
        </div>
      )}

      {/* PDF Viewer Modal */}
      {previewDocument && (
        <PDFViewer
          document={previewDocument}
          onClose={() => setPreviewDocument(null)}
        />
      )}
    </div>
  );
};

export default DocumentLibrary;