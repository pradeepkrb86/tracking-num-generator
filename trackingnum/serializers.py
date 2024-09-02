from rest_framework import serializers
from django.core.validators import RegexValidator
from uuid import UUID
from datetime import datetime
from rest_framework.exceptions import ValidationError
from dateutil import parser
import pycountry

def validate_country_code(value):
    """Validate that the given value is a valid ISO 3166-1 alpha-2 country code."""
    if not pycountry.countries.get(alpha_2=value):
        raise ValidationError(f"'{value}' is not a valid ISO 3166-1 alpha-2 country code.")

class CustomDateTimeField(serializers.DateTimeField):
    def to_internal_value(self,value):
        try:
            parsed_datetime = parser.parse(value)
        except (ValueError,TypeError) as e:
            self.fail("invalid",format="RFC 3339",input=value)
        if isinstance(parsed_datetime,datetime):
            return parsed_datetime
        else:
            self.fail("invalid",format="RFC 3339",input=value)

class CustomerOrderDataSerializer(serializers.Serializer):
    origin_country_id = serializers.CharField(max_length=2,
                                              validators=[validate_country_code],
                                              required=True)
    destination_country_id = serializers.CharField(max_length=2,
                                              validators=[validate_country_code],
                                              required=True)
    weight = serializers.DecimalField(
        max_digits=10,
        decimal_places=3,
        required=True
    )
    created_at = CustomDateTimeField(required=True)
    customer_id = serializers.UUIDField(required=True)
    customer_name = serializers.CharField(required=True)
    customer_slug = serializers.SlugField(required=True)

    def validate_created_at(self, value):
        if value > datetime.now(value.tzinfo):
            raise ValidationError("created_at cannot be in the future.")
        return value
