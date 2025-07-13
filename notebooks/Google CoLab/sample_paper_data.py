# Sample paper data for testing the knowledge graph system
# This simulates what would be extracted from a real research paper

SAMPLE_PAPER_DATA = {
    "title": "Machine Learning for Drug Discovery: A Comprehensive Review",
    "content": """
Machine Learning for Drug Discovery: A Comprehensive Review

Authors: Dr. Sarah Chen (MIT), Prof. Michael Torres (Stanford), Dr. Lisa Wang (UC Berkeley)

Abstract:
This comprehensive review examines the application of machine learning techniques to drug discovery processes. 
We analyze various computational approaches including deep learning, graph neural networks, and transformer 
architectures for molecular property prediction and drug-target interaction modeling.

Introduction:
Drug discovery is a complex and expensive process that traditionally takes 10-15 years and costs billions of dollars. 
Machine learning has emerged as a powerful tool to accelerate various stages of this process, from initial target 
identification to clinical trial optimization. Recent advances in artificial intelligence, particularly deep learning 
and graph-based methods, have shown remarkable promise in predicting molecular properties, identifying potential 
drug candidates, and understanding biological mechanisms.

Methods:
We conducted a systematic review of machine learning applications in drug discovery, focusing on:

1. Molecular Property Prediction
- Graph Convolutional Networks (GCNs) for molecular representation
- Transformer models adapted for SMILES sequences
- Recurrent Neural Networks for sequential molecular data
- Support Vector Machines for classical QSAR modeling

2. Drug-Target Interaction Prediction
- Matrix factorization techniques
- Deep neural networks with protein sequence embeddings
- Graph-based approaches combining molecular and protein structures
- Ensemble methods for improved prediction accuracy

3. Virtual Screening and Lead Optimization
- Generative adversarial networks for novel molecule design
- Reinforcement learning for molecular optimization
- Variational autoencoders for chemical space exploration
- Multi-objective optimization algorithms

Datasets and Benchmarks:
Our analysis covers major datasets used in computational drug discovery:

- ChEMBL: Large-scale bioactivity database with 2.2M compounds
- PubChem: Comprehensive chemical information resource
- ZINC: Collection of commercially available compounds for virtual screening
- QM9: Quantum mechanical properties for 134K small molecules
- Tox21: Toxicity data from environmental health screening
- SIDER: Side effect information for marketed drugs
- DrugBank: Comprehensive drug and drug target database

Technologies and Tools:
The review encompasses various software frameworks and computational tools:

- Deep Learning: TensorFlow, PyTorch, Keras
- Cheminformatics: RDKit, OpenEye, ChemAxon
- Molecular Modeling: Schrödinger Suite, MOE, AMBER
- Graph Processing: DGL, PyTorch Geometric, NetworkX
- Cloud Computing: AWS, Google Cloud, Microsoft Azure
- Visualization: ChimeraX, PyMOL, VMD

Results and Applications:
Machine learning has demonstrated significant impact across multiple drug discovery applications:

1. Target Identification and Validation
- Genomic data analysis for disease mechanism understanding
- Protein-protein interaction network analysis
- Biomarker discovery using omics integration
- Disease phenotype prediction from molecular signatures

2. Hit Discovery and Lead Identification
- Virtual high-throughput screening acceleration
- Novel scaffold identification through generative models
- Fragment-based drug design optimization
- Natural product-inspired molecule generation

3. Lead Optimization and ADMET Prediction
- Absorption, Distribution, Metabolism, Excretion, Toxicity (ADMET) modeling
- Drug-drug interaction prediction
- Solubility and permeability optimization
- Selectivity enhancement through structure-activity relationships

4. Clinical Trial Design and Patient Stratification
- Biomarker-driven patient selection
- Adverse event prediction and monitoring
- Dose optimization using pharmacokinetic modeling
- Trial endpoint prediction and success probability estimation

Challenges and Future Directions:
Despite significant progress, several challenges remain in applying machine learning to drug discovery:

- Data quality and standardization issues
- Limited availability of negative control data
- Interpretability of complex deep learning models
- Integration of multi-modal biological data
- Regulatory acceptance of AI-driven predictions
- Reproducibility and validation across different datasets

The field is rapidly evolving with emerging trends including:
- Foundation models for molecular and protein representation
- Federated learning for collaborative drug discovery
- Causal inference methods for mechanism understanding
- Quantum machine learning for molecular simulation
- Digital twins for personalized medicine approaches

Conclusions:
Machine learning has fundamentally transformed drug discovery by enabling more efficient exploration of chemical 
and biological space. The integration of diverse data types, advanced algorithmic approaches, and high-performance 
computing infrastructure continues to accelerate the identification and development of new therapeutic compounds. 
Future success will depend on continued collaboration between computational scientists, medicinal chemists, and 
clinical researchers to translate algorithmic advances into improved patient outcomes.

Funding and Acknowledgments:
This work was supported by NIH grants R01-GM123456 and R01-AI789012, NSF Award CHE-2021001, and the 
MIT-Harvard Center for AI in Drug Discovery. We thank our collaborators at Roche, Novartis, and 
Genentech for valuable discussions and data sharing agreements.

References:
[1] Chen, S. et al. "Deep learning for molecular property prediction" Nature Methods 18, 123-135 (2021)
[2] Torres, M. et al. "Graph neural networks in drug discovery" Cell Chemical Biology 28, 456-468 (2021)
[3] Wang, L. et al. "Transformer models for chemical informatics" JACS 143, 789-801 (2021)
""",
    "pages": 12,
    "char_count": 4892
}

# Pre-extracted entities that would come from LLM processing
SAMPLE_ENTITIES = {
    "authors": [
        "Dr. Sarah Chen",
        "Prof. Michael Torres", 
        "Dr. Lisa Wang",
        "Chen, S.",
        "Torres, M.",
        "Wang, L."
    ],
    "institutions": [
        "MIT",
        "Stanford", 
        "UC Berkeley",
        "MIT-Harvard Center for AI in Drug Discovery",
        "Roche",
        "Novartis",
        "Genentech"
    ],
    "methods": [
        "Graph Convolutional Networks",
        "Transformer models",
        "Recurrent Neural Networks",
        "Support Vector Machines",
        "Matrix factorization",
        "Deep neural networks",
        "Generative adversarial networks",
        "Reinforcement learning",
        "Variational autoencoders",
        "Ensemble methods"
    ],
    "concepts": [
        "Drug discovery",
        "Machine learning",
        "Molecular property prediction",
        "Drug-target interaction",
        "Virtual screening",
        "Lead optimization",
        "ADMET prediction",
        "Clinical trial design",
        "Patient stratification",
        "QSAR modeling"
    ],
    "datasets": [
        "ChEMBL",
        "PubChem", 
        "ZINC",
        "QM9",
        "Tox21",
        "SIDER",
        "DrugBank"
    ],
    "technologies": [
        "TensorFlow",
        "PyTorch",
        "Keras",
        "RDKit",
        "OpenEye",
        "ChemAxon",
        "Schrödinger Suite",
        "MOE",
        "AMBER",
        "DGL",
        "PyTorch Geometric",
        "NetworkX",
        "AWS",
        "Google Cloud",
        "Microsoft Azure"
    ]
}