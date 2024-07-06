from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from .database import get_db
from . import models, schemas
from typing import List

router = APIRouter()

@router.post("/books/", response_model=schemas.Book)
async def create_book(book: schemas.BookCreate, db: AsyncSession = Depends(get_db)):
    db_book = models.Book(**book.dict())
    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.get("/books/", response_model=List[schemas.Book])
async def read_books(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Book).offset(skip).limit(limit).options(joinedload(models.Book.reviews)))
    books = result.scalars().all()
    return books

@router.get("/books/{book_id}", response_model=schemas.Book)
async def read_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id).options(joinedload(models.Book.reviews)))
    book = result.scalar_one_or_none()
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/books/{book_id}", response_model=schemas.Book)
async def update_book(book_id: int, book: schemas.BookCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    for key, value in book.dict().items():
        setattr(db_book, key, value)

    db.add(db_book)
    await db.commit()
    await db.refresh(db_book)
    return db_book

@router.delete("/books/{book_id}", response_model=schemas.Book)
async def delete_book(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Book).where(models.Book.id == book_id))
    db_book = result.scalar_one_or_none()
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    await db.delete(db_book)
    await db.commit()
    return db_book

@router.post("/books/{book_id}/reviews/", response_model=schemas.Review)
async def create_review(book_id: int, review: schemas.ReviewCreate, db: AsyncSession = Depends(get_db)):
    db_review = models.Review(**review.dict(), book_id=book_id)
    db.add(db_review)
    await db.commit()
    await db.refresh(db_review)
    return db_review

@router.get("/books/{book_id}/reviews/", response_model=List[schemas.Review])
async def read_reviews(book_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Review).where(models.Review.book_id == book_id))
    reviews = result.scalars().all()
    return reviews
