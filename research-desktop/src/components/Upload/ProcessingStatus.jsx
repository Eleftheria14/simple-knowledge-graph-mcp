import React from 'react';
import { HiCheckCircle, HiXCircle, HiClock, HiDocument, HiCollection } from 'react-icons/hi';

const ProcessingStatus = ({ 
  grobidConnected, 
  isProcessing, 
  batchProgress,
  currentFileIndex,
  batchQueue,
  results,
  processingSteps 
}) => {
  // Processing state
  if (isProcessing) {
    return (
      <div className="mb-6">
        <div className="flex items-center justify-center">
          <div className="bg-blue-900/20 border border-blue-500/30 text-blue-400 px-6 py-4 rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <HiClock className="w-5 h-5 animate-spin" />
              <span className="text-sm font-medium">
                {batchProgress.total > 1 ? 'Processing Batch' : 'Processing Document'}
              </span>
            </div>
            
            {batchProgress.total > 1 && (
              <div className="space-y-2">
                <div className="flex justify-between text-xs">
                  <span>File {currentFileIndex + 1} of {batchProgress.total}</span>
                  <span>{batchProgress.completed} completed</span>
                </div>
                <div className="bg-blue-800 rounded-full h-2">
                  <div 
                    className="bg-blue-400 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${(batchProgress.completed / batchProgress.total) * 100}%` }}
                  />
                </div>
                {batchQueue[currentFileIndex] && (
                  <div className="text-xs text-blue-300 truncate">
                    {batchQueue[currentFileIndex].path.split('/').pop()}
                  </div>
                )}
              </div>
            )}
            
            {/* Current Step */}
            <div className="mt-3 space-y-1">
              {processingSteps.map((step) => (
                <div key={step.id} className="flex items-center space-x-2 text-xs">
                  <div className={`w-3 h-3 rounded-full ${
                    step.status === 'completed' ? 'bg-green-400' :
                    step.status === 'in_progress' ? 'bg-blue-400 animate-pulse' :
                    step.status === 'failed' ? 'bg-red-400' : 'bg-gray-600'
                  }`} />
                  <span className={
                    step.status === 'completed' ? 'text-green-300' :
                    step.status === 'in_progress' ? 'text-blue-300' :
                    step.status === 'failed' ? 'text-red-300' : 'text-gray-400'
                  }>
                    {step.label}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Results state
  if (results.length > 0) {
    const successCount = results.filter(r => r.success).length;
    const errorCount = results.length - successCount;
    const totalChars = results.reduce((sum, r) => sum + (r.content_length || 0), 0);

    return (
      <div className="mb-6">
        <div className="flex items-center justify-center">
          <div className="bg-green-900/20 border border-green-500/30 text-green-400 px-6 py-4 rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <HiCheckCircle className="w-5 h-5" />
              <span className="text-sm font-medium">Processing Complete</span>
            </div>
            
            <div className="grid grid-cols-3 gap-4 text-xs">
              <div className="text-center">
                <div className="flex items-center justify-center space-x-1 mb-1">
                  <HiDocument className="w-4 h-4" />
                  <span className="font-medium">{successCount}</span>
                </div>
                <div className="text-green-300">Documents Parsed</div>
              </div>
              
              {errorCount > 0 && (
                <div className="text-center">
                  <div className="flex items-center justify-center space-x-1 mb-1">
                    <HiXCircle className="w-4 h-4 text-red-400" />
                    <span className="font-medium text-red-400">{errorCount}</span>
                  </div>
                  <div className="text-red-300">Errors</div>
                </div>
              )}
              
              <div className="text-center">
                <div className="flex items-center justify-center space-x-1 mb-1">
                  <HiCollection className="w-4 h-4" />
                  <span className="font-medium">{(totalChars / 1000).toFixed(0)}K</span>
                </div>
                <div className="text-green-300">Characters</div>
              </div>
            </div>
            
            {successCount > 0 && (
              <div className="mt-3 pt-3 border-t border-green-500/20">
                <div className="text-xs text-green-300 text-center">
                  Ready for entity extraction → Click "2. Extract Entities" tab
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Default connection state
  return (
    <div className="mb-6 flex items-center">
      <div className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
        grobidConnected 
          ? 'bg-green-900/20 border-green-500/30 text-green-400' 
          : 'bg-red-900/20 border-red-500/30 text-red-400'
      }`}>
        {grobidConnected ? (
          <HiCheckCircle className="w-5 h-5" />
        ) : (
          <HiXCircle className="w-5 h-5" />
        )}
        <span className="text-sm font-medium">
          GROBID Server {grobidConnected ? 'Connected' : 'Disconnected'}
        </span>
        {grobidConnected && (
          <span className="text-xs text-green-300 ml-2">
            Ready to process PDFs
          </span>
        )}
      </div>
    </div>
  );
};

export default ProcessingStatus;