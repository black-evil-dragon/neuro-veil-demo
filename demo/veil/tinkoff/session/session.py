import functools
import logging
import time
import requests


log = logging.getLogger("neuro")
log.setLevel(logging.DEBUG)

def retry(attempts=2):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(attempts):
                try:
                    time.sleep(.1)
                    return func(*args, **kwargs)
                except Exception as error:
                    log.error(f'Ошибка! Попытка {i+1}\t{error}')
                    time.sleep(2)
        return wrapper
    return decorator


def catch(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try: return func(*args, **kwargs)
        except Exception as error:
            log.exception(f'Ошибка!\t{error}')
    return wrapper

class Session:
    def __init__(self, url: str, token: str):
        self.url = url
        self.session = requests.Session()
        self.token = token

        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }

        self.session.headers = self.headers



    def get(self, url: str) -> requests.Response:
        return self.session.get(url)

    @retry()
    def post(self, url: str, data='') -> requests.Response:
        response = self.session.post(url, data=data, json=data)

        if response.status_code != 200:
            raise Exception('Статус ответа не равен 200')
        return response