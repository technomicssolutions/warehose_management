# Create your views here.
import sys
import ast
import simplejson
import datetime as dt
from datetime import datetime
from decimal import *
from num2words import num2words
import math
import os

from django.db import IntegrityError
from django.db.models import Max
from django.contrib.auth.views import password_reset
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.conf import settings

from sales.models import *
from inventory.models import InventoryItem
from web.models import Customer, OwnerCompany

from reportlab.lib.units import cm
from reportlab.lib.units import inch
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Frame, Image, Table, TableStyle, Paragraph, SimpleDocTemplate, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_JUSTIFY

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from django.http import HttpResponse

class SalesEntry(View):
    def get(self, request, *args, **kwargs):
        
        current_date = dt.datetime.now().date()

        inv_number = SalesInvoice.objects.aggregate(Max('id'))['id__max']

        if not inv_number:
            inv_number = 1
            prefix = 'INV'
        else:
            inv_number = inv_number + 1
            prefix = SalesInvoice.objects.latest('id').prefix
        
        invoice_number = prefix + str(inv_number)
        return render(request, 'sales/sales_entry.html',{
            'sales_invoice_number': invoice_number,
            'current_date': current_date.strftime('%d/%m/%Y'),
        })


    def post(self, request, *args, **kwargs):

        sales_dict = ast.literal_eval(request.POST['sales'])
        sales, sales_created = Sales.objects.get_or_create(sales_invoice_number=sales_dict['sales_invoice_number'])
        sales.sales_invoice_number = sales_dict['sales_invoice_number']
        sales.sales_invoice_date = datetime.strptime(sales_dict['sales_invoice_date'], '%d/%m/%Y')
        
        salesman = User.objects.get(first_name=sales_dict['staff']) 
        
        sales.discount = sales_dict['net_discount']
        sales.round_off = sales_dict['roundoff']
        sales.net_amount = sales_dict['net_total']
        sales.grant_total = sales_dict['grant_total']

        sales.salesman = salesman  
        sales.lpo_number = sales_dict['lpo_number']      
        sales.save()
        sales_items = sales_dict['sales_items']
        for sales_item in sales_items:
           
            item = Item.objects.get(code=sales_item['item_code'])
            s_item, item_created = SalesItem.objects.get_or_create(item=item, sales=sales)
            inventory, created = Inventory.objects.get_or_create(item=item)
            if sales_created:

                inventory.quantity = inventory.quantity - int(sales_item['qty_sold'])
            else:
                inventory.quantity = inventory.quantity + s_item.quantity_sold - int(sales_item['qty_sold'])      

            inventory.save()
                    
            s_item, item_created = SalesItem.objects.get_or_create(item=item, sales=sales)
            s_item.sales = sales
            s_item.item = item
            s_item.quantity_sold = sales_item['qty_sold']
            s_item.discount_given = sales_item['disc_given']
            s_item.net_amount = sales_item['net_amount']
            s_item.selling_price = sales_item['unit_price']
            s_item.save()

            stock, created = SalesmanStock.objects.get_or_create(item=item, salesman=salesman)
            if created:
                stock.quantity = int(sales_item['qty_sold'])                
            else:
                if sales_created:
                    stock.quantity = stock.quantity + int(sales_item['qty_sold'])
                else:
                    stock.quantity = stock.quantity - s_item.quantity_sold + int(sales_item['qty_sold'])
            selling_price = sales_item['unit_price']
            stock.selling_price = selling_price
            stock.unit_price = inventory.unit_price
            stock.discount_permit_percentage = inventory.discount_permit_percentage
            stock.discount_permit_amount = inventory.discount_permit_amount
            stock.save()

        sales_invoice, created = SalesInvoice.objects.get_or_create(sales=sales)
        sales.save()
        sales_invoice.date = sales.sales_invoice_date
        sales_invoice.invoice_no = sales.sales_invoice_number
        sales_invoice.save()
                    
        res = {
            'result': 'Ok',
            'sales_invoice_id': 'sales_invoice.id',
        }
        response = simplejson.dumps(res)
        status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")
    

class SalesReturnView(View):
    def get(self, request, *args, **kwargs):
        if SalesReturn.objects.exists():
            invoice_number = int(SalesReturn.objects.aggregate(Max('return_invoice_number'))['return_invoice_number__max']) + 1
        else:
            invoice_number = 1
        if not invoice_number:
            invoice_number = 1
        return render(request, 'sales/return_entry.html', {
            'invoice_number' : invoice_number,
        })

    def post(self, request, *args, **kwargs):


        post_dict = request.POST['sales_return']

        post_dict = ast.literal_eval(post_dict)
        sales = Sales.objects.get(sales_invoice_number=post_dict['sales_invoice_number'])
        sales_return, created = SalesReturn.objects.get_or_create(sales=sales, return_invoice_number = post_dict['invoice_number'])
        sales_return.date = datetime.strptime(post_dict['sales_return_date'], '%d/%m/%Y')
        sales_return.net_amount = post_dict['net_return_total']
        sales_return.save()        

        return_items = post_dict['sales_items']

        for item in return_items:
            return_item = Item.objects.get(code=item['item_code'])
            s_return_item, created = SalesReturnItem.objects.get_or_create(item=return_item, sales_return=sales_return)
            s_return_item.amount = item['returned_amount']
            s_return_item.return_quantity = item['returned_quantity']
            s_return_item.save()

            inventory = Inventory.objects.get(item=return_item)
            inventory.quantity = inventory.quantity + int(item['returned_quantity'])
            inventory.save()
        response = {
                'result': 'Ok',
            }
        status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")

  	
class ViewSales(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'sales/view_sales.html',{})

class SalesDetails(View):
    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            invoice_number = request.GET['invoice_no']
            try:
                sales = Sales.objects.get(sales_invoice_number=invoice_number)
            except:
                sales = None
            if sales:
                sales_items = SalesItem.objects.filter(sales=sales)

                sl_items = []

                for item in sales_items:
                    sl_items.append({
                        'item_code': item.item.code,
                        'item_name': item.item.name,
                        'barcode': item.item.barcode,
                        'stock': item.item.inventory_set.all()[0].quantity,
                        'unit_price': item.item.inventory_set.all()[0].selling_price,
                        'tax': item.item.tax,
                        'uom': item.item.uom.uom,
                        'quantity_sold': item.quantity_sold,
                        'discount_given': item.discount_given,


                    })
                sales_dict = {
                    'invoice_number': sales.sales_invoice_number,
                    'sales_invoice_date': sales.sales_invoice_date.strftime('%d/%m/%Y'),
                    'customer': sales.customer.customer_name,
                    'sales_man': sales.salesman.user.first_name,
                    'net_amount': sales.net_amount,
                    'round_off': sales.round_off,
                    'grant_total': sales.grant_total,
                    'discount': sales.discount,
                    'sales_items': sl_items
                }
                res = {
                    'result': 'Ok',
                    'sales': sales_dict
                }
            else:
                res = {
                    'result': 'No Sales entry for this invoice number',
                }
            response = simplejson.dumps(res)
            status_code = 200
            return HttpResponse(response, status = status_code, mimetype="application/json")

        return render(request, 'sales/view_sales.html',{})

