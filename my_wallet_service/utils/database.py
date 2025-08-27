from my_wallet_service.utils.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from typing import Generator
from sqlalchemy import text
import logging
logger = logging.getLogger(__name__)

Base = declarative_base()
# Create engine instance
engine = create_engine(
        str(settings.database_url),
        poolclass=QueuePool,                            # стандартный пул соединений с ограничением по количеству одновременно открытых соединений.
        pool_size=settings.database_pool_size,          # Количество соединений в пуле, которое SQLAlchemy держит открытыми одновременно
        max_overflow=settings.database_max_overflow,    # Сколько дополнительных соединений можно создать сверх pool_size при пиковых нагрузках
        pool_timeout=settings.database_pool_timeout,    # Время ожидания свободного соединения из пула
        pool_recycle=settings.database_pool_recycle,    # Время жизни соединения в секундах, после которого оно будет закрыто и заменено новым.
        pool_pre_ping=True,                             # SQLAlchemy перед использованием соединения отправляет "ping" в базу.
        echo=settings.debug,                            # логирует все SQL-запросы в stdout. (если True)
        future=True,                                    # новый SQLAlchemy 2.0 API
)
# Create session factory
SessionLocal = sessionmaker(
    bind=engine,                # привязка к движку
    autoflush=False,            # не «сбрасывает» изменения автоматически перед запросами
    autocommit=False,           # явно вызываем commit(), а не автокоммит
    expire_on_commit=False,     # не «сбрасывает» все объекты после commit.
    future=True                 # Включает новый стиль SQLAlchemy 2.0
)


'''creating session'''
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def check_database_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection established successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False
