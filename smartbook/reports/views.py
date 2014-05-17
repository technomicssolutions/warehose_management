# Create your views here.
import sys
import os
import os.path

from django.db import IntegrityError
import simplejson
from datetime import datetime
from django.contrib.auth.views import password_reset
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from sales.models import *
from expenses.models import Expense
from inventory.models import *
from purchase.models import PurchaseItem
from django.core.files import File

import math

from purchase.models import Purchase, VendorAccount, PurchaseReturn

from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Image, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse

class Reports(View):
	def get(self, request, *args, **kwarg):
		return render(request, 'reports/report.html', {})

class SalesReports(View):
    def get(self, request, *args, **kwarg):        
        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        p.setFontSize(15)

        round_off = 0
        grant_total = 0
        total_profit = 0
        total_discount = 0
        total_cp = 0
        total_sp = 0
        cost_price = 0
        i = 0 

        report_type = request.GET.get('report_type', '')

        if not report_type:
            return render(request, 'reports/sales_reports.html', {
                'report_type' : 'date',
                })

        if report_type == 'date': 

            start = request.GET['start_date']
            end = request.GET['end_date']
           
            if not start:            
                ctx = {
                    'msg' : 'Please Select Start Date',
                    'start_date' : start,
                    'end_date' : end,
                    'report_type' : 'date',
                }
                return render(request, 'reports/sales_reports.html', ctx)
            elif not end:
                ctx = {
                    'msg' : 'Please Select End Date',
                    'start_date' : start,
                    'end_date' : end,
                    'report_type' : 'date',
                }
                return render(request, 'reports/sales_reports.html', ctx) 

                 
            else:

                start_date = datetime.strptime(start, '%d/%m/%Y')
                end_date = datetime.strptime(end, '%d/%m/%Y')

                p.drawString(350, 900, 'Date Wise Sales Report')
                p.setFontSize(13)
                p.drawString(50, 875, "Date")
                p.drawString(150, 875, "Invoice Number")
                p.drawString(250, 875, "Item Name")
                p.drawString(350, 875, "Quantity")
                p.drawString(450, 875, "Discount")
                p.drawString(550, 875, "Selling Price")
                p.drawString(650,875, "Average Cost Price")
                p.drawString(800, 875, "Total")
                p.drawString(900, 875, "Profit")

                y = 850

                sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date)
                if sales.count()>0:
                    for sale in sales:
                        round_off = round_off + sale.round_off
                        items = sale.salesitem_set.all()
                        for item in items:
                            discount = item.discount_given                         
                            dates = item.sales.sales_invoice_date
                            invoice_no = item.sales.sales_invoice_number
                            qty = item.quantity_sold
                            item_name = item.item.name
                            inventorys = item.item.inventory_set.all()
                            selling_price = 0  
                            if item.selling_price:
                                selling_price = item.selling_price
                            else:
                                inventory = inventorys[0]                            
                                selling_price = inventory.selling_price
                            	

                            purchases = item.item.purchaseitem_set.all()
                            avg_cp = 0
                            if purchases.count()>0:                                
                                for purchase in purchases:                                
                                    cost_price = cost_price + purchase.cost_price
                                    i = i + 1
                                avg_cp = cost_price/i 


                            total = selling_price * qty
                            # profit = (selling_price - avg_cp)*qty
                            profit = round(((selling_price - avg_cp)*qty) - discount,0)
                            avg_cp = math.ceil(avg_cp*100)/100                           
                            grant_total = grant_total + total
                            total_profit = total_profit + profit
                            total_discount = total_discount + discount

                            avg_cp = math.ceil(avg_cp*100)/100

                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                            p.drawString(50, y, dates.strftime('%d/%m/%y'))
                            p.drawString(150, y, str(invoice_no))
                            p.drawString(250, y, item_name)
                            p.drawString(350, y, str(qty))
                            p.drawString(450, y, str(discount))
                            p.drawString(550, y, str(selling_price))
                            p.drawString(650,y,str(avg_cp))
                            p.drawString(800, y, str(total))
                            p.drawString(900, y, str(profit))
                            
                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()
                p.drawString(50, y, 'Round Off : '+str(round_off))
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(350, y, '')
                p.drawString(450, y, str(total_discount))
                p.drawString(550, y, '')
                p.drawString(800, y, str(grant_total))
                p.drawString(900, y, str(total_profit))

                p.showPage()
                p.save()


        elif report_type == 'item':

            start = request.GET['start_date']
            end = request.GET['end_date']
            item_code = request.GET['item']          

            
            if not start:            
                ctx = {
                    'msg' : 'Please Select Start Date ',
                    'start_date' : start,
                    'end_date' : end,
                    'item' : item_code,                    
                    'report_type' : 'item',
                }
                return render(request, 'reports/sales_reports.html', ctx)
            elif not end:
                ctx = {
                    'msg' : 'Please Select End Date',
                    'start_date' : start,
                    'end_date' : end,
                    'item' : item_code,
                    'report_type' : 'item',
                }
                return render(request, 'reports/sales_reports.html', ctx) 
            elif item_code == 'select':
                ctx = {
                    'msg' : 'Please Select an Item',
                    'start_date' : start,
                    'end_date' : end,
                    'item' : item_code,
                    'report_type' : 'item',
                }
                return render(request, 'reports/sales_reports.html', ctx) 
            else:

                start_date = datetime.strptime(start, '%d/%m/%Y')
                end_date = datetime.strptime(end, '%d/%m/%Y')

                p.drawString(325, 900, 'Item Wise Sales Report')
                p.setFontSize(13)
                p.drawString(50, 875, "Item Code")
                p.drawString(150, 875, "Item Name")
                p.drawString(250, 875, "Total Quantity")
                p.drawString(350, 875, "Discount")
                p.drawString(450, 875, "Cost Price")
                p.drawString(550, 875, "Selling Price")
                p.drawString(650,875, "Total") 
                p.drawString(750, 875, "Profit")     

                y = 850       
                item = Item.objects.get(code=item_code)
                salesitems = SalesItem.objects.filter(sales__sales_invoice_date__gte=start_date, sales__sales_invoice_date__lte=end_date,item=item)
                # sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date)
                # if sales.count()>0:
                #     for sale in sales:
                #         items = sale.salesitem_set.all()
                if salesitems.count()>0:

                    for salesitem in salesitems:
                        discount = salesitem.discount_given                         
                        total_qty = salesitem.quantity_sold
                        item_name = salesitem.item.name
                        item_code = salesitem.item.code
                        inventorys = salesitem.item.inventory_set.all()
                        selling_price = 0                            
                        if inventorys.count()>0:
                        	inventory = inventorys[0]                            
                        	selling_price = inventory.selling_price                            

                        purchases = salesitem.item.purchaseitem_set.all()
                        avg_cp = 0
                        if purchases.count()>0:
                            for purchase in purchases:
                                cost_price = cost_price + purchase.cost_price
                                i = i + 1
                            avg_cp = cost_price/i
                        total = selling_price * total_qty
                        # profit = (selling_price - avg_cp)*total_qty
                        profit = round(((selling_price - avg_cp)*total_qty) - discount,0)

                        total_profit = total_profit + profit
                        total_discount = total_discount + discount
                        total_cp = total_cp + avg_cp
                        total_sp = total_sp + selling_price
                        grant_total = grant_total + total

                        avg_cp = math.ceil(avg_cp*100)/100
                        

                        y = y - 30
                        if y <= 270:
                            y = 850
                            p.showPage()
                        p.drawString(50, y, str(item_code))
                        p.drawString(150, y, item_name)
                        p.drawString(250, y, str(total_qty))
                        p.drawString(350, y, str(discount))
                        p.drawString(450, y, str(avg_cp))
                        p.drawString(550, y, str(selling_price))
                        p.drawString(650,y, str(total)) 
                        p.drawString(750, y, str(profit))

                total_cp = math.ceil(total_cp*100)/100 

                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()
                p.drawString(50, y, '')
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(350, y, str(total_discount))
                p.drawString(450, y, str(total_cp))
                p.drawString(550, y, str(total_sp))

                p.drawString(650, y, str(grant_total))
                p.drawString(750, y, str(total_profit)) 

                p.showPage()
                p.save()

            
        elif report_type == 'customer':
            start = request.GET['start_date']
            end = request.GET['end_date']       
            customer_name = request.GET['customer_name']

            if start is None:
                return render(request, 'reports/sales_reports.html', {})
            if not start:            
                ctx = {
                    'msg' : 'Please Select Start Date',
                    'start_date' : start,
                    'end_date' : end,
                    'customer' : customer_name,
                    'report_type' : 'customer',
                }
                return render(request, 'reports/sales_reports.html', ctx)
            elif not end:
                ctx = {
                    'msg' : 'Please Select End Date',
                    'start_date' : start,
                    'end_date' : end,
                    'customer' : customer_name,
                    'report_type' : 'customer',
                }
                return render(request, 'reports/sales_reports.html', ctx) 
            elif customer_name == 'select':
                ctx = {
                    'msg' : 'Please Select Customer Name',
                    'start_date' : start,
                    'end_date' : end,
                    'customer' : customer_name,
                    'report_type' : 'customer',
                }
                return render(request, 'reports/sales_reports.html', ctx)
            else:


                start_date = datetime.strptime(start, '%d/%m/%Y')
                end_date = datetime.strptime(end, '%d/%m/%Y')

                p.drawString(350, 900, 'Customer Wise Sales Report')
                p.setFontSize(13)
                p.drawString(50, 875, "Date")
                p.drawString(150, 875, "Invoice Number")
                p.drawString(250, 875, "Item Name")
                p.drawString(350, 875, "Quantity")
                p.drawString(450, 875, "Discount")
                p.drawString(550, 875, "Average Cost Price")
                p.drawString(700, 875, "Selling Price")
                p.drawString(800, 875, "Total") 
                p.drawString(900, 875, "Profit")
                
                y = 850

                
                customer = Customer.objects.get(customer_name = customer_name)
                sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date,customer=customer)
                if sales.count()>0:
                    for sale in sales:
                        items = sale.salesitem_set.all()
                        for item in items:
                            dates = item.sales.sales_invoice_date
                            invoice_no = item.sales.sales_invoice_number
                            item_name = item.item.name
                            qty = item.quantity_sold
                            discount = item.discount_given
                            inventorys = item.item.inventory_set.all()
                            selling_price = 0                            
                            if inventorys.count()>0:
                            	inventory = inventorys[0]                            
                            	selling_price = inventory.selling_price
                            
                            total = selling_price * qty

                            purchases = item.item.purchaseitem_set.all()
                            avg_cp = 0
                            if purchases.count()>0:                                
                                for purchase in purchases:
                                    cost_price = cost_price + purchase.cost_price
                                    i = i + 1
                                avg_cp = cost_price/i
                            # profit = (selling_price - avg_cp)*qty
                           
                            profit = math.ceil((selling_price - avg_cp)*qty) - float(discount)

                            total_profit = total_profit + profit
                            total_discount = total_discount + discount                            
                            total_sp = total_sp + selling_price
                            grant_total = grant_total + total

                            avg_cp = math.ceil(avg_cp*100)/100

                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                            p.drawString(50, y, dates.strftime('%d-%m-%Y'))
                            p.drawString(150, y, str(invoice_no))
                            p.drawString(250, y, item_name)
                            p.drawString(350, y, str(qty))
                            p.drawString(450, y, str(discount))
                            p.drawString(550, y, str(avg_cp))
                            p.drawString(700, y, str(selling_price))
                            p.drawString(800, y, str(total)) 
                            p.drawString(900, y, str(profit))
                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()
                p.drawString(50, y, '')
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(350, y, '')
                p.drawString(450, y, str(total_discount))
                p.drawString(700, y, str(total_sp))
                p.drawString(800, y, str(grant_total)) 
                p.drawString(900, y, str(total_profit))


                p.showPage()
                p.save()

            
        elif report_type == 'salesman':
            start = request.GET['start_date']
            end = request.GET['end_date']
            salesman_name = request.GET['salesman_name']

            if start is None:
                return render(request, 'reports/sales_reports.html', {})
            if not start:            
                ctx = {
                    'msg' : 'Please Select Start Date',
                    'start_date' : start,
                    'end_date' : end,
                    'salesman' : salesman_name,
                    'report_type' : 'salesman',
                }
                return render(request, 'reports/sales_reports.html', ctx)
            elif not end:
                ctx = {
                    'msg' : 'Please Select End Date',
                    'start_date' : start,
                    'end_date' : end,
                    'salesman' : salesman_name,
                    'report_type' : 'salesman',

                }
                return render(request, 'reports/sales_reports.html', ctx) 
            elif salesman_name == 'select':
                ctx = {
                    'msg' : 'Please Select Salesman Name',
                    'start_date' : start,
                    'end_date' : end,
                    'salesman' : salesman_name,
                    'report_type' : 'salesman',
                    
                }
                return render(request, 'reports/sales_reports.html', ctx)
            else:

                start_date = datetime.strptime(start, '%d/%m/%Y')
                end_date = datetime.strptime(end, '%d/%m/%Y')

                p.drawString(425, 900, 'Salesman Wise Sales Report')
                p.setFontSize(13)
                p.drawString(50, 875, "Date")
                p.drawString(150, 875, "Invoice Number")
                p.drawString(250, 875, "Item Name")
                p.drawString(350, 875, "Quantity")
                p.drawString(450, 875, "Discount")
                p.drawString(550,875, "Average Cost Price")
                p.drawString(700, 875, "Selling Price")
                p.drawString(800, 875, "Total") 
                p.drawString(900, 875, "Profit")

                y = 850
                
                
                desig = Designation.objects.get(title = 'salesman')                
                salesmen = Staff.objects.filter(designation = desig, user__first_name=salesman_name)                
                sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date,salesman=salesmen)
                
                if sales.count()>0:                    
                    for sale in sales:
                        items = sale.salesitem_set.all()
                        for item in items:
                            dates = item.sales.sales_invoice_date
                            invoice_no = item.sales.sales_invoice_number
                            item_name = item.item.name
                            qty = item.quantity_sold
                            discount = item.discount_given
                            inventorys = item.item.inventory_set.all()
                            selling_price = 0                            
                            if inventorys.count()>0:
                            	inventory = inventorys[0]                            
                            	selling_price = inventory.selling_price
                            
                            total = selling_price * qty

                            purchases = item.item.purchaseitem_set.all()
                            avg_cp = 0
                            if purchases.count()>0:                                
                                for purchase in purchases:
                                    cost_price = cost_price + purchase.cost_price
                                    i = i + 1
                                avg_cp = cost_price/i
                            # profit = (selling_price - avg_cp)*qty
                            profit = round(((selling_price - avg_cp)*qty) - discount,0)

                            total_profit = total_profit + profit
                            total_discount = total_discount + discount                            
                            total_sp = total_sp + selling_price
                            grant_total = grant_total + total

                            avg_cp = math.ceil(avg_cp*100)/100
                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                            p.drawString(50, y, dates.strftime('%d-%m-%Y'))
                            p.drawString(150, y, str(invoice_no))
                            p.drawString(250, y, item_name)
                            p.drawString(350, y, str(qty))
                            p.drawString(450, y, str(discount))
                            p.drawString(550, y, str(avg_cp))
                            p.drawString(700, y, str(selling_price))
                            p.drawString(800, y, str(total)) 
                            p.drawString(900, y, str(profit))
                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()
                p.drawString(50, y, '')
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(350, y, '')
                p.drawString(450, y, str(total_discount))
                p.drawString(700, y, str(total_sp))
                p.drawString(800, y, str(grant_total)) 
                p.drawString(900, y, str(total_profit))


                p.showPage()
                p.save()

            
        return response
        
            

