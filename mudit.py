from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup as BS
from requests.exceptions import HTTPError


app = FastAPI()

class ScrapeRequest(BaseModel):
    url: str
    keyword: Optional[str] = None
    limit: Optional[int] = 10


def hackernews_scrapper(url: str, keyword: str = None, limit: int = 10) -> Dict:
    results = []
    try:
        response = requests.get(url)
        # Debugger
        # print("URL IS.:", response)

        if response.status_code == 200:
            soup = BS(response.content, "html.parser")
            if keyword:
                headline = soup.find(class_="Story_title")
                if headline:
                    results.append({
                        "title": headline.get_text(),
                        "link": headline.find("a").get("href")
                    })
            else:
                headlines = soup.find_all(class_="titleline")
                for headline in headlines[:limit]:
                    results.append({
                        "title": headline.get_text(),
                        "link": headline.find("a").get("href")
                    })

        return {
            "results": results,
            "msg": "Success",
            "status": 0
        }
    except HTTPError as e:
        return {
            "results": [],
            "msg": "Unable to Scrape",
            "status": 1
        }
    except Exception as e:
        return {
            "results": [],
            "msg": "Something went wrong.",
            "status": 1
        }
    return hackernews_scrapper(request.url, request.keyword, request.limit)

@app.get("/headlines/")
def get_scraped_headlines():
    url = "https://news.ycombinator.com/"
    result = hackernews_scrapper(url)
    # Debugger
    # print("url is.:", result)

    formatted_results = [{"title": item["title"], "link": item["link"]} for item in result["results"]]

    return {"headlines": formatted_results}
