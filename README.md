# YouCam Skin Analysis

YouCam Skin Analysis adalah aplikasi web modern yang dirancang untuk memberikan analisis kulit tingkat profesional menggunakan kecerdasan buatan (Artificial Intelligence). Aplikasi ini memanfaatkan integrasi dengan YouCam AI Skin Analysis API untuk mendeteksi berbagai kondisi kulit seperti jerawat, kerutan, tekstur, pori-pori, dan banyak lagi, memberikan wawasan yang dapat ditindaklanjuti secara instan kepada pengguna.

## Tinjauan Proyek

Proyek ini merupakan implementasi full-stack yang menggabungkan backend FastAPI dengan frontend React modern, menampilkan UI futuristik dengan tema dark yang elegan. Aplikasi ini menekankan pengalaman pengguna yang premium dan profesional, dengan glassmorphism effects, glowing accents, dan layout yang compact untuk kenyamanan maksimal.

### Fitur Utama

- **Analisis Kulit AI Komprehensif**: Mendeteksi 14+ skin concerns termasuk acne, pores, wrinkles, texture, age spots, dan lainnya
- **Upload Fleksibel**: Drag & drop atau click to browse dengan preview real-time
- **Hasil Instan**: Real-time polling untuk status analisis dengan feedback visual
- **Dashboard Interaktif**: Visualisasi composite image dengan top 3 worst concerns
- **UI Futuristik**: Dark theme dengan cyan/blue accents dan glassmorphism effects
- **Compact Layout**: Optimized spacing untuk mengurangi scrolling (~40% lebih compact)
- **Color-Coded Scores**: Visual indicators untuk memudahkan interpretasi hasil
- **Responsive Design**: Mobile-friendly dengan optimizations untuk berbagai screen sizes

## Teknologi

### Backend
- **FastAPI** - Modern async web framework untuk Python
- **httpx** - Async HTTP client untuk API integration
- **Pillow** - Image processing dan composite visualization
- **Pydantic** - Data validation dan settings management
- **Python 3.11** - Latest Python runtime

### Frontend
- **React 18** - Modern UI framework dengan hooks
- **Vite** - Next-generation frontend tooling
- **Axios** - Promise-based HTTP client
- **Lucide React** - Beautiful icon library
- **CSS3** - Advanced styling dengan glassmorphism dan animations

## Hasil Pengujian & Demo

Berikut adalah dokumentasi visual dari aplikasi:

### 1. Upload Interface (Futuristic Dark Theme)

| Upload Page |
| :---: |
| ![Upload Interface](assets/gos-input.png) |

**Fitur Upload:**
- Dark futuristic gradient background dengan cyan/purple radial overlays
- Glassmorphism upload zone dengan glowing borders
- Text: "Take a selfie for comprehensive skin analysis"
- Drag & drop support dengan visual feedback

### 2. Processing Status

| Analyzing... |
| :---: |
| ![Processing](assets/processing.jpeg) |

**Real-time Status:**
- Progress indicator dengan attempt counter (1-720 attempts)
- "This may take up to 1 hour" warning
- Transparent overlay dengan blur effect

### 3. Results Dashboard (Compact & Professional)

| Analysis Results |
| :---: |
| ![Results Dashboard](assets/results.jpeg) |

**Dashboard Features:**
- **Header Cards**: Overall Skin Score (78/100) dan Skin Age (35 years) dengan glowing text
- **Main Visual**: Large composite image (600px max-width) dengan cyan border glow
- **Top 3 Concerns**: Mini cards showing worst scores:
  - Texture: 67 (Good)
  - Droopy Lower Eyelid: 70 (Good)
  - Eye Bag: 73 (Good)
- **Score Guide**: Color-coded legend (Excellent/Good/Needs Attention)

### 4. Composite Visualization

| Composite Output |
| :---: |
| ![Composite](assets/gos-output.jpg) |

**Composite Features:**
- Multi-mask overlay visualization
- Color-coded regions untuk different skin concerns
- Professional-grade analysis visualization

> **Design Highlights**:
> - **Futuristic Black Theme**: Deep black backgrounds dengan subtle cyan/purple overlays
> - **Glassmorphism**: `backdrop-filter: blur(16px)` dengan transparent backgrounds
> - **Glowing Effects**: Cyan borders dengan `box-shadow: 0 0 20px rgba(0, 212, 255, 0.2)`
> - **Compact Spacing**: Padding reduced dari 2rem → 1.25rem untuk professional density

---

## Roadmap & Implementation Status

### Completed (v1.0.0)
- [x] FastAPI backend dengan async processing
- [x] YouCam API v2.0 integration (complete pipeline)
  - File upload dengan presigned URLs
  - Task submission dengan SD mode untuk speed optimization
  - Polling mechanism dengan real-time status
  - ZIP extraction untuk scores dan masks
