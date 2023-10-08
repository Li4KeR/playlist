from app import app
from config import ip, port

if __name__ == "__main__":
    app.run(host=ip, port=port)
