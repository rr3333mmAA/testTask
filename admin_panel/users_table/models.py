from django.db import models

class Category(models.Model):
    subcategory = models.CharField(max_length=100, primary_key=True)
    category = models.CharField(max_length=100)

    class Meta:
        db_table = 'category'

class Catalog(models.Model):
    product = models.CharField(max_length=100)
    quantity = models.IntegerField()
    description = models.CharField(max_length=255)
    img_path = models.CharField(max_length=255)
    subcategory = models.CharField(max_length=100)
    price = models.IntegerField()

    class Meta:
        db_table = 'catalog'

class Users(models.Model):
    user_tgid = models.IntegerField()
    address = models.CharField(max_length=255)

    class Meta:
        db_table = 'users'

class Cart(models.Model):
    user_tgid = models.IntegerField()
    product = models.CharField(max_length=100)
    quantity = models.IntegerField()
    amount = models.IntegerField()

    class Meta:
        db_table = 'cart'
