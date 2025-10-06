from functools import lru_cache
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
import logging
from common.setting import get_settings



logger = logging.getLogger(__name__)
Base = declarative_base()


def build_connection_str(user, password, host, port, db=None, isAsync=False):
    """
    Build MySQL connection string
    """
    driver = 'aiomysql' if isAsync else 'pymysql'
    db_part = f"/{db}" if db else ""
    return f"mysql+{driver}://{user}:{password}@{host}:{port}{db_part}"


class MysqlDatabase:
    def __init__(self):
        settings = get_settings()
        self._username = settings.DB_USER
        self._password = settings.DB_PW
        self._host = settings.DB_HOST
        self._port = settings.DB_PORT
        self._db_name = settings.DB_NAME
        
        self.create_database()
        self.create_tables()
        self.create_async_engine_with_db()
        self.create_async_session()
        
        logger.info("Init instance database")


    def create_async_engine_with_db(self):
        # Main engine (connected to target DB)
        self.async_engine = create_async_engine(
            build_connection_str(
                self._username, self._password, 
                self._host, self._port, 
                self._db_name, isAsync=True
            ),
            pool_pre_ping=True,
            pool_recycle=3600,
            future=True
        )
        logger.info("Create async engine")
        

    def create_async_session(self):
        self.async_session = sessionmaker(
            autocommit=False, autoflush=False, bind=self.async_engine,
            expire_on_commit=False, class_=AsyncSession
        )
        logger.info("Create async session")
        

    def create_database(self):
        """
        Create the database if it does not exist.
        """
        root_engine = create_engine(
            build_connection_str(self._username, self._password, 
                                 self._host, self._port),
            pool_pre_ping=True,
        )
        with root_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{self._db_name}`"))
            conn.commit()
        logger.info(f"Create the database {self._db_name}.")


    def create_tables(self):
        """
        Create tables if they do not exist.
        """
        root_engine = create_engine(
            build_connection_str(self._username, self._password, self._host, 
                                 self._port, self._db_name),
            pool_pre_ping=True
        )
        Base.metadata.create_all(root_engine)
        logger.info("Create tables")


    async def get_db(self):
        """
        Dependency for FastAPI: yields a DB session.
        """
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

@lru_cache(maxsize=None)
def get_database() -> MysqlDatabase:
    """
    Cached singleton for MysqlDatabase instance
    """
    return  MysqlDatabase()
