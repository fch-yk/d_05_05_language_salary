# Language salary

The script renders stats for vacancies of programmers in Moscow from ["HeadHunter"](https://hh.ru/) and ["Super Job"](https://www.superjob.ru/).

## Prerequisites

Python 3.10 is required.

## Installing

- Download the project files;
- It is recommended to use [venv](https://docs.python.org/3/library/venv.html?highlight=venv#module-venv) for project isolation;
- Set up packages:

```bash
pip install -r requirements.txt
```

- Set up environmental variables in your operating system or in .env file. The variables are:

  - `SUPERJOB_API_KEY` (obligatory) - a secret key to use ["Super Job" API](https://api.superjob.ru/);
  - `POPULARITY_LIMIT` (optional, `10` by default) - the script renders stats for a programming language, only if the number of vacancies is greater than this limit.

To set up variables in .env file, create it in the root directory of the project and fill it up like this:

```bash
SUPERJOB_API_KEY=mysuperjobapikey
POPULARITY_LIMIT=5
```

## Using

- Run:

```bash
python main.py
```

## Project goals

The project was created for educational purposes.
It's a lesson for python and web developers at [Devman](https://dvmn.org).
