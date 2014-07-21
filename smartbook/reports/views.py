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
from expenses.models import Expense, ExpenseHead
from inventory.models import *
from purchase.models import PurchaseItem
from django.core.files import File

import math

from purchase.models import Purchase, VendorAccount, PurchaseReturn

from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Image, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse


def header(canvas):

        style = [
            ('FONTSIZE', (0,0), (-1, -1), 25),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica-Bold') 
        ]
        para_style = ParagraphStyle('fancy')
        para_style.fontSize = 35
        para_style.fontName = 'Helvetica-Bold'
        para = Paragraph('Fine Nuts', para_style)

        data =[['', '', para , '']]
        
        table = Table(data, colWidths=[30, 300, 400, 100], rowHeights=50, style=style)
        table.wrapOn(canvas, 200, 400)
        table.drawOn(canvas,50, 1000) 
        canvas.drawString(50, 1000, 'FINE NUTS TRADING LLC')
        canvas.drawString(50, 985, 'P.O.Box: 68125, Dubai, U.A.E')
        canvas.drawString(50, 970, 'Email: support@finenutsintl.com')
        canvas.drawString(50, 955, 'Web: www.finenutsintl.com')
        canvas.drawString(50, 940, 'Tel.:04 4508879, Fax: 04 4281403')
        canvas.line(50,925,950,925)

        return canvas

class Reports(View):
	def get(self, request, *args, **kwarg):
		return render(request, 'reports/report.html', {})

