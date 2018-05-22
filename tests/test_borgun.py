# -*- coding: utf-8 -*-
import hashlib, hmac
from decimal import Decimal

from django.test import TestCase
from django.http import HttpResponse, HttpResponseForbidden
from mock import MagicMock, Mock

from .models import Payment
from payments import PaymentStatus
from payments_borgun import BorgunProvider, helpers


PRIVATE_KEY = '99887766'



def get_postdata_with_sha256(payment, **kwargs):
    data = {
        'orderid': "PAYMENT%s" % payment.id,
        'amount': payment.total,
        'currency': payment.currency,
    }
    data['itemdescription_0'] = payment.description
    data['itemcount_0'] = 1
    data['itemunitamount_0'] = payment.total
    data['itemamount_0'] = payment.total
    hash_string = "{order_id}|{amount}|{currency}".format(
        order_id=data['orderid'],
        amount=payment.total,
        currency=payment.currency
    )
    data['orderhash'] = hmac.new(
        helpers.to_bytes(PRIVATE_KEY),
        msg=helpers.to_bytes(hash_string),
        digestmod=hashlib.sha256
    ).hexdigest()
    for k,v in kwargs.items():
        data[k] = v
    return data



class GatewayTest(TestCase):
    def setUp(self):
        self.payment = Payment.objects.create(
            variant='default',
            description='Book purchase',
            total=Decimal(120),
            currency='USD',
            billing_first_name='Sherlock',
            billing_last_name='Holmes',
            billing_address_1='221B Baker Street',
            billing_address_2='',
            billing_city='London',
            billing_postcode='NW1 6XE',
            billing_country_code='UK',
            billing_country_area='Greater London',
            customer_ip_address='127.0.0.1'
        )
        self.payment2 = Payment.objects.create(
            variant='default',
            description='Book purchase',
            total=Decimal(120),
            currency='USD',
            billing_first_name='Sherlock',
            billing_last_name='Holmes',
            billing_address_1='221B Baker Street',
            billing_address_2='',
            billing_city='London',
            billing_postcode='NW1 6XE',
            billing_country_code='UK',
            billing_country_area='Greater London',
            customer_ip_address='127.0.0.1'
        )
        self.payment3 = Payment.objects.create(
            variant='default',
            description='Book purchase',
            total=Decimal(120),
            currency='USD',
            billing_first_name='Sherlock',
            billing_last_name='Holmes',
            billing_address_1='221B Baker Street',
            billing_address_2='',
            billing_city='London',
            billing_postcode='NW1 6XE',
            billing_country_code='UK',
            billing_country_area='Greater London',
            customer_ip_address='127.0.0.1'
        )

    def test_get_hidden_fields(self):
        """BorgunProvider.get_hidden_fields() returns a dictionary"""
        provider = BorgunProvider(sandbox=True)
        self.assertEqual(type(provider.get_hidden_fields(self.payment)), dict)

    def test_process_data_payment_accepted(self):
        """BorgunProvider.process_data() returns a correct HTTP response"""
        self.assertEqual(self.payment.status, PaymentStatus.WAITING)
        request = MagicMock()
        request.POST = get_postdata_with_sha256(self.payment, status='OK', step='Payment')
        provider = BorgunProvider(sandbox=True)
        response = provider.process_data(self.payment, request)
        self.assertEqual(type(response), HttpResponse)
        self.assertEqual(self.payment.status, PaymentStatus.CONFIRMED)

    def test_process_data_payment_rejected(self):
        """BorgunProvider.process_data() returns a correct HTTP response"""
        self.assertEqual(self.payment2.status, PaymentStatus.WAITING)
        request = MagicMock()
        request.POST = get_postdata_with_sha256(self.payment2, status='ERROR')
        provider = BorgunProvider(sandbox=True)
        response = provider.process_data(self.payment2, request)
        self.assertEqual(type(response), HttpResponse)
        self.assertEqual(self.payment2.status, PaymentStatus.REJECTED)

    def test_incorrect_process_data(self):
        """BorgunProvider.process_data() checks POST signature"""
        self.assertEqual(self.payment3.status, PaymentStatus.WAITING)
        request = MagicMock()
        request.POST = get_postdata_with_sha256(self.payment3, orderid='00000000', status='OK')
        provider = BorgunProvider(sandbox=True)
        response = provider.process_data(self.payment3, request)
        self.assertEqual(type(response), HttpResponseForbidden)
