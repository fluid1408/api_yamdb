import csv

from django.shortcuts import get_object_or_404

from reviews.models import Genre, Category, Title, Review, Comment, User

path = 'api_yamdb/static/data/'


"""Импорт Category"""
with open('category.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_db = Category(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
        )
        row_db.save()

"""Импорт Genre"""
with open('genre.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_db = Genre(
            id=row['id'],
            name=row['name'],
            slug=row['slug'],
        )
        row_db.save()

"""Импорт Title"""
with open('titles.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_db = Title(
            id=row['id'],
            name=row['name'],
            year=row['year'],
            category=get_object_or_404(Category, pk=row['category'])
        )
        row_db.save()

"""Импорт User"""
with open('users.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_db = User(
            id=row['id'],
            username=row['username'],
            email=row['email'],
            role=row['role'],
            bio=row['bio'],
            first_name=row['first_name'],
            last_name=row['last_name']
        )
        row_db.save()

# Review
with open('review.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_db = Review(
            id=row['id'],
            title=Title.objects.get(id=row['title_id']),
            text=row['text'], author=User.objects.get(id=row['author']),
            score=row['score'], pub_date=row['pub_date']
        )
        row_db.save()

# Comment
with open('comments.csv') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        row_db = Comment(
            id=row['id'],
            review=Review.objects.get_object_or_404(id=row['review_id']),
            text=row['text'],
            author=User.objects.get_object_or_404(id=row['author']),
            pub_date=row['pub_date']
        )
        row_db.save()
