from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """
    Represents a single sellable item in the greenhouse.
    e.g., "Red Habanero Pepper" or "Yellow Bell Pepper"
    """
    
    # --- Categorization ---
    class CategoryChoices(models.TextChoices):
        HABANERO = 'habanero', 'Habanero Pepper'
        BELL = 'bell', 'Bell Pepper'
    
    class ColorChoices(models.TextChoices):
        RED = 'red', 'Red'
        YELLOW = 'yellow', 'Yellow'
        GREEN = 'green', 'Green'

    class GradeChoices(models.TextChoices):
        grade_a = 'A', 'Grade A'
        grade_b = 'B', 'Grade B'
        grade_c = 'C', 'Grade C'
    
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='products',
        help_text="Product category"
    )
    color = models.CharField(
        max_length=10,
        choices=ColorChoices.choices,
        default=ColorChoices.RED,
        help_text="Color variety"
    )
    grade = models.CharField(
        max_length=1,
        choices=GradeChoices.choices,
        default=GradeChoices.grade_a,
        help_text="Product grade"
    )

    # --- Core Details ---
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'Red Habanero Pepper')"
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,  # Auto-generated if left blank
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        help_text="Detailed description (taste, heat level, uses, etc.)"
    )
    
    # --- Pricing & Stock ---
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price per unit"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Optional discounted price"
    )
    
    class UnitChoices(models.TextChoices):
        KG = 'kg', 'Per Kilogram'
        HALF_KG = 'half_kg', 'Per Half Kg'
        QUARTER_KG = 'quarter_kg', 'Per Quarter Kg'
        PIECE = 'pc', 'Per Piece'
        BUNCH = 'bunch', 'Per Bunch'
    
    unit = models.CharField(
        max_length=10,
        choices=UnitChoices.choices,
        default=UnitChoices.KG,
        help_text="How is this sold? (e.g., by weight or count)"
    )
    
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Current available quantity"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Uncheck to hide product from the store (e.g., out of season)"
    )
    
    # --- Metadata ---
    featured_image = models.ImageField(
        upload_to='products/images/',
        blank=True,
        null=True,
        help_text="Main product photo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category', 'color']  # Groups peppers nicely in admin
        verbose_name = "Product"
        verbose_name_plural = "Products"
        # Ensure you don't accidentally create two identical products
        unique_together = ['category', 'color', 'grade', 'unit']  
    
    def __str__(self):
        return f"{self.get_color_display()} {self.category.name} ({self.grade}, {self.get_unit_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Build base slug from all attributes that make the product unique
            base_slug = slugify(
                f"{self.get_color_display()} "
                f"{self.category.name} "
                f"{self.grade} "
                f"{self.unit}"
            )
            # Ensure uniqueness
            slug = base_slug
            counter = 1
            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.slug})


class ProductImage(models.Model):
    """
    Allows multiple additional images per product (gallery view).
    """
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='products/gallery/')
    caption = models.CharField(max_length=150, blank=True)
    is_primary = models.BooleanField(
        default=False,
        help_text="Set as the main thumbnail if featured_image is empty"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"





class Order(models.Model):
    """
    Represents a customer order placed via the checkout.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    # Customer details (snapshot)
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    delivery_notes = models.TextField(blank=True)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(max_length=20, choices=[
        ('paystack', 'Paystack'),
        ('flutterwave', 'Flutterwave'),
        ('bank', 'Bank Transfer'),
    ], default='bank')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Orders'

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"


class OrderItem(models.Model):
    """
    Individual product line item within an order.
    """
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    # Optional reference to the original product (if product is later deleted, we still keep the snapshot)
    product = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )
    # Snapshot fields
    product_name = models.CharField(max_length=100)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.quantity} × {self.product_name}"

    @property
    def subtotal(self):
        return self.product_price * self.quantity


class Cart(models.Model):
    """
    Shopping cart – can be linked to a user or a session key.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # Ensure only one cart per user/session
        constraints = [
            models.UniqueConstraint(
                fields=['user'],
                condition=models.Q(user__isnull=False),
                name='unique_user_cart'
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                condition=models.Q(session_key__isnull=False),
                name='unique_session_cart'
            ),
        ]

    def __str__(self):
        if self.user:
            return f"Cart for {self.user.username}"
        return f"Cart for session {self.session_key}"

    def get_total(self):
        return sum(item.subtotal for item in self.items.all())

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    """
    Individual product in a cart.
    """
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    product = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        # A product can appear only once per cart
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.name}"

    @property
    def subtotal(self):
        # Use current product price (or discount price if applicable)
        price = self.product.discount_price if self.product.discount_price and self.product.discount_price < self.product.price else self.product.price
        return price * self.quantity



class BulkPricing(models.Model):
    """
    Defines bulk pricing for a product (e.g., crate of 5kg with tiered discounts).
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='bulk_prices',
        help_text="The pepper this bulk pricing applies to."
    )
    crate_weight_kg = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        help_text="Weight of one crate in kilograms (e.g., 5.00)"
    )
    # Tier 1: single crate
    single_crate_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price for 1 crate"
    )
    # Tier 2: 2-5 crates
    two_to_five_crate_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per crate when ordering 2-5 crates"
    )
    # Tier 3: 6+ crates
    six_plus_crate_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per crate when ordering 6 or more crates"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active bulk pricing will appear on the website"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['product', 'crate_weight_kg']
        verbose_name = "Bulk Pricing"
        verbose_name_plural = "Bulk Pricing"
        # Ensure one active pricing per product per weight
        unique_together = ['product', 'crate_weight_kg']

    def __str__(self):
        return f"{self.product.name} – {self.crate_weight_kg}kg crate"

    def discount_tier2(self):
        if self.single_crate_price and self.two_to_five_crate_price:
            return int(((self.single_crate_price - self.two_to_five_crate_price) / self.single_crate_price) * 100)
        return 0