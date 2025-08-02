import React from 'react';
import { HiCollection } from 'react-icons/hi';

const KnowledgeGraphTab = () => {
  return (
    <div className="p-8">
      <div className="max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-6 flex items-center space-x-2">
          <HiCollection className="w-6 h-6 text-purple-400" />
          <span>Knowledge Graph</span>
        </h2>
        <p className="text-gray-300">Knowledge graph interface coming soon...</p>
      </div>
    </div>
  );
};

export default KnowledgeGraphTab;