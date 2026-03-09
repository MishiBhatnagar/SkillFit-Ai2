"""
RAG-based Resume Analyzer Core Module - Day 2
"""

import PyPDF2
import re
import os
from typing import List, Dict, Any, Optional

class ResumeAnalyzer:
    def __init__(self):
        """Initialize the Resume Analyzer"""
        self.resumes = []
        print("✅ ResumeAnalyzer initialized!")
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
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
        """
        Extract email and phone from text
        
        Args:
            text: Resume text content
            
        Returns:
            Dictionary with email and phone
        """
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Phone pattern (simple)
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        
        return {
            'email': emails[0] if emails else 'Not found',
            'phone': phones[0] if phones else 'Not found'
        }
    
    def extract_skills(self, text: str, skill_list: Optional[List[str]] = None) -> List[str]:
        """
        Extract skills from text
        
        Args:
            text: Resume text content
            skill_list: Optional custom skill list
            
        Returns:
            List of found skills
        """
        if skill_list is None:
            # Common tech skills
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
    
    def process_resume(self, pdf_path: str, candidate_name: str = "") -> Dict[str, Any]:
        """
        Process a single resume
        
        Args:
            pdf_path: Path to the PDF resume
            candidate_name: Optional candidate name
            
        Returns:
            Dictionary with extracted information
        """
        print(f"\n  📄 Processing: {os.path.basename(pdf_path)}")
        
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            raise ValueError("No text extracted from PDF")
        
        # Extract information
        contact = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        
        # Get candidate name from filename if not provided
        if not candidate_name:
            candidate_name = os.path.splitext(os.path.basename(pdf_path))[0]
            candidate_name = candidate_name.replace('_', ' ').title()
        
        result = {
            'text': text[:500] + "...",  # Store preview only for now
            'metadata': {
                'candidate_name': candidate_name,
                'email': contact['email'],
                'phone': contact['phone'],
                'skills': skills,
                'filename': os.path.basename(pdf_path),
                'skill_count': len(skills)
            }
        }
        
        print(f"    ✅ Found {len(skills)} skills")
        print(f"    ✅ Email: {contact['email']}")
        
        return result
    
    def test_with_sample(self, pdf_path: str):
        """
        Test the analyzer with a sample resume
        """
        print("\n" + "="*50)
        print("🔬 Testing Resume Analyzer")
        print("="*50)
        
        try:
            result = self.process_resume(pdf_path)
            
            print("\n📊 Results:")
            print(f"  Candidate: {result['metadata']['candidate_name']}")
            print(f"  Email: {result['metadata']['email']}")
            print(f"  Phone: {result['metadata']['phone']}")
            print(f"  Skills ({len(result['metadata']['skills'])}):")
            
            # Show skills in columns
            skills = result['metadata']['skills']
            for i in range(0, len(skills), 4):
                row = skills[i:i+4]
                print("    " + "  ".join(f"{s:<15}" for s in row))
            
            print("\n✅ Test successful!")
            
        except Exception as e:
            print(f"❌ Test failed: {e}")
        
        print("="*50)

if __name__ == "__main__":
    # Quick test
    analyzer = ResumeAnalyzer()
    
    # Test with a sample file if it exists
    test_file = "data/resumes/alex_chen_python.pdf"
    if os.path.exists(test_file):
        analyzer.test_with_sample(test_file)
    else:
        print("No test resume found. Run create_sample_resumes.py first!")