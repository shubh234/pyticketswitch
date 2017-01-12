from pyticketswitch.bundle import Bundle
from pyticketswitch.order import Order


class Trolley(object):

    def __init__(self, token=None, transaction_uuid=None, bundles=None, discarded_orders=None):
        self.token = token
        self.transaction_uuid = transaction_uuid
        self.bundles = bundles
        self.discarded_orders = discarded_orders

    @classmethod
    def from_api_data(cls, data):

        raw_contents = data.get('trolley_contents', {})

        if not raw_contents:
            raw_contents = data.get('reserved_trolley', {})

        raw_bundles = raw_contents.get('bundle', [])

        bundles = [
            Bundle.from_api_data(bundle)
            for bundle in raw_bundles
        ]

        raw_discarded_orders = data.get('discarded_orders', [])

        discarded_orders = [
            Order.from_api_data(order)
            for order in raw_discarded_orders
        ]

        kwargs = {
            'token': data.get('trolley_token'),
            'bundles': bundles,
            'discarded_orders': discarded_orders,
            'transaction_uuid': raw_contents.get('transaction_uuid')
        }

        return cls(**kwargs)