- [x] Composite image generation dengan mask overlays
- [x] React frontend dengan modern UI components
- [x] **Futuristic Dark Theme UI/UX**
  - Black gradient backgrounds dengan cyan/blue accents
  - Enhanced glassmorphism effects (blur 16px)
  - Glowing text shadows dan borders
  - Compact layout optimizations (~40% space reduction)
- [x] Real-time polling dengan progress feedback
- [x] Error handling dan logging
- [x] Docker containerization
- [x] Responsive design untuk mobile/tablet

### Planned Enhancements
- [ ] **History & Trends**: Track skin analysis over time dengan trend graphs
- [ ] **Recommendations**: AI-generated skincare recommendations based on analysis
- [ ] **Multi-Language Support**: Internationalization (i18n)
- [ ] **PDF Reports**: Downloadable professional reports
- [ ] **Comparison Mode**: Before/after comparison functionality
- [ ] **Enhanced Visualizations**: 3D face mapping dan heat maps

### Production Readiness
- **Database Integration**: PostgreSQL untuk storing analysis history
- **Authentication & Authorization**: User accounts dengan secure session management
- **Rate Limiting**: Protect API endpoints dari abuse
- **Monitoring**: Application performance monitoring (APM)
- **CDN Integration**: Untuk faster asset delivery
- **SSL/TLS**: Secure HTTPS connections

## Instruksi Instalasi

### Prerequisites
- Docker & Docker Compose (recommended)
- Atau: Python 3.11+ dan Node.js 20+
- YouCam API Key (v2.0)

### 1. Clone Repository
```bash
git clone git@github.com:gendonholaholo/bitmoji-like.git
cd bitmoji-like
```

### 2. Configure Environment Variables

Buat file `.env` di root directory:

```bash
# YouCam API Configuration
YOUCAM_API_KEY=your_api_key_here
YOUCAM_BASE_URL=https://yce-api-01.makeupar.com/s2s/v2.0

# Backend Configuration (Optional)
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Frontend Configuration (Optional)
VITE_API_URL=http://localhost:8000/api
```

