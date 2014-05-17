import sys
import ast
import simplejson
import datetime as dt
from datetime import datetime

from django.contrib.auth.views import password_reset
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.db.models import Max

from inventory.models import Item
from inventory.models import UnitOfMeasure
from inventory.models import Brand

from web.models import (UserProfile, Vendor, Customer, TransportationCompany)
from purchase.models import Purchase, PurchaseItem, VendorAccount, PurchaseReturn, PurchaseReturnItem
from inventory.models import Inventory
from expenses.models import Expense, ExpenseHead

class PurchaseDetail(View):

    def get(self, request, *args, **kwargs):
        try:
            invoice_number = request.GET.get('invoice_no', '')
            purchase  = Purchase.objects.get(purchase_invoice_number=int(invoice_number))
            purchase_items = PurchaseItem.objects.filter(purchase=purchase)
            items_list = []
            for item in purchase_items:
                ret_quantity = 0
                inventory = Inventory.objects.get(item=item.item)
                purchase_returns = PurchaseReturn.objects.filter(purchase=purchase)
                for ret in purchase_returns:
                    ret_items = PurchaseReturnItem.objects.filter(purchase_return=ret, item=item.item)
                    for itm in ret_items:
                        ret_quantity = ret_quantity + itm.quantity
                items_list.append({
                    'item_code': item.item.code,
                    'item_name': item.item.name,
                    'barcode': item.item.barcode,
                    'uom': item.item.uom.uom,
                    'current_stock': inventory.quantity,
                    'frieght': item.item_frieght,
                    'frieght_unit': item.frieght_per_unit,
                    'handling': item.item_handling,
                    'handling_unit': item.handling_per_unit,                
                    'selling_price': inventory.selling_price,
                    'qty_purchased': item.quantity_purchased,
                    'cost_price': item.cost_price,
                    'permit_disc_amt': inventory.discount_permit_amount,
                    'permit_disc_percent': inventory.discount_permit_percentage,
                    'net_amount': item.net_amount,
                    'unit_price': inventory.unit_price,
                    'expense': item.expense,
                    'expense_unit': item.expense_per_unit,
                    'already_ret_quantity': ret_quantity
                })

            purchase_dict = {
                'purchase_invoice_number': purchase.purchase_invoice_number,
                'vendor_invoice_number': purchase.vendor_invoice_number,
                'vendor_do_number': purchase.vendor_do_number,
                'brand': purchase.brand.brand,
                'vendor': purchase.vendor.user.first_name,
                'transport': purchase.transportation_company.company_name,
                'vendor_invoice_date': purchase.vendor_invoice_date.strftime('%d/%m/%Y'),
                'purchase_invoice_date': purchase.purchase_invoice_date.strftime('%d/%m/%Y'), 
                'purchase_items': items_list,
                'vendor_amount': purchase.vendor_amount,
                'net_total': purchase.net_total,
                'purchase_expense': purchase.purchase_expense,
                'discount': purchase.discount,
                'grant_total': purchase.grant_total    
            }
            res = {
                'result': 'Ok',
                'purchase': purchase_dict
            } 
            response = simplejson.dumps(res)
            status_code = 200
        except Exception as ex:
            res = {
                'result': 'No item with this purchase NO'+ str(ex),
                'purchase': {}
            } 
            response = simplejson.dumps(res)
            status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")