class SalesReports(View):
    def get(self, request, *args, **kwarg):        
        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))
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
            payment_mode = request.GET['payment_mode']
            print payment_mode
           
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

                report_heading = 'Date Wise Sales Report' + ' - ' + payment_mode + ' - ' + start + ' - ' + end
                start_date = datetime.strptime(start, '%d/%m/%Y')
                end_date = datetime.strptime(end, '%d/%m/%Y')
                p = header(p)
                p.drawString(350, 900, report_heading)
                p.setFontSize(13)
                p.drawString(50, 875, "Date")
                p.drawString(110, 875, "Invoice Number")
                p.drawString(210, 875, "Item Name")
                p.drawString(420, 875, "Quantity")
                p.drawString(490, 875, "Discount")
                p.drawString(550, 875, "Selling Price")
                p.drawString(650,875, "Average Cost Price")
                p.drawString(800, 875, "Total")
                p.drawString(900, 875, "Profit")

                y = 850

                sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date, payment_mode=payment_mode)
                if sales.count()>0:
                    for sale in sales:
                        round_off = round_off + sale.round_off
                        ctx_item_list = []

                        for s_item in sale.salesitem_set.all(): 
                            if s_item.delivery_note_item.item.id not in ctx_item_list:
                                ctx_item_list.append(s_item.delivery_note_item.item.id)
                        for item_id in ctx_item_list:
                            quantity = 0
                            avg_cp = 0
                            total = 0
                            profit = 0
                            discount = 0
                            for item in sale.salesitem_set.filter(delivery_note_item__item__id =item_id):
                                discount = item.discount_amount + discount                        
                                dates = item.sales.sales_invoice_date
                                invoice_no = item.sales.sales_invoice_number
                                quantity = int(item.quantity_sold) + int(quantity)
                                item_name = item.delivery_note_item.item.name if item.delivery_note_item else ''
                                inventorys = item.delivery_note_item.item if item.delivery_note_item else ''
                                selling_price = 0  
                                if item.selling_price:
                                    selling_price = item.selling_price	

                                try:
                                    purchases = item.delivery_note_item.item.purchaseitem_set.all()
                                    purchase_count = purchases.count()
                                except:
                                    purchase_count = 0
                                # purchases = item.delivery_note_item.item.purchaseitem_set.all() if item.delivery_note_item else []
                                avg_cp = 0
                                if purchase_count > 0:                                
                                    for purchase in purchases:                                
                                        cost_price = cost_price + purchase.cost_price
                                        i = i + 1
                                    avg_cp = cost_price/i 

                                total_item_sale = item.selling_price * item.quantity_sold
                                total = total_item_sale + total
                                total_item_sale = 0
                                # profit = (selling_price - avg_cp)*qty
                                profit = round(((selling_price - avg_cp)*quantity) - discount,0)
                                avg_cp = math.ceil(avg_cp*100)/100                           
                                
                                total_profit = total_profit + profit
                                total_discount = total_discount + discount

                                avg_cp = math.ceil(avg_cp*100)/100
                            grant_total = grant_total + total
                            y = y - 30
                            if y <= 135:
                                y = 850
                                p.showPage()
                                p = header(p)
                            p.drawString(50, y, dates.strftime('%d/%m/%y'))
                            p.drawString(120, y, str(invoice_no))
                            p.drawString(200, y, item_name)
                            p.drawString(450, y, str(quantity))
                            p.drawString(500, y, str(discount))
                            p.drawString(570, y, str(selling_price))
                            p.drawString(650,y,str(avg_cp))
                            p.drawString(800, y, str(total))
                            p.drawString(900, y, str(profit))
                            
                y = y - 30
                if y <= 135:
                    y = 850
                    p.showPage()
                    p = header(p)
                p.drawString(50, y, 'Round Off : '+str(round_off))
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(350, y, '')
                p.drawString(500, y, str(total_discount))
                p.drawString(550, y, '')
                p.drawString(800, y, str(grant_total))
                p.drawString(900, y, str(total_profit))

                p.showPage()
                p.save()


        elif report_type == 'item':

            start = request.GET['start_date']
            end = request.GET['end_date']
            item_code = request.GET['item']          
            payment_mode = request.GET['payment_mode']
            print payment_mode
            
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
                p = header(p)
                report_heading = 'Item Wise Sales Report' + ' - ' + payment_mode + ' - ' + item_code
                p.drawString(325, 900, report_heading)
                p.setFontSize(13)
                p.drawString(50, 875, "Item Code")
                p.drawString(120, 875, "Item Name")
                p.drawString(350, 875, "Total Quantity")
                p.drawString(450, 875, "Discount")
                p.drawString(550, 875, "Cost Price")
                p.drawString(650, 875, "Selling Price")
                p.drawString(750,875, "Total") 
                p.drawString(850, 875, "Profit")     

                y = 850       
                item = InventoryItem.objects.get(code=item_code)
                salesitems = SalesItem.objects.filter(sales__sales_invoice_date__gte=start_date, sales__sales_invoice_date__lte=end_date, delivery_note_item__item=item, sales__payment_mode=payment_mode)
                # sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date)
                # if sales.count()>0:
                #     for sale in sales:
                #         items = sale.salesitem_set.all()
                if salesitems.count()>0:

                    for salesitem in salesitems:
                        discount = salesitem.discount_amount                         
                        total_qty = salesitem.quantity_sold
                        item_name = salesitem.delivery_note_item.item.name
                        item_code = salesitem.delivery_note_item.item.code
                        selling_price = 0                            
                        if salesitem.selling_price:                       
                        	selling_price = salesitem.selling_price                            

                        try:
                            purchases = item.delivery_note_item.item.purchaseitem_set.all()
                            purchase_count = purchases.count()
                        except:
                            purchase_count = 0
                        
                        # purchases = salesitem.delivery_note_item.item.purchaseitem_set.all()
                        avg_cp = 0
                        if purchase_count > 0:
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
                        if y <= 135:
                            y = 850
                            p.showPage()
                            p = header(p)
                        p.drawString(50, y, str(item_code))
                        p.drawString(120, y, item_name)
                        p.drawString(400, y, str(total_qty))
                        p.drawString(450, y, str(discount))
                        p.drawString(550, y, str(avg_cp))
                        p.drawString(650, y, str(selling_price))
                        p.drawString(750,y, str(total)) 
                        p.drawString(850, y, str(profit))

                total_cp = math.ceil(total_cp*100)/100 

                y = y - 30
                if y <= 135:
                    y = 850
                    p.showPage()
                    p = header(p)
                p.drawString(50, y, '')
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(450, y, str(total_discount))
                p.drawString(550, y, str(total_cp))
                p.drawString(650, y, str(total_sp))

                p.drawString(750, y, str(grant_total))
                p.drawString(850, y, str(total_profit)) 

                p.showPage()
                p.save()

            
        elif report_type == 'customer':
            start = request.GET['start_date']
            end = request.GET['end_date']       
            customer_name = request.GET['customer_name']
            payment_mode = request.GET['payment_mode']
            print payment_mode

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
                p = header(p)

                report_heading = 'Customer Wise Sales Report' + ' - ' + payment_mode + ' - ' + customer_name
                p.drawString(350, 900, report_heading)
                p.setFontSize(13)
                p.drawString(50, 875, "Date")
                p.drawString(110, 875, "Invoice Number")
                p.drawString(250, 875, "Item Name")
                p.drawString(430, 875, "Quantity")
                p.drawString(490, 875, "Discount")
                p.drawString(550, 875, "Average Cost Price")
                p.drawString(700, 875, "Selling Price")
                p.drawString(800, 875, "Total") 
                p.drawString(900, 875, "Profit")
                
                y = 850

                
                customer = Customer.objects.get(customer_name = customer_name)
                sales = Sales.objects.filter(sales_invoice_date__gte=start_date, sales_invoice_date__lte=end_date, customer=customer, payment_mode=payment_mode)
                if sales.count()>0:
                    for sale in sales:
                        ctx_item_list = []
                        for s_item in sale.salesitem_set.all(): 
                            if s_item.delivery_note_item.item.id not in ctx_item_list:
                                ctx_item_list.append(s_item.delivery_note_item.item.id)
                        for item_id in ctx_item_list:
                            qty = 0
                            avg_cp = 0
                            total = 0
                            profit = 0
                            discount = 0
                            for item in sale.salesitem_set.filter(delivery_note_item__item__id =item_id):
                                dates = item.sales.sales_invoice_date
                                invoice_no = item.sales.sales_invoice_number
                                item_name = item.delivery_note_item.item.name if item.delivery_note_item else ''
                                qty = int(item.quantity_sold) + qty
                                discount = item.discount_amount
                                selling_price = 0                            
                                if item.selling_price:                        
                                	selling_price = item.selling_price
                                
                                total = selling_price * qty
                                avg_cp = 0
                                purchase_count = 0
                                
                                try:
                                    purchases = item.delivery_note_item.item.purchaseitem_set.all()
                                    purchase_count = purchases.count()
                                except:
                                    purchase_count = 0
                                if purchase_count>0:                                
                                    for purchase in purchases:
                                        cost_price = cost_price + purchase.cost_price
                                        i = i + 1
                                    avg_cp = cost_price/i
                                # profit = (selling_price - avg_cp)*qty
                               
                                profit = math.ceil((selling_price - avg_cp)*qty) - float(discount)

                                total_profit = total_profit + profit
                                total_discount = total_discount + discount                            
                                total_sp = total_sp + selling_price
                                

                                avg_cp = math.ceil(avg_cp*100)/100
                            grant_total = grant_total + total

                            y = y - 30
                            if y <= 135:
                                y = 850
                                p.showPage()
                                p = header(p)
                            p.drawString(50, y, dates.strftime('%d-%m-%Y'))
                            p.drawString(140, y, str(invoice_no))
                            p.drawString(200, y, item_name)
                            p.drawString(450, y, str(qty))
                            p.drawString(500, y, str(discount))
                            p.drawString(550, y, str(avg_cp))
                            p.drawString(700, y, str(selling_price))
                            p.drawString(800, y, str(total)) 
                            p.drawString(900, y, str(profit))
                y = y - 30
                if y <= 135:
                    y = 850
                    p.showPage()
                    p = header(p)
                p.drawString(50, y, '')
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(350, y, '')
                p.drawString(500, y, str(total_discount))
                p.drawString(700, y, str(total_sp))
                p.drawString(800, y, str(grant_total)) 
                p.drawString(900, y, str(total_profit))


                p.showPage()
                p.save()

            
        elif report_type == 'salesman':
            start = request.GET['start_date']
            end = request.GET['end_date']
            salesman_name = request.GET['salesman_name']
            payment_mode = request.GET['payment_mode']
            print payment_mode

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
                report_heading = 'Salesman Wise Sales Report' + ' - ' + salesman_name + ' - ' + payment_mode
                p = header(p)

                p.drawString(425, 900, report_heading)
                p.setFontSize(13)
                p.drawString(30, 875, "Date")
                p.drawString(100, 875, "Invoice Number")
                p.drawString(200, 875, "Item Name")
                p.drawString(420, 875, "Quantity")
                p.drawString(500, 875, "Discount")
                p.drawString(570,875, "Average Cost Price")
                p.drawString(700, 875, "Selling Price")
                p.drawString(800, 875, "Total") 
                p.drawString(900, 875, "Profit")

                y = 850
                         
                salesmen = User.objects.filter(first_name=salesman_name)                
                sales = Sales.objects.filter(sales_invoice_date__gte=start_date,sales_invoice_date__lte=end_date,salesman=salesmen, payment_mode=payment_mode)
                
                if sales.count()>0:                    
                    for sale in sales:
                        ctx_item_list = []
                        for s_item in sale.salesitem_set.all(): 
                            if s_item.delivery_note_item.item.id not in ctx_item_list:
                                ctx_item_list.append(s_item.delivery_note_item.item.id)
                        for item_id in ctx_item_list:
                            qty = 0
                            avg_cp = 0
                            total = 0
                            profit = 0
                            discount = 0
                            for item in sale.salesitem_set.filter(delivery_note_item__item__id =item_id):
                                dates = item.sales.sales_invoice_date
                                invoice_no = item.sales.sales_invoice_number
                                item_name = item.delivery_note_item.item.name if item.delivery_note_item else ''
                                qty = int(item.quantity_sold) + int(qty)
                                discount = item.discount_amount
                                selling_price = 0                            
                                if item.selling_price:                          
                                	selling_price = item.selling_price
                                
                                total = selling_price * qty

                                # purchases = item.delivery_note_item.item.purchaseitem_set.all()
                                try:
                                    purchases = item.delivery_note_item.item.purchaseitem_set.all()
                                    purchase_count = purchases.count()
                                except:
                                    purchase_count = 0
                                avg_cp = 0
                                if purchase_count > 0:                                
                                    for purchase in purchases:
                                        cost_price = cost_price + purchase.cost_price
                                        i = i + 1
                                    avg_cp = cost_price/i
                                # profit = (selling_price - avg_cp)*qty
                                profit = round(((selling_price - avg_cp)*qty) - discount,0)

                                total_profit = total_profit + profit
                                total_discount = total_discount + discount                            
                                total_sp = total_sp + selling_price
                                

                                avg_cp = math.ceil(avg_cp*100)/100
                            grant_total = grant_total + total
                            y = y - 30
                            if y <= 135:
                                y = 850
                                p.showPage()
                                p = header(p)
                            p.drawString(30, y, dates.strftime('%d-%m-%Y'))
                            p.drawString(120, y, str(invoice_no))
                            p.drawString(200, y, item_name)
                            p.drawString(450, y, str(qty))
                            p.drawString(510, y, str(discount))
                            p.drawString(580, y, str(avg_cp))
                            p.drawString(700, y, str(selling_price))
                            p.drawString(800, y, str(total)) 
                            p.drawString(900, y, str(profit))
                y = y - 30
                if y <= 135:
                    y = 850
                    p.showPage()
                    p = header(p)
                p.drawString(50, y, '')
                p.drawString(150, y, '')
                p.drawString(250, y, '')
                p.drawString(450, y, '')
                p.drawString(510, y, str(total_discount))
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
        p = canvas.Canvas(response, pagesize=(1000, 1100))
        p.setFontSize(15)
        report_type = request.GET.get('report_type', '')

        if not report_type:
            return render(request, 'reports/purchase_reports.html',{
                'report_type' : 'date',
                })

        if report_type == 'date':   
            p = header(p)
            
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
            p.drawString(120, 850, "Invoice No")
            p.drawString(200, 850, "Vendor Invoice")
            p.drawString(300, 850, "Item code")
            p.drawString(380, 850, "Item name")
            p.drawString(650, 850, "Unit Cost price")
            p.drawString(750, 850, "Quantity")
            p.drawString(850, 850, "Amount")

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
                        p = header(p)
                    p.drawString(50, y, purchase_item.purchase.purchase_invoice_date.strftime('%d/%m/%y'))
                    p.drawString(120, y, str(purchase_item.purchase.purchase_invoice_number))
                    p.drawString(200, y, str(purchase_item.purchase.vendor_invoice_number))
                    p.drawString(300, y, purchase_item.item.code)
                    p.drawString(380, y, purchase_item.item.name)
                    p.drawString(650, y, str(purchase_item.cost_price))
                    p.drawString(750, y, str(purchase_item.quantity_purchased))
                    p.drawString(850, y, str(purchase_item.net_amount))
                    total_amount = total_amount + purchase_item.net_amount
            y = y - 30
            if y <= 270:
                y = 850
                p.showPage()
                p = header(p)
            p.drawString(750, y, 'Total:')
            p.drawString(850, y, str(total_amount))
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
            p = header(p)

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
                    p = header(p)
                p.drawString(50, y, purchase.purchase_invoice_date.strftime('%d/%m/%y'))
                p.drawString(150, y, str(purchase.purchase_invoice_number))
                p.drawString(250, y, str(purchase.vendor_invoice_number))
                p.drawString(350, y, str(purchase.vendor_amount))
                total_amount = total_amount + purchase.vendor_amount
            y = y - 30
            if y <= 270:
                y = 850
                p.showPage()
                p = header(p)
            p.drawString(250, y, 'Total:')
            p.drawString(350, y, str(total_amount))    
            p.showPage()
            p.save()
                  
        return response      

