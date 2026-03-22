"""
RAG-based Resume Analyzer Core Module - Day 4 (Complete)
"""

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import PyPDF2
import re
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

class ResumeAnalyzer:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """Initialize with embedding model"""
        print(f"🔄 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.resumes = []
        self.metadata = []
        self.embeddings = []
        print(f"✅ Model loaded! Embedding dimension: {self.model.get_sentence_embedding_dimension()}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    print(f"    📄 Extracted page {page_num + 1}")
            return text
        except Exception as e:
            print(f"    ❌ Error extracting PDF: {e}")
            return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract email and phone"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        
        return {
            'email': emails[0] if emails else 'Not found',
            'phone': phones[0] if phones else 'Not found'
        }
    
    def extract_skills(self, text: str, skill_list: Optional[List[str]] = None) -> List[str]:
        """Extract skills from text"""
        if skill_list is None:
            skill_list = [
                'python', 'java', 'javascript', 'react', 'node', 'sql',
                'mongodb', 'aws', 'docker', 'kubernetes', 'tensorflow',
                'pytorch', 'machine learning', 'deep learning', 'nlp',
                'fastapi', 'django', 'flask', 'pandas', 'numpy', 'scikit-learn',
                'git', 'jenkins', 'terraform', 'linux', 'bash', 'tableau',
                'spark', 'hadoop', 'cloud', 'azure', 'gcp'
            ]
        
        text_lower = text.lower()
        found_skills = []
        for skill in skill_list:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def chunk_text(self, text: str, chunk_size: int = 300, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks for better search"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk = ' '.join(words[i:i + chunk_size])
            if chunk:
                chunks.append(chunk)
        
        print(f"    📝 Created {len(chunks)} text chunks")
        return chunks
    
    def create_embeddings(self, chunks: List[str]) -> np.ndarray:
        """Create embeddings for text chunks"""
        print(f"    🧮 Creating embeddings for {len(chunks)} chunks...")
        embeddings = self.model.encode(chunks)
        return embeddings
    
    def process_resume(self, pdf_path: str, candidate_name: str = "") -> Dict[str, Any]:
        """Process a single resume with embeddings"""
        print(f"\n  📄 Processing: {os.path.basename(pdf_path)}")
        
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            raise ValueError("No text extracted from PDF")
        
        contact = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        
        if not candidate_name:
            candidate_name = os.path.splitext(os.path.basename(pdf_path))[0]
            candidate_name = candidate_name.replace('_', ' ').title()
        
        chunks = self.chunk_text(text)
        embeddings = self.create_embeddings(chunks)
        
        print(f"    ✅ Found {len(skills)} skills")
        print(f"    ✅ Email: {contact['email']}")
        print(f"    ✅ Embeddings shape: {embeddings.shape}")
        
        return {
            'text': text,
            'chunks': chunks,
            'embeddings': embeddings,
            'metadata': {
                'candidate_name': candidate_name,
                'email': contact['email'],
                'phone': contact['phone'],
                'skills': skills,
                'filename': os.path.basename(pdf_path),
                'chunk_count': len(chunks),
                'embedding_dim': embeddings.shape[1],
                'processed_date': datetime.now().isoformat()
            }
        }
    
    def save_embeddings(self, path: str = "data/embeddings"):
        """Save embeddings and metadata to disk"""
        os.makedirs(path, exist_ok=True)
        
        if len(self.embeddings) > 0:
            np.save(f"{path}/embeddings.npy", self.embeddings)
        
        metadata = [r['metadata'] for r in self.resumes]
        with open(f"{path}/metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        chunks_data = [{'filename': r['metadata']['filename'], 'chunks': r['chunks']} 
                      for r in self.resumes]
        with open(f"{path}/chunks.json", 'w') as f:
            json.dump(chunks_data, f, indent=2)
        
        print(f"✅ Saved embeddings to {path}")
        print(f"   - embeddings.npy: {self.embeddings.shape}")
        print(f"   - metadata.json: {len(metadata)} resumes")
        print(f"   - chunks.json: {len(chunks_data)} files")
    
    def load_embeddings(self, path: str = "data/embeddings") -> bool:
        """Load embeddings and metadata from disk"""
        try:
            embeddings_path = f"{path}/embeddings.npy"
            if os.path.exists(embeddings_path):
                self.embeddings = np.load(embeddings_path)
            
            with open(f"{path}/metadata.json", 'r') as f:
                metadata = json.load(f)
            
            with open(f"{path}/chunks.json", 'r') as f:
                chunks_data = json.load(f)
            
            self.resumes = []
            for i, meta in enumerate(metadata):
                chunks_info = next((c for c in chunks_data if c['filename'] == meta['filename']), None)
                if chunks_info:
                    self.resumes.append({
                        'metadata': meta,
                        'chunks': chunks_info['chunks']
                    })
            
            print(f"✅ Loaded embeddings from {path}")
            print(f"   - embeddings: {self.embeddings.shape if hasattr(self, 'embeddings') else 'None'}")
            print(f"   - resumes: {len(self.resumes)}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to load embeddings: {e}")
            return False
    
    def build_faiss_index(self, resumes_data: List[Dict[str, Any]] = None):
        """Build FAISS index from embeddings"""
        if resumes_data:
            all_embeddings = []
            self.resumes = []
            self.metadata = []
            
            for res_idx, resume in enumerate(resumes_data):
                for chunk_idx, emb in enumerate(resume['embeddings']):
                    all_embeddings.append(emb)
                    self.resumes.append(resume)
                    self.metadata.append({
                        'resume_idx': res_idx,
                        'chunk_idx': chunk_idx,
                        'candidate': resume['metadata']['candidate_name'],
                        'email': resume['metadata']['email'],
                        'filename': resume['metadata']['filename']
                    })
            
            if not all_embeddings:
                raise ValueError("No embeddings to index")
            
            self.embeddings = np.array(all_embeddings).astype('float32')
        
        if len(self.embeddings) == 0:
            raise ValueError("No embeddings available")
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)
        
        print(f"✅ FAISS index built!")
        print(f"   - Vectors: {self.index.ntotal}")
        print(f"   - Dimension: {dimension}")
        
        return self.index
    
    def save_faiss_index(self, path: str = "data/embeddings/faiss.index"):
        """Save FAISS index to disk"""
        if self.index:
            faiss.write_index(self.index, path)
            print(f"✅ FAISS index saved to {path}")
    
    def load_faiss_index(self, path: str = "data/embeddings/faiss.index") -> bool:
        """Load FAISS index from disk"""
        if os.path.exists(path):
            self.index = faiss.read_index(path)
            print(f"✅ FAISS index loaded from {path}")
            print(f"   - Vectors: {self.index.ntotal}")
            print(f"   - Dimension: {self.index.d}")
            return True
        return False
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for resumes using semantic similarity"""
        if self.index is None:
            raise ValueError("No FAISS index found. Call build_faiss_index() first.")
        
        query_emb = self.model.encode([query]).astype('float32')
        distances, indices = self.index.search(query_emb, top_k * 2)
        
        results = []
        seen_candidates = set()
        
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                meta = self.metadata[idx]
                resume = self.resumes[meta['resume_idx']]
                
                if meta['candidate'] in seen_candidates:
                    continue
                seen_candidates.add(meta['candidate'])
                
                distance = distances[0][i]
                similarity = max(0, min(100, 100 - distance))
                matched_chunk = resume['chunks'][meta['chunk_idx']]
                
                results.append({
                    'rank': len(results) + 1,
                    'candidate_name': meta['candidate'],
                    'email': meta['email'],
                    'filename': meta['filename'],
                    'skills': resume['metadata']['skills'],
                    'score': round(similarity, 2),
                    'distance': round(float(distance), 4),
                    'matched_chunk': matched_chunk[:300] + "..." if len(matched_chunk) > 300 else matched_chunk
                })
                
                if len(results) >= top_k:
                    break
        
        return results
    
    def hybrid_search(self, query: str, top_k: int = 5, 
                     skill_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Combine semantic search with skill matching"""
        semantic_results = self.semantic_search(query, top_k * 2)
        
        query_lower = query.lower()
        for result in semantic_results:
            skill_matches = sum(1 for skill in result['skills'] 
                              if skill.lower() in query_lower)
            skill_score = (skill_matches / max(len(result['skills']), 1)) * 100
            
            combined = (result['score'] * (1 - skill_weight) + 
                       skill_score * skill_weight)
            result['score'] = round(combined, 2)
            result['skill_match_score'] = round(skill_score, 2)
        
        semantic_results.sort(key=lambda x: x['score'], reverse=True)
        return semantic_results[:top_k]
    
    def test_embeddings(self, pdf_path: str):
        """Test embedding generation"""
        print("\n" + "="*60)
        print("🔬 Testing Embedding Generation")
        print("="*60)
        
        try:
            result = self.process_resume(pdf_path)
            
            print("\n📊 Results:")
            print(f"  Candidate: {result['metadata']['candidate_name']}")
            print(f"  Chunks: {result['metadata']['chunk_count']}")
            print(f"  Embedding dim: {result['metadata']['embedding_dim']}")
            print(f"  Embeddings shape: {result['embeddings'].shape}")
            print(f"  Sample embedding (first 5 values): {result['embeddings'][0][:5]}")
            
            print("\n✅ Embedding test successful!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("="*60)
    
    def test_vector_search(self):
        """Test vector search functionality"""
        print("\n" + "="*60)
        print("🔍 Testing Vector Search")
        print("="*60)
        
        if self.index is None:
            print("No index found. Please build index first!")
            return
        
        test_queries = [
            "Python developer with machine learning",
            "Data scientist with SQL",
            "DevOps engineer with Docker",
            "Full stack developer with React"
        ]
        
        for query in test_queries:
            print(f"\n📝 Query: {query}")
            results = self.semantic_search(query, top_k=2)
            for r in results:
                print(f"  Rank {r['rank']}: {r['candidate_name']} - Score: {r['score']}")

if __name__ == "__main__":
    analyzer = ResumeAnalyzer()
    test_file = "data/resumes/alex_chen_python.pdf"
    if os.path.exists(test_file):
        analyzer.test_embeddings(test_file)
    else:
        print("No test resume found. Run create_sample_resumes.py first!")