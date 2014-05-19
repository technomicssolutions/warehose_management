from django.db import models
from django.contrib.auth.models import User

from datetime import datetime

from inventory.models import Item
from inventory.models import Brand
from web.models import Customer, UserProfile


# Create your models here. 

PAYMENT_MODE = (
    ('cash', 'Cash'),
    ('cheque', 'Cheque'),
)

class Quotation(models.Model):

    to = models.ForeignKey(Customer, null=True, blank=True)
    date = models.DateField('Date', null=True, blank=True)
    attention = models.TextField('Attention', null=True, blank=True)
    subject = models.CharField('Subject', null=True, blank=True, max_length=20)
    reference_id = models.CharField('Reference no', null=True, blank=True, max_length=10)
    prefix = models.CharField('Prefix', null=True, blank=True, max_length=20, default='QO')
    processed = models.BooleanField('Is Processed', default=False)
    net_total = models.DecimalField('Net Total',max_digits=14, decimal_places=2, default=0)
    is_sales_invoice_created = models.BooleanField('Is Sales Invoice Created', default=False)
    delivery = models.CharField('Delivery', max_length=100, null=True, blank=True)
    proof = models.CharField('Proof', max_length=100, null=True, blank=True)
    payment = models.CharField('Payment', max_length=100, null=True, blank=True)
    validity = models.CharField('Validity', max_length=100, null=True, blank=True)

    def __unicode__(self):

        return str(self.reference_id)

    class Meta:

        verbose_name = 'Quotation'
        verbose_name_plural = 'Quotation'

class QuotationItem(models.Model):

    item = models.ForeignKey(Item, null=True, blank=True)
    quotation = models.ForeignKey(Quotation, null=True, blank=True)
    net_amount = models.DecimalField('Net Amount',max_digits=14, decimal_places=2, default=0)
    quantity_sold = models.IntegerField('Quantity Sold', default=0)
    discount = models.DecimalField('Total Discount',max_digits=14, decimal_places=2, default=0)  
    selling_price = models.DecimalField('Selling Price', max_digits=14, decimal_places=2, default=0)

    def __unicode__(self):

        return str(self.quotation.reference_id)

    class Meta:

        verbose_name = 'Quotation Item'
        verbose_name_plural = 'Quotation Item'


