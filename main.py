import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional

from database import create_document
from schemas import ContactMessage

app = FastAPI(title="Avalast Website API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Avalast API is running"}

@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}

@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    
    try:
        from database import db
        
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
            
    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    
    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    
    return response

@app.get("/api/company")
def get_company_profile():
    """
    Public company profile for the website. Update this as you get verified content.
    """
    return {
        "name": "Avalast OÜ",
        "tagline": "Reliable industrial and technical solutions in Estonia",
        "location": "Estonia",
        "languages": ["Estonian", "English", "Russian"],
        "services": [
            {"title": "Industrial Installations", "description": "Assembly, maintenance and optimization of industrial systems."},
            {"title": "Electrical Works", "description": "Certified electrical installations and inspections."},
            {"title": "HVAC & Ventilation", "description": "Design, installation and servicing for commercial properties."},
            {"title": "Maintenance & Support", "description": "On-call maintenance and SLA-based support."}
        ],
        "values": ["Safety", "Quality", "Reliability", "Transparency"],
        "contacts": {
            "email": "info@avalast.ee",
            "phone": "+372 0000 000",
            "address": "Tallinn, Estonia"
        }
    }

@app.post("/api/contact")
def submit_contact(message: ContactMessage):
    """Accept and store contact form submissions."""
    try:
        doc_id = create_document("contactmessage", message)
        return {"status": "ok", "id": doc_id}
    except Exception as e:
        # Database optional in preview environment; still return graceful error
        raise HTTPException(status_code=500, detail=f"Could not store message: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
