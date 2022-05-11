import requests
from flask import Flask, request
import logging

import json

app = Flask(__name__)
items = iter(['слона', 'кролика'])
item = next(items)
logging.basicConfig(level=logging.INFO)

sessionStorage = {}


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    handle_dialog(request.json, response)

    logging.info('Response: %r', request.json)

    return json.dumps(response)


def handle_dialog(req, res):
    global item, items
    user_id = req['session']['user_id']

    if req['session']['new']:

        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {item}!'
        res['response']['buttons'] = get_suggests(user_id)
        return

    for i in ['ладно', 'куплю', 'покупаю', 'хорошо']:
        if i in req['request']['nlu']['tokens']:
            # Пользователь согласился, прощаемся.
            res['response']['text'] = f'{item.capitalize()} можно найти на Яндекс.Маркете!'
            try:
                item = next(items)
                res['response']['text'] = f'А теперь купи {item}.'
                sessionStorage[user_id] = {
                    'suggests': [
                        "Не хочу.",
                        "Не буду.",
                        "Отстань!",
                    ]
                }
                res['response']['buttons'] = get_suggests(user_id)
                return
            except:
                res['response']['end_session'] = True
                return

    res['response']['text'] = 'Все говорят "%s", а ты купи %s!' % (
        req['request']['original_utterance'], item
    )
    res['response']['buttons'] = get_suggests(user_id)


# Функция возвращает две подсказки для ответа.
def get_suggests(user_id):
    session = sessionStorage[user_id]

    # Выбираем две первые подсказки из массива.
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    # Убираем первую подсказку, чтобы подсказки менялись каждый раз.
    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    # Если осталась только одна подсказка, предлагаем подсказку
    # со ссылкой на Яндекс.Маркет.
    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": f"https://market.yandex.ru/search?text={item}",
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()