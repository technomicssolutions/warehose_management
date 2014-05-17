# Create your views here.
import sys
import simplejson
import datetime as dt
from datetime import datetime

from django.db import IntegrityError

from django.contrib.auth.views import password_reset
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from .models import ExpenseHead, Expense

class Expenses(View):

    def get(self, request, *args, **kwargs):

        current_date = dt.datetime.now().date()
        expenses = Expense.objects.all().count()
        if int(expenses) > 0:
            latest_expense = Expense.objects.latest('id')
            voucher_no = int(latest_expense.voucher_no) + 1
        else:
            voucher_no = 1
        context = {
            'current_date': current_date.strftime('%d/%m/%Y'),
            'voucher_no': voucher_no
        }
        
        return render(request, 'expenses/expense.html', context)

    def post(self, request, *args, **kwargs):

        post_dict = request.POST
        expense = Expense()
        expense.created_by = request.user
        expense.expense_head = ExpenseHead.objects.get(expense_head = post_dict['head_name'])
        expense.date = datetime.strptime(post_dict['date'], '%d/%m/%Y')
        expense.voucher_no = post_dict['voucher_no']
        expense.amount = post_dict['amount']
        expense.payment_mode = post_dict['payment_mode']
        expense.narration = post_dict['narration']
        if post_dict['payment_mode'] == 'cheque':
            expense.cheque_no = post_dict['cheque_no']
            expense.cheque_date = datetime.strptime(post_dict['cheque_date'], '%d/%m/%Y')
            expense.bank_name = post_dict['bank_name']
            expense.branch = post_dict['branch']
        expense.save()
        res = {
            'result': 'ok'
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype="application/json")

class AddExpenseHead(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'expenses/add_expense_head.html', {})

    def post(self, request, *args, **kwargs):

        post_dict = request.POST

        try:
            if len(post_dict['head_name']) > 0 and not post_dict['head_name'].isspace():
                expense_head, created = ExpenseHead.objects.get_or_create(expense_head = post_dict['head_name'])
                if created:
                    context = {
                        'message' : 'Added successfully',
                    }
                else:
                    context = {
                        'message' : 'This Head name is Already Existing',
                    }
            else:
                context = {
                    'message' : 'Head name Cannot be null',
                }
        except Exception as ex:
            context = {
                'message' : post_dict['head_name']+' is already existing',
            }
        return render(request, 'expenses/add_expense_head.html', context)

class ExpenseHeadList(View):

    def get(self, request, *args, **kwargs):

        ctx_expense_head = []
        status_code = 200
        expense_heads = ExpenseHead.objects.all()
        if len(expense_heads) > 0:
            for head in expense_heads:
                ctx_expense_head.append({
                    'head_name': head.expense_head  
                })
        res = {
            'result': 'ok',
            'expense_heads':ctx_expense_head
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=status_code, mimetype="application/json")


