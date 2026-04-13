# scripts/category_normalization_rules.py

CATEGORY_NORMALIZATION_MAP = {
    # --- 時間的・動的グラフ ---
    'dynamic graphs': 'Temporal & Dynamic Graphs',
    'temporal graphs': 'Temporal & Dynamic Graphs',
    'spatiotemporal graphs': 'Temporal & Dynamic Graphs',
    'spatio-temporal graphs': 'Temporal & Dynamic Graphs',
    'spatio-temporal hypergraphs': 'Temporal & Dynamic Graphs', # Hypergraphs との関連も考慮
    'time series': 'Temporal & Dynamic Graphs',
    'temporal data': 'Temporal & Dynamic Graphs',
    'dynamic spiking': 'Temporal & Dynamic Graphs', # Spiking Neural Networks とも関連
    'trajectories': 'Temporal & Dynamic Graphs', # Object Tracking とも関連
    'human motion': 'Temporal & Dynamic Graphs', # Human Action/Pose とも関連
    'motion understanding': 'Temporal & Dynamic Graphs',
    'traffic forecasting': 'Temporal & Dynamic Graphs',

    # --- 大規模言語モデル (LLMs) ---
    'llms': 'Language Models (LLMs)',
    'large language models': 'Language Models (LLMs)',
    'language models': 'Language Models (LLMs)',
    'language models in recommendation': 'LLMs in Recommender Systems',
    'language models for recommendation': 'LLMs in Recommender Systems',
    'llm prompting': 'Prompting & LLMs',
    'llm reasoning': 'Reasoning with LLMs',
    'graph of thought': 'Reasoning with LLMs', # LLMの一種
    'llms + knowledge graphs': 'Knowledge Graphs & LLMs',
    'knowledge graphs + llms': 'Knowledge Graphs & LLMs',
    'graph language models': 'Language Models (LLMs)', # GNNs for NLP / Graph-based LLMs
    'llm benchmarks': 'Benchmarks & Datasets', # LLM specific benchmark

    # --- 知識グラフ (KGs) ---
    'knowledge graphs': 'Knowledge Graphs',
    'kgc': 'Knowledge Graph Completion', # 略語
    'knowledge graph completion': 'Knowledge Graph Completion',
    'knowledge graph reasoning': 'Knowledge Graph Reasoning',
    'knowledge graph question answering': 'KG Question Answering',
    'knowledge question answering': 'KG Question Answering', # 揺れ
    'temporal knowledge graphs': 'Temporal Knowledge Graphs',
    'multimodal knowledge graphs': 'Multimodal Knowledge Graphs',
    'entity alignment': 'Knowledge Graph Alignment',
    'inductive relation prediction': 'Knowledge Graph Reasoning', # Inductive Learningも含む
    'knowledge & reasoning': 'Knowledge Graph Reasoning', # 一般的すぎるときは注意

    # --- 自己教師あり・対照学習 ---
    'self-supervision': 'Self-Supervised & Contrastive Learning',
    'self supervision': 'Self-Supervised & Contrastive Learning', # 揺れ
    'contrastive learning': 'Self-Supervised & Contrastive Learning',
    'graph contrastive learning': 'Self-Supervised & Contrastive Learning',
    'unsupervised learning': 'Self-Supervised & Contrastive Learning', # 集約

    # --- 解釈性・説明可能性 ---
    'explainability': 'Interpretability & Explainability',
    'interpretability': 'Interpretability & Explainability',

    # --- 分類・クラスタリングタスク ---
    'node classification': 'Node & Graph Classification/Clustering',
    'graph classification': 'Node & Graph Classification/Clustering',
    'graph clustering': 'Node & Graph Classification/Clustering',
    'clustering': 'Node & Graph Classification/Clustering', # 一般的すぎる場合あり
    'multi-view clustering': 'Multi-View Learning', # Multi-view learningに集約

    # --- 分子・化学・生物情報学 ---
    'molecules': 'Molecular & Chemical Modeling',
    'proteins': 'Molecular & Chemical Modeling',
    'drug interaction': 'Molecular & Chemical Modeling',
    'conformer generation': 'Molecular & Chemical Modeling',
    'atoms': 'Molecular & Chemical Modeling',
    'materials science': 'Molecular & Chemical Modeling',
    'diffusion for molecules': 'Diffusion Models for Molecules', # Diffusionのサブカテゴリ
    'bioinformatics': 'Bioinformatics & Healthcare', # より広範
    'rna': 'Bioinformatics & Healthcare',
    'diseases': 'Bioinformatics & Healthcare',
    'histopathalogy': 'Bioinformatics & Healthcare',
    'healthcare': 'Bioinformatics & Healthcare',
    'quantum chemistry': 'Molecular & Chemical Modeling',

    # --- GNNの課題と特性 ---
    'oversmoothing': 'GNN Challenges (Oversmoothing, Oversquashing, etc.)',
    'oversquashing': 'GNN Challenges (Oversmoothing, Oversquashing, etc.)',
    'oversmoothing, oversquashing': 'GNN Challenges (Oversmoothing, Oversquashing, etc.)',
    'smoothing': 'GNN Challenges (Oversmoothing, Oversquashing, etc.)', # Oversmoothingに集約
    'long-range dependencies': 'GNN Challenges (Long-Range Dependencies)',
    'label noise': 'GNN Challenges (Label Noise & Imbalance)',
    'class-imbalanced learning': 'GNN Challenges (Label Noise & Imbalance)',
    'imbalanced data': 'GNN Challenges (Label Noise & Imbalance)',
    'homophily and heterophily': 'GNN Challenges (Homophily & Heterophily)',
    'homophily, heterophily': 'GNN Challenges (Homophily & Heterophily)', # 揺れ
    'heterophilic graphs': 'GNN Challenges (Homophily & Heterophily)',
    'heterophily': 'GNN Challenges (Homophily & Heterophily)',
    'expressivity': 'GNN Expressive Power',
    'expressivity, generalisation': 'GNN Expressive Power & Generalization', # Generalizationと分離も検討
    'equivariance': 'Equivariance & Invariance',
    'invariance': 'Equivariance & Invariance',
    'homomorphism expressivity': 'GNN Expressive Power',
    'curvature': 'Geometric Deep Learning', # Non-Euclideanに含めるか
    'snowflake hypothesis': 'Theoretical Understanding of GNNs', # 理論系

    # --- 分散・連合・スケーラビリティ ---
    'federated learning': 'Distributed & Federated Learning',
    'subgraph federated learning': 'Distributed & Federated Learning',
    'scalability': 'Scalability & Efficiency',
    'scalablility': 'Scalability & Efficiency', # タイポ
    'scalablility on molecules': 'Scalability for Molecular Modeling', # 分離
    'coarsening': 'Scalability & Efficiency', # Graph Coarsening
    'graph pooling': 'Graph Pooling & Readouts', # Poolingも効率化/表現学習の一部

    # --- 推薦システム ---
    'recommendation': 'Recommender Systems',
    'collaborative filtering': 'Recommender Systems',
    'sequential recommendation': 'Recommender Systems',
    'basket recommendation': 'Recommender Systems',
    'cross-domain recommendation': 'Recommender Systems',
    'out-of-distribution recommendation': 'Recommender Systems', # OODと組み合わせ

    # --- 堅牢性・敵対的攻撃・プライバシー・公平性 ---
    'adversarial attacks': 'Robustness & Adversarial Methods',
    'robustness': 'Robustness & Adversarial Methods',
    'privacy': 'Privacy, Fairness & Ethics',
    'fairness': 'Privacy, Fairness & Ethics',
    'ethical ai': 'Privacy, Fairness & Ethics',
    'trustworthiness': 'Privacy, Fairness & Ethics', # より広範

    # --- 3Dビジョン・点群・メッシュ ---
    '3d data': '3D Vision & Geometric DL',
    '3d scenes': '3D Vision & Geometric DL',
    '3d shapes': '3D Vision & Geometric DL',
    'point clouds': '3D Vision & Geometric DL',
    'meshes': '3D Vision & Geometric DL',
    'lidar': '3D Vision & Geometric DL',
    'hypergraphs for 3d object retrieval': '3D Vision & Geometric DL', # Hypergraphとの組み合わせ

    # --- シーン理解・視覚関係 ---
    'scene graphs': 'Scene Understanding & VQA',
    'scene graph generation': 'Scene Understanding & VQA',
    'visual relationships': 'Scene Understanding & VQA',
    'image understanding': 'Computer Vision Applications', # より一般的

    # --- マルチモーダル学習 (Vision & Languageなど) ---
    'visual question answering': 'Multimodal Learning (Vision & Language)',
    'vision + language': 'Multimodal Learning (Vision & Language)',
    'vision+text': 'Multimodal Learning (Vision & Language)', # 揺れ
    'multiple modalities': 'Multimodal Learning (Vision & Language)',
    'multimodal inferential understanding': 'Multimodal Learning (Vision & Language)',
    'text-to graph': 'Multimodal Learning (Vision & Language)', # Text-to-Imageなども含む可能性

    # --- グラフ構造学習・推論 ---
    'graph structure learning': 'Graph Structure Learning & Inference',
    'latent graph inference': 'Graph Structure Learning & Inference',
    'structure learning': 'Graph Structure Learning & Inference', # 揺れ

    # --- GNNアーキテクチャ・コンポーネント ---
    'transformers': 'Graph Transformers & Attention', # Attentionも集約
    'graph transformers': 'Graph Transformers & Attention',
    'attention': 'Graph Transformers & Attention',
    'graph diffusion': 'Diffusion Models on Graphs', # Diffusion
    'diffusion models': 'Diffusion Models on Graphs',
    'diffusion': 'Diffusion Models on Graphs',
    'flow matching': 'Diffusion Models on Graphs', # Diffusionの一種
    'flow-based modelling': 'Diffusion Models on Graphs', # 揺れ
    'hypergraphs': 'Hypergraphs & Higher-Order Models',
    'higher-order relationships': 'Hypergraphs & Higher-Order Models',
    'hypergraph': 'Hypergraphs & Higher-Order Models', # 単数形
    'simplex': 'Topological Deep Learning', # Simplicial Complexes
    'kernels': 'Graph Kernels',
    'kernel methods': 'Graph Kernels',
    'spectral methods': 'Spectral Graph Methods',
    'wavelet networks': 'Spectral Graph Methods', # Wavelets
    'graph ode': 'Continuous Graph Models (ODEs, PDEs)',
    'differential equations': 'Continuous Graph Models (ODEs, PDEs)',
    'continuous frameworks': 'Continuous Graph Models (ODEs, PDEs)',
    'non-eucledian geometry': 'Geometric Deep Learning', # Curvature, Hyperbolicなど
    'non-euclidean networks': 'Geometric Deep Learning',
    'positional encodings': 'Positional & Structural Encodings',
    'recurrent models': 'Recurrent Graph Neural Networks',
    'graph autoencoders': 'Graph Autoencoders', # Autoencodersの揺れ
    'autoencoders': 'Graph Autoencoders',

    # --- 学習パラダイム・戦略 ---
    'out-of-distribution': 'Generalization & Out-of-Distribution',
    'generalisability': 'Generalization & Out-of-Distribution',
    'distribution shifts': 'Generalization & Out-of-Distribution', # OODに集約
    'domain adaptation': 'Domain Adaptation & Transfer Learning',
    'transferability': 'Domain Adaptation & Transfer Learning',
    'transfer learning': 'Domain Adaptation & Transfer Learning',
    'pre-training': 'Pre-training & Foundation Models',
    'pretraining': 'Pre-training & Foundation Models', # 揺れ
    'graph foundation models': 'Pre-training & Foundation Models',
    'prompting': 'Prompting for GNNs', # LLM Prompting とは区別も
    'fine-tuning': 'Fine-Tuning GNNs',
    'active learning': 'Active Learning on Graphs',
    'training strategies': 'GNN Training Strategies',
    'training': 'GNN Training Strategies', # 一般的すぎるときは注意
    'data augmentation': 'Data Augmentation for Graphs',
    'augmentation': 'Data Augmentation for Graphs', # 揺れ
    'distillation': 'Knowledge Distillation for GNNs',
    'knowledge distillation': 'Knowledge Distillation for GNNs', # 揺れ
    'architecture search': 'Neural Architecture Search for GNNs',
    'hyperparameters': 'Hyperparameter Optimization',
    'simplified models': 'GNN Simplification & Efficiency',
    'unlearning': 'Machine Unlearning on Graphs',
    'class-incremental learning': 'Continual & Incremental Learning',

    # --- ドメイン特化応用 ---
    'causality': 'Causal Inference on Graphs',
    'causal perspective': 'Causal Inference on Graphs',
    'causal graphs': 'Causal Inference on Graphs',
    'anomaly detection': 'Graph Anomaly Detection',
    'graph anomaly detection': 'Graph Anomaly Detection', # 揺れ
    'outlier detection': 'Graph Anomaly Detection',
    'link prediction': 'Link Prediction',
    'graph generation': 'Graph Generative Models',
    'generative models': 'Graph Generative Models', # 揺れ
    'stochastic block models': 'Graph Generative Models', # SBM
    'reinforcement learning': 'Reinforcement Learning on Graphs',
    'combinatorial optimisation': 'Combinatorial Optimization on Graphs',
    'combinatorial optimization': 'Combinatorial Optimization on Graphs', # 揺れ
    'linear programs': 'Combinatorial Optimization on Graphs', # LP
    'linear programming': 'Combinatorial Optimization on Graphs', # 揺れ
    'mixed-integer linear programming': 'Combinatorial Optimization on Graphs', # MILP
    'planning': 'Planning with Graphs',
    'computer vision': 'Computer Vision Applications of GNNs',
    'vision': 'Computer Vision Applications of GNNs', # 一般的
    'natural language processing': 'NLP Applications of GNNs',
    'videos': 'Video Analysis with Graphs',
    'urban environments': 'Urban & Geospatial Applications',
    'urban planning': 'Urban & Geospatial Applications',
    'brain networks': 'Neuroscience Applications (Brain Networks)',
    'physics': 'Physics & Science Applications',
    'quantum computing': 'Quantum Computing & GNNs',
    'multi-agent systems': 'Multi-Agent Systems & Robotics',
    'multi-agent learning': 'Multi-Agent Systems & Robotics', # 揺れ
    'robotics': 'Multi-Agent Systems & Robotics',
    'tracking': 'Object Tracking with Graphs',
    'matching': 'Graph Matching',
    'graph matching': 'Graph Matching', # 揺れ
    'correspondence': 'Graph Matching', # Computer Visionの文脈も
    'benchmarks': 'Benchmarks & Datasets',
    'sat': 'SAT & Logic Reasoning with GNNs',
    'knowledge tracing': 'Knowledge Tracing (Education)',
    'fraud detection': 'Fraud Detection',
    'sentiment analysis': 'Sentiment Analysis with Graphs',
    'event detection': 'Event Detection with Graphs',
    'rumours': 'Misinformation & Rumor Detection',
    'affective state': 'Affective Computing with Graphs',
    'circuits': 'GNNs for Circuit Design',
    'environmental science': 'Environmental Science Applications',
    'game theory': 'Game Theory & GNNs',
    'position papers': 'Surveys & Position Papers', # Meta-category
    'stocks': 'Financial Applications (Stock Market)',
    'subgraphs': 'Subgraph Mining & Representation',
    'topological deep learning': 'Topological Deep Learning', # Simplexなど含む
    'social media': 'Social Network Analysis',
    'hallucination': 'Reliability & Hallucination in GNNs', # LLMの文脈でも

    # --- その他・未分類 ---
    'miscellaneous': 'Miscellaneous',
} 