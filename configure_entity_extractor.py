#!/usr/bin/env python3
"""
Interactive configuration tool for the Entity Extractor Agent
Create, edit, and manage entity extraction configurations
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

from processor.entity_extractor_config import (
    EntityExtractorConfig, EntityType, RelationshipType, ExtractionMode,
    create_default_config, create_academic_config, create_fast_config
)
from tools.storage.enhanced_entity_storage import set_global_entity_config

def main():
    print("🧠 Entity Extractor Configuration Tool")
    print("=" * 50)
    
    print("\n📋 Available Actions:")
    print("1. Create default entity extraction configuration")
    print("2. Create academic research configuration") 
    print("3. Create fast extraction configuration")
    print("4. Load and test existing configuration")
    print("5. View configuration templates")
    print("6. Test extraction with different configs")
    print("7. Exit")
    
    while True:
        choice = input("\n👉 Select action (1-7): ").strip()
        
        if choice == "1":
            create_and_save_config("default", create_default_config())
        elif choice == "2":
            create_and_save_config("academic", create_academic_config())
        elif choice == "3":
            create_and_save_config("fast", create_fast_config())
        elif choice == "4":
            load_and_test_config()
        elif choice == "5":
            view_templates()
        elif choice == "6":
            test_configurations()
        elif choice == "7":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please select 1-7.")

def create_and_save_config(config_type: str, config: EntityExtractorConfig):
    """Create and save an entity extraction configuration"""
    print(f"\n🔨 Creating {config_type} entity extraction configuration...")
    
    # Show configuration summary
    print(f"📊 Configuration Summary:")
    print(f"   🤖 Model: {config.model_name}")
    print(f"   🌡️  Temperature: {config.temperature}")
    print(f"   🔧 Mode: {config.extraction_mode.value}")
    print(f"   🎯 Confidence: {config.global_confidence_threshold}")
    print(f"   📋 Entity Types: {[et.value for et in config.get_enabled_entity_types()]}")
    print(f"   🔗 Relationships: {len(config.enabled_relationship_types)}")
    
    # Ask for filename
    default_filename = f"configs/entity_extractor_{config_type}.yaml"
    filename = input(f"\n💾 Save as [{default_filename}]: ").strip()
    if not filename:
        filename = default_filename
    
    # Ensure configs directory exists
    Path("configs").mkdir(exist_ok=True)
    
    try:
        config.save_to_file(filename)
        print(f"✅ Configuration saved to: {filename}")
        
        # Show usage instructions
        print(f"\n📖 Usage:")
        print(f"   from processor.entity_extractor_config import EntityExtractorConfig")
        print(f"   config = EntityExtractorConfig.load_from_file('{filename}')")
        print(f"   from tools.storage.enhanced_entity_storage import set_global_entity_config")
        print(f"   set_global_entity_config(config)")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")


def load_and_test_config():
    """Load existing config and test it"""
    print("\n📂 Load and Test Configuration")
    
    # List available configs
    configs_dir = Path("configs")
    if configs_dir.exists():
        config_files = list(configs_dir.glob("entity_extractor_*.yaml"))
        if config_files:
            print("Available entity extractor configurations:")
            for i, config_file in enumerate(config_files, 1):
                print(f"   {i}. {config_file.name}")
            
            try:
                choice = int(input(f"\nSelect config (1-{len(config_files)}): "))
                if 1 <= choice <= len(config_files):
                    config_file = config_files[choice - 1]
                    test_single_config(str(config_file))
                else:
                    print("❌ Invalid selection")
            except ValueError:
                print("❌ Please enter a number")
        else:
            print("⚠️  No entity extractor configuration files found in configs/")
    else:
        print("⚠️  configs/ directory not found")

def test_single_config(config_file: str):
    """Test a single configuration"""
    try:
        config = EntityExtractorConfig.load_from_file(config_file)
        print(f"\n✅ Loaded: {config_file}")
        
        # Show config details
        print(f"\n📊 Configuration Details:")
        print(f"   🤖 Model: {config.model_name} (temp: {config.temperature})")
        print(f"   🔧 Mode: {config.extraction_mode.value}")
        print(f"   🎯 Confidence: {config.global_confidence_threshold}")
        print(f"   📋 Entity Types: {[et.value for et in config.get_enabled_entity_types()]}")
        print(f"   🔗 Relationships: {[rt.value for rt in config.enabled_relationship_types]}")
        
        # Test with sample content
        if input("\n🧪 Test with sample content? (y/N): ").lower().startswith('y'):
            test_content = """
            This paper introduces the Transformer architecture by Vaswani et al. from Google Research.
            The Transformer uses self-attention mechanisms and has revolutionized natural language processing.
            It was published in "Attention is All You Need" in 2017 at NeurIPS.
            The architecture has been adopted by BERT, GPT, and other modern language models.
            """
            
            print("\n🔄 Testing extraction...")
            set_global_entity_config(config)
            
            from tools.storage.enhanced_entity_storage import extract_and_store_entities
            result = extract_and_store_entities.invoke({
                "content": test_content,
                "document_info": {"title": "Test Document", "type": "test"}
            })
            
            print(f"\n📊 Test Results:")
            print(f"   ✅ Success: {result['success']}")
            print(f"   🔍 Entities: {result['entities_found']}")
            print(f"   🔗 Relationships: {result['relationships_found']}")
            print(f"   🤖 Model Used: {result['configuration_used']['model_name']}")
            print(f"   🔧 Mode: {result['configuration_used']['extraction_mode']}")
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")

def test_configurations():
    """Test multiple configurations with the same content"""
    print("\n🧪 Configuration Comparison Test")
    
    test_content = input("\nEnter test content (or press Enter for default): ").strip()
    if not test_content:
        test_content = """
        This paper introduces the Transformer architecture by Vaswani et al. from Google Research.
        The Transformer uses self-attention mechanisms and has revolutionized natural language processing.
        It was published in "Attention is All You Need" in 2017 at NeurIPS.
        The architecture has been adopted by BERT, GPT, and other modern language models developed by OpenAI.
        """
    
    # Test with different configurations
    configs_to_test = [
        ("Default", create_default_config()),
        ("Academic", create_academic_config()), 
        ("Fast", create_fast_config())
    ]
    
    print(f"\n🔄 Testing {len(configs_to_test)} configurations...")
    print("=" * 60)
    
    from tools.storage.enhanced_entity_storage import extract_and_store_entities
    
    for config_name, config in configs_to_test:
        print(f"\n📋 Testing {config_name} Configuration:")
        print(f"   🤖 Model: {config.model_name} (temp: {config.temperature})")
        print(f"   🔧 Mode: {config.extraction_mode.value}")
        print(f"   🎯 Confidence: {config.global_confidence_threshold}")
        
        try:
            set_global_entity_config(config)
            result = extract_and_store_entities.invoke({
                "content": test_content,
                "document_info": {"title": f"Test - {config_name}", "type": "test"}
            })
            
            print(f"   📊 Results:")
            print(f"      ✅ Success: {result['success']}")
            print(f"      🔍 Entities: {result['entities_found']}")
            print(f"      🔗 Relationships: {result['relationships_found']}")
            
            if result.get('metadata'):
                print(f"      📈 Raw Entities: {result['raw_entities_count']}")
                print(f"      🔽 Filtered: {result['raw_entities_count'] - result['entities_found']} removed")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("💡 Compare the results to see how different configurations affect extraction!")

def view_templates():
    """View available configuration templates"""
    print("\n📋 Entity Extractor Configuration Templates:")
    print("=" * 50)
    
    print("\n1. 🔧 Default Configuration:")
    print("   - Comprehensive entity extraction")
    print("   - Person, organization, concept, technology, publication")
    print("   - Balanced confidence thresholds (0.7-0.8)")
    print("   - Good for general document processing")
    
    print("\n2. 🎓 Academic Configuration:")
    print("   - Optimized for research papers")
    print("   - Higher confidence thresholds (0.8-0.9)")
    print("   - Focus on authors, citations, methodologies")
    print("   - Includes academic relationships (AUTHORED, CITES)")
    print("   - Lower temperature (0.05) for precision")
    
    print("\n3. ⚡ Fast Configuration:")
    print("   - Quick extraction with minimal processing")
    print("   - High confidence threshold (0.8)")
    print("   - Limited entity types (person, organization, concept)")
    print("   - Shorter content analysis (2000 chars)")
    print("   - Fewer retry attempts")
    
    print("\n🎛️  Configuration Options:")
    print("   - Model: Choose LLM model and temperature")
    print("   - Entity Types: Enable/disable specific types")
    print("   - Confidence: Set thresholds per entity type")
    print("   - Relationships: Configure relationship extraction")
    print("   - Prompts: Customize extraction instructions")
    print("   - Performance: Retry logic and timeout settings")
    
    print("\n💡 All templates can be loaded, customized, and saved for your specific needs.")

if __name__ == "__main__":
    main()