from django.core.management.base import BaseCommand
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from scraper.scraper import settings as my_settings
from scraper.scraper.spiders.hh import HhruSpider
from scraper.scraper.spiders.superjob import SuperjobSpider


class Command(BaseCommand):
    help = 'Release spider'

    def handle(self, *args, **options):
        crawler_settings = Settings()
        crawler_settings.setmodule(my_settings)

        process = CrawlerProcess(settings=crawler_settings)

        process.crawl(HhruSpider)
        # process.crawl(SuperjobSpider)

        process.start()
