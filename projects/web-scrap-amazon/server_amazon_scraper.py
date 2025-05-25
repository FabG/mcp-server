import os
import asyncio
from lxml import html as lxml_html
from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright

# Define a temporary file path for the HTML content
HTML_FILE = os.path.join(os.getenv("TMPDIR", "/tmp"), "amazon_product_page.html")

# Initialize the MCP server with a descriptive name
mcp = FastMCP("Amazon Product Scraper")

print("MCP Server Initialized: Amazon Product Scraper")

@mcp.tool()
async def fetch_page(url: str) -> str:
    """
    Fetches the HTML content of the given Amazon product URL using Playwright
    and saves it to a temporary file. Returns a status message.
    """
    print(f"Executing fetch_page for URL: {url}")
    try:
        async with async_playwright() as p:
            # Launch headless Chromium browser
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            # Navigate to the URL with a generous timeout
            await page.goto(url, timeout=90000, wait_until="domcontentloaded")
            # Wait for a key element (e.g., body) to ensure basic loading
            await page.wait_for_selector("body", timeout=30000)
            # Add a small delay for any dynamic content rendering via JavaScript
            await asyncio.sleep(5)

            html_content = await page.content()
            with open(HTML_FILE, "w", encoding="utf-8") as f:
                f.write(html_content)

            await browser.close()
            print(f"Successfully fetched and saved HTML to {HTML_FILE}")
            return f"HTML content for {url} downloaded and saved successfully to {HTML_FILE}."
    except Exception as e:
        error_message = f"Error fetching page {url}: {str(e)}"
        print(error_message)
        return error_message

def _extract_xpath(tree, xpath, default="N/A"):
    """Helper function to extract text using XPath, returning default if not found."""
    try:
        # Use text_content() to get text from node and children, strip whitespace
        result = tree.xpath(xpath)
        if result:
            return result[0].text_content().strip()
        return default
    except Exception:
        return default

def _extract_price(price_str):
    """Helper function to parse price string into a float."""
    if price_str == "N/A":
        return None
    try:
        # Remove currency symbols and commas, handle potential whitespace
        cleaned_price = "".join(filter(str.isdigit or str.__eq__("."), price_str))
        return float(cleaned_price)
    except (ValueError, TypeError):
        return None

@mcp.tool()
def extract_info() -> dict:
    """
    Parses the saved HTML file (downloaded by fetch_page) to extract
    Amazon product details like title, price, rating, features, etc.
    Returns a dictionary of the extracted data.
    """
    print(f"Executing extract_info from file: {HTML_FILE}")
    if not os.path.exists(HTML_FILE):
        return {
            "error": f"HTML file not found at {HTML_FILE}. Please run fetch_page first."
        }

    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            page_html = f.read()

        tree = lxml_html.fromstring(page_html)

        # --- XPath Selectors for Amazon Product Details ---
        title = _extract_xpath(tree, '//span[@id="productTitle"]')
        # Handle different price structures (main price, sale price)
        price_whole = _extract_xpath(tree, '//span[contains(@class, "a-price-whole")]')
        price_fraction = _extract_xpath(
            tree, '//span[contains(@class, "a-price-fraction")]'
        )
        price_str = (
            f"{price_whole}.{price_fraction}"
            if price_whole != "N/A"
            else _extract_xpath(tree, '//span[contains(@class,"a-offscreen")]')
        )  # Fallback to offscreen if needed

        price = _extract_price(price_str)

        # Original price (strike-through)
        original_price_str = _extract_xpath(
            tree, '//span[@class="a-price a-text-price"]//span[@class="a-offscreen"]'
        )
        original_price = _extract_price(original_price_str)

        # Rating
        rating_text = _extract_xpath(tree, '//span[@id="acrPopover"]/@title')
        rating = None
        if rating_text != "N/A":
            try:
                rating = float(rating_text.split()[0])
            except (ValueError, IndexError):
                rating = None

        # Review Count
        reviews_text = _extract_xpath(tree, '//span[@id="acrCustomerReviewText"]')
        review_count = None
        if reviews_text != "N/A":
            try:
                review_count = int(reviews_text.split()[0].replace(",", ""))
            except (ValueError, IndexError):
                review_count = None

        # Availability
        availability = _extract_xpath(
            tree,
            '//div[@id="availability"]//span/text()',
        )

        # Features (bullet points)
        feature_elements = tree.xpath(
            '//div[@id="feature-bullets"]//li//span[@class="a-list-item"]'
        )
        features = [
            elem.text_content().strip()
            for elem in feature_elements
            if elem.text_content().strip()
        ]

        # Calculate Discount
        discount = None
        if price and original_price and original_price > price:
            discount = round(((original_price - price) / original_price) * 100)

        extracted_data = {
            "title": title,
            "price": price,
            "original_price": original_price,
            "discount_percent": discount,
            "rating_stars": rating,
            "review_count": review_count,
            "features": features,
            "availability": availability.strip(),
        }
        print(f"Successfully extracted data: {extracted_data}")
        return extracted_data

    except Exception as e:
        error_message = f"Error parsing HTML: {str(e)}"
        print(error_message)  # Added for logging
        return {"error": error_message}

if __name__ == "__main__":
    print("Starting MCP Server with stdio transport...")
    # Run the server, listening via standard input/output
    mcp.run(transport="stdio")