// ========== SIDEBAR TOGGLE (Mobile) ==========
function toggleSidebar() {
    document.getElementById('sidebar').classList.toggle('open');
    document.getElementById('sidebarOverlay').classList.toggle('active');
}

// Close sidebar on window resize to desktop
window.addEventListener('resize', function() {
    if (window.innerWidth > 768) {
        document.getElementById('sidebar').classList.remove('open');
        document.getElementById('sidebarOverlay').classList.remove('active');
    }
});

// ========== DELETE CONFIRMATION MODAL ==========
function openDeleteModal(id, name, type) {
    document.getElementById('deleteItemId').value = id;
    document.getElementById('deleteItemName').textContent = name;
    document.getElementById('deleteItemType').value = type;
    document.getElementById('deleteModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeDeleteModal() {
    document.getElementById('deleteModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Close on overlay click
document.getElementById('deleteModal').addEventListener('click', function(e) {
    if (e.target === this) closeDeleteModal();
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDeleteModal();
});

// Confirm delete
document.getElementById('confirmDeleteBtn').addEventListener('click', function() {
    const id = document.getElementById('deleteItemId').value;
    const type = document.getElementById('deleteItemType').value;

    const btn = this;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Deleting...';

    let url = '';
    if (type === 'order') {
        url = '/business/admin/api/delete-order/';
    } else if (type === 'product') {
        url = '/business/admin/api/delete-product/';
    } else {
        alertError('Unknown item type.');
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-trash-alt"></i> Delete';
        return;
    }

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify({ id: id })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alertSuccess('✅ Deleted successfully!');
            closeDeleteModal();
            setTimeout(() => location.reload(), 1200);
        } else {
            alertError('❌ Error: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        alertError('❌ Network error. Please try again.');
        console.error(err);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = '<i class="fas fa-trash-alt"></i> Delete';
        closeDeleteModal();
    });
});

// ========== EDIT MODAL ==========
function openEditModal(data) {
    const modal = document.getElementById('editModal');
    document.getElementById('editId').value = data.id;
    document.getElementById('editType').value = data.type;
    document.getElementById('editModalTitle').textContent = data.type === 'order' ? 'Order' : 'Product';

    document.getElementById('editName').value = data.name;

    const orderFields = document.getElementById('orderFields');
    const productFields = document.getElementById('productFields');
    if (data.type === 'order') {
        orderFields.style.display = 'block';
        productFields.style.display = 'none';
        document.getElementById('editStatus').value = data.status || 'pending';
        document.getElementById('editTotal').value = data.total || '0';
    } else {
        orderFields.style.display = 'none';
        productFields.style.display = 'block';
        document.getElementById('editPrice').value = data.price || '0';
        document.getElementById('editStock').value = data.stock || '0';
        document.getElementById('editAvailable').checked = data.available || false;
    }

    modal.style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeEditModal() {
    document.getElementById('editModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Click on edit buttons – populate and open modal
document.querySelectorAll('.admin-table .edit').forEach(btn => {
    btn.addEventListener('click', function() {
        const data = {
            id: this.dataset.id,
            type: this.dataset.type,
            name: this.dataset.name,
            status: this.dataset.status,
            total: this.dataset.total,
            price: this.dataset.price,
            stock: this.dataset.stock,
            available: this.dataset.available === 'true',
        };
        openEditModal(data);
    });
});

// Close modal on overlay click or Escape key
document.getElementById('editModal').addEventListener('click', function(e) {
    if (e.target === this) closeEditModal();
});
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeEditModal();
});

// ========== SAVE EDIT ==========
function saveEdit() {
    const id = document.getElementById('editId').value;
    const type = document.getElementById('editType').value;
    const payload = { id, type };

    if (type === 'order') {
        payload.status = document.getElementById('editStatus').value;
    } else {
        payload.price = parseFloat(document.getElementById('editPrice').value);
        payload.stock = parseInt(document.getElementById('editStock').value);
        payload.is_available = document.getElementById('editAvailable').checked;
    }

    const btn = document.getElementById('saveEditBtn');
    const origText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';

    fetch('/business/admin/api/update/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken(),
        },
        body: JSON.stringify(payload)
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alertSuccess('✅ Updated successfully!');
            closeEditModal();
            // Update row dynamically if possible, else reload after delay
            setTimeout(() => location.reload(), 1200);
        } else {
            alertError('❌ Error: ' + (data.error || 'Unknown error'));
            closeEditModal();
        }
    })
    .catch(err => {
        alertError('❌ Network error. Please try again.');
        console.error(err);
    })
    .finally(() => {
        btn.disabled = false;
        btn.innerHTML = origText;
        closeEditModal();
    });
}

// ========== LOGOUT with custom confirmation ==========
// Instead of native confirm, we'll use a custom modal (reuse delete modal style or create a separate one)
// For simplicity, we'll keep the native confirm but change the alert to a toast.
// However, we can create a small custom confirm modal.
// Here's a quick implementation using a custom confirm dialog:

function confirmAction(message, callback) {
    // You can build a reusable confirm modal here.
    // For brevity, we'll use the native confirm but show a toast on logout.
    if (confirm(message)) {
        alertSuccess('👋 Logging out...');
        // window.location.href = '/logout/';
    }
}



// ========== CSRF HELPER ==========
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') return value;
    }
    return '';
}

// ========== TABLE FILTER (from dashboard.js) ==========
// If you have this function in dashboard.js, you can keep it there.
// If you want to centralize, move it here.




// ========== LOGOUT MODAL ==========
function openLogoutModal() {
    document.getElementById('logoutModal').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function closeLogoutModal() {
    document.getElementById('logoutModal').style.display = 'none';
    document.body.style.overflow = '';
}

// Close on overlay click
document.getElementById('logoutModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeLogoutModal();
});

// Close on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeLogoutModal();
});

// ----- Confirm Logout: submit the hidden form -----
document.getElementById('confirmLogoutBtn')?.addEventListener('click', function() {
    const btn = this;
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging out...';
    // Submit the hidden form – will redirect to allauth logout
    document.getElementById('logoutForm').submit();
});

// ----- Trigger logout modal on link click -----
document.getElementById('logoutLink')?.addEventListener('click', function(e) {
    e.preventDefault();
    openLogoutModal();
});