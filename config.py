class Config:
    DEBUG = True
    ORIGINS = ["*"]

class DevConfig(Config):
    PORT = "5000"
    ORIGINS = ["http://localhost:5000"]
