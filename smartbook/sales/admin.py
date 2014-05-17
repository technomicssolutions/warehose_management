from django.contrib import admin
from sales.models import *

admin.site.register(Sales)
admin.site.register(SalesItem)
admin.site.register(SalesReturn)
admin.site.register(SalesReturnItem)
admin.site.register(Quotation)
admin.site.register(DeliveryNote)
admin.site.register(SalesInvoice)
admin.site.register(QuotationItem)
admin.site.register(ReceiptVoucher)
admin.site.register(DeliveryNoteItem)