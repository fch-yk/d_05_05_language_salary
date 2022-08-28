import requests
from pprint import pprint


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


def get_hh_vacancies():
    popular_languages = {}
    for language in get_languages():
        url = 'https://api.hh.ru/vacancies'
        payload = {
            'text': f'"Программист {language}" OR "{language} Программист"',
            'search_field': 'name',
            'area': 1
        }
        response = requests.get(url, params=payload, timeout=(3.05, 27))
        response.raise_for_status()
        serialized_response = response.json()
        if serialized_response['found'] <= 100:
            continue
        popular_languages[language] = serialized_response['found']

    return (popular_languages)


def main():
    # hh_vacancies_serialized = get_hh_vacancies()
    # hh_vacancies = json.dumps(
    #     hh_vacancies_serialized,
    #     ensure_ascii=False,
    #     indent="\t"
    # )
    # with open("tmp/hh.json", "w", encoding="UTF-8") as my_file:
    #     my_file.write(hh_vacancies)

    pprint(get_hh_vacancies())


if __name__ == '__main__':
    main()
