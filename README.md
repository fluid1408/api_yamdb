## API_Yamdb

API 
## Установка
#### **Требуется Python 3.7**

Чтобы перед началом работы выполните эту команду:
```
# Linux/macOS
python -m pip install -r requirements.txt

# Windows
py -m pip install -r requirements.txt
```

Для отправки email: 
```
    1) Зайти в файл settings
    2) Исправить переменные
        EMAIL_HOST_USER = 'example@domen.ru'
        EMAIL_HOST_PASSWORD = 'Пароль приложения(можно получить на сайте сервиса электронной почты )'
ИЛИ
    Заменить 
        EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    На
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

Для запуска, вы должны выполнить следующую команду:
```
# Linux/macOS
python yatube_api/manage.py

# Windows
py yatube_api/manage.py
```
## Использование 
### Регистрация нового пользователя/ обновление confirmation_code
    Отправляем POST запрос на адрес  api/v1/token/  с полями 
```     
    1) email - указываем почту пользователя
    2) username - указываем имя пользователя
```

### Получаем jwt токен 
 Отправляем POST запрос на адрес  api/v1/token/  с полями 
```     
    1) username - указываем имя пользователя
    2) confirmation_code - указываем confirmation_code
```
Получаем
```
     1) Токен access сам токен(срок действия по умолчанию 30 день)
```
### Выполнение запросов
     1) При выполнение запросов в заголовке указываем Authorization:Bearer <токен>
     2) Все запросы описаны по адресу http://localhost:8000/redoc/

## Технологии
###### 1) Django
###### 2) djangorestframework
###### 3) djangorestframework-simplejwt


## Об авторах
Трудяги из Yandex.practicum

* [Example]: https://github.com/iPROJEKT 
* [Example]: https://github.com/fluid1408 
* [Example]: https://github.com/Vediusse