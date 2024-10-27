from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

app = Flask(__name__)

def crawl_website(root_webpage, depth):
    crawled_links = set()
    queue = deque([(root_webpage, 0)])  # (URL, current depth)
    
    while queue:
        url, current_depth = queue.popleft()
        
        if current_depth < depth:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        full_url = urljoin(url, link['href'])
                        if urlparse(full_url).scheme in ['http', 'https'] and full_url not in crawled_links:
                            crawled_links.add(full_url)
                            queue.append((full_url, current_depth + 1))
            except Exception as e:
                print(f"Error crawling {url}: {str(e)}")
    
    return list(crawled_links)

@app.route('/api/crawl', methods=['POST'])
def crawl():
    data = request.json
    root_webpage = data.get('root_webpage')
    depth = data.get('depth')

    if not root_webpage or depth < 0:
        return jsonify({'status': 'error', 'data': None, 'error': 'Invalid URL or depth provided'}), 400

    crawled_links = crawl_website(root_webpage, depth)
    return jsonify({'status': 'success', 'data': {'crawled_links': crawled_links}, 'error': None})

if __name__ == '__main__':
    app.run(debug=True)


# ---------------------------------------------------  Exection  -------------------------------------------------------------

# ---------------------------------------------------  Terminal  -------------------------------------------------------------

# python app.py
# curl -X POST http://127.0.0.1:5000/api/crawl \
# -H "Content-Type: application/json" \
# -d '{"root_webpage": "https://example.com", "depth": 2}'
