from django.conf.urls import patterns, include, url

from inventory.views import *

urlpatterns = patterns('',
	url(r'^add_item/$', ItemAdd.as_view(),name='add_item'),
	url(r'^items/$', ItemList.as_view(),name='item_list'),
	url(r'^brand_list/$', BrandList.as_view(), name="brand_list"),
	url(r'^add/brand/$', AddBrand.as_view(), name="add_brand"),
	url(r'^uom_list/$', UomList.as_view(), name="uom_list"),
	url(r'^add/uom/$', AddUom.as_view(), name="add_uom"),
	url(r'^stock/$', StockView.as_view(), name="stock"),
	url(r'^openining_stock/$', OpeningStockView.as_view(), name="opening_stock"),
	url(r'^openining_stock/entry/$', AddOpeningStock.as_view(), name="opening_stock_entry"),
	url(r'^edit_stock/$', EditStockView.as_view(), name='edit_stock'),
)

