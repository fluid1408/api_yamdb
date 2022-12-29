import re
import datetime as dt

from django.core.exceptions import ValidationError
from django.conf import settings


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
        )
    uncorrect_chars = ''.join(
        set(re.findall(settings.REGULAR_EXPRESSION, value))
    )
    if uncorrect_chars != '':
        raise ValidationError(
            f'Не допустимые символы {uncorrect_chars} в нике.',
            params={'chars': uncorrect_chars},
        )
    return value


def validate_year(year):
    now_year = dt.date.today()
    if year > now_year.year:
        raise ValueError(f'Указанный год {year} не может быть больше текущего')
    return year
