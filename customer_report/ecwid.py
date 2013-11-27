# ecwid.py
# Functions for retrieving data using Ecwid's API
# TODO: This currently only gets the orders data
# TODO: Refactor __fill_in_sku_dicts into two functions
"""This module runs request to the Ecwid API to get product orders data."""

from datetime import datetime
from collections import defaultdict
from string import capwords
import itertools
import json
import urllib
from django.utils.timezone import utc

from customer_report.ecwid_settings import *
from customer_report.models import Order
from customer_report.models import Product

def __do_order_api_request(base_url):
    """
    Run the http request to ecwid and get the orders list. Ecwid will only
    return 200 records at a time so we loop until we get less than 200

    We return a list of dicts, one for each order
    """

    # Make sure product data has been filled in
    if Product.last_update == 0:
        refresh_product_data()

    orders = list()
    offset = 0
    while (1):
        url = "%s%d" % (base_url, offset)
        handle = urllib.urlopen(url)
        json_string = handle.read().decode("utf8")
        order_dict = json.loads(json_string)
        count = order_dict['count']
        # Orders are a list of dicts accessed via the 'orders' key
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
        (ECWID_URL, ECWID_STORE_ID, ORDER_AUTH_KEY, ECWID_FROM, ECWID_TO)
    orders = __do_order_api_request(base_url)
    #(sku_description, sku_orders) = __fill_in_sku_dicts(orders)
    # Delete all existing entries
    for order_obj in Order.objects.all():
        order_obj.delete()
    for order in orders:
        if order['paymentStatus'] == "CANCELLED":
            continue
        for item in order['items']:
            product_object = Product.objects.get(sku=item['sku'])
            record = Order(
                     product=product_object,
                     slot=item['name'],
                     quantity=item['quantity'],
                     customer_name=order['customerName'],
                     payment_status=order['paymentStatus'])
            record.save()
    Order.last_update = datetime.utcnow().replace(tzinfo=utc)

def __do_product_api_request(url):
    """
    Run the http request to ecwid and get the product list. 
    """
    handle = urllib.urlopen(url)
    json_string = handle.read().decode("utf8")
    return json.loads(json_string)

def refresh_product_data():
    """
    External function to get orders from Ecwid and to update the database
    with the product data
    Sample url: http://app.ecwid.com/api/v1/[STORE-ID]/products?\
        category=[CATEGORY-ID]&hidden_products=[true or false]&
        secure_auth_key=[PRODUCT-UPDATE-API-KEY]&
        from_update_date=[DATE]&to_update_date=[DATE]

    Sample Return Entry:
    {
    "id": 27670173,
    "sku": "00093",
    "quantity": 2,
    "name": "Friday, Dec. 13, 2013 - 5:12 pm",
    "price": 25.0,
    "url": "https://www.alleghenywest.org/shop-2/#!/~/product/id=27670173",
    "created": "2013-09-02 18:53:32",
    "updated": "2013-11-20 20:17:20",
    "productClassId": 0,
    "enabled": true,
    "description": "",
    "descriptionTruncated": false
    },  
    """
    url = "%s/%s/products?secure_auth_key=%s&from_date=%s&to_date=%s&hidden_products=true" \
       % (ECWID_URL, ECWID_STORE_ID, PRODUCT_AUTH_KEY, ECWID_FROM, ECWID_TO)
    products = __do_product_api_request(url)
    for product in products:
        try:
            quantity = product['quantity']
        except KeyError:
            quantity = 0
        created_time = datetime.strptime(product['created'], \
            "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)
        updated_time = datetime.strptime(product['updated'], \
            "%Y-%m-%d %H:%M:%S").replace(tzinfo=utc)
        record = Product(
             id = product['id'],
             sku = product['sku'],
             quantity = quantity,
             name = product['name'],
             price = product['price'],
             url = product['url'],
             created = created_time,
             updated = updated_time,
             productClassId = product['productClassId'],
             enabled = (product['enabled'] == 'true'),
             description = product['description'],
             descriptionTruncated = (product['descriptionTruncated'] == 'true'),
             )
        record.save()
    Product.last_update = datetime.utcnow().replace(tzinfo=utc)


