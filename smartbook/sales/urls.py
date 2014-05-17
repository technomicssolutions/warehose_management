from django.conf.urls import patterns, include, url

from sales.views import *

urlpatterns = patterns('',

	url(r'^$', SalesDetails.as_view(), name='sales_details'),	
	url(r'^entry/$', SalesEntry.as_view(), name='sales'),
	url(r'^return/$', SalesReturnView.as_view(), name='return_entry'),	
	#url(r'sales_return_entry/$', SalesReturnView.as_view(), name='return_entry'),
	url(r'view_sales/$', ViewSales.as_view(), name='view_sales'),
	url(r'create_quotation/$', CreateQuotation.as_view(), name='create_quotation'),
	url(r'^create_quotation_pdf/(?P<quotation_id>\d+)/$', CreateQuotationPdf.as_view(), name='create_quotation_pdf'),
	url(r'create_delivery_note/$', CreateDeliveryNote.as_view(), name='create_delivery_note'),
	url(r'quotaion_deliverynote_sales/$', QuotationDeliverynoteSales.as_view(), name='create_sales_entry'),
	url(r'quotation_details/$', QuotationDetails.as_view(), name='quotation_details'),
	url(r'delivery_note_details/$', DeliveryNoteDetails.as_view(), name='delivery_note_details'),
	url(r'^delivery_note_pdf/(?P<delivery_note_id>\d+)/$', DeliveryNotePDF.as_view(), name='delivery_note_pdf'),
	url(r'^sales_invoice_pdf/(?P<sales_invoice_id>\d+)/$', CreateSalesInvoicePDF.as_view(), name='sales_invoice_pdf'),
	url(r'pdf_receipt_voucher/(?P<receipt_voucher_id>\d+)/$', PrintReceiptVoucher.as_view(), name="pdf_receipt_voucher"),
	url(r'receipt_voucher/$', ReceiptVoucherCreation.as_view(), name='receipt_voucher'),
	url(r'invoice_details/$', InvoiceDetails.as_view(), name='invoice_details'),
	url(r'direct_delivery_note/$', DirectDeliveryNote.as_view(), name='direct_delivery_note'),
	url(r'latest_sales_details/$', LatestSalesDetails.as_view(), name='latest_sales_details'),
	url(r'edit_sales_invoice/$', EditSalesInvoice.as_view(), name='edit_sales_invoice'),
	url(r'edit_quotation/$', EditQuotation.as_view(), name='edit_quotation'),
	url(r'edit_delivery_note/$', EditDeliveryNote.as_view(), name='edit_delivery_note'),
)