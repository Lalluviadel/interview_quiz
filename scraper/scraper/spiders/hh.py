import scrapy
from scrapy.http import HtmlResponse

from scraper.scraper.items import ScraperItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = [
        'https://sevastopol.hh.ru/search/vacancy?clusters=true&area='
        '130&ored_clusters=true&enable_snippets=true&salary=&text=Python',
        # 'https://sevastopol.hh.ru/search/vacancy?clusters=true&area='
        # '130&ored_clusters=true&enable_snippets=true&salary=&text=Python',
    ]

    def parse(self, response: HtmlResponse, **kwargs):
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    @staticmethod
    def vacancy_parse(response: HtmlResponse):
        name = response.xpath('//h1//text()').get()

        # у HH.ru минимум 2 варианта классов для элементов, в которых они помещают зарплату
        # если выражение к основному классу вернет пустой объект, пробуем искать по второму выражению
        salary = response.xpath("//div[@class='vacancy-salary']//text()")
        if salary:
            salary = salary.getall()
        else:
            salary = response.xpath("//div[@class='vacancy-salary vacancy-salary_vacancyconstructor']//text()").getall()

        link = response.url
        item = ScraperItem(name=name, salary=salary, link=link)
        yield item
