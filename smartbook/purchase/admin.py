from django.contrib import admin
from purchase.models import *



admin.site.register(Purchase)
admin.site.register(PurchaseReturn)
admin.site.register(PurchaseItem)
admin.site.register(PurchaseReturnItem)
admin.site.register(VendorAccount)

