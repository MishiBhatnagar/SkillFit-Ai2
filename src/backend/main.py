"""
FastAPI Backend for Resume Analyzer - Day 3
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import shutil
import uvicorn

from rag_core.resume_analyzer import ResumeAnalyzer

# Initialize FastAPI
app = FastAPI(
    title="SkillFit AI API",
    description="RAG-based Resume Analysis API",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = ResumeAnalyzer()
UPLOAD_DIR = "data/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Pydantic models
class JobDescription(BaseModel):
    text: str
    top_k: int = 5

class MatchResult(BaseModel):
    rank: int
    candidate_name: str
    email: str
    skills: List[str]
    score: float
    matched_chunk: str

class ResumeMetadata(BaseModel):
    candidate_name: str
    email: str
    phone: str
    skills: List[str]
    filename: str
    skill_count: int

class HealthResponse(BaseModel):
    status: str
    resumes_loaded: int
    model_loaded: bool

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "SkillFit AI API",
        "version": "1.0.0",
        "endpoints": [
            "/health",
            "/upload-resume",
            "/match-job",
            "/resumes",
            "/docs"
        ]
    }

# Health check
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Check if API is running"""
    return {
        "status": "healthy",
        "resumes_loaded": len(analyzer.resumes),
        "model_loaded": analyzer.model is not None if hasattr(analyzer, 'model') else False
    }

# Upload resume
@app.post("/upload-resume/", tags=["Resumes"])
async def upload_resume(
    file: UploadFile = File(...),
    candidate_name: Optional[str] = None
):
    """
    Upload and process a resume PDF
    
    - **file**: PDF file to upload
    - **candidate_name**: Optional candidate name
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    try:
        # Process the resume
        resume_data = analyzer.process_resume(file_path, candidate_name or file.filename)
        
        # Rebuild index with all resumes
        all_resumes = []
        pdf_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.pdf')]
        
        for pdf in pdf_files:
            try:
                data = analyzer.process_resume(os.path.join(UPLOAD_DIR, pdf))
                all_resumes.append(data)
            except Exception as e:
                print(f"Error processing {pdf}: {e}")
                continue
        
        # Store resumes (we'll add vector search later)
        analyzer.resumes = all_resumes
        
        return {
            "status": "success",
            "candidate": resume_data['metadata']['candidate_name'],
            "email": resume_data['metadata']['email'],
            "skills": resume_data['metadata']['skills'],
            "skill_count": len(resume_data['metadata']['skills'])
        }
    except Exception as e:
        raise HTTPException(500, str(e))

# List all resumes
@app.get("/resumes/", response_model=List[ResumeMetadata], tags=["Resumes"])
async def list_resumes():
    """Get list of all processed resumes"""
    return [r['metadata'] for r in analyzer.resumes]

# Get resume by filename
@app.get("/resumes/{filename}", tags=["Resumes"])
async def get_resume(filename: str):
    """Get specific resume by filename"""
    for resume in analyzer.resumes:
        if resume['metadata']['filename'] == filename:
            return resume['metadata']
    raise HTTPException(404, "Resume not found")

# Match job (placeholder for now)
@app.post("/match-job/", response_model=List[MatchResult], tags=["Matching"])
async def match_job(job: JobDescription):
    """
    Match resumes against job description
    (Basic implementation - vector search coming in Day 4)
    """
    if not analyzer.resumes:
        raise HTTPException(400, "No resumes loaded")
    
    # Simple keyword matching for now
    results = []
    job_words = set(job.text.lower().split())
    
    for idx, resume in enumerate(analyzer.resumes[:job.top_k]):
        meta = resume['metadata']
        
        # Simple score based on skill matches
        skill_matches = sum(1 for skill in meta['skills'] if skill.lower() in job.text.lower())
        score = min(100, (skill_matches / max(len(meta['skills']), 1)) * 100)
        
        results.append({
            "rank": idx + 1,
            "candidate_name": meta['candidate_name'],
            "email": meta['email'],
            "skills": meta['skills'],
            "score": round(score, 2),
            "matched_chunk": f"Found {skill_matches} matching skills"
        })
    
    return results

# Delete resume
@app.delete("/resumes/{filename}", tags=["Resumes"])
async def delete_resume(filename: str):
    """Delete a resume by filename"""
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
        # Rebuild resumes list
        analyzer.resumes = []
        pdf_files = [f for f in os.listdir(UPLOAD_DIR) if f.endswith('.pdf')]
        for pdf in pdf_files:
            try:
                data = analyzer.process_resume(os.path.join(UPLOAD_DIR, pdf))
                analyzer.resumes.append(data)
            except:
                continue
        
        return {"status": "deleted", "filename": filename}
    raise HTTPException(404, "File not found")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)