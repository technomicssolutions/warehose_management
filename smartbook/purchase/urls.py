from django.conf.urls import patterns, include, url

from purchase.views import *

urlpatterns = patterns('',
	url(r'^$', PurchaseDetail.as_view(), name='purchase_details'),
	url(r'^entry/$', PurchaseEntry.as_view(), name='purchase'),
	url(r'^edit/$', PurchaseEdit.as_view(), name='edit_purchase'),
	url(r'^return/$', PurchaseReturnView.as_view(), name='purchase_return'),
	url(r'^return_edit/$', PurchaseReturnEdit.as_view(), name='edit_purchase_return'),
	url(r'^vendor_accounts/$', VendorAccounts.as_view(), name='vendor_accounts'),
	url(r'^vendor_account/$', VendorAccountDetails.as_view(), name='vendor_account_details'),
)