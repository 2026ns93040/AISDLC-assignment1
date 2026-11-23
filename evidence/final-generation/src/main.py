import os
import re
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from threading import Lock

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    create_engine,
    func,
    select,
    text,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.getenv("LIBRARY_DATABASE_URL", "sqlite:///library.db")
_is_memory_database = ":memory:" in DATABASE_URL
_engine_args = {"connect_args": {"check_same_thread": False}}
if _is_memory_database:
    _engine_args["poolclass"] = StaticPool
engine = create_engine(DATABASE_URL, **_engine_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
_loan_lock = Lock()


class Base(DeclarativeBase):
    pass


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    author: Mapped[str] = mapped_column(String, nullable=False)
    isbn: Mapped[str] = mapped_column(String(13), unique=True, nullable=False, index=True)
    total_copies: Mapped[int] = mapped_column(Integer, nullable=False)
    loans: Mapped[list["Loan"]] = relationship(back_populates="book")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), nullable=False, index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), nullable=False, index=True)
    loaned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    book: Mapped[Book] = relationship(back_populates="loans")
    member: Mapped[Member] = relationship(back_populates="loans")


class BookCreate(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    isbn: str = Field(pattern=r"^[0-9]{13}$")
    total_copies: int = Field(ge=1)


class BookResponse(BookCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_copies: int


class MemberCreate(BaseModel):
    name: str = Field(min_length=1)
    email: str


class MemberResponse(MemberCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LoanCreate(BaseModel):
    book_id: int
    member_id: int


class LoanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    loaned_at: datetime
    due_date: date
    returned_at: datetime | None


def _validate_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value))


def _error(status_code: int, detail: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail=detail)


def _available_copies(session: Session, book: Book) -> int:
    active = session.scalar(
        select(func.count(Loan.id)).where(
            Loan.book_id == book.id, Loan.returned_at.is_(None)
        )
    )
    return book.total_copies - int(active or 0)


def _book_response(session: Session, book: Book) -> dict:
    return {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "isbn": book.isbn,
        "total_copies": book.total_copies,
        "available_copies": _available_copies(session, book),
    }


def _utc_now() -> datetime:
    return datetime.now(UTC)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if _is_memory_database:
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="Library Book-Loan Service", lifespan=lifespan)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    messages = "; ".join(error["msg"] for error in exc.errors())
    return JSONResponse(status_code=422, content={"detail": messages})


@app.post("/books", response_model=BookResponse, status_code=201)
def create_book(payload: BookCreate):
    with SessionLocal() as session:
        if session.scalar(select(Book).where(Book.isbn == payload.isbn)):
            raise _error(409, "A book with this ISBN already exists")
        book = Book(**payload.model_dump())
        session.add(book)
        session.commit()
        session.refresh(book)
        return _book_response(session, book)


@app.get("/books/{book_id}", response_model=BookResponse)
def get_book(book_id: int):
    with SessionLocal() as session:
        book = session.get(Book, book_id)
        if book is None:
            raise _error(404, "Book not found")
        return _book_response(session, book)


@app.post("/members", response_model=MemberResponse, status_code=201)
def create_member(payload: MemberCreate):
    if not _validate_email(payload.email):
        raise _error(422, "Invalid email format")
    with SessionLocal() as session:
        normalized_email = payload.email.casefold()
        if session.scalar(
            select(Member).where(func.lower(Member.email) == normalized_email)
        ):
            raise _error(409, "A member with this email already exists")
        member = Member(name=payload.name, email=payload.email)
        session.add(member)
        session.commit()
        session.refresh(member)
        return member


@app.post("/loans", response_model=LoanResponse, status_code=201)
def create_loan(payload: LoanCreate):
    with _loan_lock, SessionLocal() as session:
        session.execute(text("BEGIN IMMEDIATE"))
        book = session.get(Book, payload.book_id)
        member = session.get(Member, payload.member_id)
        if book is None or member is None:
            session.rollback()
            raise _error(404, "Book or member not found")
        if _available_copies(session, book) <= 0:
            session.rollback()
            raise _error(409, "Book has no available copies")
        active_member_loans = session.scalar(
            select(func.count(Loan.id)).where(
                Loan.member_id == member.id, Loan.returned_at.is_(None)
            )
        )
        if int(active_member_loans or 0) >= 3:
            session.rollback()
            raise _error(409, "Member already has three active loans")
        loaned_at = _utc_now()
        loan = Loan(
            book_id=book.id,
            member_id=member.id,
            loaned_at=loaned_at,
            due_date=loaned_at.date() + timedelta(days=14),
        )
        session.add(loan)
        session.commit()
        session.refresh(loan)
        return loan


@app.post("/loans/{loan_id}/return", response_model=LoanResponse)
def return_loan(loan_id: int):
    with SessionLocal() as session:
        loan = session.get(Loan, loan_id)
        if loan is None:
            raise _error(404, "Loan not found")
        if loan.returned_at is not None:
            raise _error(409, "Loan has already been returned")
        loan.returned_at = _utc_now()
        session.commit()
        session.refresh(loan)
        return loan


@app.get("/loans/overdue", response_model=list[LoanResponse])
def list_overdue_loans():
    with SessionLocal() as session:
        return list(
            session.scalars(
                select(Loan).where(
                    Loan.returned_at.is_(None), Loan.due_date < _utc_now().date()
                )
            )
        )
