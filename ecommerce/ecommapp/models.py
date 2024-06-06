from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Product(models.Model):
    CAT=((1,'Mobile'),(2,'Cloths'),(3,'Shoes'))
    name = models.CharField(max_length=50,verbose_name='Product Name')
    price = models.IntegerField()
    cat = models.IntegerField(verbose_name='Category',choices=CAT)
    pdetails = models.CharField(max_length=50,verbose_name='Product Detail')
    is_active = models.BooleanField(default=True)
    pimage = models.ImageField(upload_to='image')

class Cart(models.Model):
    userid = models.ForeignKey('auth.User',on_delete = models.CASCADE,db_column = 'userid')
    pid = models.ForeignKey('Product',on_delete = models.CASCADE,db_column = 'pid')
    qty = models.IntegerField(default=1)

class Order(models.Model):
    orderid = models.CharField(max_length=50)
    userid = models.ForeignKey('auth.User',on_delete = models.CASCADE,db_column = 'userid')
    pid = models.ForeignKey('Product',on_delete = models.CASCADE,db_column = 'pid')
    qty = models.IntegerField(default=1)
    amt = models.FloatField()



'''
    def __str__(self):
        #return self.name
        return self.price
'''
