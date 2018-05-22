from __future__ import unicode_literals
import hashlib, hmac
from django import forms

from payments import PaymentStatus
from .helpers import to_bytes



class ProcessPaymentForm(forms.Form):
    status = forms.ChoiceField(required=True, choices=[
        ['Ok', 'Ok'],
        ['OK', 'Ok'],
        ['Cancel', 'Cancel'],
        ['CANCEL', 'Cancel'],
        ['Error', 'Error'],
        ['ERROR', 'Error'],
    ])
    orderhash = forms.CharField(required=True)
    orderid = forms.CharField(required=True)
    step = forms.ChoiceField(required=False, choices=[
        ['Payment','Payment'],
        ['Confirmation', 'Confirmation']
    ])

    def __init__(self, private_key, payment, **kwargs):
        self.payment = payment
        self.private_key = private_key
        super(ProcessPaymentForm, self).__init__(**kwargs)


    def clean(self):
        cleaned_data = super(ProcessPaymentForm, self).clean()
        if not self.errors:
            order_id = "PAYMENT%s" % self.payment.id
            if cleaned_data['orderid'] != order_id:
                self._errors['orderid'] = self.error_class(['Bad payment id (orderid field)'])

            hash_string = "{order_id}|{amount}|{currency}".format(
                order_id=order_id,
                amount=self.payment.total,
                currency=self.payment.currency
            )
            checkhash = hmac.new(
                to_bytes(self.private_key),
                msg=to_bytes(hash_string),
                digestmod=hashlib.sha256
            ).hexdigest()
            if checkhash != cleaned_data['orderhash']:
                self._errors['orderhash'] = self.error_class(['Bad hash'])
        return cleaned_data


    def save(self, *args, **kwargs):
        status = self.cleaned_data['status']
        step = self.cleaned_data.get('step', None) or ''
        if status.lower() == 'ok' and step.lower() == 'payment':
            self.payment.change_status(PaymentStatus.CONFIRMED)
        elif status.lower() == 'error':
            self.payment.change_status(PaymentStatus.REJECTED)
