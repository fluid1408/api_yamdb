import re
import datetime as dt

from django.core.exceptions import ValidationError

def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    if re.search(r'^\w.[@+-]+$', value) is None:
        r = set('^[\w.@+-]+$')
        char_value = set(value)
        uncorrect_chars = list(char_value & r)
        raise ValidationError(
            (f'Не допустимые символы  {uncorrect_chars}  в нике.'),
            params={'value': uncorrect_chars},
        )
    return value

def validate_year(year):
    now_year = dt.date.today()
    if year > now_year.year:
        raise ValueError(f'Некорректный год {year}')


