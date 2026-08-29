from django.views.generic import TemplateView
from products.models import Product

class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["products"] = Product.objects.all()[:4]  # Get the first 4 products
        return context


class AboutPageView(TemplateView):
    template_name = "pages/about.html"













