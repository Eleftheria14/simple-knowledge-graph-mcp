import React from 'react';
import { HiClock, HiCheck, HiX, HiDocumentText, HiDatabase, HiCog } from 'react-icons/hi';

const ProcessingProgress = ({
  isProcessing,
  batchProgress,
  currentFileIndex,
  batchQueue,
  processingSteps,
  processingStep
}) => {
  if (!isProcessing) return null;

  return (
    <div className="max-w-3xl mx-auto mb-8">
      <div className="border border-blue-400 bg-blue-900/20 rounded-lg p-6">
        <div className="w-full">
          <div className="flex items-center justify-center mb-4">
            <HiClock className="w-8 h-8 text-blue-400 animate-spin mr-3" />
            <h3 className="text-lg font-medium text-white">
              {batchProgress.total > 1 ? 'Batch Processing PDFs' : 'Processing PDF'}
            </h3>
          </div>
          
          {/* Main Progress Bar */}
          <div className="mb-4">
            <div className="flex justify-between text-sm text-gray-300 mb-2">
              <span>
                {batchProgress.total > 1 
                  ? `Processing file ${Math.min(currentFileIndex + 1, batchProgress.total)} of ${batchProgress.total}`
                  : 'Processing document'
                }
              </span>
              <span className="font-medium">
                {Math.round((batchProgress.completed / Math.max(batchProgress.total, 1)) * 100)}%
              </span>
            </div>
            <div className="bg-gray-700 rounded-full h-4 mb-3">
              <div 
                className="bg-gradient-to-r from-blue-500 to-green-500 h-4 rounded-full transition-all duration-500 ease-out"
                style={{ width: `${Math.max(5, (batchProgress.completed / Math.max(batchProgress.total, 1)) * 100)}%` }}
              ></div>
            </div>
            {batchQueue && batchQueue[currentFileIndex] && (
              <p className="text-sm text-blue-300 text-center">
                Current: {batchQueue[currentFileIndex].path?.split('/').pop() || 'Processing...'}
              </p>
            )}
          </div>
          
          {/* Step Status List */}
          <div className="space-y-2 mb-4">
            {processingSteps.map((step) => {
              const getStepIcon = (stepId, status) => {
                if (status === 'completed') return <HiCheck className="w-4 h-4" />;
                if (status === 'failed') return <HiX className="w-4 h-4" />;
                
                switch(stepId) {
                  case 1: return <HiDocumentText className="w-4 h-4" />;
                  case 2: return <HiCog className="w-4 h-4" />;
                  case 3: return <HiCog className="w-4 h-4" />;
                  case 4: return <HiDocumentText className="w-4 h-4" />;
                  case 5: return <HiDatabase className="w-4 h-4" />;
                  default: return step.id;
                }
              };

              return (
                <div key={step.id} className="flex items-center space-x-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                    step.status === 'completed' 
                      ? 'bg-green-500 text-white' 
                      : step.status === 'in_progress' 
                      ? 'bg-blue-500 text-white animate-pulse' 
                      : step.status === 'failed'
                      ? 'bg-red-500 text-white'
                      : 'bg-gray-600 text-gray-300'
                  }`}>
                    {getStepIcon(step.id, step.status)}
                  </div>
                  <span className={`text-sm ${
                    step.status === 'completed' 
                      ? 'text-green-400' 
                      : step.status === 'in_progress' 
                      ? 'text-blue-400' 
                      : step.status === 'failed'
                      ? 'text-red-400'
                      : 'text-gray-400'
                  }`}>
                    {step.label}
                  </span>
                </div>
              );
            })}
          </div>

          {processingStep && (
            <div className="text-center bg-gray-800 rounded-lg p-3">
              <p className="text-sm text-blue-300">{processingStep}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ProcessingProgress;