# Upsell Agent - Full Stack Application

A complete web application that analyzes PostHog events to identify upsell opportunities using AI agents. Features a modern Next.js frontend and FastAPI backend.

## 🚀 Quick Start

### Option 1: Automated Startup (Recommended)
```bash
./start.sh
```

### Option 2: Manual Startup

**Terminal 1 - Backend:**
```bash
pip install -r requirements.txt
python api_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🌐 Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 🏗️ Architecture

### Frontend (Next.js + TypeScript + Tailwind CSS)
- **File Upload**: Drag & drop JSON file upload
- **Real-time Status**: Live agent status updates
- **Results Display**: Clean task visualization
- **Sample Data**: Built-in 1000+ event dataset

### Backend (FastAPI + CrewAI)
- **REST API**: Clean API endpoints for frontend
- **File Upload**: Secure JSON file handling
- **Agent Orchestration**: CrewAI agent management
- **CORS Support**: Cross-origin requests enabled

## 📁 Project Structure

```
upsell-agent/
├── api_server.py          # FastAPI backend server
├── crew_agent.py          # CrewAI agent implementation
├── sample_events.json     # 1000+ sample events
├── config.json           # Configuration file
├── requirements.txt      # Python dependencies
├── start.sh             # Automated startup script
├── frontend/            # Next.js application
│   ├── src/
│   │   └── app/
│   │       ├── page.tsx  # Main UI component
│   │       └── layout.tsx # App layout
│   ├── package.json
│   └── ...
└── uploads/             # Uploaded files directory
```

## 🔧 API Endpoints

### `GET /` - Root
Returns API status and information.

### `GET /status` - Agent Status
Returns current agent status and message.

### `POST /upload` - File Upload
Upload PostHog events JSON file.
```json
{
  "success": true,
  "message": "File uploaded successfully. Found 1000 events.",
  "file_path": "uploads/events.json",
  "total_events": 1000
}
```

### `POST /analyze` - Analyze Events
Analyze events and return upsell opportunities.
```json
{
  "success": true,
  "message": "Analysis completed successfully. Found 7 upsell opportunities.",
  "tasks": [
    {
      "user_id": "user_183",
      "opportunity_type": "Viewing high-value product",
      "reasoning": "Viewed Enterprise Security Suite priced at 999.",
      "recommended_action": "Recommend purchasing the product as an upgrade for enhanced security."
    }
  ],
  "analysis_time": "2.34s",
  "total_events": 1000
}
```

### `GET /sample-data` - Sample Data Info
Get information about the built-in sample dataset.

## 🎨 UI Features

### Inspired by Ambiguous IO Design
- **Clean Interface**: Modern, professional design
- **Status Indicators**: Real-time agent status with color coding
- **File Upload**: Drag & drop with validation
- **Task Cards**: Clean display of upsell opportunities
- **Responsive Design**: Works on desktop and mobile

### Key Components
- **Header**: Branding and status display
- **File Upload**: JSON file selection and validation
- **Analysis Controls**: Start analysis with sample or uploaded data
- **Results Panel**: Statistics and task visualization
- **Agent Status**: Live status updates

## 🔍 Usage Workflow

1. **Start the Application**: Run `./start.sh` or start services manually
2. **Access UI**: Open http://localhost:3000
3. **Upload Data**: Either upload a JSON file or use sample data
4. **Analyze**: Click "Analyze Events" to run the AI agent
5. **Review Results**: View identified upsell opportunities
6. **Take Action**: Use recommendations to contact users

## 📊 Sample Data

The application includes a comprehensive sample dataset:
- **1000+ events** across 200 users
- **393 product views** ($29-$999 products)
- **311 feature usage** events (premium/enterprise features)
- **199 page views** (pricing, features, app pages)
- **97 usage limits** (basic plan limitations)

## 🛠️ Development

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn api_server:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### API Testing
Visit http://localhost:8000/docs for interactive API documentation.

## 🔒 Security Notes

- File uploads are validated for JSON format
- CORS is configured for localhost development
- Uploaded files are stored in `uploads/` directory
- No authentication implemented (add as needed)

## 🚀 Production Deployment

For production deployment:

1. **Backend**: Deploy FastAPI with proper WSGI server (Gunicorn)
2. **Frontend**: Build Next.js app (`npm run build`) and serve with Nginx
3. **Security**: Add authentication, HTTPS, and proper CORS configuration
4. **Monitoring**: Add logging and error tracking
5. **Scaling**: Consider containerization with Docker

## 📝 License

This project is part of the upsell-agent application suite.
