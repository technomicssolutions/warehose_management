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
	url(r'^salesman_stock/$', SalesmanStockReports.as_view(), name='salesman_stock_report'),
	url(r'^pending_salesman/$', PendingSalesmanReport.as_view(), name='pending_salesman_report'),
	url(r'^customer_payment/$', CustomerPaymentReport.as_view(), name='customer_payment_report'),
	url(r'^pending_customer/$', PendingCustomerReport.as_view(), name='pending_customer_report'),
	url(r'^completed_dn/$', CompletedDNReport.as_view(), name='completed_dn_report'),
	url(r'^vendor/$', VendorReport.as_view(), name='vendor_report'),
	url(r'^salesman_outstanding_customer', SalesmanWiseOutstandingCustomerReport.as_view() ,name='salesman_outstanding_customer')
)