class SalesReturnReport(View):
    def get(self, request, *args, **kwargs):
        
        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))
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
            p = header(p)

            p.drawString(370, 900, 'Sales Return Reports')
    

            p.drawString(50, 875, "Date")
            p.drawString(150, 875, "Invoice Number")
            p.drawString(250, 875, "Item Code")
            p.drawString(350, 875, "Item Name")
            p.drawString(650, 875, "Quantity")
            p.drawString(750, 875, "Selling Price")
            # p.drawString(650, 875, "Selling Price")
            p.drawString(850, 875, "Total")
                

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
                            inventorys = salesreturn_item.item
                            selling_price = salesreturn_item.amount

                            grant_total = grant_total + total

                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                                p = header(p)

                            p.drawString(50, y, dates.strftime('%d-%m-%Y'))
                            p.drawString(150, y, str(invoice_no))
                            p.drawString(250, y, str(item_code))
                            p.drawString(350, y, item_name)
                            p.drawString(650, y, str(qty))
                            p.drawString(750, y, str(selling_price))
                            # p.drawString(650, y, str(selling_price))
                            p.drawString(850, y, str(total))
            
            y= y - 30
            if y <= 270:
                y = 850
                p.showPage()
                p = header(p)
            p.drawString(50, y, '')
            p.drawString(150, y, '')
            p.drawString(250, y, '')
            p.drawString(350, y, '')
            p.drawString(650, y, '')
            p.drawString(750, y, '')
            p.drawString(850, y, str(grant_total))

            p.showPage()
            p.save()
        return response
      

