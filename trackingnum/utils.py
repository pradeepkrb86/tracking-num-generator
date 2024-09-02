from datetime import datetime
import pytz
from .models import TrackingNumber
from django.db import IntegrityError
def create_tracking_number(origin_country_id,destination_country_id,customer_id):
    origin_part = origin_country_id.upper()
    destination_part = destination_country_id.upper()
    customer_id_part = customer_id.replace('-','')[:12].upper()
    current_time = datetime.now(pytz.utc)
    timezone = pytz.timezone('Asia/Singapore')
    local_time = current_time.astimezone(timezone)
    formatted_time = local_time.strftime('%Y-%m-%dT%H:%M:%S%z')
    # Adjust the offset format to include a colon (e.g., +08:00 instead of +0800)
    created_at = f"{formatted_time[:-2]}:{formatted_time[-2:]}"
    tracking_number = generate_tracking_number(
        origin_part, destination_part, customer_id_part
    )
    attempt = 0 
    while True:
         try:
             TrackingNumber.objects.create(tracking_number=tracking_number, created_at=created_at)
             break
         except IntegrityError:
             attempt += 1
             tracking_number= generate_alternate_tracking_number(origin_part,destination_part,customer_id_part,attempt)
             if attempt > 50:  # Safety limit to prevent infinite loop
                raise Exception("Failed to generate a unique tracking number after multiple attempts.")
         except Exception as e:
             print("error from db is",e)
    return tracking_number,created_at


def generate_tracking_number(origin_part, destination_part, customer_id_part):
    """Generate the initial tracking number based on the provided inputs."""
    tracking_number = f"{origin_part}{destination_part}{customer_id_part}"
    return tracking_number[:16]

def generate_alternate_tracking_number(origin_part, destination_part, customer_id_part,attempt):
    """Generate alternate tracking numbers by modifying customer ID, customer name, or timestamp."""
    # Iterate by increasing the attempt number

    # Generate the new tracking number including attempt
    new_tracking_number = generate_tracking_number(
        origin_part, destination_part, customer_id_part
    )
    return new_tracking_number[:16-len(str(attempt))]+str(attempt)
