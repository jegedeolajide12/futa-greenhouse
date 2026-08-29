from django.contrib import admin
from django.utils.html import format_html
from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect
from django.urls import reverse

from .models import OrderItem, Product, ProductImage, BulkPricing, Order, Cart, CartItem


class ProductImageInline(admin.TabularInline):
    """
    Allows adding/editing multiple product images directly 
    on the Product admin page (no need for a separate admin).
    """
    model = ProductImage
    extra = 1  # One empty blank form to start
    fields = ('image', 'caption', 'is_primary')
    readonly_fields = ('uploaded_at',)
    # Show a thumbnail preview in the inline (optional but nice)
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="60" height="60" style="object-fit:cover;" />', obj.image.url)
        return "-"
    image_tag.short_description = 'Preview'
    fields = ('image_tag', 'image', 'caption', 'is_primary', 'uploaded_at')
    readonly_fields = ('uploaded_at', 'image_tag')  # image_tag is readonly, but image field is editable

class StockFilter(SimpleListFilter):
    title = 'stock status'
    parameter_name = 'stock_status'

    def lookups(self, request, model_admin):
        return (
            ('in_stock', 'In Stock (> 0)'),
            ('out_of_stock', 'Out of Stock (0)'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'in_stock':
            return queryset.filter(stock__gt=0)
        if self.value() == 'out_of_stock':
            return queryset.filter(stock=0)
        return queryset


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Main admin configuration for the Product model.
    """
    # --- List view (the table of all products) ---
    list_display = (
        'id', 
        'product_name_display',  # custom method below
        'category', 
        'color', 
        'price', 
        'unit',
        'stock', 
        'stock_status',         # colored indicator
        'is_available',
        'has_images_preview',   # shows if product has gallery images
    )
    
    list_filter = (
        'category', 
        'color', 
        'unit', 
        'is_available',
        StockFilter,  # custom filter for stock status
    )
    
    search_fields = (
        'name', 
        'description', 
        'slug'
    )
    
    ordering = ('-created_at',)
    
    # --- Edit form layout (the detail page) ---
    fieldsets = (
        ('Product Identity', {
            'fields': ('category', 'color', 'grade', 'name', 'slug', 'description')
        }),
        ('Pricing & Sales', {
            'fields': ('price', 'discount_price', 'unit'),
            'classes': ('wide',)
        }),
        ('Inventory Management', {
            'fields': ('stock', 'is_available'),
            'description': 'Set stock to 0 and uncheck "Available" to hide this product from the shop.'
        }),
        ('Main Image', {
            'fields': ('featured_image',),
            'classes': ('collapse',)  # collapsible section to save space
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
            'description': 'System timestamps (read-only)'
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'slug')  # slug is auto-generated, timestamps are read-only
    
    # --- Inline images ---
    inlines = [ProductImageInline]
    
    # --- Bulk actions (dropdown at top of list) ---
    actions = ['make_available', 'make_unavailable', 'duplicate_products']
    
    # --- Custom methods for list display ---

    def product_name_display(self, obj):
        """Returns a bolded, colored name for quick scanning."""
        color_hex = '#DC143C' if obj.color == 'red' else '#FFD700'  # crimson red / gold
        return format_html(
            '<span style="font-weight:bold; color:{};">{}</span>',
            color_hex,
            obj.name
        )
    product_name_display.short_description = 'Product'
    product_name_display.admin_order_field = 'name'
    
    def stock_status(self, obj):
        """Color-coded stock indicator."""
        if obj.stock <= 0:
            return format_html('<span style="color:red;font-weight:bold;">⚠ Out of Stock</span>')
        elif obj.stock <= 10:
            return format_html('<span style="color:orange;">⚠ Low ({})</span>', obj.stock)
        else:
            return format_html('<span style="color:green;">✓ In Stock ({})</span>', obj.stock)
    stock_status.short_description = 'Stock Status'
    stock_status.admin_order_field = 'stock'
    
    def has_images_preview(self, obj):
        """Show a green check or red cross if images exist."""
        count = obj.images.count()
        if count > 0:
            return format_html('✅ {} images', count)
        return '❌ No gallery'
    has_images_preview.short_description = 'Gallery'
    
    # --- Custom Bulk Actions ---

    @admin.action(description='✅ Mark selected as AVAILABLE')
    def make_available(self, request, queryset):
        updated = queryset.update(is_available=True)
        self.message_user(request, f'{updated} product(s) marked as available.')
    
    @admin.action(description='❌ Mark selected as UNAVAILABLE')
    def make_unavailable(self, request, queryset):
        updated = queryset.update(is_available=False)
        self.message_user(request, f'{updated} product(s) marked as unavailable.')
    
    @admin.action(description='📋 Duplicate selected products (copy with "Copy of" prefix)')
    def duplicate_products(self, request, queryset):
        """
        Creates a duplicate of each selected product, 
        appending "Copy of" to the name.
        """
        duplicated_count = 0
        for product in queryset:
            # We need to copy the product without the primary key
            old_pk = product.pk
            product.pk = None  # Django will create a new instance
            product.name = f"Copy of {product.name}"
            product.slug = f"copy-{product.slug}"  # avoid slug conflicts
            product.stock = 0  # reset stock for the copy
            product.is_available = False
            product.save()
            
            # Copy gallery images too (optional but thorough)
            for img in ProductImage.objects.filter(product_id=old_pk):
                img.pk = None
                img.product = product
                img.save()
            
            duplicated_count += 1
        
        self.message_user(request, f'{duplicated_count} product(s) duplicated successfully.')

    # --- Save logic: auto-set name if not provided ---
    def save_model(self, request, obj, form, change):
        # If name is empty, build it from category + color
        if not obj.name:
            obj.name = f"{obj.get_color_display()} {obj.category.name}"
        super().save_model(request, obj, form, change)


# Optional: You can also register ProductImage separately if you want a standalone view,
# but it's already handled via inline above.
# @admin.register(ProductImage)
# class ProductImageAdmin(admin.ModelAdmin):
#     list_display = ('product', 'image_tag', 'is_primary')





@admin.register(BulkPricing)
class BulkPricingAdmin(admin.ModelAdmin):
    list_display = ('product', 'crate_weight_kg', 'single_crate_price', 'two_to_five_crate_price', 'six_plus_crate_price', 'is_active')
    list_filter = ('is_active', 'product__category', 'product__color')
    search_fields = ('product__name',)
    list_editable = ('single_crate_price', 'two_to_five_crate_price', 'six_plus_crate_price', 'is_active')
    autocomplete_fields = ('product',)
    fieldsets = (
        (None, {
            'fields': ('product', 'crate_weight_kg')
        }),
        ('Tiered Pricing (per crate)', {
            'fields': ('single_crate_price', 'two_to_five_crate_price', 'six_plus_crate_price'),
            'description': 'Prices are per crate. Discount tiers: 1 crate, 2-5 crates, 6+ crates.'
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product_name', 'product_price', 'quantity', 'unit')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email', 'total', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('full_name', 'email', 'id')
    readonly_fields = ('subtotal', 'delivery_fee', 'total', 'created_at', 'updated_at')
    inlines = [OrderItemInline]
    

admin.site.register(Cart)
admin.site.register(CartItem)