class PurchaseEntry(View):

    def get(self, request, *args, **kwargs):
    	brand = Brand.objects.all()
    	vendor = Vendor.objects.all()
        transport = TransportationCompany.objects.all()
        if Purchase.objects.exists():
            invoice_number = int(Purchase.objects.aggregate(Max('purchase_invoice_number'))['purchase_invoice_number__max']) + 1
        else:
            invoice_number = 1
        if not invoice_number:
            invoice_number = 1
        return render(request, 'purchase/purchase_entry.html',{
        	'invoice_number': invoice_number,
    	})

    def post(self, request, *args, **kwargs):
        
        purchase_dict = ast.literal_eval(request.POST['purchase'])
        purchase, purchase_created = Purchase.objects.get_or_create(purchase_invoice_number=purchase_dict['purchase_invoice_number'])
        purchase.purchase_invoice_number = purchase_dict['purchase_invoice_number']
        purchase.vendor_invoice_number = purchase_dict['vendor_invoice_number']
        purchase.vendor_do_number = purchase_dict['vendor_do_number']
        purchase.vendor_invoice_date = datetime.strptime(purchase_dict['vendor_invoice_date'], '%d/%m/%Y')
        purchase.purchase_invoice_date = datetime.strptime(purchase_dict['purchase_invoice_date'], '%d/%m/%Y')
        brand = Brand.objects.get(brand=purchase_dict['brand'])
        purchase.brand = brand
        vendor = Vendor.objects.get(user__first_name=purchase_dict['vendor_name'])       
        transport = TransportationCompany.objects.get(company_name=purchase_dict['transport'])
        purchase.vendor = vendor
        purchase.transportation_company = transport
        if purchase_dict['discount']:
            purchase.discount = purchase_dict['discount']
        else:
            purchase.discount = 0
        purchase.net_total = purchase_dict['net_total']
        purchase.purchase_expense = purchase_dict['purchase_expense']
        purchase.grant_total = purchase_dict['grant_total']

        vendor_account, vendor_account_created = VendorAccount.objects.get_or_create(vendor=vendor)
        if vendor_account_created:
            vendor_account.total_amount = purchase_dict['vendor_amount']
            vendor_account.balance = purchase_dict['vendor_amount']
        else:
            if purchase_created:
                vendor_account.total_amount = vendor_account.total_amount + purchase_dict['vendor_amount']
                vendor_account.balance = vendor_account.balance + purchase_dict['vendor_amount']
            else:
                vendor_account.total_amount = vendor_account.total_amount - purchase.vendor_amount + purchase_dict['vendor_amount']
                vendor_account.balance = vendor_account.balance - purchase.vendor_amount + purchase_dict['vendor_amount']
        vendor_account.save()       
        purchase.vendor_amount = purchase_dict['vendor_amount']
        purchase.save()

        

        # Save purchase_expense in Expense
        if Expense.objects.exists():
            voucher_no = int(Expense.objects.aggregate(Max('voucher_no'))['voucher_no__max']) + 1
        else:
            voucher_no = 1
        if not voucher_no:
            voucher_no = 1
        expense = Expense()
        expense.created_by = request.user
        expense.expense_head, created = ExpenseHead.objects.get_or_create(expense_head = 'purchase')
        expense.date = dt.datetime.now().date().strftime('%Y-%m-%d')
        expense.voucher_no = voucher_no
        expense.amount = purchase_dict['purchase_expense']
        expense.payment_mode = 'cash'
        expense.narration = 'By purchase'
        expense.save()        

        purchase_items = purchase_dict['purchase_items']
        deleted_items = purchase_dict['deleted_items']

        for p_item in deleted_items:
            item = Item.objects.get(code = p_item['item_code']) 
            ps_item = PurchaseItem.objects.get(item=item)           
            inventory = Inventory.objects.get(item=item)
            inventory.quantity = inventory.quantity + ps_item.quantity_purchased
            inventory.save()
            ps_item.delete()

        for purchase_item in purchase_items:

            item = Item.objects.get(code=purchase_item['item_code'])
            p_item, item_created = PurchaseItem.objects.get_or_create(item=item, purchase=purchase)
            inventory, created = Inventory.objects.get_or_create(item=item)
            if created:
                inventory.quantity = int(purchase_item['qty_purchased'])                
            else:
                if purchase_created:
                    inventory.quantity = inventory.quantity + int(purchase_item['qty_purchased'])
                else:
                    inventory.quantity = inventory.quantity - p_item.quantity_purchased + int(purchase_item['qty_purchased'])
            inventory.selling_price = purchase_item['selling_price']
            inventory.unit_price = purchase_item['unit_price']
            inventory.discount_permit_percentage = purchase_item['permit_disc_percent']
            inventory.discount_permit_amount = purchase_item['permit_disc_amt']
            inventory.vendor = vendor
            inventory.save()  
                    
            p_item, item_created = PurchaseItem.objects.get_or_create(item=item, purchase=purchase)
            p_item.purchase = purchase
            p_item.item = item
            p_item.quantity_purchased = purchase_item['qty_purchased']
            p_item.item_frieght = purchase_item['frieght']
            p_item.frieght_per_unit = purchase_item['frieght_unit']
            p_item.item_handling = purchase_item['handling']
            p_item.handling_per_unit = purchase_item['handling_unit']
            p_item.expense = purchase_item['expense']
            p_item.expense_per_unit = purchase_item['expense_unit']
            p_item.cost_price = purchase_item['cost_price']
            p_item.net_amount = purchase_item['net_amount']
            p_item.save()
                    
        res = {
            'result': 'Ok',
        } 

        response = simplejson.dumps(res)
        status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")


class PurchaseEdit(View):
    def get(self, request, *args, **kwargs):
    	
        return render(request, 'purchase/edit_purchase_entry.html',{})

class VendorAccounts(View):
    def get(self, request, *args, **kwargs):
        vendor_accounts =  VendorAccount.objects.all()
        vendors = Vendor.objects.all()
        return render(request, 'purchase/vendor_accounts.html', {
            'vendor_accounts' : vendor_accounts,
            'vendors': vendors
        })
        

