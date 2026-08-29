// ========== CART DATA (Simulated – same as cart page) ==========
let cartItems = [{
    id: 1,
    name: 'Red Habanero',
    price: 1500,
    qty: 2,
    image: "{% static 'images/red-habanero.webp' %}"
}, {
    id: 3,
    name: 'Red Bell Pepper',
    price: 1200,
    qty: 3,
    image: "{% static 'images/red-bell-pepper.webp' %}"
}, {
    id: 4,
    name: 'Yellow Bell Pepper',
    price: 1300,
    qty: 1,
    image: "{% static 'images/yellow-bell-pepper.webp' %}"
}];

const deliveryFee = 500;

// ========== DOM REFS ==========
const orderItemsContainer = document.getElementById('orderItems');
const summarySubtotal = document.getElementById('summarySubtotal');
const summaryDelivery = document.getElementById('summaryDelivery');
const summaryTotal = document.getElementById('summaryTotal');
const navBadge = document.getElementById('navCartBadge');

// ========== RENDER ORDER SUMMARY ==========
function renderOrderSummary() {
    const totalItems = cartItems.reduce((sum, item) => sum + item.qty, 0);
    navBadge.textContent = totalItems;

    // Items list
    orderItemsContainer.innerHTML = cartItems.map(item => `
        <div class="order-item">
            <span class="item-name">
                ${item.name}
                <span class="qty-badge">×${item.qty}</span>
            </span>
            <span class="item-price">₦${(item.price * item.qty).toLocaleString()}</span>
        </div>
    `).join('');

    // Totals
    const subtotal = cartItems.reduce((sum, item) => sum + (item.price * item.qty), 0);
    const total = subtotal + deliveryFee;

    summarySubtotal.textContent = `₦${subtotal.toLocaleString()}`;
    summaryDelivery.textContent = `₦${deliveryFee.toLocaleString()}`;
    summaryTotal.textContent = `₦${total.toLocaleString()}`;
}

// ========== PAYMENT METHOD SELECTION ==========
let selectedPayment = 'paystack';

function selectPayment(el, method) {
    document.querySelectorAll('.payment-method').forEach(m => m.classList.remove('selected'));
    el.classList.add('selected');
    selectedPayment = method;
}

// ========== PLACE ORDER ==========
function placeOrder(e) {
    e.preventDefault();

    const btn = document.getElementById('placeOrderBtn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

    // Simulate order processing
    setTimeout(() => {
        btn.innerHTML = '<i class="fas fa-check"></i> Order Placed!';
        btn.style.background = '#34D399';
        btn.style.color = '#0B170B';

        // Show success message
        alert(
            '✅ Order placed successfully!\n\n' +
            'Order Summary:\n' +
            cartItems.map(i => `${i.name} × ${i.qty}`).join('\n') +
            `\n\nPayment Method: ${selectedPayment.toUpperCase()}` +
            `\nTotal: ${summaryTotal.textContent}\n` +
            `\nWe\'ll send a confirmation to your email shortly.`
        );

        // Reset
        btn.disabled = false;
        btn.innerHTML = originalText;
        btn.style.background = '';
        btn.style.color = '';

        // In a real app, redirect to thank-you page or payment gateway
        // window.location.href = "/order-confirmation/";

    }, 2000);
}

// ========== NAV TOGGLE ==========
function toggleNav() {
    document.getElementById('navLinks').classList.toggle('active');
}
document.addEventListener('click', function(e) {
    const nav = document.getElementById('navLinks');
    const ham = document.getElementById('hamburger');
    if (nav.classList.contains('active') && !nav.contains(e.target) && !ham.contains(e.target)) {
        nav.classList.remove('active');
    }
});

// ========== INIT ==========
document.addEventListener('DOMContentLoaded', renderOrderSummary);

// Expose functions globally for inline use
window.selectPayment = selectPayment;
window.placeOrder = placeOrder;