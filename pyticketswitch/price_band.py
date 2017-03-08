from pyticketswitch.cost_range import CostRange
from pyticketswitch.discount import Discount
from pyticketswitch.seat import Seat, SeatBlock
from pyticketswitch.mixins import JSONMixin


class PriceBand(JSONMixin, object):
    """Describes a set of tickets with the same ticket type and price.

    Attributes:
        code (str): the price band identifier.
        default_discount (:class:`Discount <pyticketswitch.discount.Discount>`):
            this is the discount that will be assumed if no other discount
            is specified at reservation time. It holds the prices for the price
            band.
        description (str): human readable description of the price band if
            available.
        cost_range (:class:`CostRange <pyticketswitch.cost_range.CostRange>`):
            summary data for the price band including offers.
        no_singles_cost_range (:class:`CostRange <pyticketswitch.cost_range.CostRange>`):
            summary data for the price band including offers.
        example_seats (list): list of :class:`Seats <pyticketswitch.seat.Seat>`
            that can be used as examples of what the user might get when they
            reserved tickets in this price band.
        example_seats_are_real (bool): when :obj:`True` this field indicates
            that the example seats are in fact real seats and will be the ones
            we attempt to reserve at the reservation stage. When :obj:`False`
            these seats merely examples retrieved from cached data, and have
            likely already been purchased.
        seat_blocks (list): list of
            :class:`SeatBlocks <pyticketswitch.seat.SeatBlock>`. When available
            this are the contiguous seats that are available for purchase.
            :class:`SeatBlocks <pyticketswitch.seat.SeatBlock>` contain
            :class:`Seats <pyticketswitch.seat.Seat>`.

    """

    def __init__(self, code, default_discount, description=None,
                 cost_range=None, no_singles_cost_range=None,
                 example_seats=None, example_seats_are_real=True,
                 seat_blocks=None):

        self.code = code
        self.description = description
        self.cost_range = cost_range
        self.no_singles_cost_range = no_singles_cost_range
        self.default_discount = default_discount
        self.example_seats = example_seats
        self.example_seats_are_real = example_seats_are_real
        self.seat_blocks = seat_blocks

    @classmethod
    def from_api_data(cls, data):
        """Creates a new **PriceBand** object from API data from ticketswitch.

        Args:
            data (dict): the part of the response from a ticketswitch API call
                that concerns a price band.

        Returns:
            :class:`PriceBand <pyticketswitch.order.PriceBand>`: a new
            :class:`PriceBand <pyticketswitch.order.PriceBand>` object
            populated with the data from the api.

        """
        api_cost_range = data.get('cost_range', {})
        api_no_singles_cost_range = api_cost_range.get('no_singles_cost_range', {})
        cost_range = None
        no_singles_cost_range = None

        if api_cost_range:
            api_cost_range['singles'] = True
            cost_range = CostRange.from_api_data(api_cost_range)

        if api_no_singles_cost_range:
            api_no_singles_cost_range['singles'] = False
            no_singles_cost_range = CostRange.from_api_data(
                api_no_singles_cost_range)

        discount = Discount.from_api_data(data)

        kwargs = {
            'code': data.get('price_band_code', None),
            'description': data.get('price_band_desc', None),
            'cost_range': cost_range,
            'no_singles_cost_range': no_singles_cost_range,
            'default_discount': discount,
            'example_seats_are_real': data.get('example_seats_are_real', True),
        }

        example_seats_data = data.get('example_seats')
        if example_seats_data:
            example_seats = [
                Seat.from_api_data(seat)
                for seat in example_seats_data
            ]
            kwargs.update(example_seats=example_seats)

        seat_block_data = data.get('free_seat_blocks')
        if seat_block_data:
            seat_blocks = [
                SeatBlock.from_api_data(seat_block)
                for seat_block in seat_block_data.get('seat_block', [])
            ]
            kwargs.update(seat_blocks=seat_blocks)

        return cls(**kwargs)

    def get_seats(self):
        """Get all seats in child seat blocks

        Returns:
            list: list of :class:`Seats <pyticketswitch.seat.Seat>`.

        """
        if not self.seat_blocks:
            return []

        return [
            seat
            for seat_block in self.seat_blocks
            for seat in seat_block.seats or []
        ]

    def __repr__(self):
        if self.description:
            return u'<PriceBand {}:{}>'.format(self.code, self.description)
        return u'<PriceBand {}>'.format(self.code)
