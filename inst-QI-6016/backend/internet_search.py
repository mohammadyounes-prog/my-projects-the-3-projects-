import requests
from bs4 import BeautifulSoup
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID

SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

def perform_google_search(query: str, num_results: int = 5):
    """
    Performs a Google search and returns the results.
    """
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "num": num_results,
    }

    try:
        response = requests.get(SEARCH_URL, params=params)
        response.raise_for_status()
        search_results = response.json()
        return search_results.get("items", [])
    except requests.exceptions.RequestException as e:
        return {"error": f"Network or API error: {e}"}
    except Exception as e:
        return {"error": f"An unexpected error occurred: {e}"}

def fetch_page_content(url: str) -> str:
    """
    Fetches the content of a web page and extracts the text.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Use BeautifulSoup to parse the HTML and extract text
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
            
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None
    except Exception as e:
        print(f"Error parsing URL {url}: {e}")
        return None

# Example usage (for testing purposes)
if __name__ == "__main__":
    test_query = "what is photosynthesis"
    print(f"Searching for: {test_query}")
    search_results = perform_google_search(test_query, num_results=3)

    if "error" in search_results:
        print(f"Error: {search_results['error']}")
    elif not search_results:
        print("No search results found.")
    else:
        for i, result in enumerate(search_results):
            print(f"\n--- Result {i+1} ---")
            print(f"Title: {result.get('title')}")
            print(f"Snippet: {result.get('snippet')}")
            print(f"Link: {result.get('link')}")

        # Test fetching content from the first link
        first_link = search_results[0].get('link')
        if first_link:
            print(f"\n--- Fetching content from: {first_link} ---")
            content = fetch_page_content(first_link)
            if content:
                # Print first 500 characters of the content
                print(content[:500] + "...")
            else:
                print("Failed to fetch content.")
