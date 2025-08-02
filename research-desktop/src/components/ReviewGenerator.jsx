import React, { useState, useRef } from 'react';

const ReviewGenerator = ({ onGenerate }) => {
  const [topic, setTopic] = useState('');
  const [citationStyle, setCitationStyle] = useState('APA');
  const [maxSources, setMaxSources] = useState(20);
  const [includeSummary, setIncludeSummary] = useState(true);
  const [isGenerating, setIsGenerating] = useState(false);
  const [review, setReview] = useState(null);
  const [selectedSections, setSelectedSections] = useState({
    introduction: true,
    methodology: true,
    findings: true,
    discussion: true,
    conclusion: true,
    references: true
  });
  
  const textAreaRef = useRef(null);

  const citationStyles = [
    { value: 'APA', label: 'APA (American Psychological Association)' },
    { value: 'IEEE', label: 'IEEE (Institute of Electrical and Electronics Engineers)' },
    { value: 'Nature', label: 'Nature' },
    { value: 'MLA', label: 'MLA (Modern Language Association)' }
  ];

  const sampleReview = {
    topic: 'Transformer Architecture and Attention Mechanisms',
    sections: {
      introduction: `The Transformer architecture has revolutionized natural language processing since its introduction by Vaswani et al. (2017). This literature review examines the development, applications, and impact of transformer-based models in various NLP tasks.`,
      
      methodology: `This review synthesizes findings from 20 peer-reviewed papers published between 2017-2024, focusing on transformer architectures, attention mechanisms, and their applications. Sources were selected based on citation count, relevance, and methodological rigor.`,
      
      findings: `Key findings indicate that transformer models consistently outperform traditional RNN and CNN architectures across multiple benchmarks. The self-attention mechanism enables parallel processing and better handling of long-range dependencies (Devlin et al., 2018; Brown et al., 2020).`,
      
      discussion: `The success of transformers stems from their ability to model complex relationships in sequential data through attention mechanisms. However, computational requirements and interpretability remain significant challenges (Rogers et al., 2020).`,
      
      conclusion: `Transformer architectures represent a paradigm shift in NLP, enabling breakthrough performance across diverse tasks. Future research should focus on efficiency improvements and better interpretability methods.`,
      
      references: [
        'Vaswani, A., Shazeer, N., Parmar, N., et al. (2017). Attention is all you need. In Advances in Neural Information Processing Systems (pp. 5998-6008).',
        'Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. arXiv preprint arXiv:1810.04805.',
        'Brown, T., Mann, B., Ryder, N., et al. (2020). Language models are few-shot learners. Advances in neural information processing systems, 33, 1877-1901.',
        'Rogers, A., Kovaleva, O., & Rumshisky, A. (2020). A primer on neural network models for natural language processing. Journal of Artificial Intelligence Research, 57, 615-731.'
      ]
    },
    statistics: {
      totalSources: 20,
      keyEntities: 45,
      citationNetworks: 8,
      generatedAt: new Date().toISOString()
    }
  };

  const handleGenerate = async () => {
    if (!topic.trim()) return;

    setIsGenerating(true);
    try {
      // TODO: Replace with actual MCP API call
      if (window.electronAPI?.mcpAPI) {
        const result = await window.electronAPI.mcpAPI.generateLiteratureReview(topic, {
          citationStyle,
          maxSources,
          includeSummary
        });
        setReview(result);
      } else {
        // Use sample data for demo
        await new Promise(resolve => setTimeout(resolve, 3000));
        setReview(sampleReview);
      }

      if (onGenerate) {
        onGenerate(topic, { citationStyle, maxSources, includeSummary });
      }
    } catch (error) {
      console.error('Review generation failed:', error);
      // Show error notification
    } finally {
      setIsGenerating(false);
    }
  };

  const handleExport = async (format) => {
    if (!review) return;

    try {
      const result = await window.electronAPI.showSaveDialog({
        filters: [
          { name: 'Word Document', extensions: ['docx'] },
          { name: 'LaTeX', extensions: ['tex'] },
          { name: 'Markdown', extensions: ['md'] },
          { name: 'Plain Text', extensions: ['txt'] }
        ].filter(f => f.extensions[0] === format)
      });

      if (!result.canceled) {
        // TODO: Implement actual export functionality
        console.log(`Exporting review as ${format} to ${result.filePath}`);
      }
    } catch (error) {
      console.error('Export failed:', error);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      // Show success notification
    });
  };

  const handleSectionToggle = (section) => {
    setSelectedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  return (
    <div className="flex flex-col h-full bg-slate-900">
      {/* Header */}
      <div className="p-6 bg-slate-800 border-b border-slate-700">
        <h2 className="text-lg font-semibold text-white mb-4">📝 Literature Review Generator</h2>
        
        {/* Configuration */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="input-group">
              <label className="input-label">Research Topic</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., Transformer architecture and attention mechanisms"
                className="input"
                disabled={isGenerating}
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="input-group">
                <label className="input-label">Citation Style</label>
                <select
                  value={citationStyle}
                  onChange={(e) => setCitationStyle(e.target.value)}
                  className="input"
                  disabled={isGenerating}
                >
                  {citationStyles.map(style => (
                    <option key={style.value} value={style.value}>
                      {style.label}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="input-group">
                <label className="input-label">Max Sources</label>
                <input
                  type="number"
                  min="5"
                  max="100"
                  value={maxSources}
                  onChange={(e) => setMaxSources(parseInt(e.target.value))}
                  className="input"
                  disabled={isGenerating}
                />
              </div>
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="input-group">
              <label className="input-label">Include Sections</label>
              <div className="grid grid-cols-2 gap-2 mt-2">
                {Object.entries(selectedSections).map(([section, selected]) => (
                  <label key={section} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={selected}
                      onChange={() => handleSectionToggle(section)}
                      className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                      disabled={isGenerating}
                    />
                    <span className="text-sm text-gray-300 capitalize">
                      {section.replace(/([A-Z])/g, ' $1').trim()}
                    </span>
                  </label>
                ))}
              </div>
            </div>
            
            <label className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={includeSummary}
                onChange={(e) => setIncludeSummary(e.target.checked)}
                className="rounded bg-slate-700 border-slate-600 text-blue-600 focus:ring-blue-500"
                disabled={isGenerating}
              />
              <span className="text-gray-300">Include summary statistics</span>
            </label>
          </div>
        </div>
        
        <div className="flex items-center justify-between mt-6">
          <button
            onClick={handleGenerate}
            disabled={isGenerating || !topic.trim()}
            className="btn btn-primary px-8"
          >
            {isGenerating ? (
              <>
                <div className="spinner mr-2" />
                Generating Review...
              </>
            ) : (
              'Generate Literature Review'
            )}
          </button>
          
          {review && (
            <div className="flex space-x-2">
              <button
                onClick={() => handleExport('docx')}
                className="btn btn-secondary text-sm"
                title="Export as Word document"
              >
                📄 Word
              </button>
              <button
                onClick={() => handleExport('tex')}
                className="btn btn-secondary text-sm"
                title="Export as LaTeX"
              >
                📜 LaTeX
              </button>
              <button
                onClick={() => handleExport('md')}
                className="btn btn-secondary text-sm"
                title="Export as Markdown"
              >
                📝 Markdown
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-hidden">
        {isGenerating ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="spinner mb-4"></div>
              <h3 className="text-lg font-semibold text-white mb-2">Generating Literature Review</h3>
              <p className="text-gray-400">Analyzing knowledge graph and generating academic content...</p>
              <div className="mt-4 text-sm text-gray-500 space-y-1">
                <p>🔍 Searching for relevant entities and relationships</p>
                <p>📚 Gathering citation networks and source materials</p>
                <p>✍️ Generating structured academic content</p>
              </div>
            </div>
          </div>
        ) : review ? (
          <div className="flex h-full">
            {/* Review Content */}
            <div className="flex-1 overflow-y-auto p-6">
              <div className="max-w-4xl mx-auto space-y-8">
                {/* Title */}
                <div className="text-center border-b border-slate-700 pb-6">
                  <h1 className="text-3xl font-bold text-white mb-2">
                    Literature Review: {review.topic}
                  </h1>
                  <p className="text-gray-400">
                    Generated on {new Date(review.statistics.generatedAt).toLocaleDateString()}
                  </p>
                </div>

                {/* Sections */}
                {Object.entries(review.sections).map(([section, content]) => {
                  if (section === 'references') return null;
                  if (!selectedSections[section]) return null;
                  
                  return (
                    <section key={section} className="prose prose-invert max-w-none">
                      <div className="flex items-center justify-between mb-4">
                        <h2 className="text-xl font-semibold text-white capitalize m-0">
                          {section.replace(/([A-Z])/g, ' $1').trim()}
                        </h2>
                        <button
                          onClick={() => copyToClipboard(content)}
                          className="btn btn-ghost text-sm"
                          title="Copy section"
                        >
                          📋
                        </button>
                      </div>
                      <p className="text-gray-300 leading-relaxed">{content}</p>
                    </section>
                  );
                })}

                {/* References */}
                {selectedSections.references && review.sections.references && (
                  <section className="prose prose-invert max-w-none">
                    <div className="flex items-center justify-between mb-4">
                      <h2 className="text-xl font-semibold text-white m-0">References</h2>
                      <button
                        onClick={() => copyToClipboard(review.sections.references.join('\n\n'))}
                        className="btn btn-ghost text-sm"
                        title="Copy references"
                      >
                        📋
                      </button>
                    </div>
                    <div className="space-y-3">
                      {review.sections.references.map((ref, index) => (
                        <p key={index} className="text-gray-300 text-sm leading-relaxed">
                          {ref}
                        </p>
                      ))}
                    </div>
                  </section>
                )}
              </div>
            </div>

            {/* Statistics Sidebar */}
            {includeSummary && review.statistics && (
              <div className="w-80 bg-slate-800 border-l border-slate-700 p-6">
                <h3 className="text-lg font-semibold text-white mb-4">📊 Review Statistics</h3>
                
                <div className="space-y-4">
                  <div className="card">
                    <div className="card-body">
                      <div className="text-2xl font-bold text-blue-400">
                        {review.statistics.totalSources}
                      </div>
                      <div className="text-sm text-gray-400">Total Sources</div>
                    </div>
                  </div>
                  
                  <div className="card">
                    <div className="card-body">
                      <div className="text-2xl font-bold text-green-400">
                        {review.statistics.keyEntities}
                      </div>
                      <div className="text-sm text-gray-400">Key Entities</div>
                    </div>
                  </div>
                  
                  <div className="card">
                    <div className="card-body">
                      <div className="text-2xl font-bold text-purple-400">
                        {review.statistics.citationNetworks}
                      </div>
                      <div className="text-sm text-gray-400">Citation Networks</div>
                    </div>
                  </div>
                  
                  <div className="text-xs text-gray-500 pt-4 border-t border-slate-700">
                    <p>Style: {citationStyle}</p>
                    <p>Generated: {new Date(review.statistics.generatedAt).toLocaleString()}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-gray-500">
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-xl font-semibold mb-2">Generate Literature Review</h3>
              <p className="mb-4">Enter a research topic to generate an AI-powered literature review</p>
              <div className="text-sm text-gray-400 space-y-1 max-w-md">
                <p>✅ Analyzes your knowledge graph for relevant sources</p>
                <p>✅ Generates structured academic content</p>
                <p>✅ Includes proper citations and references</p>
                <p>✅ Exports to multiple formats (Word, LaTeX, Markdown)</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ReviewGenerator;