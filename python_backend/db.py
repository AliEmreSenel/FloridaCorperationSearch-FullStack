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
    corp_id = Column(Integer, ForeignKey("corperations.id"), index=True)
    internal_name = Column(String)
    name = Column(String)
    value = Column(String)
    corperation = relationship("Corperation", back_populates="filing_info")


class Officer(Base):
    __tablename__ = "officers"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corperations.id"), index=True)
    title = Column(String)
    name = Column(String)
    address = Column(String)
    corperation = relationship("Corperation", back_populates="officers")


class AnnualReport(Base):
    __tablename__ = "annual_reports"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corperations.id"), index=True)
    report_year = Column(Integer)
    filing_date = Column(String)
    corperation = relationship("Corperation", back_populates="annual_reports")


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    corp_id = Column(Integer, ForeignKey("corperations.id"), index=True)
    title = Column(String)
    link = Column(String)
    corperation = relationship("Corperation", back_populates="documents")


class Corperation(Base):
    __tablename__ = "corperations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, index=True)
    type = Column(String)
    filing_info = relationship("FilingInfo", back_populates="corperation")
    principal_addr = Column(String)
    principal_addr_changed = Column(String)
    mailing_addr = Column(String)
    mailing_addr_changed = Column(String)
    registered_name = Column(String)
    registered_addr = Column(String)
    registered_name_changed = Column(String)
    registered_addr_changed = Column(String)
    officers = relationship("Officer", back_populates="corperation")
    annual_reports = relationship("AnnualReport", back_populates="corperation")
    documents = relationship("Document", back_populates="corperation")


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


def insert_search_into_db(db, info):
    """
    Insert search results into the database.
    """
    corp = Corperation(
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
    for officer in info["officers"]:
        db.add(
            Officer(
                corp_id=corp.id,
                title=officer["title"],
                name=(officer["name"] if "name" in officer else None),
                address=(officer["address"] if "address" in officer else None),
            )
        )
    for report in info["annual_reports"]:
        db.add(
            AnnualReport(
                corp_id=corp.id,
                report_year=report["report_year"],
                filing_date=report["filing_date"],
            )
        )
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
    return corp
