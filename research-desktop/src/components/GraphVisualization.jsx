import React, { useEffect, useRef, useState } from 'react';

// Lazy load Cytoscape to prevent crashes
let cytoscape = null;
let extensionsLoaded = false;

const loadCytoscape = async () => {
  if (!cytoscape) {
    try {
      const cytoscapeModule = await import('cytoscape');
      cytoscape = cytoscapeModule.default;
      
      // Try to load extensions
      if (!extensionsLoaded) {
        try {
          const dagre = await import('cytoscape-dagre');
          const fcose = await import('cytoscape-fcose');
          cytoscape.use(dagre.default);
          cytoscape.use(fcose.default);
          extensionsLoaded = true;
        } catch (extError) {
          console.warn('Could not load Cytoscape extensions:', extError);
        }
      }
    } catch (error) {
      console.error('Failed to load Cytoscape:', error);
      return null;
    }
  }
  return cytoscape;
};

const GraphVisualization = ({ data, onNodeSelect, onEdgeSelect }) => {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedLayout, setSelectedLayout] = useState('fcose');
  const [filterType, setFilterType] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState(null);

  // Sample data for demonstration
  const sampleData = {
    nodes: [
      { data: { id: 'transformer', label: 'Transformer Architecture', type: 'concept', confidence: 0.95 } },
      { data: { id: 'attention', label: 'Attention Mechanism', type: 'concept', confidence: 0.92 } },
      { data: { id: 'bert', label: 'BERT', type: 'model', confidence: 0.98 } },
      { data: { id: 'vaswani', label: 'Vaswani et al.', type: 'author', confidence: 1.0 } },
      { data: { id: 'nlp', label: 'Natural Language Processing', type: 'field', confidence: 0.89 } },
      { data: { id: 'self-attention', label: 'Self-Attention', type: 'concept', confidence: 0.94 } },
    ],
    edges: [
      { data: { id: 'e1', source: 'transformer', target: 'attention', label: 'uses', confidence: 0.9 } },
      { data: { id: 'e2', source: 'bert', target: 'transformer', label: 'based_on', confidence: 0.95 } },
      { data: { id: 'e3', source: 'vaswani', target: 'transformer', label: 'authored', confidence: 1.0 } },
      { data: { id: 'e4', source: 'transformer', target: 'nlp', label: 'applied_to', confidence: 0.88 } },
      { data: { id: 'e5', source: 'attention', target: 'self-attention', label: 'includes', confidence: 0.92 } },
    ]
  };

  const graphData = data.nodes?.length > 0 ? data : sampleData;

  const layoutOptions = {
    fcose: {
      name: 'fcose',
      quality: 'default',
      randomize: false,
      animate: true,
      animationDuration: 1000,
      fit: true,
      padding: 50,
      nodeSeparation: 75,
      idealEdgeLength: 100,
      edgeElasticity: 0.45,
      nestingFactor: 0.1,
      gravity: 0.25,
      numIter: 2500,
      tile: true,
      tilingPaddingVertical: 10,
      tilingPaddingHorizontal: 10
    },
    dagre: {
      name: 'dagre',
      rankDir: 'TB',
      align: 'DR',
      ranker: 'tight-tree',
      animate: true,
      animationDuration: 1000,
      fit: true,
      padding: 50
    },
    circle: {
      name: 'circle',
      animate: true,
      animationDuration: 1000,
      fit: true,
      padding: 50
    },
    cose: {
      name: 'cose',
      animate: true,
      animationDuration: 1000,
      fit: true,
      padding: 50,
      nodeRepulsion: 400000,
      idealEdgeLength: 100,
      edgeElasticity: 100,
      nestingFactor: 5,
      gravity: 80,
      numIter: 1000,
      initialTemp: 200,
      coolingFactor: 0.95,
      minTemp: 1.0
    }
  };

  const getNodeColor = (type) => {
    const colors = {
      concept: '#3b82f6',    // blue
      model: '#10b981',      // green
      author: '#f59e0b',     // yellow
      field: '#8b5cf6',      // purple
      paper: '#ef4444',      // red
      default: '#6b7280'     // gray
    };
    return colors[type] || colors.default;
  };

  const getNodeSize = (confidence) => {
    return Math.max(20, confidence * 50);
  };

  useEffect(() => {
    if (!containerRef.current) return;

    const initializeGraph = async () => {
      setIsLoading(true);

      // Destroy existing instance
      if (cyRef.current) {
        cyRef.current.destroy();
      }

      // Load Cytoscape
      const cy = await loadCytoscape();
      if (!cy) {
        setLoadError('Failed to load graph visualization library');
        setIsLoading(false);
        return;
      }

    // Filter data based on current filters
    let filteredNodes = graphData.nodes;
    let filteredEdges = graphData.edges;

    if (filterType !== 'all') {
      filteredNodes = graphData.nodes.filter(node => node.data.type === filterType);
      const nodeIds = new Set(filteredNodes.map(node => node.data.id));
      filteredEdges = graphData.edges.filter(edge => 
        nodeIds.has(edge.data.source) && nodeIds.has(edge.data.target)
      );
    }

    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      filteredNodes = filteredNodes.filter(node => 
        node.data.label.toLowerCase().includes(term)
      );
      const nodeIds = new Set(filteredNodes.map(node => node.data.id));
      filteredEdges = filteredEdges.filter(edge => 
        nodeIds.has(edge.data.source) && nodeIds.has(edge.data.target)
      );
    }

      // Create new Cytoscape instance
      cyRef.current = cy({
      container: containerRef.current,
      elements: {
        nodes: filteredNodes,
        edges: filteredEdges
      },
      style: [
        {
          selector: 'node',
          style: {
            'background-color': (ele) => getNodeColor(ele.data('type')),
            'label': 'data(label)',
            'width': (ele) => getNodeSize(ele.data('confidence')),
            'height': (ele) => getNodeSize(ele.data('confidence')),
            'text-valign': 'center',
            'text-halign': 'center',
            'color': '#ffffff',
            'text-outline-width': 2,
            'text-outline-color': '#000000',
            'font-size': '12px',
            'font-weight': 'bold',
            'border-width': 2,
            'border-color': '#ffffff',
            'border-opacity': 0.5,
            'text-wrap': 'wrap',
            'text-max-width': '80px',
            'font-family': 'Inter, Arial, sans-serif'
          }
        },
        {
          selector: 'node:selected',
          style: {
            'border-width': 4,
            'border-color': '#fbbf24',
            'border-opacity': 1
          }
        },
        {
          selector: 'edge',
          style: {
            'width': (ele) => Math.max(2, ele.data('confidence') * 6),
            'line-color': '#64748b',
            'target-arrow-color': '#64748b',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
            'label': 'data(label)',
            'font-size': '10px',
            'color': '#e2e8f0',
            'text-outline-width': 1,
            'text-outline-color': '#000000',
            'text-rotation': 'autorotate',
            'font-family': 'Inter, Arial, sans-serif'
          }
        },
        {
          selector: 'edge:selected',
          style: {
            'line-color': '#fbbf24',
            'target-arrow-color': '#fbbf24',
            'width': 4
          }
        }
      ],
      layout: layoutOptions[selectedLayout],
      minZoom: 0.1,
      maxZoom: 3,
      wheelSensitivity: 0.2
    });

    // Event handlers
    cyRef.current.on('tap', 'node', (event) => {
      const node = event.target;
      if (onNodeSelect) {
        onNodeSelect(node.data());
      }
    });

    cyRef.current.on('tap', 'edge', (event) => {
      const edge = event.target;
      if (onEdgeSelect) {
        onEdgeSelect(edge.data());
      }
    });

      cyRef.current.on('layoutstop', () => {
        setIsLoading(false);
      });
    };

    initializeGraph();

    return () => {
      if (cyRef.current) {
        cyRef.current.destroy();
      }
    };
  }, [graphData, selectedLayout, filterType, searchTerm, onNodeSelect, onEdgeSelect]);

  const handleLayoutChange = (layout) => {
    setSelectedLayout(layout);
  };

  const handleZoomFit = () => {
    if (cyRef.current) {
      cyRef.current.fit();
    }
  };

  const handleCenter = () => {
    if (cyRef.current) {
      cyRef.current.center();
    }
  };

  const nodeTypes = [...new Set(graphData.nodes.map(node => node.data.type))];

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Controls */}
      <div className="flex items-center justify-between p-4 bg-slate-800 border-b border-slate-700">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-semibold text-white">🕸️ Knowledge Graph</h2>
          
          {/* Layout selector */}
          <select
            value={selectedLayout}
            onChange={(e) => handleLayoutChange(e.target.value)}
            className="input text-sm"
          >
            <option value="fcose">Force Layout</option>
            <option value="dagre">Hierarchical</option>
            <option value="circle">Circular</option>
            <option value="cose">Spring</option>
          </select>
          
          {/* Type filter */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="input text-sm"
          >
            <option value="all">All Types</option>
            {nodeTypes.map(type => (
              <option key={type} value={type}>
                {type.charAt(0).toUpperCase() + type.slice(1)}s
              </option>
            ))}
          </select>
          
          {/* Search */}
          <input
            type="text"
            placeholder="Search nodes..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="input text-sm w-48"
          />
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={handleCenter}
            className="btn btn-ghost text-sm"
            title="Center Graph"
          >
            🎯
          </button>
          <button
            onClick={handleZoomFit}
            className="btn btn-ghost text-sm"
            title="Fit to Screen"
          >
            🔍
          </button>
          <span className="text-sm text-gray-400">
            {graphData.nodes.length} nodes, {graphData.edges.length} edges
          </span>
        </div>
      </div>
      
      {/* Graph container */}
      <div className="flex-1 relative">
        <div ref={containerRef} className="w-full h-full graph-container" />
        
        {isLoading && (
          <div className="absolute inset-0 bg-slate-900 bg-opacity-75 flex items-center justify-center">
            <div className="text-center">
              <div className="spinner mb-2"></div>
              <p className="text-gray-400">Rendering graph...</p>
            </div>
          </div>
        )}
        
        {loadError && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-red-400">
              <div className="text-6xl mb-4">⚠️</div>
              <h3 className="text-xl font-semibold mb-2">Graph Visualization Error</h3>
              <p className="mb-4">{loadError}</p>
              <button 
                onClick={() => window.location.reload()} 
                className="btn btn-secondary"
              >
                Retry
              </button>
            </div>
          </div>
        )}
        
        {graphData.nodes.length === 0 && !isLoading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">📄</div>
              <h3 className="text-xl font-semibold mb-2">No Data Yet</h3>
              <p>Upload some PDFs to start building your knowledge graph</p>
            </div>
          </div>
        )}
      </div>
      
      {/* Legend */}
      <div className="p-4 bg-slate-800 border-t border-slate-700">
        <div className="flex items-center space-x-6 text-sm">
          <span className="text-gray-400">Legend:</span>
          {nodeTypes.map(type => (
            <div key={type} className="flex items-center space-x-2">
              <div 
                className="w-3 h-3 rounded-full" 
                style={{ backgroundColor: getNodeColor(type) }}
              />
              <span className="text-gray-300 capitalize">{type}s</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default GraphVisualization;