# 🚀 Quick Start Guide

## Simple Scientific Paper RAG + Knowledge Graph

**Get started in 5 minutes!** Analyze papers with AI using natural language chat.

---

## ⚡ Quick Setup

### 1. **Activate Environment**
```bash
source langchain-env/bin/activate
```

### 2. **Install Dependencies** (if needed)
```bash
pip install -r requirements.txt
```

### 3. **Start Ollama** (Required!)
```bash
# Make sure these models are installed:
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

### 4. **Open Notebook**
```bash
jupyter notebook notebooks/Simple_Paper_RAG_Chat.ipynb
```

---

## 💬 How to Use

### **Step 1: Load Your Paper**
```python
# Change this to your PDF path
pdf_path = "path/to/your/paper.pdf"
chat_system = analyze_paper_with_chat(pdf_path)
```

### **Step 2: Ask Questions**
```python
response = chat_system.chat("What are the main findings?")
print(response['answer'])
```

### **Step 3: Explore Entities**
```python
entities = chat_system.get_entities()
print(entities)
```

---

## 🎯 Example Questions

### **Content Questions (RAG):**
- "What are the main findings?"
- "Explain the methodology"
- "What were the results?"
- "How does this compare to other work?"

### **Entity Questions (Knowledge Graph):**
- "Who are the authors?"
- "What methods were used?"
- "What concepts are important?"
- "How are the methods related?"

### **Combined Questions:**
- "Tell me about [specific method] and how it's used"
- "What are the key concepts and their relationships?"

---

## 🔧 What It Does

### **🤖 RAG (Retrieval-Augmented Generation)**
- Chunks your paper into 499 pieces
- Creates semantic embeddings
- Finds relevant content for your questions
- Generates intelligent answers

### **🕸️ Knowledge Graph** 
- Extracts entities: authors, methods, concepts, metrics
- Finds relationships between entities
- Enables entity-based exploration
- Shows connections in your paper

### **💬 Intelligent Chat**
- Auto-detects if you need RAG or Graph
- Routes questions to best system
- Combines information intelligently
- Maintains conversation context

---

## 📊 Performance

**Your test results:**
- ✅ **Paper Processing**: ~30-60 seconds
- ✅ **Knowledge Graph**: 19 entities, 6 relationships  
- ✅ **RAG Chunks**: 499 chunks created
- ✅ **Query Speed**: ~3-5 seconds per question

---

## 🎯 Perfect For

- **📚 Research**: Understand complex papers quickly
- **🔍 Literature Review**: Extract key insights efficiently
- **🧠 Learning**: Explore new concepts and methods
- **📝 Writing**: Get properly formatted citations
- **🔗 Discovery**: Find connections between ideas

---

## 🚀 Next Steps

1. **Try the example paper** first to understand the workflow
2. **Load your own PDFs** - any scientific paper works
3. **Experiment with questions** - be specific for better answers
4. **Explore entities** - discover the paper's structure
5. **Use for research** - build your personal AI research assistant

---

## 💡 Tips

- **Be specific** in questions for better answers
- **Try different question types** (factual vs analytical)
- **Explore entities** to understand paper structure
- **Use follow-up questions** to dive deeper
- **The system learns** from your conversation!

---

## 🔧 Troubleshooting

**Import errors?**
```bash
pip install langgraph networkx
```

**Ollama not working?**
```bash
ollama serve
ollama list  # Check models installed
```

**PDF not loading?**
- Check file path is correct
- Ensure PDF is readable (not corrupted)
- Try a different PDF first

---

**🎉 Happy researching with AI!**

Your personal scientific paper intelligence system is ready to transform how you read and understand research papers.