class VendorAccountDetails(View):
    def get(self, request, *args, **kwargs):
        try:
            vendor = get_object_or_404(Vendor, user__first_name=request.GET['vendor'])
            vendor_account =  VendorAccount.objects.get(vendor=vendor)
            res = {
                'result': 'Ok',
                'vendor_account': {
                    'vendor_account_date' : vendor_account.date.strftime('%d/%m/%Y') if vendor_account.date else '',
                    'payment_mode': vendor_account.payment_mode,
                    'narration': vendor_account.narration,
                    'total_amount': vendor_account.total_amount,
                    'amount_paid': vendor_account.paid_amount,
                    'balance_amount': vendor_account.balance,
                    'cheque_date': vendor_account.cheque_date.strftime('%d/%m/%Y') if vendor_account.cheque_date else '',
                    'cheque_no': vendor_account.cheque_no,
                    'bank_name': vendor_account.bank_name,
                    'branch_name': vendor_account.branch_name,
                    'vendor': vendor_account.vendor.user.first_name
                }
            } 

            response = simplejson.dumps(res)
            status_code = 200
        except:
            response = {
                'result': 'Vendor or VendorAccount does not exists',
            }
            status_code = 201
        return HttpResponse(response, status = status_code, mimetype="application/json")

    def post(self, request, *args, **kwargs):

        vendor_account_dict = ast.literal_eval(request.POST['vendor_account'])
        vendor = get_object_or_404(Vendor, user__first_name=vendor_account_dict['vendor'])
        vendor_account, created =  VendorAccount.objects.get_or_create(vendor=vendor) 
        vendor_account.date = datetime.strptime(vendor_account_dict['vendor_account_date'], '%d/%m/%Y')
        vendor_account.payment_mode = vendor_account_dict['payment_mode']
        vendor_account.narration = vendor_account_dict['narration']
        vendor_account.amount = int(vendor_account_dict['amount'])
        # vendor_account.total_amount = int(vendor_account_dict['total_amount'])
        vendor_account.paid_amount = vendor_account.paid_amount + vendor_account.amount  #int(vendor_account_dict['amount_paid'])
        vendor_account.balance = vendor_account.balance - vendor_account.amount  #int(vendor_account_dict['balance_amount'])        
        if vendor_account_dict['cheque_date'] != "null" :
            vendor_account.cheque_no = int(vendor_account_dict['cheque_no'])
            vendor_account.cheque_date = datetime.strptime(vendor_account_dict['cheque_date'], '%d/%m/%Y') 
            vendor_account.bank_name = vendor_account_dict['bank_name']
            vendor_account.branch_name = vendor_account_dict['branch_name']
        vendor_account.save()
        response = {
                'result': 'Ok',
            }
        status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")

class PurchaseReturnView(View):

    def get(self, request, *args, **kwargs):
        if PurchaseReturn.objects.exists():
            invoice_number = int(PurchaseReturn.objects.aggregate(Max('return_invoice_number'))['return_invoice_number__max']) + 1
        else:
            invoice_number = 1
        if not invoice_number:
            invoice_number = 1
        return render(request, 'purchase/purchase_return.html', {
            'invoice_number' : invoice_number,
        })

    def post(self, request, *args, **kwargs):
        post_dict = request.POST['purchase_return']
        post_dict = ast.literal_eval(post_dict)
        purchase = Purchase.objects.get(purchase_invoice_number=post_dict['purchase_invoice_number'])
        purchase_return, created = PurchaseReturn.objects.get_or_create(purchase=purchase, return_invoice_number = post_dict['invoice_number'])
        purchase_return.date = datetime.strptime(post_dict['purchase_return_date'], '%d/%m/%Y')
        purchase_return.net_amount = post_dict['net_return_total']
        purchase_return.save()
        
        vendor_account = VendorAccount.objects.get(vendor=purchase.vendor)
        vendor_account.total_amount = vendor_account.total_amount - int(post_dict['net_return_total'])
        vendor_account.save()

        return_items = post_dict['purchase_items']

        for item in return_items:
            return_item = Item.objects.get(code=item['item_code'])
            p_return_item, created = PurchaseReturnItem.objects.get_or_create(item=return_item, purchase_return=purchase_return)
            p_return_item.amount = item['returned_amount']
            p_return_item.quantity = item['returned_quantity']
            p_return_item.save()

            inventory = Inventory.objects.get(item=return_item)
            inventory.quantity = inventory.quantity - int(item['returned_quantity'])
            inventory.save()
        response = {
                'result': 'Ok',
            }
        status_code = 200
        return HttpResponse(response, status = status_code, mimetype="application/json")


class PurchaseReturnEdit(View):

    def get(self, request, *args, **kwargs):
        
        return render(request, 'purchase/vendor_accounts.html', {
            
        })
