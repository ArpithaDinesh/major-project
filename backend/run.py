import uvicorn
import os
import sys

if __name__ == "__main__":
    # Ensure current directory is in sys.path
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
        
    print("=" * 60)
    print("🧠 Starting MindSync FastAPI Backend Server")
    print("📡 Local API URL:    http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Status:    http://localhost:8000/api/health")
    print("=" * 60)
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
