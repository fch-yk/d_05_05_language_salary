from pprint import pprint
from statistics import mean

import requests
from environs import Env
from urllib.parse import unquote


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
    if salary is None:
        return None
    if salary['currency'] != 'RUR':
        return None

    salary_from = 0 if salary['from'] is None else salary['from']
    salary_to = 0 if salary['to'] is None else salary['to']

    return predict_salary(salary_from, salary_to)


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
    serialized_response = response.json()

    return (
        serialized_response['items'],
        serialized_response['found'],
        serialized_response['pages']
    )


def get_hh_statictics(languages, popularity_limit):
    hh_statistics = {}
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
            if rub_salary is None:
                continue
            salaries.append(rub_salary)

        hh_statistics[language] = {
            'vacancies_found': found,
            'vacancies_processed': len(salaries),
            'average_salary': get_average_salary(salaries)
        }

    return hh_statistics


def get_sj_vacancies(superjob_api_key, page, language):
    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {'X-Api-App-Id': superjob_api_key}
    development_specialization_code = 48
    profession_only_code = 1
    payload = {
        'page': page,
        'keywords[0][keys]': f'Программист {language}',
        'keywords[0][srws]': profession_only_code,
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
    serialized_response = response.json()

    return (
        serialized_response['objects'],
        serialized_response['total'],
        serialized_response['more']
    )


def get_sj_statistics(superjob_api_key, languages, popularity_limit):

    sj_statistics = {}
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
            if rub_salary is None:
                continue
            salaries.append(rub_salary)

        sj_statistics[language] = {
            'vacancies_found': total,
            'vacancies_processed': len(salaries),
            'average_salary': get_average_salary(salaries)
        }

    return sj_statistics


def main():
    env = Env()
    env.read_env()
    superjob_api_key = env('SUPERJOB_API_KEY')
    popularity_limit = env.int('POPULARITY_LIMIT', 100)
    languages = get_languages()

    hh_statistics = get_hh_statictics(languages, popularity_limit)
    pprint(hh_statistics)

    sj_statistics = get_sj_statistics(
        superjob_api_key,
        languages,
        popularity_limit
    )
    pprint(sj_statistics)


if __name__ == '__main__':
    main()
