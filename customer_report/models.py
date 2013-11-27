from django.db import models

class Product(models.Model):
    """
    Ecwid product information
    """
    id = models.CharField(max_length=16)
    sku = models.CharField(max_length=5, primary_key=True)
    quantity = models.IntegerField()
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    url = models.URLField()
    created = models.DateTimeField()
    updated = models.DateTimeField()
    productClassId = models.CharField(max_length=16)
    enabled = models.BooleanField()
    description = models.TextField()
    descriptionTruncated = models.BooleanField()

    last_update = 0

    def __unicode__(self):
        return self.name

class Order(models.Model):
    """
    Ecwid product order information
    """
    product = models.ForeignKey(Product)
    slot = models.CharField(max_length=50)
    customer_name = models.CharField(max_length=255)
    quantity = models.IntegerField()
    payment_status = models.CharField(max_length=15)
    
    last_updated = 0

    def __unicode__(self):
        return self.slot