class PurchaseReports(View):
    def get(self, request, *args, **kwargs):
        
        
        status_code = 200
        total_amount = 0
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        p.setFontSize(15)
        report_type = request.GET.get('report_type', '')

        if not report_type:
            return render(request, 'reports/purchase_reports.html',{
                'report_type' : 'date',
                })

        if report_type == 'date':               
            p.drawCentredString(400, 900, 'Purchase Report Date wise')
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

            if not start_date:
                return render(request, 'reports/purchase_reports.html',{
                    'msg': 'Please Enter start date',
                    'start_date' : start_date,
                    'end_date' : end_date,
                    'report_type' : 'date',
                })
            if not end_date:
                return render(request, 'reports/purchase_reports.html',{
                    'msg': 'Please Enter end date',
                    'start_date' : start_date,
                    'end_date' : end_date,
                    'report_type' : 'date',
                })
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
            purchases = Purchase.objects.filter(purchase_invoice_date__gte=start_date, purchase_invoice_date__lte=end_date).order_by('purchase_invoice_date')
            p.setFontSize(13)
            p.drawString(50, 850, "Date")
            p.drawString(150, 850, "Invoice No")
            p.drawString(250, 850, "Vendor Invoice")
            p.drawString(350, 850, "Item code")
            p.drawString(450, 850, "Item name")
            p.drawString(550, 850, "Unit Cost price")
            p.drawString(650, 850, "Quantity")
            p.drawString(750, 850, "Amount")

            y = 820
            p.setFontSize(12)
            total_amount = 0
            for purchase in purchases:
                purchase_items = purchase.purchaseitem_set.all()
                for purchase_item in purchase_items:                    
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                    p.drawString(50, y, purchase_item.purchase.purchase_invoice_date.strftime('%d/%m/%y'))
                    p.drawString(150, y, str(purchase_item.purchase.purchase_invoice_number))
                    p.drawString(250, y, str(purchase_item.purchase.vendor_invoice_number))
                    p.drawString(350, y, purchase_item.item.code)
                    p.drawString(450, y, purchase_item.item.name)
                    p.drawString(550, y, str(purchase_item.cost_price))
                    p.drawString(650, y, str(purchase_item.quantity_purchased))
                    p.drawString(750, y, str(purchase_item.net_amount))
                    total_amount = total_amount + purchase_item.net_amount
            y = y - 30
            if y <= 270:
                y = 850
                p.showPage()
            p.drawString(650, y, 'Total:')
            p.drawString(750, y, str(total_amount))
            p.showPage()
            p.save()
        elif report_type == 'vendor':
            vendor_name = request.GET['vendor']

            if vendor_name == 'select':
                return render(request, 'reports/purchase_reports.html',{
                    'msg': 'Please Select Vendor Name',
                    'report_type' : 'vendor',
                    
                })


            vendor = Vendor.objects.get(user__first_name = vendor_name)
            purchases = Purchase.objects.filter(vendor = vendor)
            
            p.drawCentredString(400, 900, 'Purchase Report Vendor wise')
            p.setFontSize(13)
            p.drawString(50, 875, "Date")
            p.drawString(150, 875, "Invoice No")
            p.drawString(250, 875, "Vendor Invoice")
            p.drawString(370, 875, "Amount")
            p.setFontSize(12)  
            y = 850
            total_amount = 0
            for purchase in purchases:
                            
                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()
                p.drawString(50, y, purchase.purchase_invoice_date.strftime('%d/%m/%y'))
                p.drawString(150, y, str(purchase.purchase_invoice_number))
                p.drawString(250, y, str(purchase.vendor_invoice_number))
                p.drawString(350, y, str(purchase.vendor_amount))
                total_amount = total_amount + purchase.vendor_amount
            y = y - 30
            if y <= 270:
                y = 850
                p.showPage()
            p.drawString(250, y, 'Total:')
            p.drawString(350, y, str(total_amount))    
            p.showPage()
            p.save()
                  
        return response      

