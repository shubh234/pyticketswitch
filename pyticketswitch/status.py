from pyticketswitch.trolley import Trolley
from pyticketswitch.user import User
from pyticketswitch.utils import isostr_to_datetime
from pyticketswitch.country import Country
from pyticketswitch.mixins import JSONMixin
from pyticketswitch.address import Address


class Status(JSONMixin, object):
    """Describes the current state of a transaction

    Attributes:
        status (str): the currency status of the transaction.
        reserved_at (datetime.datetime): the date and time when the transaction
            was reserved.
        purchased_at (datetime.datetime): the date and time when the transaction
            was purchased.
        trolley (:class:`Trolley <pyticketswitch.trolley.Trolley>`): the
            contents of the transactions trolley.
        external_sale_page (str): the page that was rendered to the customer
            after the transaction was completed. This is only available if
            it was passed into the API at purchase time.
        languages (list): list of IETF language tags relevant to the
            transaction.
        remote_site (str): the remote site the transaction was reserved and
            purchased under.
        unreserved_orders (list): list of :class:`Orders
            <pyticketswitch.order.Order`>` that failed to reserve.
        prefilled_address (:class:`Address <pyticketswitch.address.Address>`):
            some address information that should be used to prefill any
            customer address fields. This is primarily used on B2B accounts.
        needs_payment_card (bool): When :obj:`True` indicates that this
            reservation will require :class:`CardDetails
            <pyticketswitch.payment_methods.CardDetails>` as the payment method
            at purchase time.
        needs_email_address (bool): When :obj:`True` indicates that the
            customer needs to provide a valid email address at purchase time.
        needs_agent_reference (bool): When :obj:`True` indicates that an agent
            reference should be provided at purchase time.
        can_edit_address (bool): When :obj:`False` indicates that the prefilled
            customer address provided by **prefilled_address** should not be
            edited.
        allowed_countries (list): list of :class:`Countries
            <pyticketswitch.country.Country>` that are acceptable for the
            customers postal address to be from.
        minutes_left (float): the number of minutes left before a reservation
            expires.

    """

    def __init__(self, status=None, reserved_at=None, trolley=None,
                 purchased_at=None, external_sale_page=None,
                 languages=None, remote_site=None, reserve_user=None,
                 prefilled_address=None, needs_payment_card=False,
                 needs_email_address=False, needs_agent_reference=False,
                 can_edit_address=False, allowed_countries=None,
                 minutes_left=None):

        self.status = status
        self.reserved_at = reserved_at
        self.purchased_at = purchased_at
        self.trolley = trolley
        self.external_sale_page = external_sale_page
        self.languages = languages
        self.remote_site = remote_site
        self.reserve_user = reserve_user
        self.prefilled_address = prefilled_address
        self.needs_payment_card = needs_payment_card
        self.needs_email_address = needs_email_address
        self.needs_agent_reference = needs_agent_reference
        self.can_edit_address = can_edit_address
        self.allowed_countries = allowed_countries
        self.minutes_left = minutes_left

    @classmethod
    def from_api_data(cls, data):
        """Creates a new Status object from API data from ticketswitch.

        Args:
            data (dict): the part of the response from a ticketswitch API call
                that concerns a transactions state.

        Returns:
            :class:`Status <pyticketswitch.status.Status>`: a new
            :class:`Status <pyticketswitch.status.Status>` object
            populated with the data from the api.

        """
        kwargs = {
            'status': data.get('transaction_status'),
            'trolley': Trolley.from_api_data(data),
            'remote_site': data.get('remote_site'),
            'can_edit_address': data.get('can_edit_address'),
            'needs_agent_reference': data.get('needs_agent_reference'),
            'needs_email_address': data.get('needs_email_address'),
            'needs_payment_card': data.get('needs_payment_card'),
            'minutes_left': data.get('minutes_left_on_reserve'),
        }

        reserved_raw = data.get('reserve_iso8601_date_and_time')
        if reserved_raw:
            kwargs.update(reserved_at=isostr_to_datetime(reserved_raw))

        purchased_raw = data.get('purchase_iso8601_date_and_time')
        if purchased_raw:
            kwargs.update(purchased_at=isostr_to_datetime(purchased_raw))

        external_sale_page_raw = data.get('external_sale_page_raw')
        if external_sale_page_raw:
            raise NotImplemented("don't know what this looks like yet")

        reserve_user_data = data.get('reserve_user')
        if reserve_user_data:
            reserve_user = User.from_api_data(reserve_user_data)
            kwargs.update(reserve_user=reserve_user)

        languages_raw = data.get('language_list')
        if languages_raw:
            kwargs.update(languages=languages_raw)

        allowed_countries = data.get('allowed_countries')
        if allowed_countries is not None:
            countries = [
                Country(key, description=description)
                for key, description in allowed_countries.items()
            ]
            countries.sort(key=lambda x: x.code)
            kwargs.update(allowed_countries=countries)

        address = data.get('prefilled_address')
        if address is not None:
            kwargs.update(prefilled_address=Address.from_api_data(address))

        return cls(**kwargs)
