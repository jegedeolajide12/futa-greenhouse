# products/utils.py
from datetime import time, timedelta
from django.utils import timezone
from datetime import datetime

def calculate_delivery_date(order_created_at):
    """
    Returns a timezone-aware datetime for the scheduled delivery (start of window).
    - Sunday orders -> Monday next.
    - Weekday orders within 8am-5pm -> same day.
    - Weekday orders outside hours -> next business day (skip Sunday).
    """
    # Convert to local time (assuming WAT / UTC+1)
    local_time = timezone.localtime(order_created_at)
    weekday = local_time.weekday()          # 0=Monday, 6=Sunday
    order_time = local_time.time()

    # Business hours
    business_start = time(8, 0)
    business_end = time(17, 0)

    # If Sunday -> Monday
    if weekday == 6:
        delivery_date = local_time.date() + timedelta(days=1)
    else:
        # Check if within business hours
        if business_start <= order_time <= business_end:
            delivery_date = local_time.date()          # same day
        else:
            delivery_date = local_time.date() + timedelta(days=1)  # next day
            # If that next day is Sunday, push to Monday
            while delivery_date.weekday() == 6:
                delivery_date += timedelta(days=1)

    # Combine date with 8:00 AM (start of window)
    delivery_datetime = datetime.combine(delivery_date, time(8, 0))
    # Make it timezone-aware (use current timezone)
    return timezone.make_aware(delivery_datetime, timezone.get_current_timezone())