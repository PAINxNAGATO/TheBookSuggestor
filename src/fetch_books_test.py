from services import fetch_top_books

def main():
    genre = "Biography"  # Replace with the genre you want to fetch books for
    books = fetch_top_books(genre)

    if books:
        print(f"Fetched {len(books)} books in genre '{genre}':")
        for idx, book in enumerate(books, start=1):
            print(f"{idx}. {book.title} by {book.author} - Rating: {book.rating}")
    else:
        print(f"No books fetched for genre '{genre}'.")

if __name__ == "__main__":
    main()