class DailyReport(View):
    def get(self, request, *args, **kwargs):

        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))
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
            # header 
            p = header(p)


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
                    if y <= 135:
                        y = 850
                        p.showPage()
                        p = header(p)
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

                    if y <= 135:
                        y = 850
                        p.showPage()
                        p = header(p)
                    
                    p.drawString(50, y, (expense.date).strftime('%d-%m-%Y'))
                    p.drawString(150, y, 'By Voucher '+str(expense.voucher_no)+','+expense.narration)
                    p.drawString(550, y, '')
                    p.drawString(650, y, str( expense.amount))    
                    
                    total_expense = total_expense + expense.amount 
            total_expense = total_expense + round_off + discount
            difference = total_income - total_expense

            y = y-30
            if y <= 135:
                y = 850
                p.showPage()
                p = header(p)
            p.drawString(50, y, '')
            p.drawString(150, y, 'TotalRoundOff-Sales')
            p.drawString(550, y, '')
            p.drawString(650, y, str(round_off))

            y = y-30
            if y <= 135:
                y = 850
                p.showPage()
                p = header(p)
            p.drawString(50, y, '')
            p.drawString(150, y, 'TotalDiscount-Sales')
            p.drawString(550, y, '')
            p.drawString(650, y, str(discount))            

            
            y = y-30
            if y <= 135:
                y = 850
                p.showPage()
                p = header(p)
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
        p = canvas.Canvas(response, pagesize=(1000, 1100))
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
            p = header(p)

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
                                p = header(p)
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
            p = header(p)

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
                                p = header(p)
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
        p = canvas.Canvas(response, pagesize=(1000, 1100))
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
            p = header(p)

            p.drawString(410, 900, 'Expense Report')

            p.drawString(200, 870, "Date")
            p.drawString(300, 870, "Particulars")
            p.drawString(450, 870, "Narration")
            p.drawString(650, 870, "Salesman") 
            p.drawString(750, 870, "Amount") 
            y = 850
            salesman_name = request.GET['salesman_name']
            if salesman_name != 'select':
                salesman = User.objects.get(first_name=salesman_name)
            else:
                salesman = None
            head_name = request.GET['expense_head']
            if head_name != 'select':
                expense_head = ExpenseHead.objects.get(expense_head=head_name)
            else:
                expense_head = None
            
            if salesman and expense_head:
                expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date, salesman=salesman,expense_head=expense_head).order_by('date')
            elif salesman and not expense_head:
                expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date, salesman=salesman).order_by('date')
            elif expense_head and not salesman:
                expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date, expense_head=expense_head).order_by('date')
            else:
                expenses = Expense.objects.filter(date__gte=start_date, date__lte=end_date).order_by('date')
            if len(expenses) > 0: 
                for expense in expenses:
                    
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                        p = header(p)

                    p.drawString(200, y, expense.date.strftime('%d/%m/%Y'))
                    p.drawString(300, y, expense.expense_head.expense_head)
                    p.drawString(450, y, expense.narration)
                    p.drawString(650, y, expense.salesman.first_name if expense.salesman else '')
                    p.drawString(750, y, str(expense.amount))

                    total_amount = total_amount + expense.amount
            y = y - 30

            p.drawString(50, y, '')
            p.drawString(150, y, '')
            p.drawString(650, y, 'Total: ')
            p.drawString(750, y, str(total_amount))

            p.showPage()
            p.save()
        return response                   
    
 

class VendorAccountsReport(View):
    def get(self, request, *args, **kwargs):

        status_code = 200
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))
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
                p = header(p)

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
                            p = header(p)

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
                p = header(p)

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
                            p = header(p)


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
        p = canvas.Canvas(response, pagesize=(1000, 1100))

        status_code = 200
        stocks = InventoryItem.objects.all()
        p = header(p)

        p.drawString(400, 900, 'Stock Report')

        y = 850
        p.drawString(40, y, 'Item Code')
        p.drawString(110, y, 'Item Name')
        p.drawString(330, y, 'Barcode')
        p.drawString(380, y, 'Brand Name')    
        p.drawString(480, y, 'Stock')
        p.drawString(540, y, 'UOM')
        p.drawString(600, y, 'Unit Price')
        p.drawString(680, y, 'Tax')
        p.drawString(760, y, 'Discount')
        p.drawString(840, y, 'Stock By value')
        
        y = y - 50 
        if len(stocks) > 0:
            for stock in stocks:
                p.drawString(40, y, stock.code)
                p.drawString(110, y, stock.name)
                p.drawString(330, y, str(stock.barcode))
                p.drawString(380, y, str(stock.brand.brand) if stock.brand else '')                
                p.drawString(480, y, str(stock.quantity))
                p.drawString(540, y, str(stock.uom.uom) if stock.uom else '')
                p.drawString(600, y, str(stock.unit_price))
                p.drawString(680, y, str(stock.tax))
                p.drawString(760, y, str(stock.discount_permit_percentage))
                p.drawString(840, y, str(stock.quantity * stock.unit_price))
                y = y - 30
                if y <= 270:
                    y = 850
                    p.showPage()
                    p = header(p)

        p.showPage()
        p.save()
        return response



