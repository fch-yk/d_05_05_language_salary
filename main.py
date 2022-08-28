from pprint import pprint
from statistics import mean

import requests
from environs import Env


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
        response = requests.get(url, params=payload, timeout=(3.05, 27))
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


def predict_rub_salary(vacancy):
    if vacancy is None:
        return None
    if vacancy['currency'] != 'RUR':
        return None
    if vacancy['from'] is None and vacancy['to'] is None:
        return None
    if vacancy['from'] is None and vacancy['to'] is not None:
        return vacancy['to'] * 0.8
    if vacancy['from'] is not None and vacancy['to'] is None:
        return vacancy['from'] * 1.2

    return int(mean((vacancy['from'], vacancy['to'])))


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
            rub_salary = predict_rub_salary(vacancy['salary'])
            if rub_salary is None:
                continue
            salaries.append(rub_salary)

        popular_languages[language] = {
            'vacancies_found': found,
            'vacancies_processed': len(salaries),
            'average_salary': get_average_salary(salaries)
        }

    return (popular_languages)


def get_superjob_statistics(superjob_api_key):

    url = 'https://api.superjob.ru/2.0/vacancies/'
    page = 0
    headers = {'X-Api-App-Id': superjob_api_key}

    # payload = {
    #     'text': f'"Программист {language}" OR "{language} Программист"',
    #     'search_field': 'name',
    #     'area': 1,
    #     'page': page,
    # }
    response = requests.get(
        url,
        # params=payload,
        headers=headers,
        timeout=(3.05, 27)
    )
    response.raise_for_status()
    serialized_response = response.json()
    for vacancy in serialized_response['objects']:
        pprint(vacancy['profession'])


def main():
    env = Env()
    env.read_env()
    superjob_api_key = env('SUPERJOB_API_KEY')
    pprint(get_superjob_statistics(superjob_api_key))
    # pprint(get_hh_statictics())


if __name__ == '__main__':
    main()
