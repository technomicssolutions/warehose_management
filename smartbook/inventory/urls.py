from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from inventory.views import *

urlpatterns = patterns('',
	url(r'^add_item/$', login_required(ItemAdd.as_view()),name='add_item'),
	url(r'^items/$', login_required(ItemList.as_view()),name='item_list'),
	url(r'^edit_item/(?P<item_id>\d+)/$', login_required(EditItem.as_view()),name='edit_item'),
	url(r'^brand_list/$', login_required(BrandList.as_view()), name="brand_list"),
	url(r'^add/brand/$', login_required(AddBrand.as_view()), name="add_brand"),
	url(r'^uom_list/$', login_required(UomList.as_view()), name="uom_list"),
	url(r'^add/uom/$', login_required(AddUom.as_view()), name="add_uom"),
	url(r'^stock/$', login_required(StockView.as_view()), name="stock"),
	url(r'^openining_stock/$', login_required(OpeningStockView.as_view()), name="opening_stock"),
	url(r'^openining_stock/entry/$', login_required(AddOpeningStock.as_view()), name="opening_stock_entry"),
	url(r'^edit_stock/$', login_required(EditStockView.as_view()), name='edit_stock'),
)
