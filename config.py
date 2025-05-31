import os
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('FLASK_HOST', '127.0.0.1')
    PORT = int(os.environ.get('FLASK_PORT', 5000))
    
    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///chatbot.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Security Configuration
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None
    
    # Rate Limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL', 'memory://')
    RATELIMIT_DEFAULT = "100 per hour"
    
    # Chatbot Configuration
    CHATBOT_NAME = os.environ.get('CHATBOT_NAME', 'Data Engineering Assistant')
    MAX_MESSAGE_LENGTH = int(os.environ.get('MAX_MESSAGE_LENGTH', 500))
    MAX_CONVERSATION_HISTORY = int(os.environ.get('MAX_CONVERSATION_HISTORY', 50))
    RESPONSE_TIMEOUT = int(os.environ.get('RESPONSE_TIMEOUT', 30))
    
    # AI/ML Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    MODEL_NAME = os.environ.get('MODEL_NAME', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.environ.get('MAX_TOKENS', 150))
    TEMPERATURE = float(os.environ.get('TEMPERATURE', 0.7))
    
    # Vector Database Configuration
    VECTOR_DB_TYPE = os.environ.get('VECTOR_DB_TYPE', 'chroma')  # chroma, pinecone, weaviate
    PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
    PINECONE_ENVIRONMENT = os.environ.get('PINECONE_ENVIRONMENT')
    CHROMA_PERSIST_DIRECTORY = os.environ.get('CHROMA_PERSIST_DIRECTORY', './chroma_db')
    
    # Embedding Configuration
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    EMBEDDING_DIMENSION = int(os.environ.get('EMBEDDING_DIMENSION', 384))
    
    # Knowledge Base Configuration
    KNOWLEDGE_BASE_PATH = os.environ.get('KNOWLEDGE_BASE_PATH', './data/knowledge_base.json')
    DOCUMENTS_PATH = os.environ.get('DOCUMENTS_PATH', './data/documents/')
    INDEX_UPDATE_INTERVAL = int(os.environ.get('INDEX_UPDATE_INTERVAL', 3600))  # seconds
    
    # Logging Configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'chatbot.log')
    LOG_MAX_BYTES = int(os.environ.get('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.environ.get('LOG_BACKUP_COUNT', 5))
    
    # CORS Configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', './uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'txt,pdf,docx,csv').split(','))
    
    # Cache Configuration
    CACHE_TYPE = os.environ.get('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT', 300))
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    # Monitoring Configuration
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    ENABLE_METRICS = os.environ.get('ENABLE_METRICS', 'False').lower() == 'true'
    METRICS_PORT = int(os.environ.get('METRICS_PORT', 8000))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False
    
    # More verbose logging in development
    LOG_LEVEL = 'DEBUG'
    
    # Disable security features for development
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False
    
    # Relaxed rate limiting for development
    RATELIMIT_DEFAULT = "1000 per hour"


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    
    # Strict security in production
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_ENABLED = True
    
    # Production rate limiting
    RATELIMIT_DEFAULT = "60 per hour"
    
    # Production logging
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    
    # Use in-memory database for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Fast testing
    BCRYPT_LOG_ROUNDS = 4


# Configuration mapping
config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config_map.get(env, config_map['default'])

class ChatbotSettings:
    """Chatbot-specific settings and knowledge base configuration"""
    
    # Intent Classification
    INTENT_CONFIDENCE_THRESHOLD = 0.7
    FALLBACK_RESPONSES = [
        "I'm not sure I understand. Could you rephrase that?",
        "Can you tell me more about what you're looking for?",
        "I'd be happy to help! Could you be more specific?",
        "That's an interesting question. Can you provide more context?"
    ]
    
    # Knowledge Base Categories
    KNOWLEDGE_CATEGORIES = {
        'data_engineering': {
            'keywords': ['pipeline', 'etl', 'data', 'warehouse', 'lake', 'streaming'],
            'priority': 1
        },
        'databases': {
            'keywords': ['sql', 'nosql', 'postgres', 'mongodb', 'redis', 'database'],
            'priority': 1
        },
        'cloud_platforms': {
            'keywords': ['aws', 'azure', 'gcp', 'cloud', 's3', 'bigquery'],
            'priority': 2
        },
        'programming': {
            'keywords': ['python', 'spark', 'pandas', 'airflow', 'kafka'],
            'priority': 2
        },
        'general': {
            'keywords': ['hello', 'hi', 'help', 'what', 'how', 'why'],
            'priority': 3
        }
    }
    
    # Response Templates
    RESPONSE_TEMPLATES = {
        'greeting': [
            "Hello! I'm your Data Engineering Assistant. How can I help you today?",
            "Hi there! Ready to dive into some data engineering topics?",
            "Welcome! I'm here to help with all your data engineering questions."
        ],
        'clarification': [
            "Could you provide more details about {}?",
            "I'd like to help with {}. Can you be more specific?",
            "Tell me more about what you want to know regarding {}."
        ],
        'error': [
            "I apologize, but I encountered an error processing your request.",
            "Something went wrong. Please try rephrasing your question.",
            "I'm having trouble with that request. Could you try again?"
        ]
    }
    
    # Personality Settings
    PERSONALITY = {
        'tone': 'professional_friendly',
        'expertise_level': 'intermediate', }