> **Catatan**: Untuk mendapatkan YouCam API Key, silakan kunjungi [Perfect Corp Developer Portal](https://developer.perfectcorp.com/)

### 3. Run with Docker (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Access the application:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

### 4. Development Setup (Without Docker)

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

## Project Structure

```
youcam/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI application entry
│   │   ├── config.py                  # Settings & environment config
│   │   ├── schemas.py                 # Pydantic models
│   │   ├── routes/
│   │   │   └── api.py                 # API endpoints
│   │   └── services/
│   │       ├── youcam_service.py      # YouCam API integration
│   │       └── image_processing.py    # Composite generation
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadSection.jsx      # Upload UI component
│   │   │   ├── UploadSection.css
│   │   │   ├── ResultsDashboard.jsx   # Results display
│   │   │   └── ResultsDashboard.css
│   │   ├── services/
│   │   │   └── api.js                 # API client
│   │   ├── App.jsx                    # Main app component
│   │   ├── App.css
│   │   ├── index.css                  # Global styles & theme
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
├── assets/                            # Screenshots & documentation
├── docker-compose.yml
├── .gitignore
└── README.md
```

## API Documentation

### Backend Endpoints

#### 1. Upload & Analyze
```http
POST /api/analyze
Content-Type: multipart/form-data

Body:
  file: <image file>

Response: 200 OK
{
  "task_id": "string",
  "status": "processing"
}
```

#### 2. Get Results
```http
GET /api/result/{task_id}

Response: 200 OK (when completed)
{
  "task_id": "string",
  "status": "completed",
  "scores": {
    "all": { "score": 78 },
    "skin_age": 35,
    "acne": { "ui_score": 85, ... },
    "pore": { "ui_score": 72, ... },
    ...
  },
  "composite_image": "base64_string",
  "original_image": "base64_string"
}
```

### YouCam API Pipeline

```
1. Upload File
   POST /v2.0/file/skin-analysis
   → Get file_id

2. Submit Task
   POST /v2.0/task/skin-analysis
   Body: { "src_file_id": "...", "dst_actions": [...] }
   → Get task_id

3. Poll Status (every 5s)
   GET /v2.0/task/skin-analysis/{task_id}
   → Wait for task_status: "success"

4. Download Results
   GET {results.url}
   → Download ZIP file

5. Extract & Process
   - Extract score_info.json
   - Extract mask PNG files
   - Generate composite visualization
```

## Skin Analysis Metrics

### Primary Concerns (14 Metrics)
| Concern | Category | Description |
|---------|----------|-------------|
| Acne | Blemishes | Pimples and acne spots detection |
| Pore | Texture | Enlarged pores visibility |
| Wrinkle | Aging | Fine lines and wrinkles |
| Texture | Smoothness | Overall skin texture quality |
| Age Spot | Pigmentation | Dark spots and hyperpigmentation |
| Redness | Inflammation | Skin redness and irritation |
| Oiliness | Oil Level | Sebum production level |
| Radiance | Glow | Skin brightness and luminosity |
| Moisture | Hydration | Skin hydration level |
| Firmness | Elasticity | Skin firmness and elasticity |
| Eye Bag | Eye Area | Under-eye puffiness |
| Dark Circle | Eye Area | Dark circles under eyes |
| Droopy Upper Eyelid | Eye Area | Upper eyelid sagging |
| Droopy Lower Eyelid | Eye Area | Lower eyelid sagging |

### Score Interpretation
- **75-100 (Excellent)**: 🟢 Green - Optimal condition
- **50-74 (Good)**: 🟠 Amber - Moderate attention needed
- **0-49 (Needs Attention)**: 🔴 Red - Requires improvement

## Design System

### Color Palette (Futuristic Dark Theme)
```css
/* Primary */
--primary: #00d4ff;           /* Cyan - Main accent */
--primary-dark: #0ea5e9;      /* Electric Blue */
--secondary: #a855f7;         /* Neon Purple */

/* Backgrounds */
--bg-primary: #0a0a0a;        /* Deep Black */
--bg-secondary: #1a1a2e;      /* Dark Blue-Gray */
--bg-tertiary: #0f1419;       /* Dark Gray */

/* Status Colors */
--success: #10b981;           /* Green - Excellent */
--warning: #f59e0b;           /* Amber - Good */
--danger: #ef4444;            /* Red - Needs Attention */
```

### Glassmorphism Effect
```css
.glass-card {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 212, 255, 0.3);
  box-shadow: 
    0 8px 32px rgba(0, 0, 0, 0.5),
    0 0 20px rgba(0, 212, 255, 0.1),
    inset 0 0 20px rgba(255, 255, 255, 0.02);
}
```

### Spacing System (Optimized)
```css
--spacing-xs: 0.5rem;    /* 8px */
--spacing-sm: 0.75rem;   /* 12px */
--spacing-md: 1rem;      /* 16px */
--spacing-lg: 1.25rem;   /* 20px - optimized from 1.5rem */
--spacing-xl: 1.5rem;    /* 24px - optimized from 2rem */
--spacing-2xl: 2rem;     /* 32px - optimized from 3rem */
```

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `YOUCAM_API_KEY` | ✅ | - | YouCam API key dari developer portal |
| `YOUCAM_BASE_URL` | ❌ | `https://yce-api-01.makeupar.com/s2s/v2.0` | Base URL untuk YouCam API |
| `CORS_ORIGINS` | ❌ | `http://localhost:5173,http://localhost:3000` | Allowed CORS origins |

### Frontend (.env)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | ❌ | `/api` | Backend API base URL |

## Performance Considerations

### Optimizations Implemented
- **Compact Layout**: 40% reduction in vertical spacing untuk better information density
- **Image Optimization**: Max-width 600px untuk composite images (dari 800px)
- **Lazy Loading**: Components loaded on-demand
- **Debounced Polling**: 5-second intervals untuk task status checks
- **Base64 Caching**: Results cached di frontend untuk menghindari re-fetch

### Performance Metrics
- **Initial Load**: < 2s (with Vite HMR)
- **Time to Interactive**: < 3s
- **Analysis Processing**: 30-60s (YouCam API dependent)
- **Results Rendering**: < 500ms

## Troubleshooting

### Common Issues

**1. Error 400 from YouCam API**
- ✅ Verify API key validity
- ✅ Check if API quota exceeded
- ✅ Ensure image format is supported (JPG/PNG)
- ✅ Validate image size (< 10MB)

**2. Docker Build Fails**
- ✅ Ensure Docker is running
- ✅ Check Docker Compose version (v2.0+)
- ✅ Verify .env file exists dengan valid values

**3. Frontend Can't Connect to Backend**
- ✅ Check VITE_API_URL di frontend/.env
- ✅ Verify CORS_ORIGINS di backend includes frontend URL
- ✅ Ensure backend is running on port 8000

**4. Analysis Takes Too Long**
- ℹ️ Normal processing time: 30-60 seconds
- ℹ️ Max timeout: 1 hour (720 attempts × 5s)
- ✅ Check network connectivity
- ✅ Verify YouCam API status

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- **Backend**: Follow PEP 8 guidelines, use `ruff` for linting
- **Frontend**: Use ESLint dengan provided config
- **Commits**: Use conventional commits format

## License

MIT License - see LICENSE file for details

## Author

**Ghaws Shafadonia**  
Email: fafaghaws@live.com  
GitHub: [@gendonholaholo](https://github.com/gendonholaholo)

## Acknowledgments

- [Perfect Corp / YouCam](https://www.perfectcorp.com/) - AI Skin Analysis API
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI framework
- [Vite](https://vitejs.dev/) - Build tool

---

**⭐ Star this repository** jika projek ini membantu Anda!

**🔗 Repository**: [github.com/gendonholaholo/bitmoji-like](https://github.com/gendonholaholo/bitmoji-like)
