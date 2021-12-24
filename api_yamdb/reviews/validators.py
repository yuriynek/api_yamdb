from datetime import datetime

from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _


def validate_year(value):
    if value < 0:
        raise ValidationError(_('Year can not be less than zero!'),
                              code='invalid')
    if value > datetime.today().year:
        raise ValidationError(_('Year can not be more than current year!'),
                              code='invalid')
