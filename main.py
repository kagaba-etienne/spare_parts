import logging.config
from app.db import init_db
from app import app
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize database
init_db()

if __name__ == '__main__':
    logging.config.fileConfig('logging.conf')

    # Define logger
    logger = logging.getLogger('app')

    # Start the FastAPI application server
    import uvicorn

    uvicorn.run(app, host=os.getenv('HOST'), port=int(os.getenv('PORT', 8000)))
