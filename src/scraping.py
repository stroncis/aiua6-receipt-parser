import requests
import re


def fetch_html(url, timeout=10):
    """
    Fetch HTML content from a URL. Returns HTML string or None.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            return resp.text
        else:
            print(f"Failed to fetch {url}, status: {resp.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None


def extract_vmi_content(qr_url):
    """
    Scrape kvitas.vmi.lt
    Extract relevant content from the HTML.
    """
    print(f"Scraping data from: {qr_url}")
    if not qr_url:
        print("No QR URL provided.")
        return None, None
    sum_match = ''
    address_match = ''
    try:
        html = fetch_html(qr_url)
        if html is None:
            print("Failed to retrieve QR page.")
            return None, None
        sum_match = re.search(r'Suma.*?(\d+[.,]\d+)', html)
        address_match = re.search(r'Adresas.*?<td[^>]*>(.*?)<', html, re.DOTALL)
    except Exception as e:
        print(f"Error scraping QR page: {e}")
    return sum_match, address_match
