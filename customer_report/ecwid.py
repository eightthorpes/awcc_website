
from collections import defaultdict
import itertools
import json
import logging
import sys
import urllib
import urlparse
from customer_report.ecwid_settings import *
from customer_report.models import Order

from pprint import PrettyPrinter
pp = PrettyPrinter(indent=4)

class ecwid_api():
    def __init__(self):
        self.base_url = "%s/%s/orders?secure_auth_key=%s&from_date=%s&to_date=%s&offset=" % (ECWID_URL, ECWID_STORE_ID, ECWID_AUTH_KEY, ECWID_FROM, ECWID_TO)
        self.sku_description = \
            defaultdict(itertools.repeat('None ordered yet').next)
        self.sku_orders = defaultdict(list)
        self.orders = list()

    def __do_http_request(self):
        offset = 0
        while (1):
            url = "%s%d" % (self.base_url, offset)
            f = urllib.urlopen(url)
            json_string = f.read().decode("utf8")
            order_dict = json.loads(json_string)
            count = order_dict['count']
            self.orders += (order_dict['orders'])
            if count < 200:
                break
            offset += 200

    def __fill_in_sku_dicts(self):
        for order in self.orders:
            # Filter out "canceled" from orders
            if order['paymentStatus'] == "CANCELLED":
                continue
            items = order['items']
            customerName = order['customerName']
            for item in items:
                quantity = item['quantity']
                if ECWID_SKUS.count(item['sku']) == 0:
                    continue
                self.sku_orders[item['sku']].append({
                        'customerName': customerName,
                        'quantity': quantity,
                        'paymentStatus': order['paymentStatus']})
                self.sku_description[item['sku']] = item['name']

    def update_db(self):
        self.__do_http_request()
        self.__fill_in_sku_dicts()
        # Delete all existing entries
        for order in Order.objects.all():
            order.delete()
        for sku in ECWID_SKUS:
            for order in self.sku_orders[sku]:
                o = Order(
                        sku=sku,
                        slot=self.sku_description[sku],
                        quantity=order['quantity'],
                        customer_name=order['customerName'],
                        payment_status=order['paymentStatus'])
                o.save()
