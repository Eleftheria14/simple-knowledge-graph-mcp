#!/usr/bin/env python3
"""
Process PDF files using GROBID for superior academic analysis
GROBID-POWERED - specialized for research papers with citations and structured data
"""
import sys
import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

async def main():
    print("📚 GROBID Academic Literature Processing")
    print("=" * 60)
    
    # Set up Literature folder
    literature_folder = Path("/Users/aimiegarces/Agents/Literature")
    
    if not literature_folder.exists():
        print(f"❌ Literature folder not found: {literature_folder}")
        return
    
    # Find PDF files
    pdf_files = list(literature_folder.glob("*.pdf"))
    if not pdf_files:
        print(f"📁 No PDF files found in: {literature_folder}")
        return
    
    print(f"📁 Found {len(pdf_files)} PDF files:")
    for i, pdf in enumerate(pdf_files, 1):
        print(f"   {i}. {pdf.name}")
    
    # Check GROQ API key (still needed for entity extraction)
    groq_key = os.getenv('GROQ_API_KEY')
    
    if not groq_key:
        print("\n⚠️  Missing GROQ_API_KEY:")
        print("   ❌ GROQ_API_KEY needed for entity extraction")
        print("\n💡 Please set GROQ_API_KEY in .env file")
        return
    
    print(f"\n✅ GROQ API Key configured for entity extraction")
    print(f"   🤖 GROQ_API_KEY: {groq_key[:10]}...")
    
    # Check GROBID service
    try:
        from processor.tools.grobid_tool import GrobidProcessor
        grobid_processor = GrobidProcessor()
        
        if not grobid_processor.is_alive():
            print(f"\n❌ GROBID service not running!")
            print(f"   🐳 Start GROBID: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0")
            print(f"   🔍 Or check: curl http://localhost:8070/api/isalive")
            return
        
        print(f"✅ GROBID service running at http://localhost:8070")
        print(f"✅ Academic PDF processing with GROBID ready!")
        
    except Exception as e:
        print(f"❌ GROBID setup error: {e}")
        return
    
    # Load configurations - use GROBID processing
    try:
        from processor.config import ProcessorConfig
        from processor.orchestrator_config import OrchestratorConfig, WorkflowType
        from processor.entity_extractor_config import EntityExtractorConfig
        from tools.storage.enhanced_entity_storage import set_global_entity_config
        from processor.document_pipeline import DocumentOrchestrator
        
        print(f"\n🔧 Loading GROBID Processing Configurations...")
        
        # Base configuration
        base_config = ProcessorConfig()
        print(f"   ✅ Base config loaded")
        
        # GROBID orchestrator configuration
        orch_config = OrchestratorConfig.load_from_file('configs/orchestrator_grobid.yaml')
        print(f"   ✅ GROBID orchestrator config: {orch_config.processing_mode.value}")
        print(f"      Default workflow: {orch_config.default_workflow.value}")
        print(f"      Tools: {orch_config.enabled_tools}")
        
        # Academic entity extractor configuration
        entity_config = EntityExtractorConfig.load_from_file('configs/entity_extractor_academic.yaml')
        set_global_entity_config(entity_config)
        print(f"   ✅ Entity config: {entity_config.extraction_mode.value}")
        print(f"      Confidence threshold: {entity_config.global_confidence_threshold}")
        print(f"      Entity types: {[et.value for et in entity_config.get_enabled_entity_types()]}") 
        
        # Initialize orchestrator
        print(f"\n🤖 Initializing GROBID DocumentOrchestrator...")
        orchestrator = DocumentOrchestrator(base_config, orch_config)
        print(f"   ✅ Orchestrator ready with {len(orchestrator.tools)} tools")
        print(f"   🔧 GROBID tools: {[tool.name for tool in orchestrator.tools]}")
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Process each PDF with GROBID
    print(f"\n🚀 Starting GROBID Academic Processing...")
    print("=" * 60)
    
    processed = 0
    failed = 0
    total_academic_features = 0  # Track academic features extracted
    
    for i, pdf_file in enumerate(pdf_files, 1):
        print(f"\n📄 Processing {i}/{len(pdf_files)}: {pdf_file.name}")
        print("-" * 50)
        
        try:
            # Process with GROBID workflow
            print(f"🔄 Starting GROBID academic processing...")
            result = await orchestrator.process_document(
                str(pdf_file), 
                WorkflowType.RESEARCH_PAPER
            )
            
            print(f"\n📊 Processing Results for {pdf_file.name}:")
            print(f"   ✅ Success: {result.get('success', False)}")
            print(f"   🚀 Workflow: {result.get('workflow_used', 'unknown')}")
            print(f"   🔧 Tools used: {result.get('tools_used', [])}")
            print(f"   📝 Steps: {result.get('processing_steps', 0)}")
            
            if result.get('success'):
                processed += 1
                
                # Estimate academic features extracted
                academic_features = 0
                if 'grobid_extract' in result.get('tools_used', []):
                    academic_features += 5  # Title, authors, structure, etc.
                if 'extract_and_store_entities' in result.get('tools_used', []):
                    academic_features += 3  # Entities, relationships, concepts
                total_academic_features += academic_features
                
                print(f"   🎉 {pdf_file.name} processed with GROBID!")
                print(f"   🎓 Academic features extracted: ~{academic_features}")
                
                # Show success criteria if available
                if 'success_criteria_met' in result:
                    criteria = result['success_criteria_met']
                    print(f"   ✅ Success criteria met: {criteria}")
                
            else:
                failed += 1
                error = result.get('error', 'Unknown error')
                print(f"   ❌ {pdf_file.name} failed: {error}")
            
            # Show agent response preview
            if result.get('agent_response'):
                response_preview = str(result['agent_response'])[:200].replace('\n', ' ')
                print(f"   💬 Agent response: {response_preview}...")
                
        except Exception as e:
            failed += 1
            print(f"   ❌ Exception processing {pdf_file.name}: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 50)
    
    # Final summary
    print(f"\n🏁 GROBID Academic Processing Complete!")
    print("=" * 60)
    print(f"📊 Final Results:")
    print(f"   ✅ Successfully processed: {processed}")
    print(f"   ❌ Failed: {failed}")
    print(f"   📁 Total files: {len(pdf_files)}")
    print(f"   🎓 Academic features extracted: ~{total_academic_features}")
    
    if processed > 0:
        print(f"\n🎉 {processed} research papers processed with GROBID and added to your knowledge graph!")
        print(f"💡 You can now query for:")
        print(f"   👥 Author collaboration networks")
        print(f"   🔗 Citation relationships between papers")
        print(f"   📊 Research methodologies and concepts")
        print(f"   🏛️  Institutional affiliations and connections")
        print(f"🚀 All processing done with GROBID's superior academic understanding!")
    
    if failed > 0:
        print(f"\n⚠️  {failed} files failed processing. Check the error messages above for details.")
        print(f"💡 Ensure GROBID service is running: docker run -d -p 8070:8070 lfoppiano/grobid:0.8.0")

if __name__ == "__main__":
    asyncio.run(main())