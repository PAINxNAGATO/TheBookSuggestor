import requests
from typing import List
from models import Book  # Import your Book model

GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
MAX_RESULTS_PER_PAGE = 40  # Google Books API max limit per request
TOTAL_BOOKS_TO_FETCH = 100

def fetch_top_books(genre: str) -> List[Book]:
    books = []
    start_index = 0
    remaining_books_to_fetch = TOTAL_BOOKS_TO_FETCH

    try:
        while remaining_books_to_fetch > 0:
            params = {
                "q": f"subject:{genre}",  # Search by genre
                "orderBy": "relevance",   # Order by relevance
                "startIndex": start_index,
                "maxResults": min(MAX_RESULTS_PER_PAGE, remaining_books_to_fetch)  # Limit to remaining books
            }

            response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
            response.raise_for_status()  # Raise an error for bad responses (4xx or 5xx)
            data = response.json().get("items", [])

            if not data:
                break

            for item in data:
                volume_info = item.get("volumeInfo")
                if volume_info:
                    title = volume_info.get("title", "Unknown Title")
                    authors = volume_info.get("authors", ["Unknown Author"])
                    rating = volume_info.get("averageRating", 0.0)
                    genre = volume_info.get("categories", ["Unknown Genre"])[0] if volume_info.get("categories") else "Unknown Genre"

                    book = Book(title=title, author=", ".join(authors), rating=rating, genre=genre)
                    books.append(book)

                    remaining_books_to_fetch -= 1
                    if remaining_books_to_fetch <= 0:
                        break

            start_index += MAX_RESULTS_PER_PAGE

    except requests.RequestException as e:
        print(f"Error fetching books: {e}")

    return books[:TOTAL_BOOKS_TO_FETCH]  # Return up to 100 books
