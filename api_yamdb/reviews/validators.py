import re
import datetime as dt

from django.core.exceptions import ValidationError

def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^[\w.@+-]+$', value) is None:
        raise ValidationError(
            (f'Не допустимые символы <{value}> в нике.'),
            params={'value': re.search(r'^[\w.@+-]+$', value)},
        )
    return value

def validate_year(year):
    now_year = dt.date.today()
    if year > now_year.year:
        raise ValueError(f'Некорректный год {year}')


