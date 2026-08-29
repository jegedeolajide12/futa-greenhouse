// ========== CART DROPDOWN ==========

function updateCartBadge(count) {
    const badge = document.getElementById('cartCount');
    if (badge) badge.textContent = count;
}

function renderCartDropdown(items, total) {
    const container = document.getElementById('cartItemsContainer');
    const totalSpan = document.getElementById('cartTotal');
    const countSpan = document.getElementById('cartItemCount');
    if (!container) return;

    if (!items || items.length === 0) {
        container.innerHTML = `
            <div class="cart-empty">
                <i class="fas fa-shopping-bag"></i>
                Your cart is empty.
            </div>
        `;
        if (totalSpan) totalSpan.textContent = '₦0';
        if (countSpan) countSpan.textContent = '0 items';
        return;
    }

    let html = '';
    items.forEach(item => {
        const imageUrl = item.image || '/static/images/placeholder.jpg';
        html += `
            <div class="cart-item" data-id="${item.id}">
                <img src="${imageUrl}" alt="${item.name}" loading="lazy" />
                <div class="item-info">
                    <div class="item-name">${item.name}</div>
                    <div class="item-details">
                        <span class="qty">Qty: ${item.quantity}</span>
                        <span>₦${item.price.toFixed(0)} / ${item.unit || 'unit'}</span>
                    </div>
                </div>
                <div class="item-price">₦${item.subtotal.toFixed(0)}</div>
                <button class="remove-btn" onclick="removeFromCart('${item.id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
    });

    container.innerHTML = html;
    if (totalSpan) totalSpan.textContent = `₦${total.toFixed(0)}`;
    if (countSpan) countSpan.textContent = `${items.reduce((sum, i) => sum + i.quantity, 0)} items`;
}

function fetchCart() {
    fetch(CART_ITEMS_URL)
        .then(res => res.json())
        .then(data => {
            updateCartBadge(data.count);
            renderCartDropdown(data.items, data.total);
        })
        .catch(err => console.error('Cart fetch error:', err));
}

// ========== CART DROPDOWN ==========

// Make it global and return the fetch promise
window.addToCart = function(productId, quantity = 1) {
    return fetch(CART_ADD_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ product_id: productId, quantity: quantity })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_count);
            fetchCart(); // refresh dropdown
            return data; // return data so caller can use it
        } else {
            throw new Error(data.message || 'Failed to add item');
        }
    });
};

// --- Remove from Cart (returns Promise) ---
window.removeFromCart = function(productId) {
    return fetch(CART_REMOVE_URL, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ product_id: productId })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            updateCartBadge(data.cart_count);
            fetchCart();
            alertSuccess('Item removed from cart.'); // <-- auto toast
            return data;
        } else {
            alertError('Could not remove item.');
            throw new Error(data.message || 'Failed');
        }
    })
    .catch(err => {
        alertError('Something went wrong.');
        console.error(err);
        throw err;
    });
};

function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }
    return '';
}

// Close dropdown when clicking outside
document.addEventListener('click', function(e) {
    const cartIcon = document.getElementById('cartToggle');
    const dropdown = document.getElementById('cartDropdown');
    if (cartIcon && dropdown && !cartIcon.contains(e.target)) {
        // Hover-based: no need to close on click, but we keep it for accessibility
    }
});

// Load cart on page load
document.addEventListener('DOMContentLoaded', function() {
    fetchCart();
});