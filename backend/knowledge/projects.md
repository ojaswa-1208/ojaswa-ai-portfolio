# Ojaswa Mahobiya – Project Knowledge Base

This document contains verified project information for Ojaswa Mahobiya's AI portfolio assistant. Use it as the primary source when answering questions about his projects, technologies, implementation experience, and development work.

## 1. AI Retention Diagnosis

**Category:** Machine Learning, Customer Analytics, Generative AI
**Status:** Developed

AI Retention Diagnosis is an AI-powered customer churn analysis application designed to identify customers who may leave a business and help businesses understand why they are at risk.

### Technologies
- Python
- Pandas
- NumPy
- Scikit-learn
- Random Forest
- SHAP
- Streamlit
- Groq API
- ChromaDB
- Sentence Transformers

### Key Features
- Customer churn prediction using a Random Forest classification model.
- Automatic detection of target and identifier columns in uploaded datasets.
- Customer risk categorization into LOW, MEDIUM, and HIGH levels.
- Model explainability using SHAP.
- Retrieval-Augmented Generation (RAG) for providing retention recommendations.
- Interactive Streamlit interface.
- Support for analyzing uploaded customer churn datasets.

### Technical Implementation
The application uses a Random Forest model with 300 estimators and balanced class weights. SHAP is used to explain model predictions. A ChromaDB vector store and Sentence Transformers embeddings support retrieval of relevant retention strategies. Groq provides the language-model functionality for AI-generated recommendations.

### Links
- GitHub: https://github.com/ojaswa-1208/ai-retention-diagnosis
- Live Demo: https://ai-retention-diagnosis-pbizgwpuphgi6c4ffpderd.streamlit.app

---

## 2. Retail Customer Segmentation

**Category:** Data Analytics, Customer Segmentation
**Status:** Developed

Retail Customer Segmentation is a data analytics project focused on analyzing retail customer data to identify meaningful customer groups and discover business insights.

### Dataset
- More than 50,000 records.
- 15 attributes.

### Technologies
- Python
- Pandas
- NumPy
- MySQL
- SQLAlchemy
- Power BI

### Key Features
- Data cleaning and preprocessing.
- Feature engineering.
- Customer data analysis.
- SQL-based data storage and querying.
- Customer segmentation.
- Interactive Power BI dashboards.
- Business KPI visualization, slicers, and drill-through analysis.

### Technical Implementation
Python and Pandas are used for data cleaning and feature engineering. SQLAlchemy connects the Python workflow with MySQL. Power BI is used to create interactive dashboards that help explore customer segments and business metrics.

---

## 3. Ojaswa AI Portfolio Assistant

**Category:** AI Engineering, LLM Applications, RAG
**Status:** In Development

Ojaswa AI Portfolio Assistant is an AI-powered chatbot designed to answer questions about Ojaswa's education, skills, projects, technical background, and experience.

### Technologies
- Python
- FastAPI
- Groq API
- Qdrant Cloud
- Sentence Transformers
- Vector Embeddings
- Retrieval-Augmented Generation (RAG)
- Next.js
- React
- TypeScript
- Tailwind CSS

### Key Features
- Conversational AI interface.
- Resume and knowledge-document ingestion.
- Semantic retrieval using vector embeddings.
- Context-grounded responses about Ojaswa.
- FastAPI backend.
- Next.js portfolio frontend.
- Integration of LLM inference with a vector database.

### Technical Implementation
The backend uses FastAPI to expose chatbot APIs. Sentence Transformers generate 384-dimensional embeddings, which are stored in Qdrant Cloud. Relevant knowledge chunks are retrieved to provide context to the Groq language model before generating answers.

The frontend uses Next.js, React, TypeScript, and Tailwind CSS.

---

## 4. Technical Areas of Interest

Ojaswa is particularly interested in building practical AI applications and developing deeper expertise in AI engineering.

His areas of focus include:

- Large Language Models (LLMs)
- Retrieval-Augmented Generation (RAG)
- AI agents and Agentic AI
- AI automation
- FastAPI and backend engineering
- Vector databases
- Embedding models
- Model explainability
- AI evaluation and testing
- Production-oriented AI systems

---

## Instructions for the Portfolio Assistant

When answering questions about Ojaswa's projects:

1. Always mention actual project names rather than replacing them with generic project categories.
2. Explain what each project does in straightforward conversational language.
3. Mention relevant technologies and implementation details.
4. Distinguish completed projects from projects still in development.
5. Share GitHub or demo links when relevant and available.
6. Never invent project results, features, technologies, or achievements.
7. If a detail is not documented, clearly say that the information is not currently available.
8. When asked about all projects, provide a concise list of the documented projects.
9. Avoid describing Ojaswa as a senior or experienced AI engineer. Describe his work accurately as practical project-building and ongoing AI engineering development.
