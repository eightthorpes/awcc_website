from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
import django_tables2 as tables
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum

from customer_report.models import Order
import customer_report.ecwid
from customer_report.ecwid_settings import *

class OrderTable(tables.Table):
    class Meta:
        model = Order
        attrs = {'width':'60%'}
        exclude = ("id", "sku",)

def auth_and_login(request, onsuccess='/', onfail='/login/'):
    user = authenticate(username=request.POST['username'], 
            password=request.POST['password'])
    if user is not None:
        login(request, user)
        print "Login success"
        return redirect(onsuccess)
    else:
        print "Login failed"
        return redirect(onfail)

def loginview(request):
    context = {}
    context.update(csrf(request))
    return render_to_response('login.html', context)

def logout_view(request):
    logout(request)
    return redirect("/login/")

@login_required(login_url='/login/')
def all_orders(request):
    customer_report.ecwid.refresh_order_data()
    query_set = Order.objects.exclude(payment_status='DECLINED')

    table = OrderTable(query_set)
    return render_to_response(
            'customer_reports/all_orders.html',
            {"table": table},
            context_instance=RequestContext(request))

@login_required(login_url='/login/')
def grouped_time(request):
    customer_report.ecwid.refresh_order_data()
    query_set = Order.objects.exclude(payment_status='DECLINED')

    sku_list = list()
    sku_list.append(TOUR_SKUS)
    sku_list.append(BRUNCH_SKUS)
    sku_list.append(LUNCH_SKUS)
    sku_list.append(DINNER_SKUS)
    sku_list.append(TRAIN_SKUS)
   
    page_data = list()
    for sku_dict in sku_list:
        orders = query_set.filter(sku__in=sku_dict['skus'])
        slots = list(set(orders.values_list('slot', flat=True)))
        slots.sort()
        for slot in slots:
            orders_by_slot = orders.filter(slot=slot)
            quantity_sum = orders_by_slot.aggregate(Sum('quantity'))
            name = "%s - %s" % (sku_dict['name'], slot)
            table = OrderTable(orders_by_slot)
            table_dict = {'name': name,
                          'sum': quantity_sum['quantity__sum'],
                          'table': table}
            page_data.append(table_dict) 

    return render_to_response(
            'customer_reports/grouped_time.html',
            {"page_data": page_data},
            context_instance=RequestContext(request))
