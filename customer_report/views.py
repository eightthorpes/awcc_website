from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.template import RequestContext
from django.shortcuts import render_to_response, redirect
import django_tables2 as tables
from django.contrib.auth import authenticate, login, logout

from customer_report.models import Order
import customer_report.ecwid

class OrderTable(tables.Table):
    class Meta:
        model = Order
        attrs = {'align': 'right','width':'100%'}

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
def grouped_time(request):
    customer_report.ecwid.refresh_order_data()

    query_set = Order.objects.exclude(payment_status='DECLINED')
    table = OrderTable(query_set)
    return render_to_response(
            'customer_reports/grouped_time.html',
            {"table": table},
            context_instance=RequestContext(request))
