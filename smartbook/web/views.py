# Create your views here.

import sys
import simplejson
import os
import shutil
import re

from django.db import IntegrityError
from django.core.management import call_command
from django.contrib.auth.views import password_reset
from django.shortcuts import get_object_or_404, render
from django.views.generic.base import View
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from web.models import (UserProfile, Vendor, Customer, TransportationCompany)


class Home(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, 'home.html',context)

class Login(View):

    def post(self, request, *args, **kwargs):

        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user and user.is_active:
            login(request, user)
        else:
            context = {
                'message' : 'Username or password is incorrect'
            }
            return render(request, 'home.html',context)
        return HttpResponseRedirect(reverse('home'))

class Logout(View):

    def get(self, request, *args, **kwargs):

        logout(request)
        return HttpResponseRedirect(reverse('home'))

class UserList(View):
    def get(self, request, *args, **kwargs):
        user_type = kwargs['user_type']
        ctx_vendors = []

        ctx_staffs = []


        ctx_customers = []
        ctx_salesman = []
        if user_type == 'Salesman':
            users = UserProfile.objects.filter(user_type='Salesman')
            if request.is_ajax():
                if len(users) > 0:
                    for usr in users:
                        ctx_salesman.append({
                            'staff_name': usr.user.first_name,
                        })
                res = {
                    'salesmen': ctx_salesman,
                    
                } 

                response = simplejson.dumps(res)
                status_code = 200
                return HttpResponse(response, status = status_code, mimetype="application/json")
        elif user_type == 'vendor':
            users = Vendor.objects.all()
            if request.is_ajax():
                if len(users) > 0:
                    for usr in users:
                        ctx_vendors.append({
                            'vendor_name': usr.user.first_name if usr.user.first_name else user.username,
                        })
                res = {
                    'vendors': ctx_vendors,
                    
                } 
                
                response = simplejson.dumps(res)
                status_code = 200
                return HttpResponse(response, status = status_code, mimetype="application/json")
        elif user_type == 'customer':
            users = Customer.objects.all()

            
            if request.is_ajax():
                if len(users) > 0:
                    for customer in users:
                        ctx_customers.append({
                            'customer_name': customer.customer_name,
                        })
                res = {
                    'customers': ctx_customers,
                    
                } 


                response = simplejson.dumps(res)
                status_code = 200
                return HttpResponse(response, status = status_code, mimetype="application/json")
        elif user_type == 'salesman': 
        
            salesmen = UserProfile.objects.filter(user_type = 'Salesman')

            if request.is_ajax():
                if len(salesmen)>0:
                    for salesman in salesmen:
                        ctx_salesman.append({
                            'salesman_name' : salesman.user.first_name if salesman.user.first_name else salesman.user.username,
                        })
                res = {
                    'salesmen' : ctx_salesman,
                } 
                

                response = simplejson.dumps(res)
                status_code = 200
                return HttpResponse(response, status = status_code, mimetype="application/json")

        return render(request, 'user_list.html',{
            'users': users,
            'user_type': user_type
        })

class RegisterSalesman(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'register_user.html',{'user_type': kwargs['user_type'], 'salesman': 'salesman'})

