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
        set(re.findall(settings.UNCORRECT_USERNAME_CHARS, value))
    )
    if uncorrect_chars:
        raise ValidationError(
            f'Не допустимые символы {uncorrect_chars} в нике.',
            params={'chars': uncorrect_chars},
        )
    return value


def validate_year(year):
    today = dt.date.today()
    if year > today.year:
        raise ValidationError(
            f'Указанный год {year} не может быть больше текущего '
            f'{today.year}')
    return year
