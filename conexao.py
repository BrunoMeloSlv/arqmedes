from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Configurações de conexão ao banco de dados
DB_USER = os.getenv('DB_USER', 'consorcios')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'z83Xowj7bIuQU!')
DB_HOST = os.getenv('DB_HOST', 'consorcios.vpshost8729.mysql.dbaas.com.br')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_NAME = os.getenv('DB_NAME', 'consorcios')


DATABASE_URL = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?connect_timeout=6000'


engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,         
    max_overflow=20,      
    pool_timeout=30,      
    pool_recycle=3600,    
    pool_pre_ping=True    
)

def get_session():
    """Cria uma sessão para interação com o banco de dados."""
    Session = sessionmaker(bind=engine)
    return Session()

def get_connection():
    """Obtém uma conexão direta ao banco de dados com commit automático."""
    connection = engine.connect()
    connection = connection.execution_options(isolation_level="AUTOCOMMIT")
    return connection
