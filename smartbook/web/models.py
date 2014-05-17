from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

USER_TYPE = (
    ('vendor', 'Vendor'),
    ('customer', 'Customer'),
    ('Salesman','Salesman')
)

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    user_type = models.CharField('User Type', max_length=10, choices=USER_TYPE)
    house_name = models.CharField('House name', null=True, blank=True, max_length=50)
    street = models.CharField('Street', null=True, blank=True, max_length=50)
    city = models.CharField('City', null=True, blank=True, max_length=50)
    district = models.CharField('District', null=True, blank=True, max_length=50)
    pin = models.CharField('Pin', max_length=10, null=True, blank=True,)
    mobile = models.CharField('Mobile', max_length=15, null=True, blank=True)
    land_line = models.CharField('Land Line',max_length=15, blank=True)
    email_id = models.CharField('Email Id', max_length=30)

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profile'

class Vendor(models.Model):
    user = models.ForeignKey(User)
    contact_person = models.CharField('Contact Person', max_length=50)  

    def save(self, *args, **kwargs):
        profile = self.user.userprofile_set.all()
        if len(profile) == 0:
            profile = UserProfile.objects.create(user = self.user)
        super(Vendor, self).save(*args, **kwargs)

    def __unicode__(self):
        return "vendor - "+self.user.first_name
    

    class Meta:

        verbose_name = 'Vendor'
        verbose_name_plural = 'Vendor'

    
class Customer(models.Model):
    
    customer_name = models.CharField('Name of the customer', null=True, blank=True, max_length=50)
    house_name = models.CharField('House name', null=True, blank=True, max_length=50)
    street = models.CharField('Street', null=True, blank=True, max_length=50)
    city = models.CharField('City', null=True, blank=True, max_length=50)
    district = models.CharField('District', null=True, blank=True, max_length=50)
    pin = models.CharField('Pin', max_length=10, null=True, blank=True,)
    mobile_number = models.CharField('Mobile Number', max_length=15, null=True, blank=True)
    land_line = models.CharField('Land Line', max_length=25, null=True, blank=True)
    customer_id = models.CharField('Customer Id(Email id)', max_length=75)

    def __unicode__(self):
        return "customer - "+ str(self.customer_name)

    # def save(self, *args, **kwargs):
    #     profile = self.user.userprofile_set.all()
    #     if len(profile) == 0:
    #         profile = UserProfile.objects.create(user = self.user)
    #     super(Customer, self).save(*args, **kwargs)


    class Meta:

        verbose_name = 'Customer'
        verbose_name_plural = 'Customer'

class TransportationCompany(models.Model):

    company_name = models.CharField('Company Name', null=True, blank=True, max_length=50)

    def __unicode__(self):

        return self.company_name

    class Meta:

        verbose_name = 'Transportation Company'
        verbose_name_plural = 'Transportation Company'

class OwnerCompany(models.Model):

    company_name = models.CharField('Company Name', max_length=100)
    logo = models.FileField('Logo', upload_to = "uploads/logo/", null=True, blank=True)

    def __unicode__(self):

        return self.company_name

    class Meta:

        verbose_name = 'Owner Company'
        verbose_name_plural = 'Owner Company'

