import React from 'react';
import { HiCog } from 'react-icons/hi';

const TabNavigation = ({ 
  currentTab, 
  setCurrentTab, 
  results, 
  entityResults 
}) => {
  return (
    <div className="max-w-6xl mx-auto mb-8">
      <div className="border-b border-gray-700">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setCurrentTab('upload')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              currentTab === 'upload'
                ? 'border-blue-500 text-blue-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            1. Upload & Parse
          </button>
          <button
            onClick={() => setCurrentTab('extraction')}
            disabled={results.length === 0}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              currentTab === 'extraction'
                ? 'border-green-500 text-green-400'
                : results.length === 0
                ? 'border-transparent text-gray-600 cursor-not-allowed'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            2. Extract Entities
          </button>
          <button
            onClick={() => setCurrentTab('knowledge-graph')}
            disabled={entityResults.length === 0}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              currentTab === 'knowledge-graph'
                ? 'border-purple-500 text-purple-400'
                : entityResults.length === 0
                ? 'border-transparent text-gray-600 cursor-not-allowed'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            3. Knowledge Graph
          </button>
          
          {/* Settings Tab - Always available */}
          <div className="flex-1"></div>
          <button
            onClick={() => setCurrentTab('settings')}
            className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-1 ${
              currentTab === 'settings'
                ? 'border-orange-500 text-orange-400'
                : 'border-transparent text-gray-400 hover:text-gray-300 hover:border-gray-300'
            }`}
          >
            <HiCog className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </nav>
      </div>
    </div>
  );
};

export default TabNavigation;