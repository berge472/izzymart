import requests
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class BookLookup:
    """
    Utility class for looking up books using ISBN/UPC.
    Uses Open Library API (free, no key required) as primary source,
    with Google Books API as fallback.
    """

    def __init__(self):
        self.openlibrary_url = "https://openlibrary.org/api/books"
        self.google_books_url = "https://www.googleapis.com/books/v1/volumes"
        self.headers = {
            'User-Agent': 'IzzyMart/1.0 (Book Lookup Service)',
        }

    def lookup_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Look up a book by ISBN using Open Library first, then Google Books as fallback.

        Args:
            isbn: ISBN-10 or ISBN-13 number

        Returns:
            Complete book information dictionary or None
        """
        try:
            logger.info(f"Looking up ISBN {isbn}")

            # Try Open Library first (free, no key required)
            book_data = self._lookup_openlibrary(isbn)

            if book_data:
                logger.info(f"Book found in Open Library: {book_data.get('name')}")
                return book_data

            # Fallback to Google Books
            logger.info("Book not found in Open Library, trying Google Books...")
            book_data = self._lookup_google_books(isbn)

            if book_data:
                logger.info(f"Book found in Google Books: {book_data.get('name')}")
                return book_data

            logger.warning(f"Book not found in any source for ISBN: {isbn}")
            return None

        except Exception as e:
            logger.error(f"Unexpected error in book lookup: {str(e)}")
            return None

    def _lookup_openlibrary(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Look up a book using Open Library API.

        Args:
            isbn: ISBN number

        Returns:
            Book information dictionary or None
        """
        try:
            # Open Library API: https://openlibrary.org/dev/docs/api/books
            url = f"{self.openlibrary_url}?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Open Library returned status {response.status_code} for ISBN {isbn}")
                return None

            data = response.json()
            key = f"ISBN:{isbn}"

            if key not in data:
                logger.warning(f"Book not found in Open Library: {isbn}")
                return None

            book = data[key]
            return self._extract_openlibrary_data(book, isbn)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Open Library for ISBN {isbn}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Open Library response: {str(e)}")
            return None

    def _lookup_google_books(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Look up a book using Google Books API.

        Args:
            isbn: ISBN number

        Returns:
            Book information dictionary or None
        """
        try:
            # Google Books API: https://developers.google.com/books/docs/v1/using
            url = f"{self.google_books_url}?q=isbn:{isbn}"
            response = requests.get(url, headers=self.headers, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Google Books returned status {response.status_code} for ISBN {isbn}")
                return None

            data = response.json()

            if data.get('totalItems', 0) == 0:
                logger.warning(f"Book not found in Google Books: {isbn}")
                return None

            # Get the first book result
            book = data['items'][0]
            return self._extract_google_books_data(book, isbn)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching from Google Books for ISBN {isbn}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error parsing Google Books response: {str(e)}")
            return None

    def _extract_openlibrary_data(self, book: Dict, isbn: str) -> Dict[str, Any]:
        """Extract and format book data from Open Library response."""
        book_data = {
            'product_type': 'book',
            'upc': isbn,
            'isbn': isbn,
            'name': book.get('title'),
            'description': book.get('subtitle'),
            'tags': [],
            'metadata': {}
        }

        # Extract authors
        authors = book.get('authors', [])
        if authors:
            book_data['author'] = ', '.join([author.get('name', '') for author in authors])

        # Extract publisher
        publishers = book.get('publishers', [])
        if publishers:
            book_data['publisher'] = publishers[0].get('name')

        # Extract publication date
        if book.get('publish_date'):
            book_data['publication_date'] = book['publish_date']

        # Extract page count
        if book.get('number_of_pages'):
            book_data['page_count'] = book['number_of_pages']

        # Extract categories/subjects
        subjects = book.get('subjects', [])
        if subjects:
            book_data['categories'] = [subject.get('name', '') for subject in subjects[:5]]  # Limit to 5
            book_data['tags'] = book_data['categories']

        # Extract cover image
        if book.get('cover'):
            # Open Library provides small, medium, and large covers
            cover = book['cover']
            if cover.get('large'):
                book_data['image_url'] = cover['large']
            elif cover.get('medium'):
                book_data['image_url'] = cover['medium']
            elif cover.get('small'):
                book_data['image_url'] = cover['small']

        # Add metadata
        book_data['metadata']['source'] = 'Open Library'
        if book.get('url'):
            book_data['metadata']['openlibrary_url'] = book['url']

        return book_data

    def _extract_google_books_data(self, item: Dict, isbn: str) -> Dict[str, Any]:
        """Extract and format book data from Google Books response."""
        volume_info = item.get('volumeInfo', {})

        book_data = {
            'product_type': 'book',
            'upc': isbn,
            'isbn': isbn,
            'name': volume_info.get('title'),
            'description': volume_info.get('description'),
            'tags': [],
            'metadata': {}
        }

        # Extract authors
        authors = volume_info.get('authors', [])
        if authors:
            book_data['author'] = ', '.join(authors)

        # Extract publisher
        if volume_info.get('publisher'):
            book_data['publisher'] = volume_info['publisher']

        # Extract publication date
        if volume_info.get('publishedDate'):
            book_data['publication_date'] = volume_info['publishedDate']

        # Extract page count
        if volume_info.get('pageCount'):
            book_data['page_count'] = volume_info['pageCount']

        # Extract language
        if volume_info.get('language'):
            book_data['language'] = volume_info['language']

        # Extract categories
        categories = volume_info.get('categories', [])
        if categories:
            book_data['categories'] = categories
            book_data['tags'] = categories

        # Extract cover image
        image_links = volume_info.get('imageLinks', {})
        if image_links:
            # Prefer larger images
            if image_links.get('extraLarge'):
                book_data['image_url'] = image_links['extraLarge']
            elif image_links.get('large'):
                book_data['image_url'] = image_links['large']
            elif image_links.get('medium'):
                book_data['image_url'] = image_links['medium']
            elif image_links.get('thumbnail'):
                book_data['image_url'] = image_links['thumbnail']
            elif image_links.get('smallThumbnail'):
                book_data['image_url'] = image_links['smallThumbnail']

        # Add metadata
        book_data['metadata']['source'] = 'Google Books'
        if item.get('selfLink'):
            book_data['metadata']['google_books_url'] = item['selfLink']

        return book_data


# Global instance
book_lookup = BookLookup()


def lookup_book_by_isbn(isbn: str) -> Optional[Dict[str, Any]]:
    """
    Convenience function to lookup a book by ISBN.

    Args:
        isbn: ISBN-10 or ISBN-13 number

    Returns:
        Complete book information or None
    """
    return book_lookup.lookup_by_isbn(isbn)