class SalesmanStockReports(View):
    
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))

        status_code = 200
        salesman_name = request.GET.get('salesman_name')
        print salesman_name
        if salesman_name is None:
            return render(request, 'reports/salesman_stock_report.html', {})
        if salesman_name:
            if salesman_name == 'select':
                context = {
                    'message': 'Please Choose Salesman'
                }
                return render(request, 'reports/salesman_stock_report.html', context) 
            salesman = User.objects.get(first_name=salesman_name)
            delivery_notes = DeliveryNote.objects.filter(salesman=salesman)
        
        p = header(p)

        p.drawString(400, 900, 'Salesman Stock Report - ' + salesman_name)

        y = 850
        p.drawString(190, y, 'Item Code')
        p.drawString(280, y, 'Item Name')
        p.drawString(610, y, 'Total Quantity')    
        p.drawString(700, y, 'Sold Quantity')
        p.drawString(790, y, 'Pending')
        
        ctx_item_list = []
        for delivery_note in delivery_notes:
            for d_item in delivery_note.deliverynoteitem_set.all():
                if d_item.item.id not in ctx_item_list:
                    ctx_item_list.append(d_item.item.id)

        y = y - 50 
        for item_id in ctx_item_list:
            item = InventoryItem.objects.get(id=item_id)
            quantity_sold = 0
            total_quantity = 0
            for delivery_note in delivery_notes:
                for d_item in delivery_note.deliverynoteitem_set.filter(item__id=item_id):
                    quantity_sold = quantity_sold + d_item.quantity_sold
                    total_quantity = total_quantity + d_item.total_quantity
            p.drawString(190, y, item.code)
            p.drawString(280, y, item.name)
            p.drawString(610, y, str(total_quantity))
            p.drawString(700, y, str(quantity_sold))
            p.drawString(790, y, str(int(total_quantity) - int(quantity_sold)))
            
            y = y - 30
            if y <= 270:
                y = 850
                p.showPage()
                p = header(p)

        p.showPage()
        p.save()
        return response