class RegisterUser(View):
    def get(self, request, *args, **kwargs):
        user_type = kwargs['user_type']
        return render(request, 'register_user.html',{'user_type': user_type})
        

    def post(self, request, *args, **kwargs):
       
        context={}
        user_type = kwargs['user_type']
        message = ''
        template = 'register_user.html'
        email_validation = (re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", request.POST['email']) )
        if request.POST['name'] == '':
            message = "Please enter name"
        if user_type == "Salesman":
            if request.POST['username'] == '':
                message = "Please enter username"
            elif request.POST['password'] == '':
                message = "Please enter password"
            elif request.POST['email'] == '':
                message = "Please enter email"
            elif email_validation == None:
                message = "Please enter a valid email id"

        if message:
            context = {
                'error_message': message,
                'user_type': user_type
            }
            context.update(request.POST)            
            return render(request, template, context)
        else:
            if user_type == 'Salesman':
                try:
                    user = User.objects.get(email = request.POST['email'])
                    message = "Salesman with this email id already exists"
                    context = {
                        'error_message': message,
                        'user_type': user_type,
                        'salesman': 'salesman'
                    }
                    context.update(request.POST)            
                    return render(request, template, context)
                    
                except Exception as ex:
                    print "in Exception == ", str(ex)
                    user, created = User.objects.get_or_create(username = request.POST['username'])
                    if not created:
                        message = "Salesman with this name already exists"
                        context = {
                            'error_message': message,
                            'user_type': user_type,
                            'salesman': 'salesman'
                        }
                        context.update(request.POST)            
                        return render(request, template, context)
                    else:                        
                        user.set_password(request.POST['password'])
                        user.save()
                        context = {
                            'message' : 'Salesman added correctly',
                            'user_type': user_type,
                            'salesman': 'salesman'
                        }
                    user.email = request.POST['email']
                    user.first_name = request.POST['name']
                    user.save()

            elif user_type == 'vendor':
                user, created = User.objects.get_or_create(username=request.POST['name']+user_type, first_name = request.POST['name'])
                if not created:    
                    message = 'Vendor with this name already exists'
                    if request.is_ajax():
                        res = {
                            'result': 'error',
                            'message': 'Designation Already exists'
                        }
                        response = simplejson.dumps(res)
                        return HttpResponse(response, status = 500, mimetype="application/json")
                    else:
                        context = {
                            'error_message': message,
                            'user_type': user_type
                        }
                        context.update(request.POST)
                        return render(request, template, context)
                else:
                    vendor = Vendor()  
                    vendor.contact_person= request.POST['contact_person']
                    user.is_active = False
                    user.save()
                    vendor.user = user
                    vendor.save()
                    if request.is_ajax():
                        res = {
                            'result': 'ok',
                            'vendor_name': user.first_name
                        }
                        response = simplejson.dumps(res)
                        return HttpResponse(response, status = 200, mimetype="application/json")
                    context = {
                        'messgae': "vendor added Successfully",
                        'user_type': user_type
                    }
                    context.update(request.POST)
            
            userprofile = UserProfile()
            userprofile.user_type=user_type
            userprofile.user = user
            userprofile.house_name =request.POST['house']
            userprofile.street = request.POST['street']
            userprofile.city = request.POST['city']
            userprofile.district = request.POST['district']
            userprofile.pin = request.POST['pin']
            userprofile.mobile = request.POST['mobile']
            userprofile.land_line = request.POST['phone']
            userprofile.email_id = request.POST['email']
            userprofile.save()

            return render(request, 'register_user.html',context)
            
        
class EditUser(View):

    def get(self, request, *args, **kwargs):

        user_type = kwargs['user_type']
        if user_type == 'customer':
            userprofile = Customer.objects.get(id=kwargs['user_id'])
            return render(request, 'edit_user.html',{'user_type': user_type,'profile': userprofile})
        else:
            userprofile = UserProfile.objects.get(user_id=kwargs['user_id'])
            if user_type == 'vendor':
                return render(request, 'edit_user.html',{'user_type': user_type, 'profile': userprofile})
            elif user_type == 'Salesman':
                return render(request, 'edit_user.html',{
                    'user_type': user_type,
                    'profile': userprofile

                })

    def post(self, request, *args, **kwargs):

        user_type = kwargs['user_type']
        post_dict = request.POST
        if user_type == 'customer':
            customer = Customer.objects.get(id = kwargs['user_id'])
            if request.POST['name'] == '':
                context = {
                    'message': 'Name cannot be null',
                    'user_type': user_type,
                    'profile': customer
                }
                context.update(request.POST)
                return render(request, 'edit_user.html',context)
            elif request.POST['email'] == '':
                context = {
                    'message': 'Email cannot be null',
                    'user_type': user_type,
                    'profile': customer
                }
                context.update(request.POST)
                return render(request, 'edit_user.html',context)
            customer.customer_name = request.POST['name']
            customer.house_name =request.POST['house']
            customer.street = request.POST['street']
            customer.city = request.POST['city']
            customer.district = request.POST['district']
            customer.pin = request.POST['pin']
            customer.mobile_number = request.POST['mobile']
            customer.land_line = request.POST['phone']
            customer.customer_id = request.POST['email']
            customer.save()
            context = {
                'message' : 'Customer edited correctly',
                'user_type': user_type,
                'profile': customer
            }
            return render(request, 'edit_user.html',context)
        else:
            

            user = User.objects.get(id= kwargs['user_id'])
            userprofile, created = UserProfile.objects.get_or_create(user = user)
            email_validation = (re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", request.POST['email']) )
            if email_validation == None:
                message = "Please enter a valid email id"
                context = {
                    'message': message,
                    'user_type': user_type,
                    'profile': userprofile
                }
                context.update(request.POST)
                return render(request, 'edit_user.html',context)
            user.first_name = post_dict['name']
            
            user.email = post_dict['email']

            user.save()
            
            userprofile.user_type=user_type
            userprofile.user = user
            userprofile.house_name =request.POST['house']
            userprofile.street = request.POST['street']
            userprofile.city = request.POST['city']
            userprofile.district = request.POST['district']
            userprofile.pin = request.POST['pin']
            userprofile.mobile = request.POST['mobile']
            userprofile.land_line = request.POST['phone']
            userprofile.email_id = request.POST['email']
            userprofile.save()
            if user_type == 'vendor':
                user.username= post_dict['name']+user_type
                user.save()
                vendor = user.vendor_set.all()[0]  
                vendor.contact_person= request.POST['contact_person']
                vendor.user = user
                vendor.save()
                context = {
                    'message' : 'Vendor edited correctly',
                    'user_type': user_type,
                    'profile': userprofile
                }
                return render(request, 'edit_user.html',context)
            elif user_type == 'Salesman':
                user.username = request.POST['username']
                user.save()
                userprofile.user = user
                userprofile.save()
                
                context = {
                    'message' : 'Salesman edited correctly',
                    'user_type': user_type,
                    'profile': userprofile
                }
                return render(request, 'edit_user.html',context)

class AddDesignation(View):

    def post(self, request, *args, **kwargs):
        if len(request.POST['new_designation']) > 0 and not request.POST['new_designation'].isspace():
            designation, created = Designation.objects.get_or_create(title=request.POST['new_designation']) 
            if not created:
                res = {
                    'result': 'error',
                    'message': 'Designation Already exists'
                }
            else:
                res = {
                    'result': 'ok',
                    'designation': designation.title
                }
        else:
            res = {
                 'result': 'error',
                 'message': 'Designation Cannot be null'
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')

class DeleteUser(View):

    def get(self, request, *args, **kwargs):

        user_type = kwargs['user_type']
        if request.user.is_superuser:
            if user_type == 'customer':
                customer = Customer.objects.get(id=kwargs['user_id'])
                customer.delete()
            else:
                user = User.objects.get(id=kwargs['user_id'])            
                user.delete()
                context = {
                    'message': 'Deleted Successfully'
                }
        else:
            context = {
                'message': "You don't have permission to perform this action"
            }
        return HttpResponseRedirect(reverse('users', kwargs={'user_type': user_type}))

class TransportationCompanyList(View):

    def get(self, request, *args, **kwargs):

        ctx = []
        transportationcompanies = TransportationCompany.objects.all()
        if len(transportationcompanies) > 0:
            for transportationcompany in transportationcompanies:
                ctx.append({
                    'company_name': transportationcompany.company_name,    
                })
        res = {
            'company_names': ctx,    
        }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype="application/json")

class AddTransportationCompany(View):

    def post(self, request, *args, **kwargs):

        if len(request.POST['new_company']) > 0 and not request.POST['new_company'].isspace():
            new_company, created = TransportationCompany.objects.get_or_create(company_name=request.POST['new_company']) 
            if not created:
                res = {
                    'result': 'error',
                    'message': 'Company name already exists'
                }
            else:
                res = {
                    'result': 'ok',
                    'company_name': new_company.company_name
                }
        else:
            res = {
                 'result': 'error',
                 'message': 'Company name cannot be null'
            }
        response = simplejson.dumps(res)
        return HttpResponse(response, status=200, mimetype='application/json')


class ResetPassword(View):

    def get(self, request, *args, **kwargs):

        user = User.objects.get(id=kwargs['user_id'])
        context = {
            'user_id': user.id
        }
        return render(request, 'reset_password.html', context)

    def post(self, request, *args, **kwargs):

        context = {}
        user = User.objects.get(id=kwargs['user_id'])
        user.set_password(request.POST['password'])
        user.save()
        if user == request.user:
            logout(request)
            return HttpResponseRedirect(reverse('home'))  
        else:
            user_type = user.userprofile_set.all()[0].user_type 
            return HttpResponseRedirect(reverse('users', kwargs={'user_type': user_type}))


class BackupView(View):
    
    def get(self, request, *args, **kwargs):        
        call_command('dbbackup')
        return HttpResponseRedirect('/backups/')

class ClearBackup(View):    
            
    def get(self, request, *args, **kwargs):       
        path = os.path.dirname(__file__)
        path = path.split('web')[0]
        path = path+'media/'
        for root, dirs, files in os.walk(path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        return HttpResponseRedirect('/backups/')

class CreateCustomer(View):

    def get(self, request, *args, **kwargs):

        user_type = 'customer'
        return render(request, 'register_user.html',{'user_type': user_type})

    def post(self, request, *args, **kwargs):

        if not request.is_ajax:
            if request.POST['name'] == '':
                context = {
                    'error_message': 'Please enter the name',
                    'user_type': 'customer',
                }
                context.update(request.POST)
                return render(request, 'register_user.html',context)
            elif request.POST['email'] == '':
                context = {
                    'error_message': 'Please enter the email id',
                    'user_type': 'customer',
                }
                context.update(request.POST)
                return render(request, 'register_user.html',context)
        customer, created = Customer.objects.get_or_create(customer_name = request.POST['name'])
        if not created:
            if request.is_ajax():
                res = {
                    'result': 'error',
                    'message': 'Customer with this name already exists',
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status = 200, mimetype="application/json")
            else:
                context = {
                    'error_message': 'Customer with this name already exists',
                    'user_type': 'customer',
                }
                context.update(request.POST)
                return render(request, 'register_user.html',context)
        else:
            customer.customer_name = request.POST['name']
            customer.house_name = request.POST['house'] 
            customer.street = request.POST['street']
            customer.city = request.POST['city']
            customer.district = request.POST['district'] 
            customer.pin = request.POST['pin']
            customer.mobile_number = request.POST['mobile']
            customer.land_line = request.POST['phone']
            customer.save()
            if request.is_ajax():
                res = {
                    'result': 'ok',
                    'customer_name': customer.customer_name
                }
                response = simplejson.dumps(res)
                return HttpResponse(response, status = 200, mimetype="application/json")

        context = {
            'message' : 'Customer added correctly',
            'user_type': 'customer'
        }
        return render(request, 'register_user.html',context)
