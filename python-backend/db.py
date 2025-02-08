import os
from sqlalchemy import ForeignKey, create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# Use an environment variable for the database URL; adjust the default as needed.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://backend:backend@localhost:5432/corperate_info_db"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class FilingInfo(Base):
    __tablename__ = "filing_info"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corporations.id"), index=True)
    internal_name = Column(String)
    name = Column(String)
    value = Column(String)
    corporation = relationship("Corporation", back_populates="filing_info")


class Officer(Base):
    __tablename__ = "officers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corporations.id"), index=True)
    title = Column(String)
    name = Column(String)
    address = Column(String)
    corporation = relationship("Corporation", back_populates="officers")


class AnnualReport(Base):
    __tablename__ = "annual_reports"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corporations.id"), index=True)
    report_year = Column(Integer)
    filing_date = Column(String)
    corporation = relationship("Corporation", back_populates="annual_reports")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corporations.id"), index=True)
    title = Column(String)
    link = Column(String)
    corporation = relationship("Corporation", back_populates="documents")


class Corporation(Base):
    __tablename__ = "corporations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    search_id = Column(Integer, ForeignKey("searches.id"), index=True)
    name = Column(String, index=True)
    type = Column(String)
    filing_info = relationship("FilingInfo", back_populates="corporation")
    principal_addr = Column(String)
    principal_addr_changed = Column(String)
    mailing_addr = Column(String)
    mailing_addr_changed = Column(String)
    registered_name = Column(String)
    registered_addr = Column(String)
    registered_name_changed = Column(String)
    registered_addr_changed = Column(String)
    officers = relationship("Officer", back_populates="corporation")
    annual_reports = relationship("AnnualReport", back_populates="corporation")
    documents = relationship("Document", back_populates="corporation")
    searches = relationship("Search", back_populates="results")


class Search(Base):
    __tablename__ = "searches"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    search_query = Column(String)
    search_status = Column(String)
    error_message = Column(String)
    results = relationship("Corporation", back_populates="searches")


def init_db():
    """
    Initialize the database by creating all tables.
    """
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency for getting a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_new_search(search_query):
    """
    Create a new search in the database.
    """
    db = SessionLocal()
    search = Search(search_query=search_query, search_status="pending")
    db.add(search)
    db.commit()
    db.refresh(search)
    db.close()
    return search.id


def insert_search_into_db(search_id, info):
    """
    Insert search results into the database.
    """
    db = SessionLocal()
    corp = Corporation(
        search_id=search_id,
        name=info["corp_name"],
        type=info["corp_type"],
        principal_addr=info["principal_addr"],
        principal_addr_changed=(
            info["principal_addr_changed"] if "principal_addr_changed" in info else None
        ),
        mailing_addr=info["mailing_addr"],
        mailing_addr_changed=(
            info["mailing_addr_changed"] if "mailing_addr_changed" in info else None
        ),
        registered_name=info["registered_name"],
        registered_addr=info["registered_addr"],
        registered_name_changed=(
            info["registered_name_changed"]
            if "registered_name_changed" in info
            else None
        ),
        registered_addr_changed=(
            info["registered_addr_changed"]
            if "registered_addr_changed" in info
            else None
        ),
    )
    db.add(corp)
    db.commit()
    for filing_info in info["filing_info"]:
        db.add(
            FilingInfo(
                corp_id=corp.id,
                internal_name=filing_info["internal_name"],
                name=filing_info["name"],
                value=filing_info["value"],
            )
        )
    if "officers" in info:
        for officer in info["officers"]:
            db.add(
                Officer(
                    corp_id=corp.id,
                    title=officer["title"],
                    name=(officer["name"] if "name" in officer else None),
                    address=(officer["address"] if "address" in officer else None),
                )
            )
    if "annual_reports" in info:
        for report in info["annual_reports"]:
            db.add(
                AnnualReport(
                    corp_id=corp.id,
                    report_year=report["report_year"],
                    filing_date=report["filing_date"],
                )
            )
    if "documents" in info:
        for document in info["documents"]:
            db.add(
                Document(
                    corp_id=corp.id,
                    title=document["title"],
                    link=document["link"],
                )
            )
    db.commit()
    db.refresh(corp)

    search = db.query(Search).filter(Search.id == search_id).first()
    search.search_status = "completed"
    search.results = [corp]
    db.commit()
    db.refresh(search)
    db.close()


def insert_search_error_into_db(search_id, error_message):
    """
    Insert a search error into the database.
    """
    db = SessionLocal()
    search = db.query(Search).filter(Search.id == search_id).first()
    search.search_status = "error"
    search.error_message = error_message
    db.commit()
    db.refresh(search)
    db.close()
