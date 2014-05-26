from django.db import models
from django.contrib.auth.models import User

# Create your models here.

from web.models import *

class UnitOfMeasure(models.Model):

	uom = models.CharField('Unit Of Measure', max_length=50, unique=True)
	
	def __unicode__(self):
		return self.uom
        

class Brand(models.Model):

	brand = models.CharField('Brand', max_length=51, unique=True)
	
	
	def __unicode__(self):
		return self.brand

class InventoryItem(models.Model):

	code = models.CharField('Item Code', max_length=10, unique=True)
	name = models.CharField('Name', max_length=50)
	description = models.TextField('Description', max_length=50,null=True, blank=True)
	uom = models.ForeignKey(UnitOfMeasure, null=True, blank=True)
	brand = models.ForeignKey(Brand, null=True, blank=True)
	barcode = models.CharField('Barcode', max_length=50,null=True, blank=True)
	tax = models.DecimalField('Tax',max_digits=14, decimal_places=2, default=0)
	quantity = models.IntegerField('Quantity', default=0)
	unit_price = models.DecimalField('Unit Price',max_digits=14, decimal_places=2, default=0)
	selling_price = models.DecimalField('Selling Price',max_digits=14, decimal_places=2, default=0)
	discount_permit_percentage = models.DecimalField('Discount permitted percentage',max_digits=14, decimal_places=3, default=0,null=True, blank=True)
	discount_permit_amount = models.DecimalField('Discount permitted amount',max_digits=14, decimal_places=3, default=0,null=True, blank=True)

	def __unicode__(self):
		return self.code

	class Meta:
		verbose_name_plural = 'Inventory'
		

class OpeningStock(models.Model):
	item = models.ForeignKey(InventoryItem)
	quantity = models.IntegerField('Quantity', default=0)
	unit_price = models.DecimalField('Unit Price',max_digits=14, decimal_places=2, default=0)
	selling_price = models.DecimalField('Selling Price',max_digits=14, decimal_places=2, default=0)
	discount_permit_percentage = models.DecimalField('Discount permitted percentage',max_digits=14, decimal_places=3, default=0,null=True, blank=True)
	discount_permit_amount = models.DecimalField('Discount permitted amount',max_digits=14, decimal_places=3, default=0,null=True, blank=True)

	def __unicode__(self):
		return self.item.code

	class Meta:
		verbose_name_plural = 'Opening Stock'
