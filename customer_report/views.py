from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django.http import HttpResponse
import django_tables2 as tables
from customer_report.models import Order
import customer_report.ecwid

class OrderTable(tables.Table):
    class Meta:
        model = Order

def grouped_time(request):
    customer_report.ecwid.refresh_order_data()

    query_set = Order.objects.all()
    table = OrderTable(query_set)
    return render_to_response('customer_reports/grouped_time.html',
            {"table": table},
            context_instance=RequestContext(request))
