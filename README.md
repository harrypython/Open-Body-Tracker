# Open Body Tracker

A secure, self-hosted, open-source platform for longitudinal tracking and visualization of anthropometric and physical assessment data.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd open-body-tracker
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your secure values
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL 15
- **Storage**: Local file system (Docker volumes)

## 📁 Project Structure

```
open-body-tracker/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py      # Application entry point
│   │   ├── config.py    # Configuration settings
│   │   └── database.py  # Database connection
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.ts
├── data/                # Persistent data storage
│   ├── postgres/        # Database files
│   └── photos/          # Uploaded photos
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🔒 Security Notes

**IMPORTANT**: Before deploying to production:
1. Change the `SECRET_KEY` in `.env`
2. Change the `POSTGRES_PASSWORD` in `.env`
3. Review CORS origins settings
4. Ensure proper firewall rules are in place

## 📊 Features (Planned)

- User authentication (JWT-based)
- Assessment tracking with Jackson-Pollock 7-site protocol
- Body composition calculations (BMI, WHR, Body Fat %)
- Photo uploads with before/after comparison
- Longitudinal data visualization
- CSV import/export
- Multi-language support (i18n)

## 🧪 Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

## 📝 License

Open Source - See LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please read our contributing guidelines before submitting PRs.
