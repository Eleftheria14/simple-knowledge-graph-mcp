import React from 'react';
import { HiCollection, HiChevronLeft, HiChevronRight, HiPlus, HiTrash } from 'react-icons/hi';

const Sidebar = ({
  showSidebar,
  setShowSidebar,
  sessions,
  currentSession,
  setCurrentSession,
  newSessionName,
  setNewSessionName,
  creatingSession,
  createNewSession,
  deletingSessionId,
  deleteSession
}) => {
  return (
    <div className={`${showSidebar ? 'w-80' : 'w-12'} bg-gray-800 border-r border-gray-700 flex-shrink-0 transition-all duration-300`}>
      {/* Sidebar Header */}
      <div className="pt-8 pb-4 px-4 border-b border-gray-700">
        <div className="flex items-center justify-between">
          {showSidebar && (
            <h2 className="text-lg font-semibold flex items-center space-x-2">
              <HiCollection className="w-5 h-5 text-blue-400" />
              <span>PDF Sessions</span>
            </h2>
          )}
          <button
            onClick={() => setShowSidebar(!showSidebar)}
            className="p-2 hover:bg-gray-700 rounded-lg transition-colors group"
          >
            {showSidebar ? (
              <HiChevronLeft className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            ) : (
              <HiChevronRight className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
            )}
          </button>
        </div>
      </div>

      {showSidebar && (
        <div className="flex-1 overflow-y-auto">
          {/* New Session Button */}
          <div className="p-4 border-b border-gray-700">
            <div className="space-y-2">
              <input
                type="text"
                value={newSessionName}
                onChange={(e) => setNewSessionName(e.target.value)}
                placeholder="Session name..."
                disabled={creatingSession}
                className={`w-full px-3 py-2 border rounded text-sm focus:ring-2 focus:ring-blue-500 ${
                  creatingSession
                    ? 'bg-gray-600 border-gray-500 cursor-not-allowed'
                    : 'bg-gray-700 border-gray-600'
                }`}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !creatingSession) {
                    createNewSession(newSessionName || null);
                  }
                }}
              />
              <button
                onClick={() => {
                  createNewSession(newSessionName || null);
                }}
                disabled={creatingSession}
                className={`w-full px-3 py-2 rounded text-sm font-medium flex items-center justify-center space-x-2 transition-colors ${
                  creatingSession 
                    ? 'bg-gray-600 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {creatingSession ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    <span>Creating...</span>
                  </>
                ) : (
                  <>
                    <HiPlus className="w-4 h-4" />
                    <span>New Session</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Sessions List */}
          <div className="p-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`p-3 mb-2 rounded cursor-pointer transition-colors ${
                  currentSession?.id === session.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-700 hover:bg-gray-600'
                }`}
                onClick={() => {
                  setCurrentSession(session);
                }}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h3 className="text-sm font-medium truncate">{session.name}</h3>
                    <div className="text-xs text-gray-300 mt-1">
                      <div>{session.document_count} documents</div>
                      <div>{new Date(session.last_updated).toLocaleDateString()}</div>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (window.confirm('Delete this session? Documents will be kept.')) {
                        deleteSession(session.id, false);
                      }
                    }}
                    disabled={deletingSessionId === session.id}
                    className={`ml-2 p-1 rounded transition-colors ${
                      deletingSessionId === session.id
                        ? 'text-gray-400 cursor-not-allowed'
                        : 'text-red-400 hover:text-red-300 hover:bg-red-900/20'
                    }`}
                  >
                    {deletingSessionId === session.id ? (
                      <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <HiTrash className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Sidebar;