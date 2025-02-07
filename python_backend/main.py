from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from db import get_db, insert_search_into_db, init_db
from parser import search_company_by_name


app = FastAPI(title="Python Backend", version="0.1.0")


@app.get("/search/corporation/name/{name}")
def search_corporation_by_name(name: str, db: Session = Depends(get_db)):
    try:
        info = search_company_by_name(name)
        insert_search_into_db(db, info)
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"An unexpected error occurred: {e}"}
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn

    init_db()
    uvicorn.run(app, host="0.0.0.0", port=8000)
