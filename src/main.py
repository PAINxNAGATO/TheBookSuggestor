from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from transformers import pipeline, Conversation
from typing import List
from pydantic import BaseModel
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

class Book(BaseModel):
    title: str
    author: str
    rating: float

# Initialize the conversational pipeline
conversational_pipeline = pipeline("conversational", model="microsoft/DialoGPT-medium")

# Store books data to simulate a stateful interaction
books_data = {"books": [], "top_books": [], "selected_book": None}

@app.get("/", response_class=HTMLResponse)
def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/recommend-books", response_class=HTMLResponse)
async def fetch_top_books(request: Request, genre: str = Form(...)):
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

    global books_data
    books_data["books"] = books  # Store the fetched books

    return templates.TemplateResponse("books.html", {"request": request, "books": books})

@app.post("/top-ten-books", response_class=HTMLResponse)
async def fetch_top_ten_books(request: Request):
    global books_data
    top_books = sorted(books_data["books"], key=lambda x: x.rating, reverse=True)[:10]
    books_data["top_books"] = top_books  # Store the top 10 books

    return templates.TemplateResponse("top_books.html", {"request": request, "top_books": top_books})

@app.post("/select-book", response_class=HTMLResponse)
async def select_book(request: Request, book_title: str = Form(...)):
    global books_data
    print(f"Top books: {books_data['top_books']}")
    selected_book = next((book for book in books_data["top_books"] if book.title == book_title), None)
    print(f"Selected book: {selected_book}")
    books_data["selected_book"] = selected_book  # Store the selected book

    return templates.TemplateResponse("selected_book.html", {"request": request, "selected_book": selected_book})

@app.post("/interact", response_class=HTMLResponse)
async def interact_with_model(request: Request, user_input: str = Form(...)):
    conversation = Conversation(user_input)
    response = conversational_pipeline([conversation])
    return templates.TemplateResponse("response.html", {"request": request, "response": response[0].generated_responses[-1].text})

@app.post("/thank-you", response_class=HTMLResponse)
async def thank_you(request: Request):
    return templates.TemplateResponse("thank_you.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
