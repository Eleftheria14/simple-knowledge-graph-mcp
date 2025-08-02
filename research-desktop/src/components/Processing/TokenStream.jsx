import React, { useState, useEffect, useRef } from 'react';

const TokenStream = ({ isActive, className = "", persistedTokens, isStreaming }) => {
  const [streamContent, setStreamContent] = useState("");
  const streamRef = useRef(null);
  
  // Display content from multiple sources
  const displayContent = streamContent || persistedTokens || "";
  
  // Handle persisted tokens when streaming is complete
  useEffect(() => {
    if (!isStreaming && persistedTokens && persistedTokens !== streamContent) {
      console.log('🟢 TokenStream: Setting persisted tokens, length:', persistedTokens.length);
      setStreamContent(persistedTokens);
    }
  }, [persistedTokens, isStreaming]);
  
  // Also update during streaming if persistedTokens is being updated
  useEffect(() => {
    if (isStreaming && persistedTokens) {
      console.log('🟢 TokenStream: Updating during streaming, length:', persistedTokens.length);
      setStreamContent(persistedTokens);
    }
  }, [persistedTokens, isStreaming]);
  
  // Clear tokens when streaming starts
  useEffect(() => {
    if (isActive && isStreaming) {
      setStreamContent("");
    }
  }, [isActive, isStreaming]);
  
  // Auto-scroll to bottom when content updates
  useEffect(() => {
    if (streamRef.current) {
      streamRef.current.scrollTop = streamRef.current.scrollHeight;
    }
  }, [displayContent]);
  
  // Expose methods to parent for token updates
  useEffect(() => {
    console.log('🟢 TokenStream: Setting up global functions');
    
    // Create global function for token updates
    window.addStreamToken = (token) => {
      console.log('🟢 TokenStream: addStreamToken called with:', token);
      setStreamContent(prev => {
        const newContent = prev + token;
        console.log('🟢 TokenStream: Updated content length:', newContent.length);
        return newContent;
      });
    };
    
    window.clearStreamTokens = () => {
      console.log('🟢 TokenStream: clearStreamTokens called');
      setStreamContent("");
    };
    
    console.log('🟢 TokenStream: Global functions set up successfully');
    
    // Cleanup
    return () => {
      console.log('🟡 TokenStream: Cleaning up global functions');
      delete window.addStreamToken;
      delete window.clearStreamTokens;
    };
  }, []);
  
  if (!isActive) return null;
  
  return (
    <div className={`mt-6 ${className}`}>
      <h4 className="text-sm font-medium text-gray-300 mb-3 flex items-center">
        <div className={`w-2 h-2 ${isStreaming ? 'bg-green-400 animate-pulse' : 'bg-blue-400'} rounded-full mr-2`}></div>
        🌊 {isStreaming ? 'Live Token Stream' : 'Last Token Stream'} (Groq Llama 3.1 8B)
      </h4>
      <div 
        ref={streamRef}
        className="bg-black/50 rounded-lg p-4 max-h-64 overflow-y-auto border border-green-600 scroll-smooth"
      >
        <div className="font-mono text-sm text-green-300 whitespace-pre-wrap leading-relaxed">
          {displayContent || <span className="text-gray-400">Waiting for tokens...</span>}
          {isStreaming && <span className="animate-pulse text-yellow-400">▊</span>}
        </div>
      </div>
      <div className="text-xs text-gray-500 mt-2 flex justify-between">
        <span>{isStreaming ? 'Real-time token streaming' : 'Final tokens preserved'}</span>
        <span>{displayContent.length} characters</span>
      </div>
    </div>
  );
};

export default TokenStream;