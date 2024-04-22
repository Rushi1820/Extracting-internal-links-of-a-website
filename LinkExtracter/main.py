from fastapi import FastAPI
from router import crawl_and_store_links
from db import setup_database
import uvicorn


app = FastAPI()

setup_database()

app.include_router(crawl_and_store_links.router)

if __name__ == "__main__":
    crawl_and_store_links.schedule_crawl.scheduler.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
