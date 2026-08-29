from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

class StaffRequiredMixin(LoginRequiredMixin):
    """Verify that the current user is staff."""
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied  # or redirect to a 'not allowed' page
        return super().dispatch(request, *args, **kwargs)




def staff_required(view_func):
    """Decorator to restrict access to staff users."""
    decorated_view = login_required(view_func)
    return user_passes_test(lambda u: u.is_staff)(decorated_view)