class DeliveryNote(models.Model):

    quotation = models.ForeignKey(Quotation, null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    delivery_note_number = models.CharField('Delivery Note Serial number', max_length=50, null=True, blank=True)
    date = models.DateField('Date', null=True, blank=True)
    lpo_number = models.CharField('LPO Number', null=True, blank=True, max_length=20)
    prefix = models.CharField('Prefix', null=True, blank=True, max_length=20, default='DN')
    processed = models.BooleanField('Is Processed', default=False)
    net_total = models.DecimalField('Net Total',max_digits=14, decimal_places=2, default=0)


    def __unicode__(self):

        return str(self.delivery_note_number)

    class Meta:

        verbose_name = 'Delivery Note'
        verbose_name_plural = 'Delivery Note'


class DeliveryNoteItem(models.Model):

    item = models.ForeignKey(Item, null=True, blank=True)
    delivery_note = models.ForeignKey(DeliveryNote, null=True, blank=True)
    net_amount = models.DecimalField('Net Amount', max_digits=14, decimal_places=2, default=0)
    quantity_sold = models.IntegerField('Quantity Sold', default=0)
    discount = models.DecimalField('Total Discount', max_digits=14, decimal_places=2, default=0)

    def __unicode__(self):

        return str(self.delivery_note.delivery_note_number)

    class Meta:

        verbose_name = 'Delivery Note Item'
        verbose_name_plural = 'Delivery Note Item'


class Sales(models.Model): 

    sales_invoice_number = models.CharField('Sales Invoice Number', null=True, blank=True, max_length=10)
    sales_invoice_date = models.DateField('Sales Invoice Date', null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    salesman = models.ForeignKey(User, null=True, blank=True)
    payment_mode = models.CharField('Payment Mode', null=True, blank=True, max_length=25)
    card_number = models.IntegerField('Card Number',null=True, blank=True)
    bank_name = models.CharField('Bank Name',max_length=50,null=True, blank=True)
    net_amount = models.DecimalField('Net Amount',max_digits=14, decimal_places=2, default=0)
    round_off = models.DecimalField('Net Round Off',max_digits=14, decimal_places=2, default=0)
    grant_total = models.DecimalField('Grand Total',max_digits=14, decimal_places=2, default=0)
    discount = models.DecimalField('Total Discount',max_digits=14, decimal_places=2, default=0)
    quotation = models.ForeignKey(Quotation, null=True, blank=True)
    delivery_note = models.ForeignKey(DeliveryNote, null=True, blank=True)
    lpo_number = models.CharField('LPO Number', null=True, blank=True, max_length=30)

    def __unicode__(self):

        return str(self.sales_invoice_number)

    class Meta:

        verbose_name = 'Sales'
        verbose_name_plural = 'Sales'


class SalesInvoice(models.Model):

    quotation = models.ForeignKey(Quotation, null=True, blank=True)
    delivery_note = models.ForeignKey(DeliveryNote, null=True, blank=True)
    sales = models.ForeignKey(Sales)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    date = models.DateField('Date', null=True, blank=True)
    invoice_no = models.CharField('Invoice Number',null=True, blank=True, max_length=20)
    prefix =  models.CharField('Prefix', max_length=20, default='INV')
    is_processed = models.BooleanField('Processed', default=False)


    def __unicode__(self):

        return str(self.invoice_no)

    class Meta:

        verbose_name = 'Sales Invoice'
        verbose_name_plural = 'Sales Invoice'

class SalesItem(models.Model):

    item = models.ForeignKey(Item)
    sales = models.ForeignKey(Sales)
    quantity_sold = models.IntegerField('Quantity Sold', default=0)
    discount_given = models.DecimalField('Discount Given',max_digits=14, decimal_places=2, default=0)  
    selling_price = models.DecimalField('Selling Price', max_digits=14, decimal_places=2, default=0) 
    net_amount = models.DecimalField('Sold Net Amount', max_digits=14, decimal_places=2, default=0)
    
    
    def __unicode__(self):

        return str(self.sales.sales_invoice_number)

    class Meta:

        verbose_name = 'Sales Items'
        verbose_name_plural = 'Sales Items'

class SalesReturn(models.Model):
    sales = models.ForeignKey(Sales)
    return_invoice_number = models.IntegerField('Sales Return invoice number', unique=True)
    date = models.DateField('Date', null=True, blank=True)
    net_amount = models.IntegerField('Total', null=True, blank=True)
    

    def __unicode__(self):
        return str(self.sales.sales_invoice_number)

class SalesReturnItem(models.Model):
    sales_return = models.ForeignKey(SalesReturn, null=True, blank=True)
    item = models.ForeignKey(Item, null=True, blank=True)
    return_quantity = models.IntegerField('Return Quantity', null=True, blank=True)
    amount = models.IntegerField('Amount', null=True, blank=True)

    def __unicode__(self):

        return str(self.sales_return.return_invoice_number)

class ReceiptVoucher(models.Model):

    sales_invoice = models.ForeignKey(SalesInvoice, null=True, blank=True)
    receipt_voucher_no = models.CharField('Receipt Voucher No', null=True, blank=True, max_length=30)
    date = models.DateField('Date', null=True, blank=True)
    customer = models.ForeignKey(Customer, null=True, blank=True)
    sum_of = models.DecimalField('Sum of', max_digits=14, decimal_places=2, default=0)
    cheque_no = models.CharField('Check Number', null=True, blank=True, max_length=50)
    bank = models.CharField('Bank', null=True, blank=True, max_length=100)
    dated = models.DateField('Dated', null=True, blank=True)
    payment_mode = models.CharField('Payment Mode', null=True, blank=True, max_length=40, choices=PAYMENT_MODE)
    prefix = models.CharField('Prefix', null=True, blank=True, max_length=20, default='RV')

    def __unicode__(self):

        return str(self.sales_invoice.invoice_no)

    class Meta:

        verbose_name = 'Receipt Voucher'
        verbose_name_plural = 'Receipt Voucher'








        


