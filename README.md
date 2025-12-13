# YouCam Skin Analysis Application

Web application untuk menganalisis kondisi kulit menggunakan YouCam AI Skin Analysis API.

## Features

- 🎯 Upload gambar selfie dengan drag & drop
- 🔬 Analisis komprehensif 14+ skin concerns (HD mode)
- 📊 Dashboard visual dengan color-coded scores
- 🎨 Modern UI dengan glassmorphism design
- ⚡ Real-time polling untuk hasil analisis

## Tech Stack

### Backend
- FastAPI - REST API framework
- httpx - Async HTTP client
- Pillow - Image processing
- Pydantic - Data validation

### Frontend
- React 18 - UI framework
- Vite - Build tool
- Axios - HTTP client
- Framer Motion - Animations
- Lucide React - Icons

## Getting Started

### Prerequisites

- Docker & Docker Compose
- YouCam API Key (v2.0)

### Installation

1. Clone repository:
```bash
cd /Users/ghawsshafadonia/Documents/Belajar/Gos/youcam
```

2. Copy environment file:
```bash
cp .env.example .env
```

3. Edit `.env` dan masukkan YouCam API Key:
```bash
YOUCAM_API_KEY=your_api_key_here
```

4. Start aplikasi dengan Docker:
```bash
docker-compose up --build
```

5. Buka browser:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Development (Without Docker)

### Backend
```bash
cd backend
pip install -r requirements.txt
export YOUCAM_API_KEY=your_api_key_here
export YOUCAM_SECRET_KEY=your_secret_key_here
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API Pipeline

Aplikasi mengikuti pipeline YouCam API:

1. **Upload File** → POST `/v2.0/file/skin-analysis`
   - Upload gambar, dapatkan `file_id`

2. **Submit Task** → POST `/v2.0/task/skin-analysis`
   - Submit analysis dengan `file_id`, dapatkan `task_id`

3. **Poll Task** → GET `/v2.0/task/skin-analysis/{task_id}`
   - Poll setiap 2 detik sampai status = `completed`

4. **Download Results** → Extract ZIP
   - Download ZIP dari URL
   - Extract `score_info.json` dan mask images

## Skin Analysis Categories

### HD Skincare (14 concerns)
- Wrinkle, Pore, Texture, Acne
- Redness, Oiliness, Age Spot, Radiance
- Moisture, Dark Circle, Eye Bag
- Droopy Upper Eyelid, Droopy Lower Eyelid, Firmness

### Score Interpretation
- 75-100: Excellent ✅
- 50-74: Good ⚠️
- 0-49: Needs Attention ❌

## Project Structure

```
youcam/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings
│   │   ├── schemas.py           # Pydantic models
│   │   ├── routes/
│   │   │   └── api.py           # API endpoints
│   │   └── services/
│   │       └── youcam_service.py # YouCam integration
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadSection.jsx     # Upload UI
│   │   │   └── ResultsDashboard.jsx  # Results display
│   │   ├── services/
│   │   │   └── api.js                # API calls
│   │   ├── App.jsx                   # Main component
│   │   └── index.css                 # Global styles
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
└── .env.example
```

## Environment Variables

### Backend
- `YOUCAM_API_KEY` - YouCam API key (required)
- `YOUCAM_SECRET_KEY` - YouCam Secret key (required)
- `YOUCAM_BASE_URL` - API base URL (default: https://yce-api-01.makeupar.com/s2s/v2.0)
- `CORS_ORIGINS` - Allowed CORS origins (default: localhost:5173,localhost:3000)

### Frontend
- `VITE_API_URL` - Backend API URL (default: http://localhost:8000/api)

## Notes

- Analysis biasanya memakan waktu 30-60 detik
- Max upload size: 10MB
- Supported formats: JPG, PNG
- Hasil analysis di-cache untuk menghindari re-fetch

## License

MIT
