# import needed libraries
import os
import sys
import pytz
import django
# Django Setup
sys.path.append('D:/Code/gigtape/') # These have to be here because they must be done before importing django setup and event.models
os.environ['DJANGO_SETTINGS_MODULE'] = 'gigtape.settings'
django.setup()
#from django.conf import settings
from django.templatetags.static import static
#from django.db import connection
from django.utils import timezone
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, ElementNotInteractableException, TimeoutException
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from events.models import Venue, Event
from django.db import IntegrityError
import time
import requests
import re



# Scrapers    
def scrape_vastavirta(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the main that contains the events
    main = soup.find('main', id='content')

    # Find all divs that contain an event
    divs = main.find_all('div', class_='vv-custom-events')

    for div in divs:
        event = {}

        h3 = div.find('h3', class_='vv-events-heading')
        if h3:
            parts = h3.text.split(' - ', 1)
            if len(parts) == 2:
                event['event_date'] = timezone.make_aware(datetime.strptime(parts[0][:10].strip(), '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))  # Convert to datetime
                event['event_name'] = parts[1].strip()

        p_tags = div.find_all('p')
        if p_tags and len(p_tags) > 1:
            event['event_venue'] = p_tags[0].text.strip()

        a_tag = div.find('a', href=True)
        if a_tag:
            event['event_link'] = a_tag['href']

        # Create and save Venue instance
        venue, created = Venue.objects.update_or_create(
            name=event['event_venue'],
            defaults={
            'website': url, # Use the url as the venue's website
            'venue_img': static('images/default_vastavirta.png')  # Use a default image
            }  
        )

        # Create and save Event instance
        try:
            Event.objects.update_or_create(
                venue=venue,
                event_name=event['event_name'],
                event_date=event['event_date'],
                website=url
            )
        except IntegrityError as IEr:
            print(f"Integrity Error: {IEr}")
            
def scrape_yotalo(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = soup.find_all('div', class_='mb-5')

    for event in events:
        date_str = event.find('div', class_='me-3').text[2:]  # Remove the first two characters
        year = datetime.now().year  # Get the current year

        # Parse the date string and add the current year
        date = timezone.make_aware(datetime.strptime(date_str, '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))

        # If the date is in the past, add one to the year and parse again
        if date < timezone.make_aware(datetime.now(), pytz.timezone('Europe/Helsinki')):
            date = timezone.make_aware(datetime.strptime(date_str + '.' + str)(year + 1), '%d.%m.%Y', pytz.timezone('Europe/Helsinki'))

        image = event.find('img')['src']
        event_name = event.find('div', class_='mt-md-3').text
#        event_info = event.find('div', class_='fs-6').text
        tickets_link = event.find('a', class_="button")
#        facebook_link = event.find('a', class_="facebook-link")

        # Create and save Venue instance
        venue, created = Venue.objects.update_or_create(
            name='YO-Talo',
            defaults={
            'website': url, # Use the url as the venue's website
            'venue_img': static('images/default_yotalo.png')  # Use a default image
            }
        )
        
        # Create and save Event instance
        try:
            Event.objects.update_or_create(
                venue=venue,
                event_name=event_name,
                event_date=date,
                website=tickets_link.get('href') if tickets_link else '',
                event_img=image
            )
        except IntegrityError as IEr:
            print(f"Integrity Error: {IEr}")

def scrape_tullikamari(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = soup.find_all('article', class_='event-feed-item')

    for event in events:
        date_str_1 = event.find('div', class_='event-feed-item__date').text
        date_str = ''.join(x for x in date_str_1 if x.isdigit()) 
        date = timezone.make_aware(datetime.strptime(date_str, '%d%m%Y'), pytz.timezone('Europe/Helsinki'))  # Now the date f)ormat includes the year

        image = event.find('img')['src']
        event_name = event.find('h2', class_='event-artist').text
        venue_name = event.find('li', class_='event-venue').text
        event_link = event.find('a', class_="event-link")
        
        # Create and save Venue instance
        venue, created = Venue.objects.update_or_create(
            name=venue_name,
            defaults={
            'website': url, # Use the url as the venue's website
            'venue_img': static('images/default_tullikamari.png')  # Use a default image
            }
        )

        # Create and save Event instance
        try:
            Event.objects.update_or_create(
                venue=venue,
                event_name=event_name,
                event_date=date,
                website=event_link.get('href') if event_link else '',
                event_img=image
            )
        except IntegrityError as IEr:
            print(f"Integrity Error: {IEr}")
    
def split_telakka(s):
    words = ["Ma", "Ti", "Ke", "To", "Pe", "La", "Su"]
    pattern = r'(' + '|'.join(map(re.escape, words)) + r')\s*(\d{1,2}\.\d{1,2}\.)\s*(.*?)\s*(?=(' + '|'.join(map(re.escape, words)) + r')|\Z)'
    split_list = re.findall(pattern, s)
    data_dict = {}
    for match in split_list:
        key = match[1].strip()  # Only keep the date part of the key
        value = match[2].strip()
        data_dict[key] = value
    return data_dict

def scrape_telakka(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    all_events = soup.find('div', class_='entry-content')
    events = all_events.find_all(lambda tag: tag.name == 'div' and tag.find('p'))

    for event in events:
        no_tags = event.get_text()
        split_event = split_telakka(no_tags)

        for key, value in split_event.items():
            date_str = key + str(datetime.now().year)  # Add the current year
            date = timezone.make_aware(datetime.strptime(date_str, '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))  # Now the date f)ormat includes the year
            if date < timezone.make_aware(datetime.now(), pytz.timezone('Europe/Helsinki')):
                date = timezone.make_aware(datetime.strptime(date_str + '.' + str(datetime.now()).year + 1), '%d.%m.%Y', pytz.timezone('Europe/Helsinki'))

            # Create and save Venue instance
            venue, created = Venue.objects.update_or_create(
                name='Telakka',
                defaults={
                'website': url, # Use the url as the venue's website
                'venue_img': static('images/default_telakka.jpg')  # Use a default image
                }
            )

            # Create and save Event instance
            try:
                Event.objects.update_or_create(
                    venue=venue,
                    event_name=value,
                    event_date=date,
                    website=url,  # Use the url as the event's website
                )
            except IntegrityError as IEr:
                print(f"Integrity Error: {IEr}")
                
def scrape_tavaraasema(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = soup.find_all('article', class_='event-feed-item')

    for event in events:
        date_str_1 = event.find('div', class_='event-feed-item__date').text
        date_str_2 = ''.join(x for x in date_str_1 if x.isdigit())
        date_str = date_str_2 + str(datetime.now().year)
        date = timezone.make_aware(datetime.strptime(date_str, '%d%m%Y'), pytz.timezone('Europe/Helsinki'))  # Now the date f)ormat includes the year

        image = event.find('img')['src']
        event_name = event.find('h2', class_='event-artist').text
#        event_info = event.find('ul', class_='event-feed-item__info').text
        event_link = event.find('a', class_="event-link")

        # Create and save Venue instance
        venue, created = Venue.objects.update_or_create(
            name='Tavara-Asema',
            defaults={
            'website': url, # Use the url as the venue's website
            'venue_img': static('images/default_tavaraasema.png')  # Use a default image
            }
        )

        # Create and save Event instance
        try:
            Event.objects.update_or_create(
                venue=venue,
                event_name=event_name,
                event_date=date,
                website=event_link.get('href') if event_link else '',
                event_img=image
            )
        except IntegrityError as IEr:
            print(f"Integrity Error: {IEr}")
            
def scrape_tamperetalo(url):
    
    # some helpful variables 
    retries = 0
    max_retries = 5
    success = False
    
    # Setup Edge options
    edge_options = Options()
    edge_options.use_chromium = True
#    edge_options.add_argument("--headless")  # Ensure GUI is off
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--enable-chrome-browser-cloud-management")

    # Set path to edgedriver as per your configuration
    while not success and retries < max_retries:
        try:
            #webdriver_service = Service(EdgeChromiumDriverManager().install())
            # Choose Edge Browser
            driver = webdriver.Edge(service=Service(r"C:\Users\mikko\Downloads\edgedriver_win64\msedgedriver.exe"), options=edge_options)
            driver.get(url)
            #driver.minimize_window ()
            success = True
        except requests.exceptions.ConnectionError:
            print(f"Connection error: {requests.exceptions.ConnectionError}")
            retries += 1
            print(f"Retry {retries} of {max_retries}")
            time.sleep(5)

    # Reject the cookies from pop up -window
    while True:
        try:
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, './/button[@id="onetrust-reject-btn-handler"]'))).click()
        except NoSuchElementException as NEx:
            print(f"No Such Element: {NEx}")
            break  # exit the loop if the button is not found or cannot be clicked
        except ElementClickInterceptedException as ECEx:
            print(f"Element Click Intercepted: {ECEx}")
            break
        except ElementNotInteractableException as EEx:
            print(f"Element Not Interactable: {EEx}")
            break
        except TimeoutError as TEr:
            print(f"Timeout error: {TEr}")
            break
        except TimeoutException as TEx:
            print(f"Time out exception: {TEx}")
            break
        
        
    # Click the 'Load More' Button
    while True:
        try:
            load_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'em-block-event-feed__more')]//button[contains(@class, 'button')]")))            
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(0.5)
            load_more_button.click()
        except NoSuchElementException as NEx:
            print(f"No Such Element: {NEx}")
            break  # exit the loop if the button is not found or cannot be clicked
        except ElementClickInterceptedException as ECEx:
            print(f"Element Click Intercepted: {ECEx}")
            break
        except ElementNotInteractableException as EEx:
            print(f"Element Not Interactable: {EEx}")
            break
        except TimeoutError as TEr:
            print(f"Timeout error: {TEr}")
            break
        except TimeoutException as TEx:
            print(f"Time out exception: {TEx}")
            break

    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find the div that contains the events
    div = soup.find('div', class_='em-block-event-feed__posts')

    # Find all articles that contain an event
    articles = div.find_all('article', class_='em-block-event-card') if div else []

    # Define the list of genres to filter
    genres = ["Festivaali", "Heavy metal", "Iskelmä", "Jazz & Blues", "Joulu", "Klassinen musiikki", "Kuoromusiikki", "Maailmanmusiikki", "Ooppera, operetti", "Orkesterimusiikki", "Rap ja hiphop", "Rock & Pop", "Show", "Stand Up", "Viihdekonsertti"]

    events = []

    for article in articles:
        event = {}

        date_div = article.find('div', class_='em-block-event-card__date')
        if date_div:
            time_tag = date_div.find('time')
            if time_tag:
                event['event_date'] = timezone.make_aware(datetime.strptime(time_tag['datetime'], '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))

        image_div = article.find('div', class_='em-block-event-card__image')
        if image_div:
            a_tag = image_div.find('a', href=True)
            if a_tag:
                event['event_link'] = a_tag['href']

            img_tag = image_div.find('img')
            if img_tag:
                event['image_url'] = img_tag['src']

        content_div = article.find('div', class_='em-block-event-card__content')
        if content_div:
            title_link = content_div.find('a', class_='em-block-event-card__title')
            if title_link:
                event['event_name'] = title_link.text.strip()

        details_div = article.find('div', class_='em-block-event-card__details')
        if details_div:
            location_div = details_div.find('div', class_='em-block-event-card__details__location')
            if location_div:
                event['event_venue'] = ''.join([span.text.strip() for span in location_div.find_all('span')])

            genres_div = details_div.find('div', class_='em-block-event-card__details__genres')
            if genres_div:
                event_genres = [span.text.strip() for span in genres_div.find_all('span', class_='em-block-event-card__details__genre')]
                # Check if the event's genres are in the list of genres to filter
                if any(genre in genres for genre in event_genres):
                    # Create and save Venue instance
                    venue, created = Venue.objects.update_or_create(
                        name=event['event_venue'],
                        defaults={'website': url, 'venue_img': static('images/default_tamperetalo.jpg')}  # Use the url as the venue's website
                    )

                    # Create and save Event instance
                    try:
                        Event.objects.update_or_create(
                            venue=venue,
                            event_name=event['event_name'],
                            event_date=event['event_date'],
                            website=url,  # Use the url as the event's website
                            event_img=event['image_url']
                        )
                    except IntegrityError as IEr:
                        print(f"Integrity Error: {IEr}")
        
def scrape_paappa(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all divs that contain the events
    divs = soup.find_all('div', class_='et_pb_text_inner')

    # If there are at least two such divs, select the second one
    if len(divs) >= 2:
        div = divs[1]
    else:
        print("Could not find the second div with class 'et_pb_text_inner'")
        return

    # Get all the pieces of text separated by <br> tags
    lines = [text for text in div.stripped_strings]

    for line in lines:
        # Split the line into date and event name at the second period
        parts = line.split('.', 2)
    
        if len(parts) == 3:
            date_str = parts[0][3:].strip() + '.' + parts[1].strip() + '.' + str(datetime.now().year)  # Add the current year
            date = timezone.make_aware(datetime.strptime(date_str, '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))  # Now the date f)ormat includes the year

            event_name = parts[2].strip()

            # Create and save Venue instance
            venue, created = Venue.objects.update_or_create(
                name='Paappa',  # Use a fixed venue name
                defaults={'website': url, 'venue_img': static('images/default_paappa.png')}  # Use the url as the venue's website
            )

            # Create and save Event instance
            Event.objects.update_or_create(
                venue=venue,
                event_name=event_name,
                event_date=date,
                website=url,  # Use the url as the event's website
                event_img=static('images/default_paappa.png')  # Use a default image
            )

def scrape_olympia(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = soup.find_all('div', class_='keikka')

    for event in events:
        dates = event.find_all(lambda date_tag: date_tag.name == 'p' and date_tag.find('span', class_='viikonpaiva'))
        image = event.find('img')['src']
        event_name_str = event.find('div', class_='infot').text[2:].split('\n')
        event_name = event_name_str[0]
        tickets_link = event.find('a', class_="button")

        for date in dates:
            date_str = date.text[2:]
            date = timezone.make_aware(datetime.strptime(date_str, '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))  # Now the date f)ormat includes the year
            if date < timezone.make_aware(datetime.now(), pytz.timezone('Europe/Helsinki')):
                date = timezone.make_aware(datetime.strptime(date_str[-1] + 1, '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))

            # Create and save Venue instance
            venue, created = Venue.objects.update_or_create(
                name='Olympia',  # Use a fixed venue name
                defaults={'website': url, 'venue_img': static('default_olympia.jpg')}  # Use the url as the venue's website
            )

            # Create and save Event instance
            try:
                Event.objects.update_or_create(
                    venue=venue,
                    event_name=event_name,
                    event_date=date,
                    website=tickets_link.get('href') if tickets_link else '',
                    event_img=image
                )
            except IntegrityError as IEr:
                print(f"Integrity Error: {IEr}")
            
def scrape_nokiaarena(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the section that contains the events
    section = soup.find('section', id='events-block_618b956a06806')

    # Find all divs that contain an event
    divs = section.find_all('div', class_='events__event')

    for div in divs:
        event = {}

        meta_div = div.find('div', class_='events__meta')
        if meta_div:
            date_str = meta_div.find('span', class_='events__date').text.strip() + meta_div.find('span', class_='events__year').text.strip()
            date = timezone.make_aware(datetime.strptime(date_str[:6] + str(datetime.now().year), '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))  # Convert to datetime

        image_tag = div.find('img', class_='events__image')
        if image_tag:
            event['image_url'] = image_tag['src']

        title_link = div.find('a', class_='events__titlelink')
        if title_link:
            event['event_name'] = title_link.text.strip()

        # Create and save Venue instance
        venue, created = Venue.objects.update_or_create(
            name='Nokia Arena',  # Use a fixed venue name
            defaults={'website': url, 'venue_img': static('image/default_nokiaarena.jpg')}  # Use the url as the venue's website
        )

        # Create and save Event instance
        try:
            Event.objects.update_or_create(
                venue=venue,
                event_name=event['event_name'],
                event_date=date,
                website=url,  # Use the url as the event's website
                event_img=event['image_url']
            )
        except IntegrityError as IEr:
            print(f"Integrity Error: {IEr}")
            
def scrape_glivelab(url):
    # some helpful variables 
    retries = 0
    max_retries = 5
    success = False
    
    # Setup Edge options
    edge_options = Options()
    edge_options.use_chromium = True
    edge_options.add_argument("--headless")  # Ensure GUI is off
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--no-sandbox")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--enable-chrome-browser-cloud-management")

    
    while not success and retries < max_retries:
        try:
        
            #webdriver_service = Service(EdgeChromiumDriverManager().install())
            # Choose Edge Browser
            driver = webdriver.Edge(service=Service(r"C:\Users\mikko\Downloads\edgedriver_win64\msedgedriver.exe"), options=edge_options)
            driver.get(url)
            #driver.minimize_window ()
            success = True
        except requests.exceptions.ConnectionError:
            print(f"Connection error: {requests.exceptions.ConnectionError}")
            retries += 1
            print(f"Retry {retries} of {max_retries}")
            time.sleep(5)
#    response = requests.get(url) <- was old way, didn't work.
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    WebDriverWait(driver, 10)

    events = soup.find_all('li', class_='item')

    for event in events[1:]:
        a_tag = event.find('a')
        event_link = a_tag['href']

        img_div = event.find('div', class_='img')
        image = img_div['style'].replace("background-image: url('", "").replace("')", "") if img_div else "N/A"

        event_name_div = event.find('h2', class_='title')
        event_name = event_name_div.text.strip() if event_name_div else "N/A"

        date_div = event.find('div', class_='date')
        date_str = date_div.text.strip() if date_div else "N/A"

        dow_div = event.find('div', class_='dow')
        day = dow_div.text.strip() if dow_div else "N/A"

        time_div = event.find('div', class_='time')
        time = time_div.text.strip() if time_div else "N/A"

        # Combine date and time into a single string and convert to datetime
        datetime_str = f"{date_str}"
        if datetime_str != "N/A":
            event_date = timezone.make_aware(datetime.strptime(datetime_str.split()[0] + str(datetime.now().year), '%d.%m.%Y'), pytz.timezone('Europe/Helsinki'))  # Replace with yo)ur date and time format
        else:
            event_date = timezone.make_aware(datetime.strptime("31.12.2099", '%d.%m.%Y'), pytz.timezone('Europe/Helsinki')) # Set a date that can )be recognised for error
            
        # Create and save Venue instance
        venue, created = Venue.objects.update_or_create(
            name='G Livelab',  # Use a fixed venue name
            defaults={'website': url, 'venue_img': static('/images/default_glivelab.png')}  # Use the url as the venue's website
        )

        # Create and save Event instance
        try:
            Event.objects.update_or_create(
                venue=venue,
                event_name=event_name,
                event_date=event_date,
                website=event_link,  # Use the event link as the event's website
                event_img=image
            )
        except IntegrityError as IEr:
            print(f"Integrity Error: {IEr}")
    
    print("T'SALL GOOD MAN!")