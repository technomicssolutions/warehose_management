from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

from inventory.models import Item
from inventory.models import Brand
from web.models import Vendor, TransportationCompany

# Create your models here.   


class Purchase(models.Model):
	
	purchase_invoice_number = models.IntegerField('Purchase Invoice Number', unique=True)
	vendor_invoice_number = models.CharField('Vendor Invoice Number', default='1', max_length=10)
	vendor_do_number = models.CharField('Vendor DO Number', default='1', max_length = 10)
	vendor_invoice_date = models.DateField('Vendor Invoice Date', null=True, blank=True)
	purchase_invoice_date = models.DateField('Purchase Invoice Date', null=True, blank=True)
	brand = models.ForeignKey(Brand, null=True, blank=True)
	vendor = models.ForeignKey(Vendor, null=True, blank=True)
	transportation_company = models.ForeignKey(TransportationCompany, null=True, blank=True)
	discount = models.DecimalField('Discount',max_digits=14, decimal_places=3, default=0)
	net_total = models.DecimalField('Net Total',max_digits=14, decimal_places=3, default=0)
	vendor_amount = models.DecimalField('Vendor Amount',max_digits=14, decimal_places=3, default=0)
	grant_total = models.DecimalField('Grant Total', max_digits=14, decimal_places=3, default=0)
	purchase_expense = models.DecimalField('Purchase Expense', max_digits=14, decimal_places=3, default=0)
	
	def __unicode__(self):
		return str(self.purchase_invoice_number)

	class Meta:

		verbose_name = 'Purchase'
		verbose_name_plural = 'Purchase'

class PurchaseItem(models.Model):

	item = models.ForeignKey(Item, null=True, blank=True)
	purchase = models.ForeignKey(Purchase, null=True, blank=True)
	item_frieght = models.DecimalField('Item Frieght', max_digits=14, decimal_places=3, default=0)
	frieght_per_unit = models.DecimalField('Item Frieght per Unit', max_digits=14, decimal_places=3, default=0)
	item_handling = models.DecimalField('Item Handling', max_digits=14, decimal_places=3, default=0)
	handling_per_unit = models.DecimalField('Item Handling per Unit', max_digits=14, decimal_places=3, default=0)
	expense = models.DecimalField('Expense', max_digits=14, decimal_places=3, default=0)
	expense_per_unit = models.DecimalField('Expense per Unit', max_digits=14, decimal_places=3, default=0)
	quantity_purchased = models.IntegerField('Quantity Purchased', default=0)
	cost_price = models.DecimalField('Cost Price',max_digits=14, decimal_places=3, default=0)
	net_amount = models.DecimalField('Net Amount',max_digits=14, decimal_places=3, default=0)

	def __unicode__(self):

		return str(self.purchase.purchase_invoice_number)

	class Meta:

		verbose_name = 'Purchase Items'
		verbose_name_plural = 'Purchase Items'


class PurchaseReturn(models.Model):
	purchase = models.ForeignKey(Purchase)
	return_invoice_number = models.IntegerField('Purchase Return invoice number', unique=True)
	date = models.DateField('Date', null=True, blank=True)
	net_amount = models.DecimalField('Amount', max_digits=14, decimal_places=3, default=0)

	def __unicode__(self):
		return str(self.purchase.purchase_invoice_number)

class PurchaseReturnItem(models.Model):
	purchase_return = models.ForeignKey(PurchaseReturn)
	item = models.ForeignKey(Item)
	amount = models.DecimalField('Amount', max_digits=14, decimal_places=3, default=0)
	quantity = models.IntegerField('Quantity', default=0)
	
	def __unicode__(self):
		return str(self.purchase_return.return_invoice_number)

PAYMENT_MODE = (
	('cash', 'Cash'),
	('cheque', 'Cheque')
)
class VendorAccount(models.Model):

	vendor = models.ForeignKey(Vendor, unique=True)
	date = models.DateField('Date', null=True, blank=True)
	payment_mode = models.CharField('Payment Mode', max_length=10, choices=PAYMENT_MODE, default='cash')
	narration = models.CharField('Narration', max_length=10, null=True, blank=True)
	total_amount = models.DecimalField('Total Amount', max_digits=14, decimal_places=3, default=0)
	paid_amount = models.DecimalField('Paid Amount', max_digits=14, decimal_places=3, default=0)
	balance = models.DecimalField('Balance', max_digits=14, decimal_places=3, default=0)
	cheque_no = models.IntegerField('Cheque No', null=True, blank=True)
	cheque_date = models.DateField('Cheque Date', null=True, blank=True)
	bank_name = models.CharField('Bank Name', max_length=200, null=True, blank=True)
	branch_name = models.CharField('Branch Name', max_length=200, null=True, blank=True)

	def __unicode__(self):
		return self.vendor.user.first_name
	
	
