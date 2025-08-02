import React, { useState, useEffect } from 'react';
import { HiCode, HiSave, HiRefresh, HiTemplate, HiCog, HiPlus, HiTrash, HiDuplicate } from 'react-icons/hi';

const PromptTemplateEditor = ({ templates, setTemplates }) => {
  // Use shared state from parent or initialize with defaults
  const currentTemplates = templates || {};
  const updateTemplates = setTemplates || (() => {});

  const [activeTemplate, setActiveTemplate] = useState('academic');
  const [editingTemplate, setEditingTemplate] = useState(null);
  const [hasChanges, setHasChanges] = useState(false);
  const [showNewTemplateDialog, setShowNewTemplateDialog] = useState(false);
  const [newTemplateName, setNewTemplateName] = useState('');

  const handleTemplateChange = (templateKey, field, value) => {
    updateTemplates(prev => ({
      ...prev,
      [templateKey]: {
        ...prev[templateKey],
        [field]: value
      }
    }));
    setHasChanges(true);
  };

  const saveTemplates = async () => {
    try {
      // TODO: Save to backend/config
      console.log('Saving prompt templates:', currentTemplates);
      setHasChanges(false);
      // Show success message
    } catch (error) {
      console.error('Failed to save templates:', error);
    }
  };

  const resetToDefaults = () => {
    // Reset current template to defaults
    // This would reload from backend defaults
    setHasChanges(false);
  };

  const createNewTemplate = () => {
    if (!newTemplateName.trim()) return;
    
    const templateKey = newTemplateName.toLowerCase().replace(/\s+/g, '_');
    
    if (currentTemplates[templateKey]) {
      alert('A template with this name already exists');
      return;
    }

    const newTemplate = {
      name: newTemplateName,
      systemPrompt: `You are an expert entity extraction agent specialized in analyzing document content.
Your task is to identify and extract structured knowledge from documents with high accuracy.

Extraction Mode: ${templateKey}
Domain Context: Custom template for ${newTemplateName}

Focus on precision and relevance. Only extract entities you are confident about.`,
      
      instructionTemplate: `Analyze the following document content and extract entities and relationships.

TARGET ENTITY TYPES: person, organization, concept, technology, publication
TARGET RELATIONSHIP TYPES: AUTHORED, WORKS_AT, USES, CITES, RELATED_TO, DEVELOPED

EXTRACTION GUIDELINES:
- PERSON: Extract individuals mentioned in the document
- ORGANIZATION: Extract companies, institutions, groups
- CONCEPT: Extract key ideas, theories, methodologies
- TECHNOLOGY: Extract tools, frameworks, systems
- PUBLICATION: Extract papers, books, articles

Return ONLY valid JSON format:

{
  "entities": [
    {
      "id": "unique_entity_id",
      "name": "Entity Name", 
      "type": "entity_type",
      "properties": {"key": "value"},
      "confidence": 0.0-1.0
    }
  ],
  "relationships": [
    {
      "source": "source_entity_id",
      "target": "target_entity_id", 
      "type": "RELATIONSHIP_TYPE",
      "context": "Brief explanation",
      "confidence": 0.0-1.0
    }
  ],
  "metadata": {
    "total_entities": 0,
    "total_relationships": 0,
    "extraction_mode": "${templateKey}",
    "confidence_threshold": 0.7
  }
}

Document content:
{content}`,
      
      confidenceThreshold: 0.7,
      temperature: 0.1,
      maxTokens: 4096
    };

    updateTemplates(prev => ({
      ...prev,
      [templateKey]: newTemplate
    }));
    
    setActiveTemplate(templateKey);
    setNewTemplateName('');
    setShowNewTemplateDialog(false);
    setHasChanges(true);
  };

  const duplicateTemplate = (templateKey) => {
    const originalTemplate = currentTemplates[templateKey];
    const newKey = `${templateKey}_copy`;
    let copyNumber = 1;
    let finalKey = newKey;
    
    while (currentTemplates[finalKey]) {
      finalKey = `${newKey}_${copyNumber}`;
      copyNumber++;
    }

    const duplicatedTemplate = {
      ...originalTemplate,
      name: `${originalTemplate.name} (Copy${copyNumber > 1 ? ` ${copyNumber - 1}` : ''})`
    };

    updateTemplates(prev => ({
      ...prev,
      [finalKey]: duplicatedTemplate
    }));
    
    setActiveTemplate(finalKey);
    setHasChanges(true);
  };

  const deleteTemplate = (templateKey) => {
    if (Object.keys(currentTemplates).length <= 1) {
      alert('Cannot delete the last template');
      return;
    }

    if (!confirm(`Are you sure you want to delete the "${currentTemplates[templateKey].name}" template?`)) {
      return;
    }

    const newTemplates = { ...currentTemplates };
    delete newTemplates[templateKey];
    
    updateTemplates(newTemplates);
    
    // Switch to first available template
    const firstKey = Object.keys(newTemplates)[0];
    setActiveTemplate(firstKey);
    setHasChanges(true);
  };

  // Ensure activeTemplate exists in currentTemplates
  useEffect(() => {
    if (Object.keys(currentTemplates).length > 0 && !currentTemplates[activeTemplate]) {
      setActiveTemplate(Object.keys(currentTemplates)[0]);
    }
  }, [currentTemplates, activeTemplate]);

  const currentTemplate = currentTemplates[activeTemplate];

  // Don't render if no templates are available
  if (!currentTemplate) {
    return (
      <div className="p-8">
        <div className="max-w-6xl mx-auto">
          <div className="text-center text-gray-400">
            Loading templates...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold flex items-center space-x-2">
            <HiTemplate className="w-6 h-6 text-purple-400" />
            <span>Prompt Templates</span>
          </h2>
          
          <div className="flex items-center space-x-3">
            {hasChanges && (
              <span className="text-yellow-400 text-sm">Unsaved changes</span>
            )}
            <button
              onClick={resetToDefaults}
              className="px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded-lg flex items-center space-x-2"
            >
              <HiRefresh className="w-4 h-4" />
              <span>Reset</span>
            </button>
            <button
              onClick={saveTemplates}
              disabled={!hasChanges}
              className={`px-4 py-2 rounded-lg flex items-center space-x-2 ${
                hasChanges 
                  ? 'bg-blue-600 hover:bg-blue-700' 
                  : 'bg-gray-600 cursor-not-allowed'
              }`}
            >
              <HiSave className="w-4 h-4" />
              <span>Save Changes</span>
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Template Selector */}
          <div className="lg:col-span-1">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium">Templates</h3>
              <button
                onClick={() => setShowNewTemplateDialog(true)}
                className="p-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
                title="Create New Template"
              >
                <HiPlus className="w-4 h-4" />
              </button>
            </div>
            
            <div className="space-y-2">
              {Object.entries(currentTemplates).map(([key, template]) => (
                <div
                  key={key}
                  className={`border rounded-lg transition-colors ${
                    activeTemplate === key
                      ? 'border-blue-500 bg-blue-900/20'
                      : 'border-gray-600 bg-gray-800'
                  }`}
                >
                  <button
                    onClick={() => setActiveTemplate(key)}
                    className={`w-full text-left p-3 transition-colors ${
                      activeTemplate === key ? 'text-blue-400' : 'text-white hover:text-gray-300'
                    }`}
                  >
                    <div className="font-medium">{template.name}</div>
                    <div className="text-xs text-gray-400 mt-1 capitalize">{key} mode</div>
                  </button>
                  
                  {/* Template Actions */}
                  <div className="px-3 pb-3 flex items-center space-x-2">
                    <button
                      onClick={() => duplicateTemplate(key)}
                      className="text-xs px-2 py-1 bg-gray-700 hover:bg-gray-600 rounded flex items-center space-x-1"
                      title="Duplicate Template"
                    >
                      <HiDuplicate className="w-3 h-3" />
                      <span>Copy</span>
                    </button>
                    
                    {Object.keys(currentTemplates).length > 1 && (
                      <button
                        onClick={() => deleteTemplate(key)}
                        className="text-xs px-2 py-1 bg-red-700 hover:bg-red-600 rounded flex items-center space-x-1"
                        title="Delete Template"
                      >
                        <HiTrash className="w-3 h-3" />
                        <span>Delete</span>
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>

            {/* New Template Dialog */}
            {showNewTemplateDialog && (
              <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
                <div className="bg-gray-800 border border-gray-700 rounded-lg p-6 w-96">
                  <h4 className="text-lg font-medium mb-4">Create New Template</h4>
                  
                  <div className="mb-4">
                    <label className="block text-sm font-medium mb-2">Template Name</label>
                    <input
                      type="text"
                      value={newTemplateName}
                      onChange={(e) => setNewTemplateName(e.target.value)}
                      placeholder="Enter template name..."
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                      autoFocus
                    />
                  </div>
                  
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={createNewTemplate}
                      disabled={!newTemplateName.trim()}
                      className={`flex-1 px-4 py-2 rounded font-medium ${
                        newTemplateName.trim()
                          ? 'bg-blue-600 hover:bg-blue-700'
                          : 'bg-gray-600 cursor-not-allowed'
                      }`}
                    >
                      Create Template
                    </button>
                    <button
                      onClick={() => {
                        setShowNewTemplateDialog(false);
                        setNewTemplateName('');
                      }}
                      className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded font-medium"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Template Editor */}
          <div className="lg:col-span-3 space-y-6">
            {/* Template Settings */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h4 className="font-medium mb-4 flex items-center space-x-2">
                <HiCog className="w-5 h-5" />
                <span>Template Settings</span>
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Template Name</label>
                  <input
                    type="text"
                    value={currentTemplate.name}
                    onChange={(e) => handleTemplateChange(activeTemplate, 'name', e.target.value)}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Confidence Threshold</label>
                  <input
                    type="number"
                    min="0"
                    max="1"
                    step="0.1"
                    value={currentTemplate.confidenceThreshold}
                    onChange={(e) => handleTemplateChange(activeTemplate, 'confidenceThreshold', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Temperature</label>
                  <input
                    type="number"
                    min="0"
                    max="2"
                    step="0.05"
                    value={currentTemplate.temperature}
                    onChange={(e) => handleTemplateChange(activeTemplate, 'temperature', parseFloat(e.target.value))}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>
            </div>

            {/* System Prompt */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h4 className="font-medium mb-4">System Prompt</h4>
              <textarea
                value={currentTemplate.systemPrompt}
                onChange={(e) => handleTemplateChange(activeTemplate, 'systemPrompt', e.target.value)}
                rows={6}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                placeholder="Enter system prompt..."
              />
            </div>

            {/* Instruction Template */}
            <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
              <h4 className="font-medium mb-4 flex items-center space-x-2">
                <HiCode className="w-5 h-5" />
                <span>Instruction Template</span>
              </h4>
              <textarea
                value={currentTemplate.instructionTemplate}
                onChange={(e) => handleTemplateChange(activeTemplate, 'instructionTemplate', e.target.value)}
                rows={20}
                className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                placeholder="Enter instruction template..."
              />
              <div className="mt-2 text-xs text-gray-400">
                Use {`{content}`} placeholder for document content insertion
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptTemplateEditor;