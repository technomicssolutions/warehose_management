from django.conf.urls import patterns, include, url

from expenses.views import *

urlpatterns = patterns('',
	url(r'^new_expense/$', Expenses.as_view(), name='new_expense'),
	url(r'^new_expense_head/$', AddExpenseHead.as_view(), name='new_expense_head'),
	url(r'^expense_head_list/$', ExpenseHeadList.as_view(), name='expense_heads'),
)