class CreateQuotation(View):

    def get(self, request, *args, **kwargs):

        current_date = dt.datetime.now().date()

        ref_number = Quotation.objects.aggregate(Max('id'))['id__max']
        
        if not ref_number:
            ref_number = 1
            prefix = 'QO'
        else:
            ref_number = ref_number + 1
            prefix = Quotation.objects.latest('id').prefix
        reference_number = prefix + str(ref_number)

        context = {
            'current_date': current_date.strftime('%d-%m-%Y'),
            'reference_number': reference_number,
        }

        return render(request, 'sales/create_quotation.html', context)

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            quotation_data = ast.literal_eval(request.POST['quotation'])
            quotation, quotation_created = Quotation.objects.get_or_create(reference_id=quotation_data['reference_no'])
            quotation.date = datetime.strptime(quotation_data['date'], '%d-%m-%Y')
            quotation.attention = quotation_data['attention']
            quotation.subject = quotation_data['subject']           
            quotation.net_total = quotation_data['total_amount']

            quotation.delivery = quotation_data['delivery']
            quotation.proof = quotation_data['proof']
            quotation.payment = quotation_data['payment']
            quotation.validity = quotation_data['validity']
            quotation.save()
            customer = Customer.objects.get(customer_name=quotation_data['customer'])
            quotation.to = customer
            quotation.save()

            quotation_data_items = quotation_data['sales_items']
            for quotation_item in quotation_data_items:
                item = Item.objects.get(code=quotation_item['item_code'])
                quotation_item_obj, item_created = QuotationItem.objects.get_or_create(item=item, quotation=quotation)
                inventory, created = Inventory.objects.get_or_create(item=item)
                inventory.quantity = inventory.quantity - int(quotation_item['qty_sold'])
                inventory.save()
                quotation_item_obj.net_amount = float(quotation_item['net_amount'])
                quotation_item_obj.quantity_sold = int(quotation_item['qty_sold'])
                quotation_item_obj.selling_price = float(quotation_item['unit_price'])
                quotation_item_obj.save()
            res = {
                'result': 'OK',
                'quotation_id': quotation.id,
            }

            response = simplejson.dumps(res)

            return HttpResponse(response, status=200, mimetype='application/json')

class DeliveryNotePDF(View):

    def get(self, request, *args, **kwargs):

        delivery_note_id = kwargs['delivery_note_id']
        delivery_note = DeliveryNote.objects.get(id=delivery_note_id)

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1200))

        status_code = 200
        y = 1100
        style = [
            ('FONTSIZE', (0,0), (-1, -1), 20),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
        ]

        new_style = [
            ('FONTSIZE', (0,0), (-1, -1), 30),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
        ]

        para_style = ParagraphStyle('fancy')
        para_style.fontSize = 20
        para_style.fontName = 'Helvetica'
        para = Paragraph('<b> DELIVERY NOTE </b>', para_style)

        data =[['', delivery_note.date.strftime('%d-%m-%Y'), para , delivery_note.delivery_note_number]]
        
        table = Table(data, colWidths=[30, 360, 420, 100], rowHeights=50, style=style) 

        # table.setStyle(TableStyle([
        #                ('FONTSIZE', (2,0), (2,0), 30),
        #                ]))     
        table.wrapOn(p, 200, 400)
        table.drawOn(p,50, 980)

        quotation = delivery_note.quotation

        customer_name = ''
        if delivery_note.customer:
            customer_name = delivery_note.customer.customer_name

        data=[['', customer_name, delivery_note.lpo_number if delivery_note.lpo_number else '' ]]

        table = Table(data, colWidths=[30, 540, 60], rowHeights=30, style = style)      
        table.wrapOn(p, 200, 400)
        table.drawOn(p, 50, 940)

        data=[['', '', delivery_note.date.strftime('%d-%m-%Y')]]

        table = Table(data, colWidths=[450, 120, 70], rowHeights=50, style = style)      

        table.wrapOn(p, 200, 400)
        table.drawOn(p,50, 915)

        if delivery_note.quotation:            
            data=[['', '', delivery_note.quotation.reference_id]]

            table = Table(data, colWidths=[450, 120, 70], rowHeights=40, style = style)      
            table.wrapOn(p, 200, 400)
            table.drawOn(p,50, 885)
         

        y = 800

        i = 0
        i = i + 1
        if delivery_note.quotation:
            for q_item in delivery_note.quotation.quotationitem_set.all():
                       
                y = y-40

                if y <= 270:
                    y = 800
                    p.showPage()

                data1 = [[i, q_item.item.code, q_item.item.name, q_item.quantity_sold, q_item.item.uom.uom]]
                table = Table(data1, colWidths=[80, 120, 400, 90, 100], rowHeights=40, style = style)
                table.wrapOn(p, 200, 600)
                table.drawOn(p, 10, y)
                i = i + 1
        if delivery_note.deliverynoteitem_set.all().count() > 0:
            for delivery_item in delivery_note.deliverynoteitem_set.all():
                y = y-40
                if y <= 270:
                    y = 800
                    p.showPage()

                data1 = [[i, delivery_item.item.code, delivery_item.item.name, delivery_item.quantity_sold, delivery_item.item.uom.uom]]
                table = Table(data1, colWidths=[80, 120, 400, 90, 100], rowHeights=40, style = style)
                table.wrapOn(p, 200, 600)
                table.drawOn(p, 10, y)
                i = i + 1
        p.showPage()
        p.save()
        return response


