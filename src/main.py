from fastapi import FastAPI, Request, HTTPException, Query, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List
from pydantic import BaseModel
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Book(BaseModel):
    title: str
    author: str
    rating: float

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/recommend-books", response_class=HTMLResponse)
def fetch_top_books(request: Request, genre: str = Query(..., description="The genre of books to recommend")):
    GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
    MAX_RESULTS_PER_PAGE = 40  # Max results per page from Google Books API
    MAX_TOTAL_RESULTS = 100  # Total number of results desired

    books = []
    total_results_fetched = 0

    try:
        while total_results_fetched < MAX_TOTAL_RESULTS:
            params = {
                "q": f"subject:{genre}",
                "orderBy": "relevance",
                "maxResults": min(MAX_RESULTS_PER_PAGE, MAX_TOTAL_RESULTS - total_results_fetched),
                "startIndex": total_results_fetched
            }

            response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)

            data = response.json().get("items", [])

            for item in data:
                volume_info = item.get("volumeInfo")
                if volume_info:
                    title = volume_info.get("title", "Unknown Title")
                    authors = volume_info.get("authors", ["Unknown Author"])
                    rating = volume_info.get("averageRating", 0.0)

                    book = Book(title=title, author=", ".join(authors), rating=rating)
                    books.append(book)
                    total_results_fetched += 1

            if not data:
                break  # Break out of loop if no more results

    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error fetching books: {e}")

    return templates.TemplateResponse("books.html", {"request": request, "books": books[:MAX_TOTAL_RESULTS], "genre": genre})

@app.post("/top-10-books", response_class=HTMLResponse)
def get_top_10_books(request: Request, genre: str = Form(...)):
    books = fetch_top_books(request, genre)
    top_10_books = sorted(books.context['books'], key=lambda x: x.rating, reverse=True)[:10]
    return templates.TemplateResponse("top_10_books.html", {"request": request, "books": top_10_books})

@app.post("/select-book", response_class=HTMLResponse)
def select_book(request: Request, selected_book_title: str = Form(...)):
    return templates.TemplateResponse("select_book.html", {"request": request, "selected_book_title": selected_book_title})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
