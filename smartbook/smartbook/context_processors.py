from django.contrib.sites.models import Site
from django.db import models

from web.models import *

def site_variables(request):
    current_site = Site.objects.get_current()
    owner_company = OwnerCompany.objects.all()
    if owner_company.count() > 0:
    	owner_company_name = owner_company[0].company_name
    else:
    	owner_company_name = ''
    return {
        'SITE_ROOT_URL_S': 'https://%s/'%(current_site.domain),
        'SITE_ROOT_URL': 'http://%s'%(current_site.domain),
        'owner_company_name': owner_company_name
    }
 