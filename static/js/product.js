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

// ========== QUANTITY CONTROLS ==========
function changeQty(delta) {
    const input = document.getElementById('qtyInput');
    let val = parseInt(input.value) || 1;
    val = Math.min(Math.max(val + delta, 1), 99);
    input.value = val;
}

// ========== ADD TO CART ==========
let cartCount = 0;
const badge = document.getElementById('cartCount');

// ========== ADD TO CART (delegated) ==========
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.add-to-cart-btn');
    if (!btn) return;

    const productId = btn.dataset.id;
    if (!productId) {
        console.warn('No product ID found on button');
        return;
    }

    // Get quantity from the input
    const qtyInput = document.getElementById('qtyInput');
    const qty = parseInt(qtyInput.value) || 1;

    // Call global cart function (from cart.js)
    window.addToCart(productId, qty)
        .then(() => {
            alertSuccess('Added to cart! 🛒');
        })
        .catch(err => {
            alertError('Could not add item. Please try again.');
            console.error(err);
        });

    // Visual feedback (keep this outside the promise chain)
    const orig = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-check"></i> Added!';
    btn.style.background = '#34D399';
    btn.style.color = '#0B170B';
    setTimeout(() => {
        btn.innerHTML = orig;
        btn.style.background = '';
        btn.style.color = '';
    }, 1500);
});