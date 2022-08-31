from pprint import pprint
from statistics import mean

import requests
from environs import Env
from urllib.parse import unquote


def get_hh_vacancies(language):
    vacancies = []
    found = 0
    url = 'https://api.hh.ru/vacancies'
    page = 0
    while True:
        payload = {
            'text': f'"Программист {language}" OR "{language} Программист"',
            'search_field': 'name',
            'area': 1,
            'page': page,
        }
        connect_timeout = 3.05
        read_timout = 27
        timeouts = (connect_timeout, read_timout)
        response = requests.get(url, params=payload, timeout=timeouts)
        response.raise_for_status()
        serialized_response = response.json()
        found = serialized_response['found']
        if found <= 100:
            return vacancies, 0

        vacancies = [*vacancies, *serialized_response['items']]

        page += 1
        if page >= serialized_response['pages']:
            break

    return (vacancies, found)


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

    salary_from = 0 if vacancy['from'] is None else vacancy['from']
    salary_to = 0 if vacancy['to'] is None else vacancy['to']

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


def get_hh_statictics():
    popular_languages = {}
    for language in get_languages():
        vacancies, found = get_hh_vacancies(language)
        if not found:
            continue

        salaries = []
        for vacancy in vacancies:
            rub_salary = predict_rub_salary_hh(vacancy['salary'])
            if rub_salary is None:
                continue
            salaries.append(rub_salary)

        popular_languages[language] = {
            'vacancies_found': found,
            'vacancies_processed': len(salaries),
            'average_salary': get_average_salary(salaries)
        }

    return (popular_languages)


def get_sj_statistics(superjob_api_key):

    url = 'https://api.superjob.ru/2.0/vacancies/'

    headers = {'X-Api-App-Id': superjob_api_key}
    development_specialization_code = 48
    profession_only_code = 1
    payload = {
        'keywords[0][srws]': profession_only_code,
        'keywords[0][keys]': 'Программист',
        'catalogues': development_specialization_code,
        'town': 'Москва'
    }
    connect_timeout = 3.05
    read_timeout = 27
    response = requests.get(
        url,
        params=payload,
        headers=headers,
        timeout=(connect_timeout, read_timeout)
    )
    response.raise_for_status()
    serialized_response = response.json()
    for vacancy in serialized_response['objects']:
        print(
            vacancy['profession'],
            vacancy['town']['title'],
            predict_rub_salary_sj(vacancy),
            sep=', ')

    print('total:', serialized_response['total'])

    return unquote(response.url)


def main():
    env = Env()
    env.read_env()
    superjob_api_key = env('SUPERJOB_API_KEY')
    pprint(get_sj_statistics(superjob_api_key))
    # pprint(get_hh_statictics())


if __name__ == '__main__':
    main()
