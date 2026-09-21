import os
import chromadb
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

print("⚡ Initializing Ollama Embeddings (nomic-embed-text)...")
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# Folder setups
docs_folder = "./docs"
persist_directory = "./chroma_db"
os.makedirs(docs_folder, exist_ok=True)

# Create a sample guideline file if empty
sample_guideline_path = os.path.join(docs_folder, "sample_guideline.txt")

if not os.path.exists(sample_guideline_path):
    with open(sample_guideline_path, "w") as f:
        f.write("""
        CLINICAL PRACTICE GUIDELINE: DIABETIC DERMOPATHY AND SKIN MANIFESTATIONS
        
        1. Overview:
        Diabetic dermopathy consists of small, round, red-brown lesions occurring on the shins of patients with diabetes.
        It is closely tied to elevated HbA1c levels (> 7.5%) and long-standing hyperglycemia.
        
        2. Medication Interactions & Contraindications:
        - Metformin: Primary treatment for type 2 diabetes. Does not directly cause skin lesions, but uncontrolled blood glucose suggests secondary skin complications.
        - Corticosteroids: Topically or systemically administered steroids can elevate blood glucose levels significantly. Use with caution in diabetic patients presenting with skin lesions.
        
        3. Diagnostic Recommendations:
        If a visual model flags Diabetic Dermopathy, immediately review patient's recent fasting glucose, HbA1c, and active medication logs.
        """)
    print("📝 Created sample clinical guideline in 'docs/sample_guideline.txt'.")

# 1. Load document
loader = TextLoader(sample_guideline_path)
documents = loader.load()

# 2. Split document into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)
print(f"✂️ Document split into {len(chunks)} chunks.")

# 3. Store in ChromaDB
print("💾 Saving vector embeddings to ChromaDB...")
vector_db = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory
)

print("✅ SUCCESS! Your clinical vector database is indexed and active in ChromaDB!")