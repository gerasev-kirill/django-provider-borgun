# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import hashlib, hmac, six
from django.utils.translation import get_language
from django.http import HttpResponse, HttpResponseForbidden

from payments.core import BasicProvider
from .forms import ProcessPaymentForm
from .helpers import to_bytes




class BorgunProvider(BasicProvider):
    _method = 'post'

    def __init__(self, *args, **kwargs):
        self.merchant_id = kwargs.pop('merchant_id', None)
        self.payment_gateway_id = kwargs.pop('payment_gateway_id', None)
        self.private_key = kwargs.pop('private_key', None)
        self.language = kwargs.pop('language', None)
        sandbox = kwargs.pop('sandbox', True)
        if sandbox:
            self.endpoint = kwargs.pop("endpoint", "https://test.borgun.is/SecurePay/default.aspx")
            self.merchant_id = 9275444
            self.payment_gateway_id = 16
            self.private_key = 99887766
        else:
            self.endpoint = kwargs.pop("endpoint", "https://securepay.borgun.is/securepay/ticket.aspx")
        if not isinstance(self.private_key, six.string_types):
            self.private_key = six.text_type(self.private_key)
        if not self.merchant_id or not self.payment_gateway_id or not self.private_key:
            raise ValueError("Provide merchant_id, payment_gateway_id and private_key for BorgunProvider!")

        super(BorgunProvider, self).__init__(*args, **kwargs)
        if not self._capture:
            raise ImproperlyConfigured(
                'Borgun does not support pre-authorization.'
            )


    def get_language(self):
        lang = get_language() or self.language or 'en'
        lang = lang.split('-')[0].upper()
        allowed = [
            'IS', 'EN', 'DE', 'FR', 'RU', 'ES', 'IT', 'PT', 'SI',
            'HU', 'SE', 'NL', 'PL', 'NO', 'CZ', 'SK', 'HR', 'SR',
            'RO', 'DK', 'FI', 'FO'
        ]
        if lang not in allowed:
            return 'EN'
        return lang


    def get_action(self, payment):
        return self.endpoint


    def get_return_url(self, payment, extra_data=None):
        from django.conf import settings
        url = super(BorgunProvider, self).get_return_url(payment, extra_data=extra_data)
        if hasattr(settings, 'TEST_HOSTNAME'):
            return url.replace('localhost:8000', settings.TEST_HOSTNAME)
        return url


    def get_hidden_fields(self, payment):
        order_id = "PAYMENT%s" % payment.id
        hash_string = "{merchant_id}|{success_url}|{rerver_echo_url}|{order_id}|{amount}|{currency}".format(
            merchant_id=self.merchant_id,
            success_url=payment.get_success_url(),
            rerver_echo_url=self.get_return_url(payment),
            order_id=order_id,
            amount=payment.total,
            currency=payment.currency
        )
        checkhash = hmac.new(
            to_bytes(self.private_key),
            msg=to_bytes(hash_string),
            digestmod=hashlib.sha256
        ).hexdigest()

        data = {
            'merchantid': self.merchant_id,
            'paymentgatewayid': self.payment_gateway_id,
            'orderid': order_id,
            'checkhash': checkhash,
            'amount': payment.total,
            'currency': payment.currency,
            'language': self.get_language(),
            'returnurlsuccess': payment.get_success_url(),
            'returnurlerror': payment.get_failure_url(),
            'returnurlsuccessserver': self.get_return_url(payment)
        }
        i = 0
        for item in payment.get_purchased_items():
            data['itemdescription_%s'%i] = item.name
            data['itemcount_%s'%i] = item.quantity
            data['itemunitamount_%s'%i] = item.price
            data['itemamount_%s'%i] = item.quantity * item.price
            i += 1
        if not i:
            data['itemdescription_0'] = payment.description
            data['itemcount_0'] = 1
            data['itemunitamount_0'] = payment.total
            data['itemamount_0'] = payment.total
        return data


    def process_data(self, payment, request):
        form = ProcessPaymentForm(
            private_key=self.private_key,
            payment=payment,
            data=request.POST or None
        )
        if not form.is_valid():
            cleaned_data = getattr(form, 'cleaned_data', None) or {}
            if cleaned_data.get('step', None) == 'Payment':
                return HttpResponseForbidden('<PaymentNotification>Rejected</PaymentNotification>')
            return HttpResponseForbidden('Failed')
        form.save()
        return HttpResponse('<PaymentNotification>Accepted</PaymentNotification>')