class CreateQuotationPdf(View):
    def get(self, request, *args, **kwargs):

        quotation_id = kwargs['quotation_id']
        quotation = Quotation.objects.get(id=quotation_id)

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1000))

        status_code = 200
        y = 915

        style = [
            ('FONTSIZE', (0,0), (-1, -1), 16),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
            # ('INNERGRID', (0,0), (-1,1), 0.25, colors.black),
        ]

        style1 = [
            ('FONTSIZE', (0,0), (-1, -1), 18),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
            # ('INNERGRID', (0,0), (-1,1), 0.25, colors.black),
        ]

        try:
            owner_company = OwnerCompany.objects.latest('id')
            if owner_company.logo:
                path = settings.PROJECT_ROOT.replace("\\", "/")+"/media/"+owner_company.logo.name
                p.drawImage(path, 7*cm, 30*cm, width=20*cm, preserveAspectRatio=True)
        except:
            pass


        p.roundRect(80, y-130, 840, 0.5*inch, 10, stroke=1, fill=0)
        p.setFont("Helvetica-Bold", 20)
        p.drawString(400, 800, "QUOTATION")
        p.roundRect(80, y-250, 840, 120, 20, stroke=1, fill=0)   


        data=[['To                     :', quotation.to.customer_name]]
        table = Table(data, colWidths=[125, 400], rowHeights=40, style = style)      
        table.wrapOn(p, 200, 400)
        table.drawOn(p,160, 745)

        data=[['Attention           :', quotation.attention]]
        table = Table(data, colWidths=[125, 400], rowHeights=40, style = style)       
        table.wrapOn(p, 200, 400)
        table.drawOn(p,160, 715)

        data=[['Subject             :', quotation.subject]]
        table = Table(data, colWidths=[125, 400], rowHeights=40, style = style)       
        table.wrapOn(p, 200, 400)
        table.drawOn(p,160, 685)


        data=[['Date            :', quotation.date.strftime('%d-%m-%Y')]]
        table = Table(data, colWidths=[100, 400], rowHeights=40, style = style)       
        table.wrapOn(p, 200, 400)
        table.drawOn(p,700, 745)

        data=[['Ref. id         :', quotation.reference_id]]
        table = Table(data, colWidths=[100, 400], rowHeights=40, style = style)        
        table.wrapOn(p, 200, 400)
        table.drawOn(p,700, 715)


        # data=[['Sl.No:', 'Description', 'Qty', 'Unit Price', 'Amount(AED)']]

        # table = Table(data, colWidths=[100, 350, 100, 125, 125], rowHeights=40, style = style1)
        # table.setStyle(TableStyle([                                  
        #                            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        #                            ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
        #                            # ('LINEBEFORE',(1,0), (0,-1),1,colors.black),                                  
        #                            ]))
        # table.wrapOn(p, 200, 400)
        # table.drawOn(p,105,575)


        data=[['Sl.No:']]

        table = Table(data, colWidths=[100], rowHeights=40, style = style1)
        table.setStyle(TableStyle([                                  
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                   ('ALIGN',(0,-1),(-1,-1),'CENTRE'),                               
                                   ]))
        table.wrapOn(p, 200, 400)
        table.drawOn(p,105,575)

        data=[['Description']]

        table = Table(data, colWidths=[350], rowHeights=40, style = style1)
        table.setStyle(TableStyle([                                  
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                   ('ALIGN',(0,-1),(-1,-1),'CENTRE'),                                                                    
                                   ]))
        table.wrapOn(p, 200, 400)
        table.drawOn(p,205,575)

        data=[['Qty']]

        table = Table(data, colWidths=[100], rowHeights=40, style = style1)
        table.setStyle(TableStyle([                                  
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                   ('ALIGN',(0,-1),(-1,-1),'CENTRE'),                                
                                   ]))
        table.wrapOn(p, 200, 400)
        table.drawOn(p,555,575)


        data=[['Unit Price']]

        table = Table(data, colWidths=[125], rowHeights=40, style = style1)
        table.setStyle(TableStyle([                                  
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                   ('ALIGN',(0,-1),(-1,-1),'CENTRE'),                                 
                                   ]))
        table.wrapOn(p, 200, 400)
        table.drawOn(p,655,575)


        data=[['Amount(AED)']]

        table = Table(data, colWidths=[135], rowHeights=40, style = style1)
        table.setStyle(TableStyle([                                  
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                   ('ALIGN',(0,-1),(-1,-1),'CENTRE'),                                
                                   ]))
        table.wrapOn(p, 200, 400)
        table.drawOn(p,780,575)

        y = 575

        i = 0 
        i = i + 1

        for q_item in quotation.quotationitem_set.all():   

            if y <= 135:
                p.showPage()
                y = 915          

            y = y-40

            # data1=[[i, q_item.item.name, q_item.quantity_sold, q_item.item.inventory_set.all()[0].selling_price, q_item.net_amount]]
            # table = Table(data1, colWidths=[100, 350, 100, 125, 125], rowHeights=40, style = style)
            # table.setStyle(TableStyle([
            #                            # ('INNERGRID', (0,0), (0,0), 0.25, colors.black),
            #                            # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
            #                            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            #                            ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
            #                            # ('ALIGN', (0,0), (-1,-1),'RIGHT'),
            #                            # ('SPACEBELOW', (0,0), (-1,-1), 10),
            #                            # ('BACKGROUND',(0,0),(1,0),colors.lightgrey)
            #                            ]))
            # # table.wrapOn(p, 300, 200)
            # table.wrapOn(p, 200, 400)
            # # table.drawOn(p,105,460)
            # table.drawOn(p,105, x)


            data1=[[i]]
            table = Table(data1, colWidths=[100], rowHeights=40, style = style)
            table.setStyle(TableStyle([                                      
                                       # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
                                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                       ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                       ('ALIGN', (0,0), (-1,-1),'CENTRE'),
                                       ]))
            # table.wrapOn(p, 300, 200)
            table.wrapOn(p, 200, 400)
            # table.drawOn(p,105,460)
            table.drawOn(p,105, y)


            data1=[[q_item.item.name]]
            table = Table(data1, colWidths=[350], rowHeights=40, style = style)
            table.setStyle(TableStyle([
                                       # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
                                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                       ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                       ]))
            # table.wrapOn(p, 300, 200)
            table.wrapOn(p, 200, 400)
            # table.drawOn(p,105,460)
            table.drawOn(p,205, y)


            data1=[[q_item.quantity_sold]]
            table = Table(data1, colWidths=[100], rowHeights=40, style = style)
            table.setStyle(TableStyle([
                                       # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
                                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                       ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                       ('ALIGN', (0,0), (-1,-1),'CENTRE'),
                                       ]))
            # table.wrapOn(p, 300, 200)
            table.wrapOn(p, 200, 400)
            # table.drawOn(p,105,460)
            table.drawOn(p,555, y)
            
            data1=[[q_item.selling_price]]
            table = Table(data1, colWidths=[125], rowHeights=40, style = style)
            table.setStyle(TableStyle([
                                       # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
                                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                       ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                       ('ALIGN', (0,0), (-1,-1),'RIGHT'),
                                       ]))
            # table.wrapOn(p, 300, 200)
            table.wrapOn(p, 200, 400)
            # table.drawOn(p,105,460)
            table.drawOn(p,655, y)


            data1=[[q_item.net_amount]]
            table = Table(data1, colWidths=[135], rowHeights=40, style = style)
            table.setStyle(TableStyle([
                                       # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
                                       ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                       ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                       ('ALIGN', (0,0), (-1,-1),'RIGHT'),
                                       ]))
            # table.wrapOn(p, 300, 200)
            table.wrapOn(p, 200, 400)
            # table.drawOn(p,105,460)
            table.drawOn(p,780, y)

            i = i + 1

        data=[['', quotation.net_total]]

        table = Table(data, colWidths=[650, 160], rowHeights=40, style = style)
        table.setStyle(TableStyle([
                                   # ('INNERGRID', (0,1), (-1,-1), 0.25, colors.black),
                                   ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                                   ('VALIGN',(0,-1),(-1,-1),'MIDDLE'),
                                   ('ALIGN', (0,0), (-1,-1),'RIGHT'),
                                   ]))
        table.wrapOn(p, 200, 400)
        table.drawOn(p,105,y-40)
        p.setFont("Helvetica", 15)
        if y < 270:
            p.showPage()
            y = 1000
        p.drawString(110, y-100, "Hope the above quoted prices will meet your satisfaction and for further information please do not hesitate to contact us.")
        p.drawString(110, y-140, "Delivery     : " + str(quotation.delivery))
        p.drawString(110, y-160, "Proof          : " + str(quotation.proof))
        p.drawString(110, y-180, "Payment    : " + str(quotation.payment))
        p.drawString(110, y-200, "Validity       : " + str(quotation.validity))
        p.drawString(110, y-220, "For")
        p.drawString(110, y-240, "Sunlight Stationary")
        p.drawString(110, y-260, "Authorized Signatory")
        p.drawString(700, y-260, "Prepared By")
        
        # if x >= 270:
        # p.drawString(110, 150, "For")
        # p.drawString(110, 130, "Sunlight Stationary")
        # p.drawString(110, 70, "Authorized Signatory")
        # p.drawString(700, 70, "Prepared By")
        # else:           
        #     


        # data=[['Tel: +971-2-6763571, Fax : +971-2-6763581,P.O.Box : 48296, Abu Dhabi, United Arab Emirates']]
        # table = Table(data, colWidths=[700], rowHeights=30)
        # table.setStyle(TableStyle([
        #                            # ('BOX', (0,0), (-1,-1), 0.25, colors.black),   
        #                            ('ALIGN',(0,0), (-1,-1),'CENTRE'),                                    
        #                            ]))
       
        # table.wrapOn(p, 200, 400)
        # table.drawOn(p,160, 50)

        p.showPage()
        p.save()
        return response


