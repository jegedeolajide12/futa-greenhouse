// Open order detail modal
function openOrderDetail(order) {
    document.getElementById('detailOrderId').textContent = '#' + order.id;
    document.getElementById('detailDate').textContent = order.date;
    document.getElementById('detailStatus').textContent = order.statusLabel;
    document.getElementById('detailStatus').className = 'order-status ' + order.status;

    // Items
    const itemsContainer = document.getElementById('detailItems');
    itemsContainer.innerHTML = order.items.map(item => `
        <div style="display: flex; justify-content: space-between; padding: 0.3rem 0; border-bottom: 1px solid rgba(255,255,255,0.04);">
            <span>${item.name} <span class="qty">×${item.qty}</span></span>
            <span style="color: var(--text-light);">₦${(item.price * item.qty).toLocaleString()}</span>
        </div>
    `).join('');

    document.getElementById('detailDeliveryDate').textContent = order.deliveryDate;
    document.getElementById('detailDeliveryTime').textContent = order.deliveryTime;
    document.getElementById('detailAddress').textContent = order.deliveryAddress;
    document.getElementById('detailTotal').textContent = '₦' + order.total.toLocaleString();

    // Show modal
    document.getElementById('orderDetailModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

// Close order detail modal
function closeOrderDetail() {
    document.getElementById('orderDetailModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Close on overlay click
document.addEventListener('click', function(e) {
    const overlay = document.getElementById('orderDetailModal');
    if (overlay && e.target === overlay) {
        closeOrderDetail();
    }
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeOrderDetail();
    }
});

// ========== RENDER ORDERS ==========
function renderOrders() {
    const container = document.getElementById('ordersList');
    const countSpan = document.getElementById('orderCount');

    if (!orders || orders.length === 0) {
        container.innerHTML = `
            <div class="empty-orders">
                <i class="fas fa-box-open"></i>
                <h2>No orders yet</h2>
                <p>You haven't placed any orders. Start shopping to see your orders here!</p>
                <a href="{% url 'products:shop' %}" class="btn-primary"><i class="fas fa-store"></i> Start Shopping</a>
            </div>
        `;
        countSpan.textContent = '0 orders';
        return;
    }

    countSpan.textContent = orders.length + ' order' + (orders.length > 1 ? 's' : '');

    container.innerHTML = orders.map(order => `
        <div class="order-card">
            <div class="order-header">
                <div>
                    <div class="order-id">#${order.id}</div>
                    <div class="order-date"><i class="far fa-calendar-alt"></i> ${order.date}</div>
                </div>
                <span class="order-status ${order.status}">${order.statusLabel}</span>
            </div>

            <div class="order-items">
                ${order.items.map(item => `
                    <span class="order-item">
                        ${item.name}
                        <span class="qty">×${item.qty}</span>
                        <span style="color: var(--text-muted); font-size: 0.8rem;">₦${(item.price * item.qty).toLocaleString()}</span>
                    </span>
                `).join('')}
            </div>

            <div class="order-footer">
                <div class="delivery-info">
                    <i class="fas fa-truck"></i>
                    <span>Delivery: <span class="delivery-date">${order.deliveryDate}</span></span>
                    <span style="color: var(--text-muted);">${order.deliveryTime}</span>
                    <span style="color: var(--text-muted);">•</span>
                    <span style="color: var(--text-muted); font-size: 0.85rem;" title="${order.deliveryAddress}">
                        <i class="fas fa-map-pin"></i> ${order.deliveryAddress.substring(0, 30)}${order.deliveryAddress.length > 30 ? '…' : ''}
                    </span>
                </div>
                <div style="display: flex; align-items: center; gap: 1rem;">
                    <span class="order-total">₦${order.total.toLocaleString()}</span>
                    <a href="#" class="btn-sm"><i class="fas fa-eye"></i> Details</a>
                </div>
            </div>
        </div>
    `).join('');

    // Add click handlers for "Details" buttons (same as before)
    document.querySelectorAll('.order-card .btn-sm').forEach((btn, index) => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const order = orders[index];
            openOrderDetail(order);
        });
    });
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
document.addEventListener('DOMContentLoaded', renderOrders);

// Expose toggleNav globally
window.toggleNav = toggleNav;