class PendingSalesmanReport(View):

    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))

        status_code = 200
        salesman_name = request.GET.get('salesman_name')
        
        if salesman_name is None:
            return render(request, 'reports/pending_salesman_stock_report.html', {})
        if salesman_name:
            if salesman_name == 'select':
                context = {
                    'message': 'Please Choose Salesman'
                }
                return render(request, 'reports/pending_salesman_stock_report.html', context) 
            salesman = User.objects.get(first_name=salesman_name)
            delivery_notes = DeliveryNote.objects.filter(salesman=salesman, is_pending=True)
        p = header(p)

        p.drawString(400, 900, 'Pending Delivery Note Report - ' + salesman_name)

        y = 850
        p.drawString(80, y, 'Delivery Note No')
        p.drawString(190, y, 'Item Code')
        p.drawString(280, y, 'Item Name')
        p.drawString(610, y, 'Total Quantity')    
        p.drawString(700, y, 'Sold Quantity')
        p.drawString(790, y, 'Pending')
        
        y = y - 50 
        if len(delivery_notes) > 0:
            for delivery_note in delivery_notes:
                if delivery_note.deliverynoteitem_set.all().count() > 0:
                    for d_item in delivery_note.deliverynoteitem_set.all():
                        p.drawString(80, y, delivery_note.delivery_note_number)
                        p.drawString(190, y, d_item.item.code)
                        p.drawString(280, y, d_item.item.name)
                        p.drawString(610, y, str(d_item.total_quantity))
                        p.drawString(700, y, str(d_item.quantity_sold))
                        p.drawString(790, y, str(int(d_item.total_quantity) - int(d_item.quantity_sold)))
                        y = y - 30
                        if y <= 270:
                            y = 850
                            p.showPage()
                            p = header(p)

        p.showPage()
        p.save()
        return response

class PendingCustomerReport(View):

    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))

        status_code = 200
        customer_name = request.GET.get('customer_name')
        
        if customer_name is None:
            return render(request, 'reports/pending_customer_report.html', {})
        if customer_name:
            if customer_name == 'select':
                context = {
                    'message': 'Please Choose Customer'
                }
                return render(request, 'reports/pending_customer_report.html', context) 
            elif customer_name == 'all':
                customers = Customer.objects.all()
            else:
                customer = Customer.objects.get(customer_name=customer_name)
                customer_accounts = CustomerAccount.objects.filter(customer=customer, is_complted=False)
        p = header(p)

        p.drawString(400, 900, 'Pending Customer Report - ' + customer_name)

        y = 850
        p.drawString(200, y, 'Customer Name')
        p.drawString(320, y, 'Invoice No')
        p.drawString(420, y, 'Total Amount')
        p.drawString(550, y, 'Paid') 
        p.drawString(650, y, 'Balance') 
        
        y = y - 50 
        if customer_name == 'all':
            if len(customers) > 0:
                for customer in customers:
                    customer_accounts = CustomerAccount.objects.filter(customer=customer, is_complted=False)
                    for customer_account in customer_accounts:
                            
                            p.drawString(200, y, customer_account.customer.customer_name)
                            p.drawString(320, y, customer_account.invoice_no.sales_invoice_number)
                            p.drawString(420, y, str(customer_account.total_amount))
                            p.drawString(550, y, str(customer_account.paid))
                            p.drawString(650, y, str(customer_account.balance))
                            y = y - 30
                            if y <= 270:
                                y = 850
                                p.showPage()
                                p = header(p)
        else:
            if len(customer_accounts) > 0:
                for customer_account in customer_accounts:
                    
                    p.drawString(200, y, customer_account.customer.customer_name)
                    p.drawString(320, y, customer_account.invoice_no.sales_invoice_number)
                    p.drawString(420, y, str(customer_account.total_amount))
                    p.drawString(550, y, str(customer_account.paid))
                    p.drawString(650, y, str(customer_account.balance))
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                        p = header(p)

        p.showPage()
        p.save()
        return response

