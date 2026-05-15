from datetime import date, datetime
from typing import Annotated, Literal
from fastapi import APIRouter, Depends, Path, status
from pydantic import BaseModel, Field
from exceptions import APIException

type Language = Literal["English", "Arabic", "French"]


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    author: str = Field(min_length=1, max_length=255)
    publisher: str = Field(min_length=1, max_length=255)
    published_date: date
    page_count: int = Field(gt=0)
    language: Language


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    author: str | None = Field(default=None, min_length=1, max_length=255)
    publisher: str | None = Field(default=None, min_length=1, max_length=255)
    published_date: date | None = None
    page_count: int | None = Field(default=None, gt=0)
    language: Language | None = None


class BookRead(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime


in_memory_store: list[BookRead] = [
    BookRead(
        id=1,
        title="Clean Code",
        author="Robert C. Martin",
        publisher="Prentice Hall",
        published_date=date(2008, 8, 1),
        page_count=464,
        language="English",
        created_at=datetime(2026, 5, 15, 10, 30),
        updated_at=datetime(2026, 5, 15, 10, 30),
    ),
    BookRead(
        id=2,
        title="Deep Work",
        author="Cal Newport",
        publisher="Grand Central Publishing",
        published_date=date(2016, 1, 5),
        page_count=304,
        language="English",
        created_at=datetime(2026, 5, 15, 10, 35),
        updated_at=datetime(2026, 5, 15, 10, 35),
    ),
    BookRead(
        id=3,
        title="Atomic Habits",
        author="James Clear",
        publisher="Avery",
        published_date=date(2018, 10, 16),
        page_count=320,
        language="English",
        created_at=datetime(2026, 5, 15, 10, 40),
        updated_at=datetime(2026, 5, 15, 10, 40),
    ),
    BookRead(
        id=4,
        title="فن اللامبالاة",
        author="مارك مانسون",
        publisher="دار التنوير",
        published_date=date(2020, 2, 10),
        page_count=256,
        language="Arabic",
        created_at=datetime(2026, 5, 15, 10, 45),
        updated_at=datetime(2026, 5, 15, 10, 45),
    ),
    BookRead(
        id=5,
        title="Le Petit Prince",
        author="Antoine de Saint-Exupéry",
        publisher="Gallimard",
        published_date=date(1943, 4, 6),
        page_count=96,
        language="French",
        created_at=datetime(2026, 5, 15, 10, 50),
        updated_at=datetime(2026, 5, 15, 10, 50),
    ),
]


router = APIRouter(prefix="/books", tags=["books"])


def get_book_or_404(book_id: int) -> BookRead:
    for book in in_memory_store:
        if book.id == book_id:
            return book
    raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Book not found")


@router.get("/", response_model=list[BookRead], status_code=status.HTTP_200_OK)
async def get_books():
    return in_memory_store


@router.post("/", response_model=BookRead, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookBase):
    book_id = in_memory_store[-1].id + 1 if in_memory_store else 1
    now = datetime.now()
    created_at = now
    updated_at = now
    book = BookRead(
        **data.model_dump(),
        id=book_id,
        created_at=created_at,
        updated_at=updated_at,
    )
    in_memory_store.append(book)
    return book


@router.get("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def get_book(book_id: Annotated[int, Path(gt=0)]):
    return get_book_or_404(book_id)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: Annotated[int, Path(gt=0)], _=Depends(get_book_or_404)):
    global in_memory_store
    in_memory_store = [b for b in in_memory_store if b.id != book_id]
    return


@router.put("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def update_book_full(
    data: BookBase,
    book_id: Annotated[int, Path(gt=0)],
    _=Depends(get_book_or_404),
):
    for index, book in enumerate(in_memory_store):
        if book.id == book_id:
            updated_data = book.model_dump()
            updated_data.update(data.model_dump())
            updated_data["updated_at"] = datetime.now()
            updated_book = BookRead(**updated_data)
            in_memory_store[index] = updated_book
            return updated_book
    raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Book not found")


@router.patch("/{book_id}", response_model=BookRead, status_code=status.HTTP_200_OK)
async def update_book_partial(
    data: BookUpdate,
    book_id: Annotated[int, Path(gt=0)],
    _=Depends(get_book_or_404),
):
    for index, book in enumerate(in_memory_store):
        if book.id == book_id:
            updated_data = book.model_dump()
            partial_data = data.model_dump(exclude_unset=True)
            updated_data.update(partial_data)
            updated_data["updated_at"] = datetime.now()
            updated_book = BookRead(**updated_data)
            in_memory_store[index] = updated_book
            return updated_book
    raise APIException(status_code=status.HTTP_404_NOT_FOUND, message="Book not found")
