from django.conf.urls import patterns, include, url

from reports.views import *

urlpatterns = patterns('',
	url(r'^reports/$', Reports.as_view(), name='reports'),
	url(r'^sales_reports/$', SalesReports.as_view(), name='sales_reports'),	
	url(r'^purchase/$', PurchaseReports.as_view(), name='purchase_reports'),
	url(r'^vendor_accounts/$', VendorAccountsReport.as_view(), name='vendor_accounts_report'),
	url(r'^stock_reports/$', StockReports.as_view(), name='stock_reports'),
	url(r'^salesreturn_reports/$', SalesReturnReport.as_view(), name='sales_return_report'),
	url(r'^daily_report/$', DailyReport.as_view(), name='daily_report'),
	url(r'^purchase_return/$', PurchaseReturnReport.as_view(), name='purchase_return_report'),
	url(r'^expenses/$', ExpenseReport.as_view(), name='expense_report'),
)
