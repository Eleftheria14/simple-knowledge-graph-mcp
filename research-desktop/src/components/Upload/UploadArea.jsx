import React from 'react';
import { HiCloudUpload, HiClock, HiCheck, HiUpload } from 'react-icons/hi';

const UploadArea = ({
  dragActive,
  grobidConnected,
  isProcessing,
  handleDrop,
  handleDragOver,
  handleDragEnter,
  handleDragLeave,
  handleDragEnd,
  handleFileSelect,
  results = [],
  // Processing props for beautiful centered display
  batchProgress,
  currentFileIndex,
  batchQueue,
  processingSteps,
  processingStep,
  processingProgress
}) => {
  
  // Show compact area when there are results
  const showCompactArea = results.length > 0;
  
  if (showCompactArea) {
    return (
      <div className="max-w-4xl mx-auto mb-8">
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragEnd={handleDragEnd}
          className={`border border-dashed rounded-lg p-6 text-center transition-colors ${
            isProcessing
              ? 'border-blue-400 bg-blue-900/20'
              : dragActive 
                ? 'border-blue-400 bg-blue-900/20' 
                : 'border-gray-600 hover:border-gray-500'
          } ${!grobidConnected ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
          onClick={grobidConnected ? handleFileSelect : undefined}
        >
          <div className="flex items-center justify-center space-x-3 text-sm">
            <HiCloudUpload className="w-5 h-5 text-gray-400" />
            <span className="text-gray-300">
              Drop more PDFs here or click to browse
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto mb-8">
      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragEnd={handleDragEnd}
        className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
          dragActive 
            ? 'border-blue-400 bg-blue-900/20' 
            : 'border-gray-600 hover:border-gray-500'
        } ${!grobidConnected ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
        onClick={grobidConnected ? handleFileSelect : undefined}
      >
        <div>
          <div className="text-4xl mb-4">
            <HiUpload className="w-16 h-16 mx-auto text-gray-400" />
          </div>
          <h3 className="text-lg font-medium mb-2">
            {!grobidConnected ? 'GROBID Server Disconnected' : 
             isProcessing ? 'Drop more PDFs here or click to browse' :
             'Drop PDF files here or click to browse'}
          </h3>
          <p className="text-gray-400 text-sm">
            {!grobidConnected 
              ? 'Connect to GROBID server to process PDFs' 
              : isProcessing
              ? 'You can add more files while processing is ongoing'
              : 'Upload academic papers to extract structured content and build your knowledge graph'
            }
          </p>
        </div>
      </div>
    </div>
  );
};

export default UploadArea;