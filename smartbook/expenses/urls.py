from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from expenses.views import *

urlpatterns = patterns('',
	url(r'^new_expense/$', login_required(Expenses.as_view()), name='new_expense'),
	url(r'^new_expense_head/$', login_required(AddExpenseHead.as_view()), name='new_expense_head'),
	url(r'^expense_head_list/$', login_required(ExpenseHeadList.as_view()), name='expense_heads'),
	url(r'^edit_expense/$', login_required(EditExpense.as_view()), name='edit_expense'),
	url(r'^expense_details/$', login_required(ExpenseDetails.as_view()), name='expense_details')
)
