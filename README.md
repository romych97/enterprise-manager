# Enterprise Manager

A simple but extensible management system for small businesses. The application allows small companies to manage clients, orders, tasks, and communication.

## Features

- User authentication and authorization (JWT)
- Client management
- Order tracking
- Task management with priorities and deadlines
- Notes and activity history
- Export functionality (CSV, PDF)
- Real-time notifications

## Tech Stack

### Frontend
- Next.js (latest)
- Zustand for state management
- Tailwind CSS for UI

### Backend
- Python (FastAPI)
- PostgreSQL with SQLAlchemy
- Redis for caching and real-time features

### DevOps
- Docker + docker-compose
- GitHub Actions for CI/CD

## Getting Started

### Prerequisites
- Docker and docker-compose
- Node.js (for local frontend development)
- Python 3.12+ (for local backend development)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/enterprise-manager.git
cd enterprise-manager
```

2. Create a `.env` file in the root directory with the following variables:
```env
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/enterprise_manager
REDIS_URL=redis://redis:6379
JWT_SECRET=your_jwt_secret_key
JWT_REFRESH_SECRET=your_jwt_refresh_secret_key
```

3. Start the services using docker-compose:
```bash
docker-compose up -d
```

4. The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Development

#### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 