class CreateDeliveryNote(View):

    def get(self, request, *args, **kwargs):

        current_date = dt.datetime.now().date()

        ref_number = DeliveryNote.objects.aggregate(Max('id'))['id__max']
        
        if not ref_number:
            ref_number = 1
            prefix = 'DN'
        else:
            ref_number = ref_number + 1
            prefix = DeliveryNote.objects.latest('id').prefix
        delivery_no = prefix + str(ref_number)

        context = {
            'current_date': current_date.strftime('%d-%m-%Y'),
            'delivery_no': delivery_no,
        }

        return render(request, 'sales/create_delivery_note.html', context)

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            quotation_details = ast.literal_eval(request.POST['quotation'])
            delivery_note_details = ast.literal_eval(request.POST['delivery_note'])
            quotation = Quotation.objects.get(reference_id=delivery_note_details['quotation_no'])
            
            for q_item in quotation.quotationitem_set.all():
                quotation_item_names = []
                for item_data in quotation_details['sales_items']:
                    quotation_item_names.append(item_data['item_name'])
                if q_item.item.name not in quotation_item_names:
                    item = q_item.item 
                    inventory, created = Inventory.objects.get_or_create(item=item)
                    inventory.quantity = inventory.quantity + int(q_item.quantity_sold)
                    inventory.save()
                    q_item.delete()
                else:
                    for item_data in quotation_details['sales_items']:
                        if q_item.item.code == item_data['item_code']:
                            if q_item.quantity_sold != int(item_data['qty_sold']):
                                item = q_item.item
                                inventory, created = Inventory.objects.get_or_create(item=item)
                                inventory.quantity = inventory.quantity + int(q_item.quantity_sold)
                                inventory.save()
                                inventory.quantity = inventory.quantity - int(item_data['qty_sold'])
                                inventory.save()
                                q_item.quantity_sold = int(item_data['qty_sold'])
                                q_item.save()
                            if q_item.discount != float(item_data['disc_given']):
                                q_item.discount = item_data['disc_given']
                                q_item.save()
                            if q_item.net_amount != float(item_data['net_amount']):
                                q_item.net_amount = item_data['net_amount']
                                q_item.save()
            if quotation.net_total != float(quotation_details['net_total']):
                quotation.net_total = quotation_details['net_total']
                quotation.save()

            delivery_note, created = DeliveryNote.objects.get_or_create(quotation=quotation)
            quotation.processed = True
            quotation.save()
            delivery_note.quotation = quotation
            delivery_note.customer = quotation.to
            delivery_note.date = datetime.strptime(delivery_note_details['date'], '%d-%m-%Y')
            delivery_note.lpo_number = delivery_note_details['lpo_no']
            delivery_note.delivery_note_number = delivery_note_details['delivery_note_no']
            delivery_note.save()

            res = {
                'result': 'ok',
                'delivery_note_id': delivery_note.id
            }

            response = simplejson.dumps(res)

            return HttpResponse(response, status=200, mimetype='application/json')

