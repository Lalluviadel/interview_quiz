import scrapy
from scrapy_djangoitem import DjangoItem
from vacancies.models import Vacancies


class ScraperItem(scrapy.Item):
    django_model = Vacancies
