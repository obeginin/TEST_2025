# InfoRUN Project Template

A modern, scalable web application template built with FastAPI, Next.js, and microservices architecture.

## 🏗️ Architecture Overview

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy 2.0
- **Database**: SQL Server (configurable for PostgreSQL)
- **ORM**: SQLAlchemy with async support
- **Authentication**: JWT with role-based access control
- **Validation**: Pydantic v2 schemas
- **Testing**: Pytest with factory fixtures
- **Migrations**: Alembic
- **Documentation**: Auto-generated OpenAPI/Swagger

### Frontend (Next.js)
- **Framework**: Next.js 15 with TypeScript
- **Styling**: Tailwind CSS + SCSS modules
- **State Management**: Zustand
- **UI Components**: PrimeReact
- **Build Tool**: Turbopack

### Infrastructure
- **Message Queue**: Kafka for event logging
- **Task Queue**: Celery + Redis for background tasks
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- SQL Server (or PostgreSQL)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

## 📁 Project Structure

```
infoRUN-template/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes (split by domain)
│   │   ├── core/           # Core configuration
│   │   ├── models/         # SQLAlchemy models
│   │   ├── repositories/   # Data access layer
│   │   ├── schemas/        # Pydantic validation schemas
│   │   ├── services/       # Business logic layer
│   │   └── main.py         # FastAPI application
│   ├── alembic/            # Database migrations
│   ├── tests/              # Test suite
│   └── requirements.txt
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # Reusable components
│   │   ├── features/      # Feature-based modules
│   │   ├── lib/           # Utilities and API client
│   │   └── types/         # TypeScript definitions
│   └── package.json
├── docker-compose.yml      # Development environment
└── README.md
```

## 🎯 Key Features

### Backend Features
- ✅ Clean architecture with service/repository pattern
- ✅ Comprehensive input validation with Pydantic
- ✅ Centralized error handling and logging
- ✅ Database connection pooling
- ✅ JWT authentication with role-based access
- ✅ API documentation with Swagger/OpenAPI
- ✅ Comprehensive test suite
- ✅ Database migrations with Alembic
- ✅ Background task processing with Celery
- ✅ Event logging with Kafka

### Frontend Features
- ✅ Modern React with TypeScript
- ✅ Server-side rendering with Next.js
- ✅ Responsive design with Tailwind CSS
- ✅ State management with Zustand
- ✅ Type-safe API client
- ✅ Component library with PrimeReact
- ✅ Optimized build with Turbopack

## 🔧 Configuration

### Environment Variables
See `.env.example` files in both backend and frontend directories for required environment variables.

### Database Configuration
The template supports both SQL Server and PostgreSQL. Update the database URL in your `.env` file:

```bash
# SQL Server
DATABASE_URL=mssql+pyodbc://user:pass@host/db?driver=ODBC+Driver+18+for+SQL+Server

# PostgreSQL
DATABASE_URL=postgresql://user:pass@host/db
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest tests/unit/       # Run unit tests only
pytest tests/integration/ # Run integration tests only
pytest --cov=app         # Run with coverage
```

### Frontend Tests
```bash
cd frontend
npm test                 # Run tests
npm run test:watch       # Run tests in watch mode
npm run test:coverage    # Run tests with coverage
```

## 📚 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## 🚀 Deployment

### Production Setup
1. Update environment variables for production
2. Build Docker images: `docker-compose -f docker-compose.prod.yml build`
3. Deploy with: `docker-compose -f docker-compose.prod.yml up -d`

### Environment-Specific Configs
- `docker-compose.yml` - Development environment
- `docker-compose.prod.yml` - Production environment
- `docker-compose.test.yml` - Testing environment

## 🔄 Development Workflow

1. **Feature Development**
   - Create feature branch from `main`
   - Implement backend API with tests
   - Implement frontend components
   - Add integration tests
   - Create pull request

2. **Database Changes**
   - Create new Alembic migration: `alembic revision --autogenerate -m "description"`
   - Test migration: `alembic upgrade head`
   - Commit migration file

3. **Testing**
   - Write unit tests for new functionality
   - Add integration tests for API endpoints
   - Ensure test coverage > 80%

## 📝 Code Style

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints throughout
- Write docstrings for public functions
- Use English comments only
- Maximum line length: 88 characters (Black formatter)

### Frontend (TypeScript)
- Use TypeScript strict mode
- Follow ESLint configuration
- Use functional components with hooks
- Implement proper error boundaries
- Use consistent naming conventions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This template is provided as-is for educational and commercial use.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed description