class QuotationDetails(View):

    def get(self, request, *args, **kwargs):

        
        in_sales_invoice_creation = ''
        sales_invoice_creation = request.GET.get('sales_invoice', '')

        ref_number = request.GET.get('reference_no', '')
        if sales_invoice_creation == 'true':
            quotations = Quotation.objects.filter(reference_id__istartswith=ref_number, is_sales_invoice_created=False)
        else:
            quotations = Quotation.objects.filter(reference_id__istartswith=ref_number, processed=False, is_sales_invoice_created=False)
        quotation_list = []
        for quotation in quotations:
            item_list = []
            i = 0 
            i = i + 1
            if quotation.deliverynote_set.all().count() > 0:
                delivery_note = quotation.deliverynote_set.all()[0]

                for q_item in delivery_note.deliverynoteitem_set.all():
                    item_list.append({
                        'sl_no': i,
                        'item_name': q_item.item.name,
                        'item_code': q_item.item.code,
                        'barcode': q_item.item.barcode,
                        'item_description': q_item.item.description,
                        'qty_sold': q_item.quantity_sold,
                        'tax': q_item.item.tax,
                        'uom': q_item.item.uom.uom,
                        'current_stock': q_item.item.inventory_set.all()[0].quantity if q_item.item.inventory_set.count() > 0  else 0 ,
                        'selling_price': q_item.item.inventory_set.all()[0].selling_price if q_item.item.inventory_set.count() > 0 else 0 ,
                        'discount_permit': q_item.item.inventory_set.all()[0].discount_permit_percentage if q_item.item.inventory_set.count() > 0 else 0,
                        'net_amount': q_item.net_amount,
                        'discount_given': q_item.discount,
                    })
                    i = i + 1 

            if quotation.quotationitem_set.all().count() > 0:
                for q_item in quotation.quotationitem_set.all():
                    item_list.append({
                        'sl_no': i,
                        'item_name': q_item.item.name,
                        'item_code': q_item.item.code,
                        'barcode': q_item.item.barcode,
                        'item_description': q_item.item.description,
                        'qty_sold': q_item.quantity_sold,
                        'tax': q_item.item.tax,
                        'uom': q_item.item.uom.uom,
                        'current_stock': q_item.item.inventory_set.all()[0].quantity if q_item.item.inventory_set.count() > 0  else 0 ,
                        'selling_price': q_item.item.inventory_set.all()[0].selling_price if q_item.item.inventory_set.count() > 0 else 0 ,
                        'discount_permit': q_item.item.inventory_set.all()[0].discount_permit_percentage if q_item.item.inventory_set.count() > 0 else 0,
                        'net_amount': q_item.net_amount,
                        'discount_given': q_item.discount,
                    })
                    i = i + 1
            quotation_list.append({
                'date': quotation.date.strftime('%d/%m/%Y') if quotation.date else '',
                'delivery': quotation.delivery,
                'proof': quotation.proof,
                'payment': quotation.payment,
                'attention': quotation.attention,
                'subject': quotation.subject,
                'validity': quotation.validity,
                'ref_no': quotation.reference_id,
                'customer': quotation.to.customer_name if quotation.to else '' ,
                'items': item_list,
                'net_total': quotation.net_total,
                'delivery_no': quotation.deliverynote_set.all()[0].delivery_note_number if quotation.deliverynote_set.all().count() > 0 else 0,
                'lpo_number': quotation.deliverynote_set.all()[0].lpo_number if quotation.deliverynote_set.all().count() > 0 else '',
            })

        res = {
            'quotations': quotation_list,
            'result': 'ok',
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DeliveryNoteDetails(View):

    def get(self, request, *args, **kwargs):

        delivery_no = request.GET.get('delivery_no', '')

        delivery_note_details = DeliveryNote.objects.filter(delivery_note_number__istartswith=delivery_no, is_pending=True)
        
        delivery_note_list = []
        net_total = 0

        for delivery_note in delivery_note_details:
            i = 0 
            i = i + 1
            item_list = []
            if delivery_note.deliverynoteitem_set.all().count() > 0:  
                for delivery_note_item in delivery_note.deliverynoteitem_set.all():
                    item_list.append({
                        'sl_no': i,
                        'id': delivery_note_item.item.id,
                        'item_name': delivery_note_item.item.name,
                        'item_code': delivery_note_item.item.code,
                        'barcode': delivery_note_item.item.barcode,
                        'item_description': delivery_note_item.item.description,
                        'qty_sold': delivery_note_item.quantity_sold,
                        'sold_qty': delivery_note_item.quantity_sold,
                        'tax': delivery_note_item.item.tax,
                        'uom': delivery_note_item.item.uom.uom,
                        'current_stock': delivery_note_item.total_quantity if delivery_note_item.item else 0 ,
                        'selling_price': delivery_note_item.item.selling_price if delivery_note_item.item else 0 ,
                        'discount_permit': delivery_note_item.item.discount_permit_percentage if delivery_note_item.item else 0,
                        'net_amount': delivery_note_item.net_amount,
                        'discount_given': delivery_note_item.discount,
                        'remaining_qty': int(delivery_note_item.total_quantity - delivery_note_item.quantity_sold) if delivery_note_item else 0,
                    })
                    i = i + 1
                        
            delivery_note_list.append({
                'salesman': delivery_note.salesman.first_name if delivery_note.salesman else '' ,
                'items': item_list,
                'net_total': delivery_note.net_total if delivery_note.net_total else '' ,
                'delivery_no': delivery_note.delivery_note_number,
                'lpo_number': delivery_note.lpo_number if delivery_note.lpo_number else '',
                'date': delivery_note.date.strftime('%d/%m/%Y') if delivery_note.date else '',
            })
        res = {
            'delivery_notes': delivery_note_list,
            'result': 'ok',
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class QuotationDeliverynoteSales(View):

    def get(self, request, *args, **kwargs):

        current_date = dt.datetime.now().date()

        inv_number = SalesInvoice.objects.aggregate(Max('id'))['id__max']
        
        if not inv_number:
            inv_number = 1
        else:
            inv_number = inv_number + 1
        invoice_number = 'INV' + str(inv_number)

        return render(request, 'sales/QNDN_sales_entry.html',{
            'sales_invoice_number': invoice_number,
            'current_date': current_date.strftime('%d/%m/%Y'),
        })

    def post(self, request, *args, **kwargs):

        sales_dict = ast.literal_eval(request.POST['sales'])
        delivery_note = DeliveryNote.objects.get(delivery_note_number=sales_dict['delivery_no'])
        sales = Sales.objects.create(sales_invoice_number=sales_dict['sales_invoice_number'], delivery_note=delivery_note)
        sales.sales_invoice_number = sales_dict['sales_invoice_number']
        sales.sales_invoice_date = datetime.strptime(sales_dict['sales_invoice_date'], '%d/%m/%Y')

        customer = Customer.objects.get(customer_name = sales_dict['customer'])
        not_completed_selling = []
        for item_data in sales_dict['sales_items']:
            for d_item in delivery_note.deliverynoteitem_set.all():
                if d_item.item.id == item_data['id']:
                    print d_item.quantity_sold, item_data['qty']
                    if int(d_item.quantity_sold) != int(item_data['qty_sold']):
                        d_item.quantity_sold = d_item.quantity_sold + int(item_data['qty'])
                        d_item.save()
                    if d_item.total_quantity == d_item.quantity_sold:
                        d_item.is_completed = True
                    if not d_item.is_completed:
                        not_completed_selling.append(d_item.id)
        if len(not_completed_selling) == 0:
            delivery_note.is_pending = False
            delivery_note.save()

        sales.lpo_number = sales_dict['lpo_number']

        sales.save()

        salesman = User.objects.get(first_name=sales_dict['salesman']) 
        
        sales.discount = sales_dict['net_discount']
        sales.round_off = sales_dict['roundoff']
        sales.net_amount = sales_dict['net_total']
        sales.grant_total = sales_dict['grant_total']
        sales.salesman = salesman
        sales.payment_mode = sales_dict['payment_mode']
        if sales_dict['payment_mode'] == 'card':
            sales.card_number = sales_dict['card_number']
            sales.bank_name = sales_dict['bank_name']
        sales.save()
        sales_items = sales_dict['sales_items']
        for sales_item in sales_items:
           
            item = InventoryItem.objects.get(code=sales_item['item_code'])
                    
            s_item, item_created = SalesItem.objects.get_or_create(item=item, sales=sales)
            s_item.sales = sales
            s_item.item = item
            s_item.quantity_sold = sales_item['qty']
            s_item.discount_given = sales_item['disc_given']
            s_item.net_amount = sales_item['net_amount']
            s_item.selling_price = sales_item['unit_price']
            # unit price is actually the selling price
            s_item.save()


        # Creating sales invoice 

        sales_invoice, created = SalesInvoice.objects.get_or_create(sales=sales)
        
        if sales_dict['delivery_no'] is not 0:
            delivery_note.processed = True
            delivery_note.save()
            sales.delivery_note = delivery_note
            sales_invoice.delivery_note = delivery_note
        
        sales_invoice.date = datetime.strptime(sales_dict['sales_invoice_date'], '%d/%m/%Y')
        sales_invoice.invoice_no = sales_dict['sales_invoice_number']
        sales_invoice.save()

                    
        res = {
            'result': 'Ok',
            'sales_invoice_id': sales_invoice.id,
        }
        response = simplejson.dumps(res)
        status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")
class CreateSalesInvoicePDF(View):

    def get(self, request, *args, **kwargs):

        sales_invoice_id = kwargs['sales_invoice_id']
        sales_invoice = SalesInvoice.objects.get(id=sales_invoice_id)
        sales = sales_invoice.sales

        response = HttpResponse(content_type='application/pdf')
        p = canvas.Canvas(response, pagesize=(1000, 1200))

        status_code = 200

        y = 1100
        style = [
            ('FONTSIZE', (0,0), (-1, -1), 20),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
        ]

        new_style = [
            ('FONTSIZE', (0,0), (-1, -1), 30),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica') 
        ]

        para_style = ParagraphStyle('fancy')
        para_style.fontSize = 20
        para_style.fontName = 'Helvetica'
        para = Paragraph('<b> INVOICE </b>', para_style)

        data =[['', sales_invoice.date.strftime('%d-%m-%Y'), para , sales_invoice.invoice_no]]
        
        table = Table(data, colWidths=[30, 360, 420, 100], rowHeights=50, style=style) 
        # table.setStyle(TableStyle([
        #                ('FONTSIZE', (2,0), (2,0), 30),
        #                ]))     
        table.wrapOn(p, 200, 400)
        table.drawOn(p,50, 975)

        quotation = sales_invoice.quotation

        customer_name = ''
        if sales_invoice.customer:
            customer_name = sales_invoice.customer.customer_name

        data=[['', customer_name, sales_invoice.sales.lpo_number if sales_invoice.sales else '' ]]

        table = Table(data, colWidths=[30, 540, 60], rowHeights=30, style = style)      
        table.wrapOn(p, 200, 400)
        table.drawOn(p, 50, 935)

        data=[['', '', sales_invoice.date.strftime('%d-%m-%Y')]]

        table = Table(data, colWidths=[450, 120, 70], rowHeights=50, style = style)      

        table.wrapOn(p, 200, 400)
        table.drawOn(p,50, 910)

        if sales_invoice.quotation or sales_invoice.delivery_note:            
            data=[['', '', sales_invoice.delivery_note.delivery_note_number if sales_invoice.delivery_note else sales_invoice.quotation.reference_id]]

            table = Table(data, colWidths=[450, 120, 70], rowHeights=40, style = style)      
            table.wrapOn(p, 200, 400)
            table.drawOn(p,50, 880)

        y = 790

        i = 0
        i = i + 1

        TWOPLACES = Decimal(10) ** -2
        total_amount = 0
        for s_item in sales.salesitem_set.all():
                   
            y = y-30
            if y <= 270:
                y = 790
                p.showPage()
            
            item_price = s_item.selling_price
            total_amount = total_amount + (item_price*s_item.quantity_sold)
            
            data1=[[i, s_item.item.code, s_item.item.name, s_item.quantity_sold, s_item.item.uom.uom, s_item.selling_price.quantize(TWOPLACES), s_item.net_amount]]
            table = Table(data1, colWidths=[50, 100, 440, 80, 90, 100, 50], rowHeights=40, style=style)
            table.wrapOn(p, 200, 400)
            table.drawOn(p,10,y)
            i = i + 1
        y = 600
        if y <= 270:
            y = 800
            p.showPage()
        total_amount = sales.net_amount
        try:
            total_amount = total_amount.quantize(TWOPLACES)
        except:
            total_amount = total_amount
        total_amount_in_words = num2words(total_amount).title() + ' Only'
       
        data=[[total_amount_in_words, total_amount]]  

        table = Table(data, colWidths=[700, 50], rowHeights=40, style = style)      

        table.wrapOn(p, 200, 100)
        table.drawOn(p, 200, 10)

        p.showPage()
        p.save()
        return response

class ReceiptVoucherCreation(View):

    def get(self, request, *args, **kwargs):

        current_date = dt.datetime.now().date()
        voucher_no = ReceiptVoucher.objects.aggregate(Max('id'))['id__max']
        
        if not voucher_no:
            voucher_no = 1
        else:
            voucher_no = voucher_no + 1
        voucher_no = 'RV' + str(voucher_no)

        return render(request, 'sales/create_receipt_voucher.html',{
            'current_date': current_date.strftime('%d/%m/%Y'),
            'voucher_no': voucher_no,
        })

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            receiptvoucher = ast.literal_eval(request.POST['receiptvoucher'])
            customer = Customer.objects.get(customer_name=receiptvoucher['customer'])
            sales_invoice_obj = SalesInvoice.objects.get(invoice_no=receiptvoucher['invoice_no'])
            receipt_voucher, created = ReceiptVoucher.objects.create(sales_invoice=sales_invoice_obj, customer=customer)
            # sales_invoice_obj.is_processed = True
            # sales_invoice_obj.save()
            receipt_voucher.date = datetime.strptime(receiptvoucher['date'], '%d/%m/%Y')
            
            receipt_voucher.total_amount = receiptvoucher['amount']
            receipt_voucher.paid_amount = receiptvoucher['paid_amount']
            receipt_voucher.receipt_voucher_no = receiptvoucher['voucher_no']
            receipt_voucher.payment_mode = receiptvoucher['payment_mode']
            receipt_voucher.bank = receiptvoucher['bank_name']
            receipt_voucher.cheque_no = receiptvoucher['cheque_no']
            if receiptvoucher['cheque_date']:   
                receipt_voucher.dated = datetime.strptime(receiptvoucher['cheque_date'], '%d/%m/%Y')
            receipt_voucher.save()
            customer_account, created = CustomerAccount.objects.get_or_create(customer=customer, invoice_no=sales_invoice_obj )
 
            if created:
                customer_account.total_amount = receiptvoucher['amount']
                customer_account.paid = receiptvoucher['paid_amount']
            else:
                customer_account.paid = customer_account.paid + float(receiptvoucher['paid_amount'])
            customer_account.save()
            customer_account.balance = float(customer_account.total_amount) - float(customer_account.paid)
            customer_account.save()
            if customer_account.balance == 0:
                customer_account.is_complted = True
                customer_account.save()
           
            res = {
                'result': 'OK',
                'receiptvoucher_id': receipt_voucher.id,
            }

            response = simplejson.dumps(res)

            return HttpResponse(response, status=200, mimetype='application/json')         

       
class InvoiceDetails(View):


    def get(self, request, *args, **kwargs):


        invoice_no = request.GET.get('invoice_no', '')
        sales_invoice_details = SalesInvoice.objects.filter(invoice_no__istartswith=invoice_no, is_processed=False)
        invoices = SalesInvoice.objects.filter(invoice_no__istartswith=invoice_no)
        ctx_invoice_details = []
        ctx_sales_invoices = []
        ctx_sales_item  = []
        if sales_invoice_details.count() > 0:
            for sales_invoice in sales_invoice_details:
                ctx_invoice_details.append({
                    'invoice_no': sales_invoice.invoice_no,
                    'dated': sales_invoice.date.strftime('%d-%m-%Y'),
                    'customer': sales_invoice.customer.customer_name,
                    'amount': sales_invoice.sales.quotation.net_total if sales_invoice.sales.quotation else sales_invoice.sales.net_amount
                })
        i = 0
        i = i + 1
        if invoices.count() > 0:
            for sales_invoice in invoices:
                net_amount = 0
                for sale in sales_invoice.sales.salesitem_set.all():
                    net_amount = float(sale.selling_price) * int(sale.quantity_sold)
                    ctx_sales_item.append({
                        'sl_no': i,
                        'item_name': sale.item.name,
                        'item_code': sale.item.code,
                        'barcode': sale.item.barcode,
                        'item_description': sale.item.description,
                        'qty_sold': sale.quantity_sold,
                        'tax': sale.item.tax,
                        'uom': sale.item.uom.uom,
                        'current_stock': sale.item.inventory_set.all()[0].quantity if sale.item.inventory_set.count() > 0  else 0 ,
                        'selling_price': sale.selling_price,
                        'discount_permit': sale.item.inventory_set.all()[0].discount_permit_percentage if sale.item.inventory_set.count() > 0 else 0,
                        'net_amount': net_amount,
                        'discount_given': sale.discount_given,

                    }) 
                    net_amount = 0
                    i = i + 1
                ctx_sales_invoices.append({
                    'invoice_no': sales_invoice.invoice_no,
                    'reference_no': sales_invoice.quotation.reference_id if sales_invoice.quotation else 0,
                    'date': sales_invoice.date.strftime('%d/%m/%Y'),
                    'customer': sales_invoice.customer.customer_name,
                    'delivery_note_no': sales_invoice.delivery_note.delivery_note_number if sales_invoice.delivery_note else 0,
                    'lpo_number': sales_invoice.delivery_note.lpo_number if sales_invoice.delivery_note else sales_invoice.sales.lpo_number,
                    'items': ctx_sales_item,
                    'salesman': sales_invoice.sales.salesman.user.first_name if sales_invoice.sales.salesman else '',
                    'payment_mode': sales_invoice.sales.payment_mode,
                    'card_number': sales_invoice.sales.card_number,
                    'bank_name': sales_invoice.sales.bank_name,
                    'net_total': sales_invoice.sales.net_amount,
                    'round_off': sales_invoice.sales.round_off if sales_invoice.sales.round_off else 0,
                    'grant_total': sales_invoice.sales.grant_total,
                    'discount': sales_invoice.sales.discount,
                })
                ctx_sales_item = []
        res = {
            'result': 'ok',
            'invoice_details': ctx_invoice_details, 
            'sales_invoices': ctx_sales_invoices,
        }

        response = simplejson.dumps(res)

        return HttpResponse(response, status=200, mimetype='application/json')

class PrintReceiptVoucher(View):

    def get(self, request, *args, **kwargs):

        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename=ReceiptVoucher.pdf'
        p = canvas.Canvas(response, pagesize=(1000, 1000))

        status_code = 200

        y = 850

        receipt_voucher = ReceiptVoucher.objects.get(id=kwargs['receipt_voucher_id'])

        p.setFont("Helvetica-Bold", 15)
        p.drawString(30, 950, "SUNLIGHT STATIONARY")
        p.setFont("Helvetica", 10)
        p.drawString(30, 930, "P.O.Box : 48296")
        p.drawString(30, 910, "Behind Russian Embassy")
        p.drawString(30, 890, "Ziyani, Abu Dhabi, U.A.E.")
        p.drawString(30, 870, "Tel. : +971-2-6763571")
        p.drawString(30, 850, "Fax : +971-2-6763581")
        p.drawString(30, 830, "E-mail : sunlight.stationary@yahoo.com")

        try:
            owner_company = OwnerCompany.objects.latest('id')
            if owner_company.logo:
                path = settings.PROJECT_ROOT.replace("\\", "/")+"/media/"+owner_company.logo.name
                p.drawImage(path, 400, 810, width=20*cm, preserveAspectRatio=True)
        except:
            pass  

        p.line(30,790,970,790)
        p.setFont("Helvetica", 20)
        p.drawString(440, 740, "Receipt Voucher")
        p.drawString(840, 740, 'No.')
        p.setFont("Helvetica", 15)
        p.drawString(880, 740, str(receipt_voucher.receipt_voucher_no))

        p.setFont("Times-BoldItalic", 15)
        p.drawString(30, 700, "Amount")

        data=[[receipt_voucher.sum_of,'']]

        table = Table(data, colWidths=[150,50], rowHeights=30) 

        table.setStyle(TableStyle([
           ('BOX', (0,0), (-1,-1), 0.25, colors.black),
           ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),  
           ('FONTSIZE', (0,0), (-1, -1), 14),    
           ('FONTNAME', (0,0), (-1,-1), 'Times-BoldItalic')                     
           ]))     

        table.wrapOn(p, 200, 400)
        table.drawOn(p,120, 700)

        p.drawString(840, 700, "Date")
        p.drawString(880, 705, receipt_voucher.date.strftime('%d/%m/%Y'))
        p.drawString(870, 700, "........................")

        p.drawString(30, 660, "Received from Mr./M/s.")
        p.drawString(210, 665,receipt_voucher.customer.customer_name)
        p.drawString(180, 660, "...............................................................................................................................................................................................................")

        p.drawString(30, 620, "The Sum of")
        p.drawString(150, 625,str(receipt_voucher.sum_of))
        p.drawString(110, 620, "..................................................................................................................................................................................................................................")

        p.drawString(30, 580, "On Settlement of")
        p.drawString(180, 585,str(receipt_voucher.sales_invoice.invoice_no))
        p.drawString(140, 580, "..........................................................................................................................................................................................................................")

        p.drawString(30, 540, "Cheque No")
        if receipt_voucher.cheque_no:
            p.drawString(110, 545,receipt_voucher.cheque_no)
        p.drawString(100, 540, " ..........................................................................................")

        p.drawString(450, 540, "Cash")
        if receipt_voucher.sum_of:
            p.drawString(500, 545,str(receipt_voucher.sum_of))
        p.drawString(490, 540, ".............................................................................................................................")

        p.drawString(30, 500, "Bank")
        if receipt_voucher.bank:
            p.drawString(75, 505, receipt_voucher.bank)
        p.drawString(65, 500, " ...................................................................................................")

        p.drawString(450, 500, "Dated")
        if receipt_voucher.dated:
            p.drawString(500, 505,receipt_voucher.dated.strftime('%d/%m/%Y'))
        p.drawString(490, 500, " ............................................................................................................................")

        p.drawString(30, 420, "Accountant")
        p.drawString(100, 420, " .....................................................")


        p.drawString(650, 420, "Receiver's Sign")
        p.drawString(750, 420, " ......................................................")


        p.showPage()
        p.save()
        
        return response

class LatestSalesDetails(View):

    def get(self, request, *args, **kwargs):

        customer_name = request.GET.get('customer', '')
        item_name = request.GET.get('item_name', '')
        sales_details = (SalesItem.objects.filter(item__name=item_name, sales__customer__customer_name=customer_name).order_by('-id'))[:3]
        
        ctx_sales_details = []
        for sale_item in sales_details:
            ctx_sales_details.append({
                'selling_price': sale_item.selling_price,
                'discount_given': sale_item.discount_given,
                'qty_sold': sale_item.quantity_sold,
                'date': sale_item.sales.sales_invoice_date.strftime('%d/%m/%Y'),
            })
        res = {
            'result': 'ok',
            'latest_sales_details': ctx_sales_details 
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DirectDeliveryNote(View):

    def get(self, request, *args, **kwargs):

        current_date = dt.datetime.now().date()

        ref_number = DeliveryNote.objects.aggregate(Max('id'))['id__max']
        
        if not ref_number:
            ref_number = 1
        else:
            ref_number = ref_number + 1
        delivery_no = 'DN' + str(ref_number)

        context = {
            'current_date': current_date.strftime('%d-%m-%Y'),
            'delivery_no': delivery_no,
        }

        return render(request, 'sales/direct_delivery_note.html', context)

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            delivery_note_details = ast.literal_eval(request.POST['delivery_note'])
            salesman = User.objects.get(first_name=delivery_note_details['salesman'])
            delivery_note = DeliveryNote.objects.create(salesman=salesman)
            delivery_note.date = datetime.strptime(delivery_note_details['date'], '%d-%m-%Y')
            delivery_note.lpo_number = delivery_note_details['lpo_no']
            delivery_note.delivery_note_number = delivery_note_details['delivery_note_no']
            delivery_note.net_total = delivery_note_details['net_total']
            delivery_note.save()

            delivery_note_data_items = delivery_note_details['sales_items']
            for delivery_note_item in delivery_note_data_items:
                item, created = InventoryItem.objects.get_or_create(code=delivery_note_item['item_code'])
                delivery_note_item_obj, item_created = DeliveryNoteItem.objects.get_or_create(item=item, delivery_note=delivery_note)
                item.quantity = item.quantity - int(delivery_note_item['qty_sold'])
                item.save()
                delivery_note_item_obj.net_amount = float(delivery_note_item['net_amount'])
                delivery_note_item_obj.total_quantity = int(delivery_note_item['qty_sold'])
                delivery_note_item_obj.save()

            res = {
                'result': 'ok',
            }

            response = simplejson.dumps(res)

            return HttpResponse(response, status=200, mimetype='application/json')

class EditSalesInvoice(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'sales/edit_sales_invoice.html', {})

    def post(self, request, *args, **kwargs):
        sales_invoice_details = ast.literal_eval(request.POST['invoice'])
        sales_invoice = SalesInvoice.objects.get(invoice_no = sales_invoice_details['invoice_no'])
        sales = sales_invoice.sales
        stored_item_names = []
        for s_item in sales.salesitem_set.all():
            stored_item_names.append(s_item.item.name)

        # Editing and Removing the Existing details of the sales item
        for s_item in sales.salesitem_set.all():
            s_item_names = []
            for item_data in sales_invoice_details['sales_items']:
                s_item_names.append(item_data['item_name'])

            # Removing the sales item object that is not in inputed sales items list
            if s_item.item.name not in s_item_names:
                item = s_item.item 
                inventory, created = Inventory.objects.get_or_create(item=item)
                inventory.quantity = inventory.quantity + int(s_item.quantity_sold)
                inventory.save()
                s_item.delete()
            else:
                for item_data in sales_invoice_details['sales_items']:
                    item = Item.objects.get(code=item_data['item_code'])
                    s_item, item_created = SalesItem.objects.get_or_create(item=item, sales=sales)
                    inventory, created = Inventory.objects.get_or_create(item=item)
                    if item_created:

                        inventory.quantity = inventory.quantity - int(item_data['qty_sold'])
                    else:
                        inventory.quantity = inventory.quantity + s_item.quantity_sold - int(item_data['qty_sold'])      

                    inventory.save()
                    s_item.sales = sales
                    s_item.item = item
                    s_item.quantity_sold = item_data['qty_sold']
                    s_item.discount_given = item_data['disc_given']
                    s_item.net_amount = item_data['net_amount']
                    s_item.selling_price = item_data['unit_price']
                    s_item.save()

        # Create new sales item for the newly added item
        for item_data in sales_invoice_details['sales_items']:

            if item_data['item_name'] not in stored_item_names:
                item = Item.objects.get(code=item_data['item_code'])
                s_item, item_created = SalesItem.objects.get_or_create(item=item, sales=sales)
                inventory, created = Inventory.objects.get_or_create(item=item)
                if item_created:

                    inventory.quantity = inventory.quantity - int(item_data['qty_sold'])
                else:
                    inventory.quantity = inventory.quantity + s_item.quantity_sold - int(item_data['qty_sold'])      

                inventory.save()
                s_item.sales = sales
                s_item.item = item
                s_item.quantity_sold = item_data['qty_sold']
                s_item.discount_given = item_data['disc_given']
                s_item.net_amount = item_data['net_amount']
                s_item.selling_price = item_data['unit_price']
                s_item.save()
        if sales.net_amount != sales_invoice_details['net_total']:
            sales.net_amount = sales_invoice_details['net_total']
        if sales.round_off != sales_invoice_details['roundoff']:
            sales.round_off = sales_invoice_details['roundoff']
        if sales.grant_total != sales_invoice_details['grant_total']:
            sales.grant_total = sales_invoice_details['grant_total']
        if sales.discount != sales_invoice_details['net_discount']:
            sales.discount != sales_invoice_details['net_discount']

        sales.save()

        res = {
            'result': 'ok',
            'sales_invoice_id': sales_invoice.id
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class EditQuotation(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'sales/edit_quotation.html', {})

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            quotation_data = ast.literal_eval(request.POST['quotation'])
            quotation, quotation_created = Quotation.objects.get_or_create(reference_id=quotation_data['reference_no'])
                      
            quotation.net_total = quotation_data['total_amount']
            quotation.save()
            customer = Customer.objects.get(customer_name=quotation_data['customer'])
            quotation.to = customer
            quotation.save()

            stored_item_names = []
            for q_item in quotation.quotationitem_set.all():
                stored_item_names.append(q_item.item.name)


            # Editing and Removing the Existing details of the Quotation item
            for q_item in quotation.quotationitem_set.all():
                q_item_names = []
                for item_data in quotation_data['sales_items']:
                    q_item_names.append(item_data['item_name'])

                # Removing the qutation item object that is not in inputed qutation items list

                if q_item.item.name not in q_item_names:
                    item = q_item.item 
                    inventory, created = Inventory.objects.get_or_create(item=item)
                    inventory.quantity = inventory.quantity + int(q_item.quantity_sold)
                    inventory.save()
                    q_item.delete()
                else:
                    for item_data in quotation_data['sales_items']:
                        item = Item.objects.get(code=item_data['item_code'])
                        q_item, item_created = QuotationItem.objects.get_or_create(item=item, quotation=quotation)
                        inventory, created = Inventory.objects.get_or_create(item=item)
                        if item_created:

                            inventory.quantity = inventory.quantity - int(item_data['qty_sold'])
                        else:
                            inventory.quantity = inventory.quantity + q_item.quantity_sold - int(item_data['qty_sold'])      

                        inventory.save()
                        q_item.net_amount = float(item_data['net_amount'])
                        q_item.quantity_sold = int(item_data['qty_sold'])
                        q_item.selling_price = float(item_data['unit_price'])
                        q_item.save()

            # Create new sales item for the newly added item
            for item_data in quotation_data['sales_items']:

                if item_data['item_name'] not in stored_item_names:
                    item = Item.objects.get(code=item_data['item_code'])
                    q_item, item_created = QuotationItem.objects.get_or_create(item=item, quotation=quotation)
                    inventory, created = Inventory.objects.get_or_create(item=item)
                    if item_created:

                        inventory.quantity = inventory.quantity - int(item_data['qty_sold'])
                    else:
                        inventory.quantity = inventory.quantity + q_item.quantity_sold - int(item_data['qty_sold'])      

                    inventory.save()
                    q_item.quantity_sold = item_data['qty_sold']
                    q_item.net_amount = item_data['net_amount']
                    q_item.selling_price = item_data['unit_price']
                    q_item.save()
        
            res = {
                'result': 'OK',
                'quotation_id': quotation.id,
            }

            response = simplejson.dumps(res)

            return HttpResponse(response, status=200, mimetype='application/json')


class EditDeliveryNote(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'sales/edit_delivery_note.html', {})

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            delivery_note_details = ast.literal_eval(request.POST['delivery_note'])
            
            q_stored_item_names = []
            d_stored_item_names = []
            stored_item_names = []
            delivery_note, created = DeliveryNote.objects.get_or_create(delivery_note_number=delivery_note_details['delivery_note_no'])
            delivery_note.net_total = delivery_note_details['net_total']
            delivery_note.save()

            if delivery_note.quotation:
                print "in if"
                quotation = delivery_note.quotation
                print quotation
                for d_item in delivery_note.quotation.quotationitem_set.all():
                    q_stored_item_names.append(d_item.item.name)
                
                for q_item in delivery_note.quotation.quotationitem_set.all():
                    q_item_names = []
                    for item_data in delivery_note_details['sales_items']:
                        q_item_names.append(item_data['item_name'])

                    # Removing the qutation item object that is not in inputed delivery note items list

                    if q_item.item.name not in q_item_names:
                        item = q_item.item 
                        inventory, created = Inventory.objects.get_or_create(item=item)
                        inventory.quantity = inventory.quantity + int(q_item.quantity_sold)
                        inventory.save()
                        q_item.delete()
                    else:
                        for item_data in delivery_note_details['sales_items']:
                            item = Item.objects.get(code=item_data['item_code'])
                            quotation_item = QuotationItem.objects.filter(item=item, quotation=quotation)
                            if quotation_item.count() > 0:
                                q_item = quotation_item[0]
                                inventory, created = Inventory.objects.get_or_create(item=item)
                                inventory.quantity = inventory.quantity + q_item.quantity_sold - int(item_data['qty_sold'])      

                                inventory.save()
                                q_item.net_amount = float(item_data['net_amount'])
                                q_item.quantity_sold = int(item_data['qty_sold'])
                                q_item.selling_price = float(item_data['unit_price'])
                                q_item.save()
            
            if delivery_note.deliverynoteitem_set.all().count() > 0:

                for d_item in delivery_note.deliverynoteitem_set.all():
                    d_stored_item_names.append(d_item.item.name)
                
                for d_item in delivery_note.deliverynoteitem_set.all():
                    d_item_names = []
                    for item_data in delivery_note_details['sales_items']:
                        d_item_names.append(item_data['item_name'])

                    # Removing the delivery note item object that is not in inputed delivery note items list

                    if d_item.item.name not in d_item_names:
                        item = d_item.item 
                        inventory, created = Inventory.objects.get_or_create(item=item)
                        inventory.quantity = inventory.quantity + int(d_item.quantity_sold)
                        inventory.save()
                        d_item.delete()
                    else:
                        for item_data in delivery_note_details['sales_items']:
                            item = Item.objects.get(code=item_data['item_code'])
                            delivery_note_item = DeliveryNoteItem.objects.filter(item=item, delivery_note=delivery_note)
                            if delivery_note_item.count() > 0:
                                d_item = delivery_note_item[0]
                                inventory, created = Inventory.objects.get_or_create(item=item)
                                inventory.quantity = inventory.quantity + d_item.quantity_sold - int(item_data['qty_sold'])      

                                inventory.save()
                                d_item.net_amount = float(item_data['net_amount'])
                                d_item.quantity_sold = int(item_data['qty_sold'])
                                d_item.selling_price = float(item_data['unit_price'])
                                d_item.save()

            
            stored_item_names = []
            for item_data in delivery_note_details['sales_items']:
                if item_data['item_name'] not in q_stored_item_names:
                    if item_data['item_name'] not in d_stored_item_names:
                        stored_item_names.append(item_data['item_name'])

            for item_data in delivery_note_details['sales_items']:
                if item_data['item_name'] in stored_item_names:
                    item = Item.objects.get(code=item_data['item_code'])
                    d_item, item_created = DeliveryNoteItem.objects.get_or_create(item=item, delivery_note=delivery_note)
                    inventory, created = Inventory.objects.get_or_create(item=item)
                    if item_created:
                        inventory.quantity = inventory.quantity - int(item_data['qty_sold'])
                    inventory.save()
                    d_item.quantity_sold = item_data['qty_sold']
                    d_item.net_amount = item_data['net_amount']
                    d_item.selling_price = item_data['unit_price']
                    d_item.save()


            res = {
                'result': 'ok',
                'delivery_note_id': delivery_note.id
            }
            response = simplejson.dumps(res)

            return HttpResponse(response, status=200, mimetype='application/json')



    


