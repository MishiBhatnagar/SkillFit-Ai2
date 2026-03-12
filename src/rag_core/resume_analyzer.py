"""
RAG-based Resume Analyzer Core Module - Day 4 (Embeddings)
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
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            raise ValueError("No text extracted from PDF")
        
        # Extract metadata
        contact = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        
        # Get candidate name
        if not candidate_name:
            candidate_name = os.path.splitext(os.path.basename(pdf_path))[0]
            candidate_name = candidate_name.replace('_', ' ').title()
        
        # Chunk text and create embeddings
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

if __name__ == "__main__":
    # Quick test
    analyzer = ResumeAnalyzer()
    test_file = "data/resumes/alex_chen_python.pdf"
    if os.path.exists(test_file):
        analyzer.test_embeddings(test_file)
    else:
        print("No test resume found. Run create_sample_resumes.py first!")