from django.contrib import admin
from .models import User, Title, Review, Comment

admin.site.register(User)
admin.site.register(Title)
admin.site.register(Review)
admin.site.register(Comment)
