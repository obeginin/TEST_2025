# Wallet Service

A modern, scalable wallet management API built with FastAPI and PostgreSQL, designed to handle concurrent wallet operations safely.

## 🏗️ Architecture Overview

### Backend (FastAPI)
- **Framework**: FastAPI with SQLAlchemy 2.0
- **Database**: PostgreSQL with async support
- **ORM**: SQLAlchemy with async support
- **Validation**: Pydantic v2 schemas
- **Testing**: Pytest with factory fixtures
- **Migrations**: Alembic
- **Documentation**: Auto-generated OpenAPI/Swagger

### Key Features
- ✅ Concurrent-safe wallet operations using database locks
- ✅ RESTful API for wallet management
- ✅ Comprehensive input validation with Pydantic
- ✅ Centralized error handling and logging
- ✅ Database connection pooling
- ✅ API documentation with Swagger/OpenAPI
- ✅ Comprehensive test suite
- ✅ Database migrations with Alembic
- ✅ Docker containerization

## 📋 Project Summary

### Core Requirements Implemented
1. **REST API Endpoints**:
   - `POST api/v1/wallets/<WALLET_UUID>/operation` - Perform DEPOSIT/WITHDRAW operations
   - `GET api/v1/wallets/{WALLET_UUID}` - Retrieve wallet balance

2. **Technology Stack**:
   - **Backend**: FastAPI
   - **Database**: PostgreSQL
   - **Code Style**: PEP8 compliance
   - **Migrations**: Alembic for database schema management
   - **Containerization**: Docker & Docker Compose

3. **Concurrency Safety**:
   - Row-level locking (`SELECT FOR UPDATE`)
   - Optimistic locking (version field)
   - Transactional isolation for wallet operations
   - Comprehensive concurrent testing

### Architecture Patterns (Adopted from infoRUN-template)

#### 1. Clean Architecture
- **API Layer** (`app/api/v1/wallets.py`): FastAPI endpoints with dependency injection
- **Service Layer** (`app/services/wallet_service.py`): Business logic orchestration
- **Repository Layer** (`app/repositories/wallet_repo.py`): Data access logic
- **Model Layer** (`app/models/wallet.py`): SQLAlchemy models

#### 2. Dependency Injection
- Centralized service dependencies
- Database session management
- Configuration injection

#### 3. Centralized Error Handling
- Custom exception classes (`AppException`, `NotFoundError`, `ValidationError`, etc.)
- Global exception handlers in `main.py`
- Consistent error response format

#### 4. Configuration Management
- Pydantic `BaseSettings` for type-safe configuration
- Environment variable management with `pydantic-settings`
- Database URL, logging, and API prefix configuration

### Database Design

#### Wallet Model
```sql
CREATE TABLE wallets (
    id SERIAL PRIMARY KEY,
    uuid UUID UNIQUE NOT NULL,
    balance DECIMAL(15,2) NOT NULL DEFAULT 0,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

#### Transaction Model
```sql
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    wallet_id INTEGER REFERENCES wallets(id) ON DELETE CASCADE,
    operation_type VARCHAR(20) NOT NULL,
    amount DECIMAL(15,2) NOT NULL,
    balance_before DECIMAL(15,2) NOT NULL,
    balance_after DECIMAL(15,2) NOT NULL,
    description TEXT,
    reference_id UUID UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);
```

### Concurrency Safety Mechanisms

#### 1. Row-Level Locking
```python
# In WalletRepository.get_wallet_with_lock()
wallet = await session.execute(
    select(Wallet)
    .where(Wallet.uuid == wallet_uuid)
    .with_for_update()
)
```

#### 2. Optimistic Locking
```python
# Version field prevents concurrent modifications
if wallet.version != version:
    raise ConflictError("Wallet was modified by another operation")
wallet.version += 1
```

#### 3. Transactional Operations
```python
# All wallet operations wrapped in transactions
async with session.begin():
    wallet = await self.get_wallet_with_lock(session, wallet_uuid)
    # Perform balance update
    # Create transaction record
