import asyncio
import threading
from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, selectinload

from db import (
    get_db,
    init_db,
    Corperation,
    Search,
    create_new_search,
    insert_search_into_db,
    insert_search_error_into_db,
)
from parser import search_corperation
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="Python Backend", version="0.1.0")

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_search_corperation_by_name(name, search_id):
    """
    Run a search for a corperation by name.
    """
    try:
        res = asyncio.run(search_corperation(name))
        insert_search_into_db(search_id, res)
    except Exception as e:
        insert_search_error_into_db(search_id, str(e))


@app.get("/search/corperation/name/{name}")
def search_corperation_by_name(name: str):
    search_id = create_new_search(name)
    threading.Thread(
        target=save_search_corperation_by_name, args=(name, search_id)
    ).start()
    return {"search_id": search_id}


@app.get("/results/{search_id}")
def get_corperation_details(search_id: str, db: Session = Depends(get_db)):
    search = (
        db.query(Search)
        .filter(Search.id == search_id)
        .options(
            selectinload(
                Search.results,
                Corperation.filing_info,
            ),
            selectinload(Search.results, Corperation.officers),
            selectinload(Search.results, Corperation.annual_reports),
            selectinload(Search.results, Corperation.documents),
        )
        .first()
    )
    if search is None:
        return {"status": "error", "message": "search_id not found"}
    if search.search_status == "pending":
        return {"status": "pending"}
    if search.search_status == "error":
        return {"status": "error", "message": search.error_message}
    return {"status": "completed", "results": search.results}


if __name__ == "__main__":
    import uvicorn

    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
