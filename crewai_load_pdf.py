import os
from pathlib import Path
from mem0 import MemoryClient
import PyPDF2
from typing import List, Set

# Set up mem0 API key (already configured in deck.py)
os.environ["MEM0_API_KEY"] = "API Key"

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def chunk_text(text: str, chunk_size: int = 4000) -> List[str]:
    """Split text into chunks for better memory storage."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += len(word) + 1  # +1 for space
        
        if current_size >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def get_existing_sources(client: MemoryClient) -> Set[str]:
    """Get the set of PDF sources that have already been uploaded to mem0."""
    try:
        memories = client.get_all(user_id="mem0info")
        sources = set()
        for memory in memories:
            source = memory.get('metadata', {}).get('source')
            if source:
                sources.add(source)
        return sources
    except Exception as e:
        print(f"Error retrieving existing memories: {e}")
        return set()

def load_pdfs_to_mem0():
    """Load all PDF files from the knowledge directory into mem0 for deckinfo user."""
    
    # Initialize mem0 client
    client = MemoryClient()
    
    # Define the knowledge directory path
    knowledge_dir = Path("knowledge")
    
    if not knowledge_dir.exists():
        print(f"Knowledge directory not found: {knowledge_dir}")
        return
    
    # Find all PDF files in the knowledge directory
    pdf_files = list(knowledge_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("No PDF files found in the knowledge directory.")
        return
    
    print(f"Found {len(pdf_files)} PDF files to process...")
    
    # Get existing sources to avoid duplicates
    print("Checking for existing uploads...")
    existing_sources = get_existing_sources(client)
    if existing_sources:
        print(f"Found {len(existing_sources)} files already uploaded: {', '.join(existing_sources)}")
    
    # Process each PDF file
    processed_count = 0
    skipped_count = 0
    
    for pdf_file in pdf_files:
        print(f"\nProcessing: {pdf_file.name}")
        
        # Check if this file has already been uploaded
        if pdf_file.name in existing_sources:
            print(f"  Skipping {pdf_file.name} - already uploaded to mem0")
            skipped_count += 1
            continue
        
        # Extract text from PDF
        text_content = extract_text_from_pdf(str(pdf_file))
        
        if not text_content.strip():
            print(f"No text content extracted from {pdf_file.name}")
            continue
        
        # Split content into manageable chunks
        text_chunks = chunk_text(text_content)
        print(f"Split into {len(text_chunks)} chunks")
        
        # Add each chunk to mem0 with metadata
        success_count = 0
        for i, chunk in enumerate(text_chunks):
            try:
                metadata = {
                    "source": pdf_file.name,
                    "chunk_index": i,
                    "total_chunks": len(text_chunks),
                    "file_type": "pdf",
                    "project": "mem0info"
                }
                
                # Add to mem0 memory for the deckinfo user
                result = client.add(
                    messages=[{"role": "user", "content": chunk}],
                    user_id="mem0info",
                    metadata=metadata
                )
                
                print(f"  Chunk {i+1}/{len(text_chunks)} added successfully")
                success_count += 1
                
            except Exception as e:
                print(f"  Error adding chunk {i+1} from {pdf_file.name}: {e}")
                continue
        
        if success_count > 0:
            processed_count += 1
            print(f"  Successfully uploaded {success_count}/{len(text_chunks)} chunks from {pdf_file.name}")
    
    print(f"\nPDF loading to mem0 completed!")
    print(f"Files processed: {processed_count}")
    print(f"Files skipped (already uploaded): {skipped_count}")

def search_deckinfo_memory(query: str, limit: int = 5):
    """Search the deckinfo memory for relevant information."""
    client = MemoryClient()
    
    try:
        results = client.search(
            query=query,
            user_id="mem0info",
            limit=limit
        )
        
        print(f"\nSearch results for: '{query}'")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Score: {result.get('score', 'N/A')}")
            print(f"Source: {result.get('metadata', {}).get('source', 'Unknown')}")
            print(f"Content: {result.get('memory', 'No content')[:200]}...")
            print("-" * 30)
            
    except Exception as e:
        print(f"Error searching memory: {e}")

def list_deckinfo_memories():
    """List all memories stored for the  user."""
    client = MemoryClient()
    
    try:
        memories = client.get_all(user_id="mem0info")
        
        print(f"\nTotal memories for deckinfo: {len(memories)}")
        print("=" * 50)
        
        # Group by source file
        sources = {}
        for memory in memories:
            source = memory.get('metadata', {}).get('source', 'Unknown')
            if source not in sources:
                sources[source] = 0
            sources[source] += 1
        
        for source, count in sources.items():
            print(f"{source}: {count} chunks")
            
    except Exception as e:
        print(f"Error listing memories: {e}")

if __name__ == "__main__":
    # Load PDFs to mem0
    load_pdfs_to_mem0()
    
    # Optional: List what was loaded
    print("\n" + "="*60)
    list_deckinfo_memories()
    
    # Optional: Test search functionality
    print("\n" + "="*60)
    search_deckinfo_memory("Loaded key", limit=3)
