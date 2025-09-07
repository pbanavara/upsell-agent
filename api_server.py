#!/usr/bin/env python3
"""
FastAPI backend server for the Upsell Agent
Wraps the CrewAI agent and provides API endpoints for the Next.js frontend
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import tempfile
import os
import asyncio
from datetime import datetime
import uvicorn

# Import our CrewAI agent
from crew_agent import PostHogTool, create_upsell_agent, create_upsell_task, Crew, Process, write_tasks_to_file

app = FastAPI(title="Upsell Agent API", version="1.0.0")

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class AnalysisRequest(BaseModel):
    events_file_path: Optional[str] = None
    use_sample_data: bool = False

class AnalysisResponse(BaseModel):
    success: bool
    message: str
    tasks: List[Dict[str, Any]]
    analysis_time: str
    total_events: int

class AgentStatus(BaseModel):
    status: str
    message: str
    timestamp: str

# Global state for agent status
agent_status = {
    "status": "idle",
    "message": "Agent ready",
    "timestamp": datetime.now().isoformat()
}

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Upsell Agent API", "status": "running"}

@app.get("/status")
async def get_status():
    """Get current agent status"""
    return agent_status

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_events(request: AnalysisRequest):
    """Analyze PostHog events and return upsell opportunities"""
    global agent_status
    
    try:
        # Update status
        agent_status.update({
            "status": "analyzing",
            "message": "Processing events...",
            "timestamp": datetime.now().isoformat()
        })
        
        # Determine events file path
        if request.use_sample_data:
            events_file = "sample_events.json"
        elif request.events_file_path:
            events_file = request.events_file_path
        else:
            raise HTTPException(status_code=400, detail="No events file specified")
        
        # Check if file exists
        if not os.path.exists(events_file):
            raise HTTPException(status_code=404, detail=f"Events file not found: {events_file}")
        
        # Load events to count them
        with open(events_file, 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        total_events = len(events_data)
        
        # Create PostHog tool (no API credentials needed for file analysis)
        posthog_tool = PostHogTool()
        
        # Create agent and task
        upsell_agent = create_upsell_agent(posthog_tool)
        upsell_task = create_upsell_task(upsell_agent, events_file)
        
        # Create and run crew
        crew = Crew(
            agents=[upsell_agent],
            tasks=[upsell_task],
            process=Process.sequential,
            verbose=False  # Reduce output for API
        )
        
        # Run analysis
        start_time = datetime.now()
        result = crew.kickoff()
        end_time = datetime.now()
        
        # Parse the result to extract tasks
        tasks = []
        if result:
            result_str = str(result)
            # Extract tasks from the result (simple parsing)
            lines = result_str.split('\n')
            current_task = {}
            
            for line in lines:
                line = line.strip()
                if line.startswith('User ID:'):
                    if current_task:
                        tasks.append(current_task)
                    current_task = {'user_id': line.replace('User ID:', '').strip()}
                elif line.startswith('Opportunity type:'):
                    current_task['opportunity_type'] = line.replace('Opportunity type:', '').strip()
                elif line.startswith('Reasoning:'):
                    current_task['reasoning'] = line.replace('Reasoning:', '').strip()
                elif line.startswith('Recommended action:'):
                    current_task['recommended_action'] = line.replace('Recommended action:', '').strip()
            
            if current_task:
                tasks.append(current_task)
        
        # Update status
        agent_status.update({
            "status": "completed",
            "message": f"Analysis completed. Found {len(tasks)} opportunities.",
            "timestamp": datetime.now().isoformat()
        })
        
        return AnalysisResponse(
            success=True,
            message=f"Analysis completed successfully. Found {len(tasks)} upsell opportunities.",
            tasks=tasks,
            analysis_time=f"{(end_time - start_time).total_seconds():.2f}s",
            total_events=total_events
        )
        
    except Exception as e:
        # Update status
        agent_status.update({
            "status": "error",
            "message": f"Analysis failed: {str(e)}",
            "timestamp": datetime.now().isoformat()
        })
        
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/upload")
async def upload_events_file(file: UploadFile = File(...)):
    """Upload PostHog events file"""
    try:
        # Validate file type
        if not file.filename.endswith('.json'):
            raise HTTPException(status_code=400, detail="Only JSON files are allowed")
        
        # Save uploaded file
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate JSON
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            if not isinstance(events_data, list):
                raise HTTPException(status_code=400, detail="JSON file must contain an array of events")
            
            return {
                "success": True,
                "message": f"File uploaded successfully. Found {len(events_data)} events.",
                "file_path": file_path,
                "total_events": len(events_data)
            }
            
        except json.JSONDecodeError:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Invalid JSON file")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/sample-data")
async def get_sample_data_info():
    """Get information about sample data"""
    try:
        with open("sample_events.json", 'r', encoding='utf-8') as f:
            events_data = json.load(f)
        
        return {
            "success": True,
            "total_events": len(events_data),
            "file_path": "sample_events.json",
            "description": "Sample dataset with 1000+ realistic PostHog events"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Sample data file not found")

if __name__ == "__main__":
    uvicorn.run("api_server:app", host="0.0.0.0", port=8001, reload=True)
