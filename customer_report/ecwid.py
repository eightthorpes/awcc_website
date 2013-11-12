# ecwid.py
# Functions for retrieving data using Ecwid's API
# TODO: This currently only gets the orders data
# TODO: Refactor __fill_in_sku_dicts into two functions
"""This module runs request to the Ecwid API to get product orders data."""

from collections import defaultdict
from string import capwords
import itertools
import json
import urllib

from customer_report.ecwid_settings import *
from customer_report.models import Order

def __do_http_request(base_url):
    """
    Run the http request to ecwid and get the orders list. Ecwid will only
    return 200 records at a time so we loop until we get less than 200
    """
    orders = list()
    offset = 0
    while (1):
        url = "%s%d" % (base_url, offset)
        handle = urllib.urlopen(url)
        json_string = handle.read().decode("utf8")
        order_dict = json.loads(json_string)
        count = order_dict['count']
        orders += (order_dict['orders'])
        if count < 200:
            break
        offset += 200
    return orders

def __fill_in_sku_dicts(orders):
    """
    1. Create a dictionary of product decriptions to sku numbers.
    2. Create a dictionary of orders per sku number.
    """
    sku_description = \
        defaultdict(itertools.repeat('None ordered yet').next)
    sku_orders = defaultdict(list)
    for order in orders:
        # Filter out "canceled" from orders
        if order['paymentStatus'] == "CANCELLED":
            continue
        items = order['items']
        customer_name = capwords(order['customerName'])
        for item in items:
            quantity = item['quantity']
            if ECWID_SKUS.count(item['sku']) == 0:
                continue
            sku_orders[item['sku']].append({
                    'customerName': customer_name,
                    'quantity': quantity,
                    'paymentStatus': order['paymentStatus']})
            sku_description[item['sku']] = item['name']
    return sku_description, sku_orders

def refresh_order_data():
    """
    External function to get orders from Ecwid and to update the database
    with the orders
    """
    base_url = \
        "%s/%s/orders?secure_auth_key=%s&from_date=%s&to_date=%s&offset=" % \
        (ECWID_URL, ECWID_STORE_ID, ECWID_AUTH_KEY, ECWID_FROM, ECWID_TO)
    orders = __do_http_request(base_url)
    (sku_description, sku_orders) = __fill_in_sku_dicts(orders)
    # Delete all existing entries
    for order in Order.objects.all():
        order.delete()
    for sku in ECWID_SKUS:
        for order in sku_orders[sku]:
            record = Order(
                     sku=sku,
                     slot=sku_description[sku],
                     quantity=order['quantity'],
                     customer_name=order['customerName'],
                     payment_status=order['paymentStatus'])
            record.save()
