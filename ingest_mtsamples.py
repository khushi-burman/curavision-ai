import os
import shutil
import pandas as pd
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

# 1. Clean old partial Chroma index to start fresh
persist_directory = "./chroma_db"
if os.path.exists(persist_directory):
    try:
        shutil.rmtree(persist_directory)
        print("🧹 Cleared previous partial ChromaDB data.")
    except Exception:
        pass

# 2. Locate mtsamples.csv
csv_path = "mtsamples.csv" if os.path.exists("mtsamples.csv") else "data/mtsamples.csv"
if not os.path.exists(csv_path):
    raise FileNotFoundError("Could not find mtsamples.csv in root or data/ folder.")

print(f"📂 Loading clinical data from: {csv_path}")
df = pd.read_csv(csv_path)

# 3. Filter for targeted metabolic and chronic cases (150 focused cases)
target_specialties = [
    "Endocrinology",
    "Cardiovascular / Pulmonary",
    "General Medicine",
    "Consult - History and Phy."
]

filtered_df = df[
    (df["medical_specialty"].str.strip().isin(target_specialties)) |
    (df["transcription"].str.contains("diabetes|glucose|insulin|hypertension", case=False, na=False))
].dropna(subset=["transcription"]).copy()

# Cap at 150 top cases (~600-800 chunks: optimal balance for local embedding)
filtered_df = filtered_df.drop_duplicates(subset=["transcription"]).head(150)
print(f"✅ Selected {len(filtered_df)} targeted clinical cases across {filtered_df['medical_specialty'].nunique()} specialties.")

# 4. Create Documents
documents = []
for _, row in filtered_df.iterrows():
    specialty = str(row.get("medical_specialty", "General")).strip()
    description = str(row.get("description", "Clinical Transcript")).strip()
    content = f"Specialty: {specialty}\nSummary: {description}\n\nCase Details:\n{row['transcription']}"
    
    doc = Document(
        page_content=content,
        metadata={"specialty": specialty, "description": description}
    )
    documents.append(doc)

# 5. Chunk Transcripts
text_splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=100)
chunked_docs = text_splitter.split_documents(documents)
total_chunks = len(chunked_docs)
print(f"✂️ Created {total_chunks} chunked segments.")

# 6. Initialize Chroma & Embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# 7. Batched Ingestion with Real-Time Progress
BATCH_SIZE = 64
print(f"⚡ Ingesting {total_chunks} chunks in batches of {BATCH_SIZE}...")

for i in range(0, total_chunks, BATCH_SIZE):
    batch = chunked_docs[i:i + BATCH_SIZE]
    vector_db.add_documents(batch)
    progress = min(i + BATCH_SIZE, total_chunks)
    print(f"   Processed {progress}/{total_chunks} chunks ({(progress/total_chunks)*100:.1f}%)")

print("🎉 Successfully indexed all chunks into ChromaDB!")