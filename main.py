from statistics import mean

import requests
from environs import Env
from terminaltables import AsciiTable


def predict_salary(salary_from, salary_to):
    only_to_ratio = 0.8
    only_from_ratio = 1.2
    if not salary_from and not salary_to:
        return None
    if not salary_from and salary_to:
        return int(salary_to * only_to_ratio)
    if salary_from and not salary_to:
        return int(salary_from * only_from_ratio)

    return int(mean((salary_from, salary_to)))


def predict_rub_salary_hh(vacancy):
    salary = vacancy['salary']
    if not salary:
        return None
    if salary['currency'] != 'RUR':
        return None

    return predict_salary(salary['from'], salary['to'])


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] != 'rub':
        return None

    return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


def get_average_salary(salaries: list) -> int:
    if not salaries:
        return 0
    return int(mean(salaries))


def get_languages():
    return (
        'JavaScript',
        'Java',
        'Python',
        'Ruby',
        'PHP',
        'C++',
        'C#',
        'C',
        'Go',
        'Objective-C',
        'Scala',
        'Swift',
        'TypeScript',
        'Kotlin',
        '1C',
    )


def get_hh_vacancies(page, language):

    url = 'https://api.hh.ru/vacancies'
    moscow_area = 1

    payload = {
        'text': f'"Программист {language}" OR "{language} Программист"',
        'search_field': 'name',
        'area': moscow_area,
        'page': page,
    }

    connect_timeout = 3.05
    read_timeout = 27
    timeouts = (connect_timeout, read_timeout)
    response = requests.get(url, params=payload, timeout=timeouts)
    response.raise_for_status()
    vacancies_catalog = response.json()

    return (
        vacancies_catalog['items'],
        vacancies_catalog['found'],
        vacancies_catalog['pages']
    )


def get_hh_stats(languages, popularity_limit):
    hh_stats = {}
    for language in languages:
        vacancies = []
        page = 0
        found = 0
        salaries = []

        while True:
            page_vacancies, found, pages_number = get_hh_vacancies(
                page, language)
            if found <= popularity_limit:
                break

            vacancies = [*vacancies, *page_vacancies]
            page += 1
            if page >= pages_number:
                break

        if found <= popularity_limit:
            continue

        for vacancy in vacancies:
            rub_salary = predict_rub_salary_hh(vacancy)
            if not rub_salary:
                continue
            salaries.append(rub_salary)

        hh_stats[language] = {
            'vacancies_found': found,
            'vacancies_processed': len(salaries),
            'average_salary': get_average_salary(salaries)
        }

    return hh_stats


def get_sj_vacancies(superjob_api_key, page, language):
    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {'X-Api-App-Id': superjob_api_key}
    development_specialization_code = 48
    profession_only_code = 1
    payload = {
        'page': page,
        'keywords[0][keys]': 'Программист',
        'keywords[0][srws]': profession_only_code,
        'keywords[0][skws]': 'and',
        'keywords[1][keys]': language,
        'keywords[1][srws]': profession_only_code,
        'keywords[1][skws]': 'particular',
        'catalogues': development_specialization_code,
        'town': 'Москва'
    }

    connect_timeout = 3.05
    read_timeout = 27
    timeouts = (connect_timeout, read_timeout)
    response = requests.get(
        url,
        params=payload,
        headers=headers,
        timeout=timeouts
    )
    response.raise_for_status()
    vacancies_catalog = response.json()

    return (
        vacancies_catalog['objects'],
        vacancies_catalog['total'],
        vacancies_catalog['more']
    )


def get_sj_stats(superjob_api_key, languages, popularity_limit):

    sj_stats = {}
    for language in languages:
        vacancies = []
        page = 0
        total = 0
        more = True
        salaries = []
        while more:
            page_vacancies, total, more = get_sj_vacancies(
                superjob_api_key,
                page,
                language
            )
            page += 1
            if total <= popularity_limit:
                break
            vacancies = [*vacancies, *page_vacancies]

        if total <= popularity_limit:
            continue

        for vacancy in vacancies:
            rub_salary = predict_rub_salary_sj(vacancy)
            if not rub_salary:
                continue
            salaries.append(rub_salary)

        sj_stats[language] = {
            'vacancies_found': total,
            'vacancies_processed': len(salaries),
            'average_salary': get_average_salary(salaries)
        }

    return sj_stats


def get_stats_table(job_board_stats):
    table_data = []
    table_data.append(
        [
            'Язык программирования',
            'Найдено вакансий',
            'Обработано вакансий',
            'Средняя зарплата'
        ]
    )

    for language, stats_card in job_board_stats['stats'].items():
        table_data.append(
            [
                language,
                stats_card['vacancies_found'],
                stats_card['vacancies_processed'],
                stats_card['average_salary']
            ]
        )

    table = AsciiTable(table_data, job_board_stats['title'])
    return table.table


def main():
    env = Env()
    env.read_env()
    superjob_api_key = env('SUPERJOB_API_KEY')
    popularity_limit = env.int('POPULARITY_LIMIT', 10)
    languages = get_languages()

    job_boards_stats = []

    stats = get_hh_stats(languages, popularity_limit)
    job_boards_stats.append({'title': 'HeadHunter Moscow', 'stats': stats})
    stats = get_sj_stats(superjob_api_key, languages, popularity_limit)
    job_boards_stats.append({'title': 'SuperJob Moscow', 'stats': stats})

    for job_board_stats in job_boards_stats:
        print(get_stats_table(job_board_stats), end='\n'*2)


if __name__ == '__main__':
    main()
