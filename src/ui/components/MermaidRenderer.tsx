/**
 * Knowledge Graph Mermaid Renderer
 * 
 * Adapted from DocsGPT's MermaidRenderer for visualizing knowledge graphs
 * generated from Neo4j entity and relationship data.
 */
import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface MermaidRendererProps {
  code: string;
  isLoading?: boolean;
  title?: string;
  onError?: (error: string) => void;
}

interface ZoomControls {
  factor: number;
  min: number;
  max: number;
  step: number;
}

export const KnowledgeGraphMermaidRenderer: React.FC<MermaidRendererProps> = ({
  code,
  isLoading = false,
  title = "Knowledge Graph Visualization",
  onError
}) => {
  const diagramId = useRef(`kg-mermaid-${crypto.randomUUID()}`);
  const [error, setError] = useState<string | null>(null);
  const [showCode, setShowCode] = useState<boolean>(false);
  const [showDownloadMenu, setShowDownloadMenu] = useState<boolean>(false);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);
  const downloadMenuRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Zoom functionality
  const [hoverPosition, setHoverPosition] = useState<{ x: number; y: number } | null>(null);
  const [isHovering, setIsHovering] = useState<boolean>(false);
  const [zoomControls] = useState<ZoomControls>({
    factor: 1,
    min: 0.5,
    max: 4,
    step: 0.25
  });
  const [zoomFactor, setZoomFactor] = useState<number>(zoomControls.factor);

  // Detect dark mode from system or context
  useEffect(() => {
    const checkDarkMode = () => {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches ||
                    document.documentElement.classList.contains('dark');
      setIsDarkMode(isDark);
    };

    checkDarkMode();
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    mediaQuery.addEventListener('change', checkDarkMode);
    
    return () => mediaQuery.removeEventListener('change', checkDarkMode);
  }, []);

  // Mouse interaction handlers
  const handleMouseMove = (event: React.MouseEvent) => {
    if (!containerRef.current) return;

    const rect = containerRef.current.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width;
    const y = (event.clientY - rect.top) / rect.height;

    setHoverPosition({ x, y });
  };

  const handleMouseEnter = () => setIsHovering(true);
  const handleMouseLeave = () => {
    setIsHovering(false);
    setHoverPosition(null);
  };

  // Keyboard zoom controls
  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (!isHovering) return;

    if (event.key === '+' || event.key === '=') {
      setZoomFactor(prev => Math.min(zoomControls.max, prev + zoomControls.step));
      event.preventDefault();
    } else if (event.key === '-') {
      setZoomFactor(prev => Math.max(zoomControls.min, prev - zoomControls.step));
      event.preventDefault();
    } else if (event.key === '0') {
      setZoomFactor(zoomControls.factor);
      event.preventDefault();
    }
  };

  // Mouse wheel zoom
  const handleWheel = (event: React.WheelEvent) => {
    if (!isHovering) return;

    if (event.ctrlKey || event.metaKey) {
      event.preventDefault();

      if (event.deltaY < 0) {
        setZoomFactor(prev => Math.min(zoomControls.max, prev + zoomControls.step));
      } else {
        setZoomFactor(prev => Math.max(zoomControls.min, prev - zoomControls.step));
      }
    }
  };

  const getTransformOrigin = () => {
    if (!hoverPosition) return 'center center';
    return `${hoverPosition.x * 100}% ${hoverPosition.y * 100}%`;
  };

  // Mermaid rendering
  useEffect(() => {
    const renderDiagram = async () => {
      if (!code || isLoading) return;

      try {
        // Initialize mermaid with theme
        mermaid.initialize({
          startOnLoad: true,
          theme: isDarkMode ? 'dark' : 'default',
          securityLevel: 'loose',
          suppressErrorRendering: true,
          flowchart: {
            useMaxWidth: true,
            htmlLabels: true,
            curve: 'basis'
          },
          themeVariables: {
            // Knowledge graph specific theming
            primaryColor: isDarkMode ? '#3B82F6' : '#2563EB',
            primaryTextColor: isDarkMode ? '#F3F4F6' : '#1F2937',
            primaryBorderColor: isDarkMode ? '#60A5FA' : '#3B82F6',
            lineColor: isDarkMode ? '#6B7280' : '#9CA3AF',
            sectionBkgColor: isDarkMode ? '#374151' : '#F9FAFB',
            altSectionBkgColor: isDarkMode ? '#4B5563' : '#F3F4F6',
            gridColor: isDarkMode ? '#4B5563' : '#E5E7EB',
            textColor: isDarkMode ? '#F3F4F6' : '#1F2937',
            taskBkgColor: isDarkMode ? '#1F2937' : '#FFFFFF',
            taskTextColor: isDarkMode ? '#F3F4F6' : '#1F2937',
            activeTaskBkgColor: isDarkMode ? '#3B82F6' : '#EFF6FF',
            activeTaskBorderColor: isDarkMode ? '#60A5FA' : '#3B82F6'
          }
        });

        const element = document.getElementById(diagramId.current);
        if (element) {
          element.removeAttribute('data-processed');
          await mermaid.parse(code); // Syntax validation
          mermaid.contentLoaded();
          setError(null);
        }
      } catch (err) {
        const errorMessage = `Failed to render knowledge graph: ${err instanceof Error ? err.message : String(err)}`;
        console.error('Mermaid rendering error:', err);
        setError(errorMessage);
        if (onError) onError(errorMessage);
      }
    };

    renderDiagram();
  }, [code, isDarkMode, isLoading, onError]);

  // Close download menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (downloadMenuRef.current && !downloadMenuRef.current.contains(event.target as Node)) {
        setShowDownloadMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Download functions
  const downloadSvg = (): void => {
    const element = document.getElementById(diagramId.current);
    if (!element) return;
    
    const svgElement = element.querySelector('svg');
    if (!svgElement) return;

    const svgClone = svgElement.cloneNode(true) as SVGElement;
    
    // Ensure proper SVG attributes
    if (!svgClone.hasAttribute('xmlns')) {
      svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    }

    // Set dimensions if missing
    if (!svgClone.hasAttribute('width') || !svgClone.hasAttribute('height')) {
      const viewBox = svgClone.getAttribute('viewBox')?.split(' ') || [];
      if (viewBox.length === 4) {
        svgClone.setAttribute('width', viewBox[2]);
        svgClone.setAttribute('height', viewBox[3]);
      }
    }

    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgClone);
    const svgBlob = new Blob(
      [`<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n${svgString}`],
      { type: 'image/svg+xml' }
    );

    const url = URL.createObjectURL(svgBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'knowledge-graph.svg';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const downloadPng = (): void => {
    const element = document.getElementById(diagramId.current);
    if (!element) return;

    const svgElement = element.querySelector('svg');
    if (!svgElement) return;

    const svgClone = svgElement.cloneNode(true) as SVGElement;
    
    // Ensure SVG namespace
    if (!svgClone.hasAttribute('xmlns')) {
      svgClone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
    }

    // Get dimensions
    let width = parseInt(svgClone.getAttribute('width') || '0');
    let height = parseInt(svgClone.getAttribute('height') || '0');

    if (!width || !height) {
      const viewBox = svgClone.getAttribute('viewBox')?.split(' ') || [];
      if (viewBox.length === 4) {
        width = parseInt(viewBox[2]);
        height = parseInt(viewBox[3]);
      } else {
        width = 1200;
        height = 800;
      }
      svgClone.setAttribute('width', width.toString());
      svgClone.setAttribute('height', height.toString());
    }

    // Create data URL
    const serializer = new XMLSerializer();
    const svgString = serializer.serializeToString(svgClone);
    const svgBase64 = btoa(unescape(encodeURIComponent(svgString)));
    const dataUrl = `data:image/svg+xml;base64,${svgBase64}`;

    // Convert to PNG
    const img = new Image();
    img.crossOrigin = 'anonymous';
    
    img.onload = function (): void {
      const canvas = document.createElement('canvas');
      canvas.width = width * 2; // Higher resolution
      canvas.height = height * 2;

      const ctx = canvas.getContext('2d');
      if (!ctx) {
        console.error('Could not get canvas context');
        return;
      }

      // White background
      ctx.fillStyle = isDarkMode ? '#1F2937' : '#FFFFFF';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Draw SVG
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      try {
        const pngUrl = canvas.toDataURL('image/png');
        const link = document.createElement('a');
        link.download = 'knowledge-graph.png';
        link.href = pngUrl;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      } catch (e) {
        console.error('Failed to create PNG:', e);
        downloadSvg(); // Fallback
      }
    };

    img.src = dataUrl;
  };

  const downloadMermaid = (): void => {
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = 'knowledge-graph.mmd';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const copyToClipboard = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(code);
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  const downloadOptions = [
    { label: '📄 Download as SVG', action: downloadSvg },
    { label: '🖼️ Download as PNG', action: downloadPng },
    { label: '📝 Download as Mermaid', action: downloadMermaid },
  ];

  const showControls = !isLoading && !error && code;

  return (
    <div className="w-full border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-50 dark:bg-gray-700 border-b border-gray-200 dark:border-gray-600 rounded-t-lg">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-gray-900 dark:text-gray-100">
            🧠 {title}
          </span>
          {showControls && (
            <span className="text-xs text-gray-500 dark:text-gray-400">
              ({code.split('\n').length} lines)
            </span>
          )}
        </div>
        
        {showControls && (
          <div className="flex items-center gap-2">
            {/* Copy button */}
            <button
              onClick={copyToClipboard}
              className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded text-gray-700 dark:text-gray-200"
              title="Copy Mermaid code"
            >
              📋 Copy
            </button>

            {/* Download dropdown */}
            <div className="relative" ref={downloadMenuRef}>
              <button
                onClick={() => setShowDownloadMenu(!showDownloadMenu)}
                className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-600 hover:bg-gray-200 dark:hover:bg-gray-500 rounded text-gray-700 dark:text-gray-200"
                title="Download options"
              >
                💾 Download ▼
              </button>
              {showDownloadMenu && (
                <div className="absolute right-0 z-10 mt-1 w-48 rounded-md border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700 shadow-lg">
                  <ul className="py-1">
                    {downloadOptions.map((option, index) => (
                      <li key={index}>
                        <button
                          onClick={() => {
                            option.action();
                            setShowDownloadMenu(false);
                          }}
                          className="w-full px-4 py-2 text-left text-xs hover:bg-gray-100 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200"
                        >
                          {option.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Code toggle */}
            <button
              onClick={() => setShowCode(!showCode)}
              className={`px-2 py-1 text-xs rounded ${
                showCode
                  ? 'bg-blue-100 dark:bg-blue-800 text-blue-800 dark:text-blue-200'
                  : 'bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-200'
              }`}
              title="Toggle code view"
            >
              </> Code
            </button>
          </div>
        )}
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center p-8 bg-white dark:bg-gray-800">
          <div className="text-sm text-gray-500 dark:text-gray-400">
            🔄 Generating knowledge graph visualization...
          </div>
        </div>
      ) : error ? (
        <div className="m-4 p-4 rounded border-2 border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20">
          <div className="text-sm text-red-800 dark:text-red-300 break-words">
            ❌ {error}
          </div>
        </div>
      ) : (
        <>
          {/* Diagram container */}
          <div
            ref={containerRef}
            className="relative w-full bg-white dark:bg-gray-800 p-4 overflow-auto"
            style={{
              scrollbarWidth: 'thin',
              scrollbarColor: isDarkMode ? '#4B5563 #1F2937' : '#D1D5DB #F9FAFB'
            }}
            onMouseMove={handleMouseMove}
            onMouseEnter={handleMouseEnter}
            onMouseLeave={handleMouseLeave}
            onKeyDown={handleKeyDown}
            onWheel={handleWheel}
            tabIndex={0}
          >
            {/* Zoom controls */}
            {isHovering && (
              <div className="absolute top-2 right-2 z-10 flex items-center gap-1 rounded bg-black/70 px-2 py-1 text-xs text-white">
                <button
                  onClick={() => setZoomFactor(prev => Math.max(zoomControls.min, prev - zoomControls.step))}
                  className="rounded px-1 hover:bg-gray-600"
                  title="Zoom out (Ctrl + -)"
                >
                  ➖
                </button>
                <span
                  className="cursor-pointer hover:underline min-w-[3rem] text-center"
                  onClick={() => setZoomFactor(zoomControls.factor)}
                  title="Reset zoom (Ctrl + 0)"
                >
                  {zoomFactor.toFixed(1)}x
                </span>
                <button
                  onClick={() => setZoomFactor(prev => Math.min(zoomControls.max, prev + zoomControls.step))}
                  className="rounded px-1 hover:bg-gray-600"
                  title="Zoom in (Ctrl + +)"
                >
                  ➕
                </button>
              </div>
            )}

            {/* Mermaid diagram */}
            <pre
              className="mermaid w-full select-none"
              id={diagramId.current}
              key={`mermaid-${diagramId.current}`}
              style={{
                transform: `scale(${zoomFactor})`,
                transformOrigin: getTransformOrigin(),
                transition: 'transform 0.2s ease',
                cursor: isHovering ? 'grab' : 'default',
                width: '100%',
                display: 'flex',
                justifyContent: 'center',
                minHeight: '200px'
              }}
            >
              {code}
            </pre>
          </div>

          {/* Code view */}
          {showCode && (
            <div className="border-t border-gray-200 dark:border-gray-600">
              <div className="px-4 py-2 bg-gray-50 dark:bg-gray-700">
                <span className="text-xs font-medium text-gray-900 dark:text-gray-100">
                  📝 Mermaid Source Code
                </span>
              </div>
              <pre className="p-4 text-sm bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-200 overflow-x-auto max-h-64">
                <code>{code}</code>
              </pre>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default KnowledgeGraphMermaidRenderer;