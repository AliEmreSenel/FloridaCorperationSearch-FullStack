import asyncio
import threading
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel
from starlette.status import HTTP_404_NOT_FOUND
from db import (
    get_db,
    Corporation,
    Search,
    create_new_search,
    init_db,
    insert_search_into_db,
    insert_search_error_into_db,
)
from parser import search_corporation
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


def save_search_corporation_by_name(name, search_id, num_results):
    """
    Run a search for a corporation by name.
    """
    try:
        res = asyncio.run(search_corporation(name, num_results))
        insert_search_into_db(search_id, res)
    except Exception as e:
        insert_search_error_into_db(search_id, str(e))


class CorporationSearchRequest(BaseModel):
    name: str
    num_results: int = 1


@app.post(
    "/search/corporations",
    status_code=status.HTTP_202_ACCEPTED,
    description="Create a new search for finding corporation",
)
def search_corporation_by_name(search_data: CorporationSearchRequest):
    try:
        search_id = create_new_search(search_data.name)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error creating new search {e}",
        )
    threading.Thread(
        target=save_search_corporation_by_name,
        args=(search_data.name, search_id, search_data.num_results),
    ).start()
    return {"search_id": search_id}


@app.get(
    "/results/{search_id}", description="Retrieve the results of a search by search_id"
)
def get_corporation_details(search_id: str, db: Session = Depends(get_db)):
    search = (
        db.query(Search)
        .filter(Search.id == search_id)
        .options(
            selectinload(
                Search.results,
                Corporation.filing_info,
            ),
            selectinload(Search.results, Corporation.officers),
            selectinload(Search.results, Corporation.annual_reports),
            selectinload(Search.results, Corporation.documents),
        )
        .first()
    )
    if search is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail="search_id not found",
        )
    if search.search_status == "pending":
        raise HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="pending")
    if search.search_status == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=search.error_message,
        )
    return search.results


init_db()
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
