from django.db import models

class Property(models.Model):
    property_name = models.CharField(max_length=200)
    property_cost = models.CharField(max_length=100)
    property_type = models.CharField(max_length=100)
    property_area = models.CharField(max_length=100)
    property_locality = models.CharField(max_length=200)
    property_city = models.CharField(max_length=100)
    property_link = models.URLField()

    def __str__(self):
        return self.property_name
# property_scraper/scraper.py
from selenium import webdriver
from bs4 import BeautifulSoup
from property_scraper.models import Property
from django.db.utils import IntegrityError

def scrape_99acres_data(city, locality):
    url = f"https://www.99acres.com/search/property/buy/{city}-{locality}?city={city}&preference=S&area_unit=1&res_com=R"
    driver = webdriver.Chrome()  # Configure ChromeDriver as per your setup
    driver.get(url)
    
    try:
        # Closing the cookie consent pop-up if it exists
        driver.find_element_by_class_name("cookie-notification-close").click()
    except:
        pass

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    
    properties = soup.find_all('div', class_='srpDetail')
    
    for property_data in properties:
        try:
            property_name = property_data.find('h2').text.strip()
            property_cost = property_data.find('div', class_='price').text.strip()
            property_type = property_data.find('h3').text.strip()
            property_area = property_data.find('div', class_='table-cell').text.strip()
            property_locality = locality
            property_city = city
            property_link = property_data.find('a', class_='srpTuple__propertyName')['href']
            
            # Save data to the database
            try:
                Property.objects.create(
                    property_name=property_name,
                    property_cost=property_cost,
                    property_type=property_type,
                    property_area=property_area,
                    property_locality=property_locality,
                    property_city=property_city,
                    property_link=property_link
                )
            except IntegrityError:
                # Handle duplicate entries
                pass

        except Exception as e:
            print(f"Error scraping property data: {str(e)}")

    driver.quit()
# property_scraper/management/commands/scrape_99acres.py
from django.core.management.base import BaseCommand
from property_scraper.scraper import scrape_99acres_data

class Command(BaseCommand):
    help = 'Scrape property data from 99acres and store it in MongoDB'

    def handle(self, *args, **options):
        cities_localities = [
            ('pune', 'maharashtra'),
            ('delhi', 'delhi'),
            ('mumbai', 'maharashtra'),
            ('lucknow', 'uttar-pradesh'),
            ('agra', 'uttar-pradesh'),
            ('ahmedabad', 'gujarat'),
            ('kolkata', 'west-bengal'),
            ('jaipur', 'rajasthan'),
            ('chennai', 'tamil-nadu'),
            ('bengaluru', 'karnataka'),
        ]

        for city, locality in cities_localities:
            scrape_99acres_data(city, locality)
