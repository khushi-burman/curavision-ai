from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# 1. Initialize local embeddings
embeddings = OllamaEmbeddings(model="nomic-embed-text")

# 2. Connect to the existing vector database folder
persist_directory = "./chroma_db"
vector_db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

# 3. Simulate a query (like a question coming from your app/patient input)
user_query = "What medications should be monitored when skin lesions appear?"

print(f"\n🔍 Searching vector DB for query: '{user_query}'\n")

# 4. Perform vector similarity search
results = vector_db.similarity_search(user_query, k=2)

# 5. Print retrieved chunks
for i, doc in enumerate(results, 1):
    print(f"--- 📄 Retrieved Chunk #{i} ---")
    print(doc.page_content.strip())
    print("-" * 35 + "\n")