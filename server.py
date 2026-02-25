from app import create_app
import uvicorn
from app.config import settings

app = create_app()

if __name__ == "__main__":
    uvicorn.run("server:app", host=settings.API_HOST)