class CompletedDNReport(View):

    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))

        status_code = 200
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        if start_date is None:
            return render(request, 'reports/completed_DN_report.html', {})
        if not start_date:            
            ctx = {
                'msg' : 'Please Select Start Date ',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/completed_DN_report.html', ctx)
        elif not end_date:
            ctx = {
                'msg' : 'Please Select End Date',
                'start_date' : start_date,
                'end_date' : end_date,
            }
            return render(request, 'reports/completed_DN_report.html', ctx)

        else:
            start = request.GET['start_date']
            end = request.GET['end_date']                    
            start_date = datetime.strptime(start, '%d/%m/%Y')
            end_date = datetime.strptime(end, '%d/%m/%Y')
            delivery_notes = DeliveryNote.objects.filter(is_pending=False, date__gte=start_date, date__lte=end_date).order_by('date')
            
            report_name = 'Completed DN Report ( '+ start +' - '+ end +')'
            p = header(p)

            p.drawString(350, 900, report_name )
            y = 850
            p.drawString(200, y, 'Date')
            p.drawString(280, y, 'Delivery Note No')
            p.drawString(420, y, 'Salesman')
            p.drawString(550, y, 'Total Amount')
            
            y = y - 50 
            if delivery_notes.count() > 0:
                for delivery_note in delivery_notes:
                    p.drawString(200, y, str(delivery_note.date.strftime('%d/%m/%Y')))
                    p.drawString(280, y, str(delivery_note.delivery_note_number))
                    p.drawString(420, y, delivery_note.salesman.first_name)
                    p.drawString(550, y, str(delivery_note.net_total))
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                        p = header(p)


        p.showPage()
        p.save()
        return response

class VendorReport(View):

    def get(self, request, *args, **kwargs):

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1100))

        status_code = 200
        vendor_name = request.GET.get('vendor_name')
        
        if vendor_name is None:
            return render(request, 'reports/pending_vendor_report.html', {})
        if vendor_name:
            if vendor_name == 'select':
                context = {
                    'message': 'Please Choose Vendor'
                }
                return render(request, 'reports/pending_vendor_report.html', context) 
            elif vendor_name == 'all':
                vendors = Vendor.objects.all()
            else:
                vendor = Vendor.objects.get(user__first_name=vendor_name)
                vendor_accounts = VendorAccount.objects.filter(vendor=vendor)
        p = header(p)

        p.drawString(400, 900, 'Vendor Report - ' + vendor_name)

        y = 850
        
        
        if vendor_name == 'all':
            p.drawString(200, y, 'Vendor Name')
            p.drawString(320, y, 'Total Amount')
            p.drawString(420, y, 'Paid')
            p.drawString(550, y, 'Balance')
            p.drawString(650, y, 'Payment Mode') 
            y = y - 50 
            if vendors.count() > 0:
                for vendor in vendors:
                    vendor_account = VendorAccount.objects.get(vendor=vendor)
                    p.drawString(200, y, str(vendor.user.first_name))
                    p.drawString(320, y, str(vendor_account.total_amount))
                    p.drawString(420, y, str(vendor_account.paid_amount))
                    p.drawString(550, y, str(vendor_account.balance))
                    p.drawString(650, y, str(vendor_account.payment_mode))
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                        p = header(p)
        else:
            p.drawString(200, y, 'Total Amount')
            p.drawString(320, y, 'Paid')
            p.drawString(420, y, 'Balance')
            p.drawString(550, y, 'Payment Mode') 
            y = y - 50 
            if len(vendor_accounts) > 0:
                for vendor_account in vendor_accounts:
                    
                    p.drawString(200, y, str(vendor_account.total_amount))
                    p.drawString(320, y, str(vendor_account.paid_amount))
                    p.drawString(420, y, str(vendor_account.balance))
                    p.drawString(550, y, str(vendor_account.payment_mode))
                    y = y - 30
                    if y <= 270:
                        y = 850
                        p.showPage()
                        p = header(p)

        p.showPage()
        p.save()
        return response

