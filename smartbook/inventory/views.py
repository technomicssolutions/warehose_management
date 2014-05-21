import sys
import simplejson

from django.db import IntegrityError

from django.contrib.auth.views import password_reset
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import ast

from inventory.models import *

class ItemAdd(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'inventory/new_item.html',{})

    def post(self, request, *args, **kwargs):

        if request.is_ajax():
            try:
                uom = UnitOfMeasure.objects.get(uom = request.POST['uom'])
                brand = Brand.objects.get(brand = request.POST['brand'])
                item, created = InventoryItem.objects.get_or_create(code=request.POST['code'], brand=brand, uom=uom, name=request.POST['name'])
                if not created:
                    res = {
                        'result': 'error',
                        'message': 'Item already existing'
                    }
                    status_code = 500
                else:
                    item.name=request.POST['name']
                    item.description=request.POST['description']
                    item.barcode=request.POST['barcode']
                    item.tax=request.POST['tax']
                    item.save()
                    res = {
                        'result': 'ok',
                    }  
                    status_code = 200 
                
            except Exception as ex:
                res = {
                        'result': 'error',
                        'message': 'Item already existing'
                    }
                status_code = 500

            response = simplejson.dumps(res)
            return HttpResponse(response, status = status_code, mimetype="application/json")


class ItemList(View):
    
    def get(self, request, *args, **kwargs):
        
            if request.is_ajax():
                try:
                    item_code = request.GET.get('item_code', '')
                    item_name = request.GET.get('item_name', '')
                    barcode = request.GET.get('barcode', '')
                    brand =  request.GET.get('brand', '')
                    if brand:
                        brand = Brand.objects.get(brand=brand)
                    items = []
                    if item_code:
                        if brand:
                            items = InventoryItem.objects.filter(code__istartswith=item_code, brand=brand)
                        else:
                            items = InventoryItem.objects.filter(code__istartswith=item_code)
                    elif item_name:
                        if brand:
                            items = InventoryItem.objects.filter(name__istartswith=item_name, brand=brand)
                        else:
                            items = InventoryItem.objects.filter(name__istartswith=item_name)
                    elif barcode:
                        if brand:
                            items = InventoryItem.objects.filter(barcode__istartswith=barcode, brand=brand)
                        else:
                            items = InventoryItem.objects.filter(barcode__istartswith=barcode)
                    else:
                        items = InventoryItem.objects.all()
                    item_list = []
                    i = 0
                    i = i + 1
                    for item in items:

                        item_list.append({
                            'sl_no': i,
                            'item_code': item.code,
                            'item_name': item.name,
                            'barcode': item.barcode,
                            'brand': item.brand.brand,
                            'description': item.description,
                            'tax': item.tax,
                            'uom': item.uom.uom,
                            'current_stock': item.quantity if item.quantity  else 0 ,
                            'selling_price': item.selling_price if item.selling_price else 0 ,
                            'discount_permit': item.discount_permit_percentage if item.discount_permit_percentage else 0,
                        })
                        i = i + 1

                    res = {
                        'items': item_list,
                    }
                    response = simplejson.dumps(res)

                except Exception as ex:
                    response = simplejson.dumps({'result': 'error', 'error': str(ex)})
                    status_code = 500
                status_code = 200
                return HttpResponse(response, status = status_code, mimetype = 'application/json')
            else:
                items = InventoryItem.objects.all().order_by('code')
                ctx = {
                    'items': items
                }
                return render(request, 'inventory/items_list.html',ctx)

class StockView(View):
    def get(self, request, *args, **kwargs):
        inventory = InventoryItem.objects.all().order_by('code')
        ctx = {
            'inventory': inventory
        }
        return render(request, 'inventory/stock.html',ctx)

class BrandList(View):

    def get(self, request, *args, **kwargs):

        ctx_brand = []
        brands = Brand.objects.all()
        if len(brands) > 0:
            for brand in brands:
                ctx_brand.append({
                    'brand_name': brand.brand,
                })
        res = {
            'brands': ctx_brand,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status = 200, mimetype="application/json")