```

### Key Implementation Files

#### 1. Core Configuration (`app/core/config.py`)
- Pydantic `Settings` class for application configuration
- Database URL, pooling settings
- Environment-based configuration

#### 2. Exception Handling (`app/core/exceptions.py`)
- Custom exception hierarchy
- HTTP exception conversion
- Consistent error responses

#### 3. Database Models (`app/models/wallet.py`)
- `Wallet` model with UUID, balance, currency, status, version
- `Transaction` model for operation history
- SQLAlchemy relationships and constraints

#### 4. Repository Layer (`app/repositories/wallet_repo.py`)
- `WalletRepository`: CRUD operations with concurrency safety
- `TransactionRepository`: Transaction history management
- `BaseRepository`: Generic repository pattern

#### 5. Service Layer (`app/services/wallet_service.py`)
- Business logic for wallet operations
- Operation validation and orchestration
- Error handling and transaction management

#### 6. API Endpoints (`app/api/v1/wallets.py`)
- FastAPI router with dependency injection
- Request/response validation with Pydantic
- Comprehensive error handling

### Testing Strategy

#### 1. Unit Tests (`tests/unit/test_wallet_service.py`)
- Service layer testing with mocked dependencies
- Business logic validation
- Error scenario coverage

#### 2. Integration Tests (`tests/test_concurrent_operations.py`)
- Concurrent operation testing using `ThreadPoolExecutor`
- Balance consistency verification
- Thread safety validation

#### 3. API Tests (`test_api.py`)
- Manual API endpoint testing
- End-to-end workflow validation
- Error response verification

### Docker Configuration

#### 1. Application Container (`Dockerfile`)
- Python 3.11 slim base image
- Non-root user for security
- Optimized layer caching

#### 2. Development Environment (`docker-compose.yml`)
- FastAPI service with hot reload
- PostgreSQL database with health checks
- Volume mounting for development
- Automatic migration execution

### Migration Management

#### 1. Alembic Configuration (`alembic.ini`, `alembic/env.py`)
- PostgreSQL-specific configuration
- Auto-generate support for model changes
- Environment-based database URL

#### 2. Initial Migration (`alembic/versions/0001_initial_migration.py`)
- Wallet and transaction table creation
- Proper indexing for performance
- Foreign key constraints

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)

### Docker Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd wallet-service

# Start all services
docker-compose up -d

# Wait for services to start (check logs with: docker-compose logs -f)
# The API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs

# Test the API
python test_api.py
```

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# Run database migrations
alembic upgrade head

# Start the development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📁 Project Structure

```
wallet-service/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── wallets.py      # Wallet API endpoints
│   ├── core/
│   │   ├── config.py           # Application configuration
│   │   ├── database.py         # Database connection
│   │   ├── exceptions.py       # Custom exceptions
│   │   └── responses.py        # Response models
│   ├── models/
│   │   ├── base.py             # Base model
│   │   └── wallet.py           # Wallet model
│   ├── repositories/
│   │   ├── base.py             # Base repository
│   │   └── wallet_repo.py      # Wallet repository
│   ├── schemas/
│   │   ├── common.py           # Common schemas
│   │   └── wallet.py           # Wallet schemas
│   ├── services/
│   │   └── wallet_service.py   # Wallet business logic
│   └── main.py                 # FastAPI application
├── alembic/                    # Database migrations
├── tests/                      # Test suite
├── docker-compose.yml          # Development environment
├── Dockerfile                  # Application container
└── requirements.txt            # Python dependencies
```

## 🎯 API Endpoints

### Wallet Operations
- `POST /api/v1/wallets/{wallet_uuid}/operation` - Perform wallet operation (DEPOSIT/WITHDRAW)
- `GET /api/v1/wallets/{wallet_uuid}` - Get wallet balance
- `GET /api/v1/wallets/{wallet_uuid}/balance` - Get wallet balance (alternative endpoint)
- `GET /api/v1/wallets/{wallet_uuid}/transactions` - Get wallet transaction history
- `GET /api/v1/wallets/{wallet_uuid}/statistics` - Get wallet statistics

### Request Examples

#### Deposit Money
```bash
curl -X POST "http://localhost:8000/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation" \
     -H "Content-Type: application/json" \
     -d '{
       "operation_type": "DEPOSIT",
       "amount": 1000
     }'
```

#### Withdraw Money
```bash
curl -X POST "http://localhost:8000/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000/operation" \
     -H "Content-Type: application/json" \
     -d '{
       "operation_type": "WITHDRAW",
       "amount": 500
     }'
```

#### Get Wallet Balance
```bash
curl -X GET "http://localhost:8000/api/v1/wallets/123e4567-e89b-12d3-a456-426614174000"
```

## 🔒 Concurrency Safety

The application uses PostgreSQL's `SELECT FOR UPDATE` locking mechanism to ensure thread-safe wallet operations:

- **Row-level locking**: Only the specific wallet row is locked during operations
- **Deadlock prevention**: Consistent ordering of lock acquisition
- **Transaction isolation**: All operations are wrapped in database transactions
- **Optimistic locking**: Version-based concurrency control for additional safety

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_wallet_service.py
```

### Test Concurrency
```bash
# Run concurrent operation tests
pytest tests/test_concurrent_operations.py -v
```

## 📚 API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 🚀 Deployment

### Production Setup
1. Update environment variables for production
2. Build Docker images: `docker-compose -f docker-compose.prod.yml build`
3. Deploy with: `docker-compose -f docker-compose.prod.yml up -d`

## 🔄 Development Workflow

1. **Feature Development**
   - Create feature branch from `main`
   - Implement API endpoints with tests
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

- Follow PEP 8 style guide
- Use type hints throughout
- Write docstrings for public functions
- Use English comments only
- Maximum line length: 88 characters (Black formatter)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is provided as-is for educational and commercial use.
