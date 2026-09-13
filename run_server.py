import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print(f"============================================================")
    print(f" Starting {settings.PROJECT_NAME} on http://127.0.0.1:{settings.PORT}")
    print(f" Swagger API Documentation: http://127.0.0.1:{settings.PORT}/docs")
    print(f" Connected to Next.js at: http://localhost:3000")
    print(f"============================================================")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