class SalesReturnReport(View):
    def get(self, request, *args, **kwargs):
        
        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date is None:
            return render(request, 'reports/sales_return.html', {})
        if not start_date:            
            ctx = {
                'msg' : 'Please Select Start Date ',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/sales_return.html', ctx)
        elif not end_date:
            ctx = {
                'msg' : 'Please Select End Date',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/sales_return.html', ctx)
        else:
            start = request.GET['start_date']
            end = request.GET['end_date']                    
            start_date = datetime.strptime(start, '%d/%m/%Y')
            end_date = datetime.strptime(end, '%d/%m/%Y')

            p.drawString(370, 900, 'Sales Return Reports')
    

            p.drawString(50, 875, "Date")
            p.drawString(150, 875, "Invoice Number")
            p.drawString(250, 875, "Item Code")
            p.drawString(350, 875, "Item Name")
            p.drawString(450, 875, "Quantity")
            p.drawString(550, 875, "Unit Price")
            # p.drawString(650, 875, "Selling Price")
            p.drawString(650, 875, "Total")
                

            y = 850       
      
            
            grant_total = 0

            salesreturn = SalesReturn.objects.filter(date__gte=start_date,date__lte=end_date)
            
            if salesreturn.count()>0:
                for sale in salesreturn:
                    salesreturn_items = sale.salesreturnitem_set.all()                    
                    if salesreturn_items.count()>0:
                        for salesreturn_item in salesreturn_items:
                            dates = salesreturn_item.sales_return.date
                            invoice_no = salesreturn_item.sales_return.return_invoice_number
                            qty = salesreturn_item.return_quantity
                            total = salesreturn_item.amount
                            item_name = salesreturn_item.item.name
                            item_code = salesreturn_item.item.code
                            inventorys = salesreturn_item.item.inventory_set.all()[0]
                            unitprice = inventorys.unit_price

                            grant_total = grant_total + total

                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()

                            p.drawString(50, y, dates.strftime('%d-%m-%Y'))
                            p.drawString(150, y, str(invoice_no))
                            p.drawString(250, y, str(item_code))
                            p.drawString(350, y, item_name)
                            p.drawString(450, y, str(qty))
                            p.drawString(550, y, str(unitprice))
                            # p.drawString(650, y, str(selling_price))
                            p.drawString(650, y, str(total))
            
            y= y - 30
            if y <= 270:
                y = 850
                p.showPage()
            p.drawString(50, y, '')
            p.drawString(150, y, '')
            p.drawString(250, y, '')
            p.drawString(350, y, '')
            p.drawString(450, y, '')
            p.drawString(550, y, '')
            p.drawString(650, y, str(grant_total))

            p.showPage()
            p.save()
        return response
      

class DailyReport(View):
    def get(self, request, *args, **kwargs):

        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date is None:
            return render(request, 'reports/daily_report.html', {})
        if not start_date:            
            ctx = {
                'msg' : 'Please Select Start Date ',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/daily_report.html', ctx)
        elif not end_date:
            ctx = {
                'msg' : 'Please Select End Date',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/daily_report.html', ctx)

        else:
            start = request.GET['start_date']
            end = request.GET['end_date']                    
            start_date = datetime.strptime(start, '%d/%m/%Y')
            end_date = datetime.strptime(end, '%d/%m/%Y')

            p.drawString(370, 900, 'Daily Reports')

            p.drawString(50, 870, "Date")
            p.drawString(150, 870, "Particulars/Narration")
            p.drawString(550, 870, "Income")
            p.drawString(650, 870, "Expense")           

            y = 850
            
            round_off = 0
            discount = 0
            total_income = 0
            total_expense = 0
            
            sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date)
            if sales.count()>0:
                for sale in sales:
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                    p.drawString(50, y, (sale.sales_invoice_date).strftime('%d-%m-%Y'))
                    p.drawString(150, y, 'By Sales '+str(sale.sales_invoice_number))
                    p.drawString(550, y, str(sale.grant_total))
                    p.drawString(650, y, '') 

                    round_off = round_off+sale.round_off
                    discount = discount+sale.discount
                    total_income = total_income + sale.grant_total            
            
            expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date)
            if expenses.count()>0:
                for expense in expenses:   
                    y = y - 30

                    if y <= 270:
                        y = 850
                        p.showPage()
                    
                    p.drawString(50, y, (expense.date).strftime('%d-%m-%Y'))
                    p.drawString(150, y, 'By Voucher '+str(expense.voucher_no)+','+expense.narration)
                    p.drawString(550, y, '')
                    p.drawString(650, y, str( expense.amount))    
                    
                    total_expense = total_expense + expense.amount 
            total_expense = total_expense + round_off + discount
            difference = total_income - total_expense

            y = y-30
            if y <= 270:
                y = 850
                p.showPage()
            p.drawString(50, y, '')
            p.drawString(150, y, 'TotalRoundOff-Sales')
            p.drawString(550, y, '')
            p.drawString(650, y, str(round_off))

            y = y-30
            if y <= 270:
                y = 850
                p.showPage()
            p.drawString(50, y, '')
            p.drawString(150, y, 'TotalDiscount-Sales')
            p.drawString(550, y, '')
            p.drawString(650, y, str(discount))            

            
            y = y-30
            if y <= 270:
                y = 850
                p.showPage()
            p.drawString(50, y, '')
            p.drawString(150, y, 'Total')
            p.drawString(550, y, str(total_income))
            p.drawString(650, y, str(total_expense))            

            p.showPage()
            p.save()
        return response

class PurchaseReturnReport(View):

    def get(self, request, *args, **kwargs):


        ctx_purchase_retrun_report = []
        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        p.setFontSize(15)
        report_type = request.GET.get('report_type', '')

        if not report_type:
            return render(request, 'reports/purchase_return.html',{
                'report_type' : 'date',
                })

        if report_type == 'date':               
           
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']
            
            if not start_date:
                return render(request, 'reports/purchase_return.html',{
                    'msg': 'Please Enter start date',
                    'start_date' : start_date,
                    'end_date' : end_date,
                    'report_type' : 'date',
                })
            if not end_date:
                return render(request, 'reports/purchase_return.html',{
                    'msg': 'Please Enter end date',
                    'start_date' : start_date,
                    'end_date' : end_date,
                    'report_type' : 'date',
                })
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')

            p.drawString(200, 900, 'PurchaseReturn Report Date wise Report')
            
            p.setFontSize(13)
            p.drawString(50, 850, "Date")
            p.drawString(150, 850, "Vendor Name")
            p.drawString(250, 850, "Item Name")
            p.drawString(350, 850, "Item Code")            
            p.drawString(450, 850, "Quantity")
            p.drawString(550, 850, "Amount")  
                   

            y = 820
            p.setFontSize(12)
            total_amount = 0

            purchase_returns = PurchaseReturn.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')

            if purchase_returns.count()>0:

                for purchase_return in purchase_returns:
                    purchasereturn_items = purchase_return.purchasereturnitem_set.all()
                    if purchasereturn_items.count()>0:
                        for purchasereturn_item in purchasereturn_items:

                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                            p.drawString(50, y, purchasereturn_item.purchase_return.date.strftime('%d/%m/%Y'))
                            p.drawString(150, y, purchasereturn_item.purchase_return.purchase.vendor.user.first_name)
                            p.drawString(250, y, purchasereturn_item.item.name)
                            p.drawString(350, y, purchasereturn_item.item.code)                   
                            p.drawString(450, y, str(purchasereturn_item.quantity))
                            p.drawString(550, y, str(purchasereturn_item.amount))

                            total_amount = total_amount + purchasereturn_item.amount

                    

            y = y - 30
            p.drawString(450, y, 'Total:')
            p.drawString(550, y, str(total_amount))

            p.showPage()
            p.save()
        elif report_type == 'vendor':
            vendor_name = request.GET['vendor'] 
            
            if vendor_name == 'select':
                return render(request, 'reports/purchase_return.html',{
                    'msg' : 'Please Enter Vendor Name',                    
                    'report_type' : 'vendor',
                    })         
            
            p.drawString(200, 900, 'PurchaseReturn Report Vendor wise Report')

            p.setFontSize(13)
            p.drawString(50, 850, "Date")
            p.drawString(150, 850, "Vendor Name")
            p.drawString(250, 850, "Item Name")
            p.drawString(350, 850, "Item Code")            
            p.drawString(450, 850, "Quantity")
            p.drawString(550, 850, "Amount")
             
            y = 850
            total_amount = 0

            vendor = Vendor.objects.get(user__first_name = vendor_name)
            purchase_returns = PurchaseReturn.objects.filter(purchase__vendor = vendor)

            if purchase_returns.count()>0:

                for purchase_return in purchase_returns:
                    purchasereturn_items = purchase_return.purchasereturnitem_set.all()
                    if purchasereturn_items.count()>0:
                        for purchasereturn_item in purchasereturn_items:

                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                            p.drawString(50, y, purchasereturn_item.purchase_return.date.strftime('%d/%m/%Y'))
                            p.drawString(150, y, purchasereturn_item.purchase_return.purchase.vendor.user.first_name)
                            p.drawString(250, y, purchasereturn_item.item.name)
                            p.drawString(350, y, purchasereturn_item.item.code)                   
                            p.drawString(450, y, str(purchasereturn_item.quantity))
                            p.drawString(550, y, str(purchasereturn_item.amount))

                            total_amount = total_amount + purchasereturn_item.amount

                      
                 

            y = y - 30
            p.drawString(450, y, 'Total:')
            p.drawString(550, y, str(total_amount))    
            p.showPage()
            p.save()
                  
        return response    


            

class ExpenseReport(View):

    def get(self, request, *args, **kwargs):

        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        total_amount = 0

        if start_date is None:
            return render(request, 'reports/expense_report.html', {})
        if not start_date:            
            ctx = {
                'msg' : 'Please Select Start Date ',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/expense_report.html', ctx)
        elif not end_date:
            ctx = {
                'msg' : 'Please Select End Date',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/expense_report.html', ctx)

        else:       
        
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']
            start_date = datetime.strptime(start_date, '%d/%m/%Y')
            end_date = datetime.strptime(end_date, '%d/%m/%Y')
            p.drawString(370, 900, 'Date Wise Expense Report')

            p.drawString(200, 870, "Date")
            p.drawString(300, 870, "Particulars")
            p.drawString(550, 870, "Narration")
            p.drawString(650, 870, "Amount") 
            y = 850

            expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
            if len(expenses) > 0: 
                for expense in expenses:
                    
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()

                    p.drawString(200, y, expense.date.strftime('%d/%m/%Y'))
                    p.drawString(300, y, expense.expense_head.expense_head)
                    p.drawString(550, y, expense.narration)
                    p.drawString(650, y, str(expense.amount))

                    total_amount = total_amount + expense.amount
            y = y - 30

            p.drawString(50, y, '')
            p.drawString(150, y, '')
            p.drawString(550, y, 'Total: ')
            p.drawString(650, y, str(total_amount))

            p.showPage()
            p.save()
        return response                   
    
 

class VendorAccountsReport(View):
    def get(self, request, *args, **kwargs):

        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))
        report_type = request.GET.get('report_type', '')

        if not report_type:
            return render(request, 'reports/vendor_accounts_report.html', {
                'report_type' : 'date',
                })

        if report_type == 'date':             
                                
            start_date = request.GET['start_date']
            end_date = request.GET['end_date']

            if start_date is None:
                return render(request, 'reports/vendor_accounts_report.html', {})
            if not start_date:            
                ctx = {
                    'msg' : 'Please Select Start Date',
                    'start_date' : start_date,
                    'end_date' : end_date,
                    'report_type' : 'date',
                }
                return render(request, 'reports/vendor_accounts_report.html', ctx)
            elif not end_date:
                ctx = {
                    'msg' : 'Please Select End Date',
                    'start_date' : start_date,
                    'end_date' : end_date,
                    'report_type' : 'date',
                }
                return render(request, 'reports/vendor_accounts_report.html', ctx) 
            else:
                start_date = datetime.strptime(start_date, '%d/%m/%Y')
                end_date = datetime.strptime(end_date, '%d/%m/%Y')

                p.drawString(350, 900, 'Date Wise Vendor Accounts')

                p.setFontSize(13)

                p.drawString(50, 875, "Date")
                p.drawString(150, 875, "Vendor Name")
                p.drawString(250, 875, "Payment Mode")
                p.drawString(350, 875, "Narration")
                p.drawString(450, 875, "Total Amount")
                p.drawString(550, 875, "Paid Amount")
                p.drawString(650, 875, "Balance") 

                
                y = 850

                purchase_accounts = VendorAccount.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
                if len(purchase_accounts) > 0:
                    for purchase_account in purchase_accounts:

                        y = y - 30
                        if y <= 270:
                            y = 850
                            p.showPage()

                        p.drawString(50, y, purchase_account.date.strftime('%d/%m/%Y') if purchase_account.date else '')
                        p.drawString(150, y, purchase_account.vendor.user.first_name)
                        p.drawString(250, y, purchase_account.payment_mode)
                        p.drawString(350, y, purchase_account.narration if purchase_account.narration else '')

                        p.drawString(450, y, str(purchase_account.total_amount))
                        p.drawString(550, y, str(purchase_account.paid_amount))
                        p.drawString(650, y, str(purchase_account.balance)) 

                p.showPage()
                p.save()
            
        
                
        elif report_type == 'vendor':

            vendor_name = request.GET['vendor']

            if vendor_name == 'select':            
                ctx = {
                    'msg' : 'Please Select Vendor',
                    'report_type' : 'vendor',
                }
                return render(request, 'reports/vendor_accounts_report.html', ctx)
            else:               

                p.drawString(350, 900, 'Vendor Wise Vendor Accounts')

                p.setFontSize(13)

                p.drawString(50, 875, "Date")
                p.drawString(150, 875, "Payment Mode")
                p.drawString(250, 875, "Narration")
                p.drawString(350, 875, "Total Amount")
                p.drawString(450, 875, "Paid Amount")
                p.drawString(550, 875, "Balance") 

                y = 850

                vendor = Vendor.objects.get(user__first_name = vendor_name)
                purchase_accounts = VendorAccount.objects.filter(vendor = vendor)

                if len(purchase_accounts) > 0:
                    for purchase_account in purchase_accounts:

                        y = y-30
                        if y <= 270:
                            y = 850
                            p.showPage()


                        p.drawString(50, y, purchase_account.date.strftime('%d/%m/%Y') if purchase_account.date else '')
                        p.drawString(150, y, purchase_account.payment_mode)
                        p.drawString(250, y, purchase_account.narration if purchase_account.narration else '')
                        p.drawString(350, y, str(purchase_account.total_amount))
                        p.drawString(450, y, str(purchase_account.paid_amount))
                        p.drawString(550, y, str(purchase_account.balance)) 
                p.showPage()
                p.save()
            
        return response 


class StockReports(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))

        status_code = 200
        stocks = Inventory.objects.all()
        
        p.drawString(400, 900, 'Stock Report')

        y = 850
        p.drawString(80, y, 'Item Code')
        p.drawString(160, y, 'Item Name')
        p.drawString(280, y, 'Barcode')
        p.drawString(360, y, 'Brand Name')    
        p.drawString(480, y, 'Stock')
        p.drawString(540, y, 'UOM')
        p.drawString(600, y, 'Unit Price')
        p.drawString(680, y, 'Tax')
        p.drawString(760, y, 'Discount')
        p.drawString(840, y, 'Stock By value')
        
        y = y - 50 
        if len(stocks) > 0:
            for stock in stocks:
                p.drawString(80, y, stock.item.code)
                p.drawString(160, y, stock.item.name)
                p.drawString(280, y, stock.item.barcode)
                p.drawString(360, y, stock.item.brand.brand)                
                p.drawString(480, y, str(stock.quantity))
                p.drawString(540, y, stock.item.uom.uom)
                p.drawString(600, y, str(stock.unit_price))
                p.drawString(680, y, str(stock.item.tax))
                p.drawString(760, y, str(stock.discount_permit_percentage))
                p.drawString(840, y, str(stock.quantity * stock.unit_price))
                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()

        p.showPage()
        p.save()
        return response



