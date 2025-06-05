from authx import AuthX, AuthXConfig


# Настройка AuthX
config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ALGORITHM = "HS256"  # Алгоритм шифрования
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]
config.JWT_COOKIE_CSRF_PROTECT = False
security = AuthX(config=config)