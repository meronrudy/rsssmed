
import logging
import pathlib
from typing import Dict, List, Optional
import feedparser
import httpx
from bs4 import BeautifulSoup

# Configure logging settings
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Function to parse an RSS feed and convert it to a list of dictionaries

def parse_rss(feed_url: str) -> List[Dict[str, Optional[str]]]:
    logging.info("Starting parse_rss function")
    try:
        feed = feedparser.parse(feed_url)
    except Exception as e:
        logging.error(f"Failed to parse the RSS feed: {e}")
        return []

    rss_list = []

    # Iterate through the feed entries and extract the title, link, and published date
    for entry in feed.entries:
        rss_list.append(
            {"title": entry.title, "link": entry.link, "published": entry.published}
        )
    return rss_list

# Function to fetch and save the content of each linked webpage as an HTML file
def fetch_and_save_articles(
    list_of_articles: List[Dict[str, Optional[str]]], output_dir: str
) -> None:
    logging.info("Starting fetch_and_save_articles function")

    # Create the output directory if it doesn't exist
    if not pathlib.Path(output_dir).exists():
        pathlib.Path(output_dir).mkdir(parents=True)

    # Iterate through all articles and fetch the content of each linked webpage
    for item in list_of_articles:
        try:
            with httpx.Client() as client:
                response = client.get(item["link"])

            # Follow redirects manually if necessary
            while response.is_redirect:
                redirect_url = response.headers["Location"]
                with httpx.Client() as client:
                    response = client.get(redirect_url)

            # Check if the request was successful
            if response.status_code == 200:
                html_content = response.text

                # Parse the HTML content and extract the <article> tag
                soup = BeautifulSoup(html_content, "html.parser")
                article = soup.find("article")

                # Save the content of the <article> tag as an HTML file
                file_name = f"{item['title'].replace('/', '-')}.html"
                file_path = pathlib.Path(output_dir) / file_name

                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(str(article))

                logging.info(f"Page saved: {file_path}")

            else:
                logging.warning(
                    f"Failed to fetch {item['link']}: {response.status_code} {httpx.codes.get_reason_phrase(response.status_code)}"
                )

        except Exception as e:
            logging.error(f"Failed to fetch {item['link']}: {e}")

    logging.info("Completed fetch_and_save_articles function")


def main():
    feed_url = "https://medium.com/feed/@your_username"
    rss_data = parse_rss(feed_url)
    output_dir = "saved_pages"
    fetch_and_save_articles(rss_data, output_dir)
    return f"Processed the RSS feed and saved linked pages to {output_dir}"


if __name__ == "__main__":
    main()
