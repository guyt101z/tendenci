import os
from django.conf import settings
from django.utils import simplejson
from site_settings.utils import get_setting
from perms.utils import is_admin
from corporate_memberships.models import CorpField, AuthorizedDomain

# get the corpapp default fields list from json
def get_corpapp_default_fields_list():
    json_fields_path = os.path.join(settings.PROJECT_ROOT, 
                                    "templates/corporate_memberships/regular_fields.json")
    fd = open(json_fields_path, 'r')
    data = ''.join(fd.read())
    fd.close()
    
    if data:
        return simplejson.loads(data)
    return None

def get_corporate_membership_type_choices(user, corpapp):
    cmt_list = []
    corporate_membership_types = corpapp.corp_memb_type.all()
    currency_symbol = get_setting("site", "global", "currencysymbol")
    
    for cmt in corporate_membership_types:
        cmt_list.append((cmt.id, '%s - %s%0.2f' % (cmt.name, currency_symbol, cmt.price)))
        
    return cmt_list        
   
def get_payment_method_choices(user):
    if is_admin(user):
        return (('paid - check', 'User paid by check'),
                ('paid - cc', 'User paid by credit card'),
                ('Credit Card', 'Make online payment NOW'),)
    else:
        return (('check', 'Check'),
                ('cash', 'Cash'),
                ('cc', 'Credit Card'),)
        
def update_auth_domains(corp_memb, domain_names):
    """
        Update the authorized domains for this corporate membership.
    """
    if domain_names:
        dname_list = domain_names.split(',')
        dname_list = [name.strip() for name in dname_list]
        
        # if domain is not in the list domain_names, delete it from db
        # otherwise, remove it from list
        if corp_memb.auth_domains:
            for auth_domain in list(corp_memb.auth_domains.all()):
                if auth_domain.name in dname_list:
                    dname_list.remove(auth_domain.name)
                else:
                    auth_domain.delete()
                    
        # add the rest of the domain
        for name in domain_names:
            auth_domain = AuthorizedDomain(corporate_membership=corp_memb, name=name)
            auth_domain.save()
            
            
        
        
def update_authenticate_fields(corpapp):
    """
        if corpapp.authentication_method == 'admin':
            authorized_domains.required = False
            authorized_domains.visible = False
            secret_code.required = False
            secret_code.visible = False
        elif corpapp.authentication_method == 'email':
            authorized_domains.required = True
            authorized_domains.visible = True
            secret_code.required = False
            secret_code.visible = False
        elif corpapp.authentication_method == 'secret_code':
            authorized_domains.required = False
            authorized_domains.visible = False
            secret_code.required = True
            secret_code.visible = True
    """
    if corpapp:
        authorized_domains = CorpField.objects.get(corp_app=corpapp, field_name='authorized_domains')
        secret_code = CorpField.objects.get(corp_app=corpapp, field_name='secret_code')
        if corpapp.authentication_method == 'admin':
            authorized_domains.required = 0
            authorized_domains.visible = 0
            secret_code.required = 0
            secret_code.visible = 0
        elif corpapp.authentication_method == 'email':
            authorized_domains.required = 1
            authorized_domains.visible = 1
            secret_code.required = 0
            secret_code.visible = 0
        else:   # secret_code
            authorized_domains.required = 0
            authorized_domains.visible = 0
            secret_code.required = 1
            secret_code.visible = 1
            secret_code.no_duplicates = 1
        authorized_domains.save()
        secret_code.save()  
            
            
    