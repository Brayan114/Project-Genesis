from ddgs import DDGS # <--- THE FIX

def search_internet(query):
    print(f"  [SYSTEM: Genesis is searching the web for '{query}'...]")
    try:
        # The syntax for the new library is slightly cleaner
        results = DDGS().text(query, max_results=3)
        
        if not results:
            return "No results found on the web."
        
        # Format the results for the Brain to read
        summary = "WEB SEARCH RESULTS:\n"
        for result in results:
            summary += f"- {result['title']}: {result['body']}\n"
        
        return summary
    except Exception as e:
        return f"Error searching web: {e}"