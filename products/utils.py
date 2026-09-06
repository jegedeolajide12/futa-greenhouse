from datetime import time, timedelta, datetime
from django.utils import timezone

def calculate_delivery_window(order_created_at):
    """
    Returns a tuple (delivery_start, delivery_end) as timezone-aware datetimes.
    - Sunday orders → Monday 8am-10am.
    - Weekday orders within 8am-5pm → same day, window starts 2 hours after order time,
      but the entire window must fit within 8am-5pm. If not, delivery moves to next business day.
    - Weekday orders outside 8am-5pm → next business day at 8am-10am.
    """
    local_time = timezone.localtime(order_created_at)
    weekday = local_time.weekday()          # 0=Monday, 6=Sunday
    order_time = local_time.time()
    business_start = time(8, 0)
    business_end = time(17, 0)

    # --- Determine the delivery date (same as before) ---
    if weekday == 6:  # Sunday → Monday
        delivery_date = local_time.date() + timedelta(days=1)
        start_time = time(8, 0)   # start of business day
    else:
        # Check if order is within business hours
        if business_start <= order_time <= business_end:
            delivery_date = local_time.date()
            # Proposed start = order_time + 2 hours
            proposed_start = (datetime.combine(delivery_date, order_time) + timedelta(hours=2)).time()
            proposed_end = (datetime.combine(delivery_date, proposed_start) + timedelta(hours=2)).time()
            # Ensure the entire window fits within business hours
            if proposed_start >= business_start and proposed_end <= business_end:
                start_time = proposed_start
            else:
                # Window would exceed business hours → move to next business day at 8am
                delivery_date += timedelta(days=1)
                while delivery_date.weekday() == 6:   # skip Sunday
                    delivery_date += timedelta(days=1)
                start_time = time(8, 0)
        else:
            # Outside business hours → next business day at 8am
            delivery_date = local_time.date() + timedelta(days=1)
            while delivery_date.weekday() == 6:
                delivery_date += timedelta(days=1)
            start_time = time(8, 0)

    # Build the start datetime
    delivery_start = datetime.combine(delivery_date, start_time)
    delivery_start = timezone.make_aware(delivery_start, timezone.get_current_timezone())

    # The window is exactly 2 hours long
    delivery_end = delivery_start + timedelta(hours=2)

    return delivery_start, delivery_end