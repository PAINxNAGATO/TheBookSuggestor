from pydantic import BaseModel
from typing import List

class Book(BaseModel):
    title: str
    author: str
    rating: float
    genre: str

class BookRequest(BaseModel):
    genre: str

class BookResponse(BaseModel):
    top_books: List[Book]
