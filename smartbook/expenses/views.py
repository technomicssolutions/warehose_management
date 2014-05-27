# Create your views here.
import sys
import simplejson
import datetime as dt
import ast
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
        if post_dict['salesman']:
            salesman = User.objects.get(first_name=post_dict['salesman'])
            expense.salesman = salesman
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
class ExpenseDetails(View):

    def get(self, request, *args, **kwargs):

        voucher_no = request.GET.get('voucher_no', '')
        ctx_expense_details = []
        if voucher_no:
            expenses = Expense.objects.filter(voucher_no__startswith=voucher_no)
            for expense in expenses:
                ctx_expense_details.append({
                    'voucher_no': expense.voucher_no,
                    'salesman_name': expense.salesman.first_name if expense.salesman else '',
                    'expense_head': expense.expense_head.expense_head if expense.expense_head else '',
                    'date': expense.date.strftime('%d/%m/%Y') if expense.date else '',
                    'amount': expense.amount if expense.amount else '',
                    'payment_mode': expense.payment_mode if expense.payment_mode else '',
                    'narration': expense.narration if expense.narration else '',
                    'cheque_no': expense.cheque_no if expense.cheque_no else '',
                    'cheque_date': expense.cheque_date.strftime('%d/%m/%Y') if expense.cheque_date else '',
                    'bank_name': expense.bank_name if expense.bank_name else '',
                    'branch': expense.branch if expense.branch else '',
                })

        res = {
            'expenses': ctx_expense_details,
        }
        response = simplejson.dumps(res)
        status = 200

        return HttpResponse(response, status=status, mimetype='application/json')

class EditExpense(View):

    def get(self, request, *args, **kwargs):

        return render(request, 'expenses/edit_expense.html', {})

    def post(self, request, *args, **kwargs):

        post_dict = ast.literal_eval(request.POST['expense'])
        expense = Expense.objects.get(voucher_no=post_dict['voucher_no'])
        expense.expense_head = ExpenseHead.objects.get(expense_head = post_dict['expense_head'])
        expense.date = datetime.strptime(post_dict['date'], '%d/%m/%Y')
        expense.amount = post_dict['amount']
        expense.payment_mode = post_dict['payment_mode']
        expense.narration = post_dict['narration']
        
        if post_dict['payment_mode'] == 'cheque':
            expense.cheque_no = post_dict['cheque_no']
            expense.cheque_date = datetime.strptime(post_dict['cheque_date'], '%d/%m/%Y')
            expense.bank_name = post_dict['bank_name']
            expense.branch = post_dict['branch']
        if post_dict['salesman_name']:
            salesman = User.objects.get(first_name=post_dict['salesman_name'])
            expense.salesman = salesman
        expense.save()
        res = {
            'result': 'ok'
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype="application/json")

