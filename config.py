class Config:
    DEBUG = True
    ORIGINS = ["*"]


class DevConfig(Config):
    PORT = "5000"
    ORIGINS = ["http://localhost:5000"]
    REDIS_URL = "redis://redis:6379/0"


class TestConfig(DevConfig):
    TESTING = True
    REDIS_URL = 'redis://localhost:6379/1'
