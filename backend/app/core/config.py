from pydantic_settings import BaseSettings
from decouple import config

class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./tabletennis.db")
    
    # JWT配置
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key-here")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # 应用配置
    APP_NAME: str = "乒乓球培训管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    
    # 支付配置
    WECHAT_PAY_APP_ID: str = config("WECHAT_PAY_APP_ID", default="")
    WECHAT_PAY_MCH_ID: str = config("WECHAT_PAY_MCH_ID", default="")
    ALIPAY_APP_ID: str = config("ALIPAY_APP_ID", default="")
    
    # 许可证服务器配置
    LICENSE_SERVER_URL: str = config("LICENSE_SERVER_URL", default="https://license.example.com")
    LICENSE_VALIDATION_KEY: str = config("LICENSE_VALIDATION_KEY", default="")
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    
    # 系统配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings()
