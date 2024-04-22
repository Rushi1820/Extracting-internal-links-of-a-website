from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import requests
import db 
from urllib.parse import unquote
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import APIRouter

router = APIRouter(tags=["LinkExtractor"], prefix="/Link")


def get_all_links(url, follow_external=False, ignore_tags=['script', 'style']):
  internal_links = set()
    
  try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            base_url = urlparse(url).scheme + "://" + urlparse(url).netloc
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                absolute_url = urljoin(base_url, href)
                if absolute_url.startswith(base_url):
                    internal_links.add(absolute_url)
        else:
            print("Failed to fetch webpage. Status code:", response.status_code)
  except Exception as e:
        print("An error occurred:", e)
    
  return internal_links



@router.get("/crawl")
def crawl_and_store_links():

  print("Link extraction started")
  url = "https://www.leewayhertz.com/"  

  internal_links = get_all_links(url)
  new_links = []
  updated_links = []

  if internal_links:
    try:
      conn = db.setup_database()
      print("Database connection successful")

      if conn:
        cursor = db.get_database_cursor(conn)

        if cursor:
          for internal_link in internal_links:
              cursor.execute("SELECT * FROM links WHERE url = %s", (internal_link,))
              existing_link = cursor.fetchone() 
              print("Internal Link:", internal_link)
              print("Existing Link:", existing_link)  
              if existing_link is None:  
                 cursor.execute("INSERT INTO links (url, crawl_time) VALUES (%s, NOW())", (internal_link,))
                 new_links.append(internal_link)
              else:  
                 cursor.execute("UPDATE links SET crawl_time = NOW() WHERE url = %s", (internal_link,))
                 updated_links.append(internal_link)

          conn.commit()
          print("---------------------------------.")
          print("New links are shown below:")
          for i in new_links:
            print("new link:",new_links)
        else:
          print("Failed to get database cursor.")
      else:
        print("Failed to establish database connection.")
    except Exception as e:
      print("An error occurred while storing links in the database:", e)
  else:
    print("No internal links found on the website.")
  return new_links



def schedule_crawl():
  crawl_and_store_links()

scheduler = BackgroundScheduler()
scheduler.add_job(schedule_crawl, 'interval', minutes=45) 
#scheduler.add_job(schedule_crawl, 'cron', hour=1, minute=0) to run at a particular time in a day to check for any updations or 
scheduler.start()