class AddBrand(View):

    def post(self, request, *args, **kwargs):

        if len(request.POST['brand_name']) > 0 and not request.POST['brand_name'].isspace():
            brand, created = Brand.objects.get_or_create(brand=request.POST['brand_name']) 
            if not created:
                res = {
                    'result': 'error',
                    'message': 'Brand name Already exists'
                }
            else:
                res = {
                    'result': 'ok',
                    'brand': brand.brand
                }
        else:
            res = {
                 'result': 'error',
                 'message': 'Brand name Cannot be null'
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class UomList(View):

    def get(self, request, *args, **kwargs):

        ctx_uom = []
        uoms = UnitOfMeasure.objects.all()
        if len(uoms) > 0:
            for uom in uoms:
                ctx_uom.append({
                    'uom_name': uom.uom,
                })
        res = {
            'uoms': ctx_uom,
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status = 200, mimetype="application/json")

class AddUom(View):

    def post(self, request, *args, **kwargs):

        if len(request.POST['uom_name']) > 0 and not request.POST['uom_name'].isspace():
            uom, created = UnitOfMeasure.objects.get_or_create(uom=request.POST['uom_name']) 
            if not created:
                res = {
                    'result': 'error',
                    'message': 'Uom Already exists'
                }
            else:
                res = {
                    'result': 'ok',
                    'brand': uom.uom
                }
        else:
            res = {
                 'result': 'error',
                 'message': 'Uom Cannot be null'
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class OpeningStockView(View):

    def get(self, request, *args, **kwargs):
        stock_items = OpeningStock.objects.all()
        return render(request, 'inventory/opening_stock_view.html', {
            'stock_items': stock_items
        })

class AddOpeningStock(View):

    def get(self, request, *args, **kwargs):
        items = InventoryItem.objects.all()
        return render(request, 'inventory/opening_stock.html', {
            'items': items
        })

    def post(self, request, *args, **kwargs):

        item , created= InventoryItem.objects.get_or_create(code=request.POST['item'])
        opening_stock = OpeningStock()
        opening_stock.item = item
        opening_stock.quantity = request.POST['quantity']
        opening_stock.unit_price = request.POST['unit_price']
        opening_stock.selling_price = request.POST['selling_price']
        opening_stock.discount_permit_percentage = request.POST['discount_permit_percent']
        opening_stock.discount_permit_amount = request.POST['discount_permit_amount']
        opening_stock.save()
        if created:
            item.quantity = int(request.POST['quantity'])
        else:
            item.quantity = item.quantity + int(request.POST['quantity'])
        item.unit_price = request.POST['unit_price']
        item.selling_price = request.POST['selling_price']
        item.discount_permit_amount = request.POST['discount_permit_amount']
        item.discount_permit_percentage = request.POST['discount_permit_percent']
        item.save()

        items = InventoryItem.objects.all()
        return render(request, 'inventory/opening_stock.html', {
            'items': items
        })

class EditStockView(View):
    def get(self, request, *args, **kwargs):
        stock = InventoryItem.objects.get(code=request.GET['item_code'])
        if request.is_ajax():
            res = {
                 'stock': {
                    'item': stock.code,
                    'quantity': stock.quantity,
                    'unit_price': stock.unit_price,
                    'selling_price': stock.selling_price,
                    'discount_permit_amount': stock.discount_permit_amount,
                    'discount_permit_percent': stock.discount_permit_percentage
                 },
            }
            response = simplejson.dumps(res)    
            return HttpResponse(response, status=200, mimetype='application/json')
        return render(request, 'inventory/edit_stock.html', {
            'stock': stock
        })

    def post(self, request, *args, **kwargs):

        inventory = InventoryItem.objects.get(code=request.POST['item_code'])
        inventory.unit_price = request.POST['unit_price']
        inventory.selling_price = request.POST['selling_price']
        inventory.discount_permit_amount = request.POST['discount_permit_amount']
        inventory.discount_permit_percentage = request.POST['discount_permit_percent']
        inventory.save()
        return HttpResponseRedirect(reverse('stock'))

class EditItem(View):

    def get(self, request, *args, **kwargs):
        item_id = kwargs['item_id']
        context = {
            'item_id': item_id,
        }
        ctx_item_data = []
        if request.is_ajax():
            try:
                item = InventoryItem.objects.get(id = item_id)
                ctx_item_data.append({
                    'name': item.name if item.name else '',
                    'code': item.code if item.code else '',
                    'uom': item.uom.uom if item.uom else '',
                    'brand': item.brand.brand if item.brand else '',
                    'barcode': item.barcode if item.barcode else '',
                    'tax': item.tax if item.tax else 0,
                })
                res = {
                    'result': 'error',
                    'item': ctx_item_data,
                }
                status = 200
            except Exception as ex:
                print "Exception == ", str(ex)
                ctx_item_data = []
                res = {
                    'result': 'error',
                    'item': ctx_item_data,
                }
                status = 500
            response = simplejson.dumps(res)
            return HttpResponse(response, status=status, mimetype='application/json')

        return render(request, 'inventory/edit_item.html', context)

    def post(self, request, *args, **kwargs):

        item_id = kwargs['item_id']

        item = InventoryItem.objects.get(id = item_id)
        item_data = ast.literal_eval(request.POST['item'])
        try:
            item.name = item_data['name']
            uom = UnitOfMeasure.objects.get(uom=item_data['uom'])
            brand = Brand.objects.get(brand=item_data['brand'])
            item.uom = uom
            item.brand = brand
            item.barcode = item_data['barcode']
            item.tax = item_data['tax']
            item.save()
            res = {
                'result': 'ok',
            }
            status = 200
        except Exception as Ex:
            print "Exception == ", str(Ex)
            res = {
                'result': 'error',
                'message': 'Item with this name is already existing'
            }
            status = 500
        response = simplejson.dumps(res)
        return HttpResponse(response, status=status, mimetype='application/json')