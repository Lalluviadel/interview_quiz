# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class ScraperPipeline:
    def process_item(self, item, spider):
        # для hh.ru
        if spider.name == 'hhru':
            item['min'], item['max'], item['cur'] = self.hh_process_salary(item['salary'])
        # для superjob.ru
        else:
            item['min'], item['max'], item['cur'] = self.sj_process_salary(item['salary'])

        # del (item['salary'])
        print(item)
        item.save()
        return item

# для hh.ru
    @staticmethod
    def hh_process_salary(salary):
        # работаем с вакансиями, где информация о зарплате есть
        if len(salary) > 1:
            # где оба поля можно заполнить
            if salary[2] == ' до ':
                salary_min = int(salary[1].replace('\xa0', ''))
                salary_max = int(salary[3].replace('\xa0', ''))
                currency = salary[5]
            # указана только максимальная
            elif salary[0] == 'до ':
                salary_min, salary_max, currency = None, int(salary[1].replace('\xa0', '')), salary[3]
            # указана только минимальная
            else:
                salary_min, salary_max, currency = int(salary[1].replace('\xa0', '')), None, salary[3]
        # для вакансий, где информации о зарплате нет или указано 'Договорная' и т.д.
        else:
            salary_min, salary_max, currency = None, None, None
        return salary_min, salary_max, currency

    @staticmethod
    # для superjob.ru
    def sj_process_salary(salary):
        # работаем с вакансиями, где информация о зарплате есть
        if len(salary) > 1:
            # где оба поля указаны на superjob
            if len(salary) > 3:
                salary_min = int(salary[0].replace('\xa0', ''))
                salary_max = int(salary[4].replace('\xa0', ''))
                currency = salary[6]
            # указана только минимальная
            elif salary[0] == 'от':
                salary_and_curr = salary[2].split('\xa0')
                salary_min = int(salary_and_curr[0] + salary_and_curr[1])
                salary_max = None
                currency = salary_and_curr[2]
            # указана только максимальная
            elif salary[0] == 'до':
                salary_and_curr = salary[2].split('\xa0')
                salary_min = None
                salary_max = int(salary_and_curr[0] + salary_and_curr[1])
                currency = salary_and_curr[2]
            # указана фиксированная
            else:
                sal = int(salary[0].replace('\xa0', ''))
                salary_min, salary_max, currency = sal, sal, salary[2]
        # для вакансий, где информации о зарплате нет или указано 'Договорная' и т.д.
        else:
            salary_min, salary_max, currency = None, None, None
        return salary_min, salary_max, currency
