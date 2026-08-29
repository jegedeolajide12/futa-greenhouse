

const grid = document.getElementById('productGrid');
const searchInput = document.getElementById('searchInput');
const resultCount = document.getElementById('resultCount');

function renderProducts(productsToRender) {
    if (productsToRender.length === 0) {
        grid.innerHTML = `
            <div class="no-results">
                <i class="fas fa-seedling"></i>
                <p>No peppers match your criteria. Try adjusting your filters!</p>
            </div>
        `;
        resultCount.textContent = '0';
        return;
    }

    grid.innerHTML = productsToRender.map(p => {
        // Determine badge color class based on grade
        let badgeClass = '';
        if (p.badge) {
            const badgeLower = p.badge.toLowerCase();
            if (badgeLower.includes('grade a') || badgeLower === 'a') badgeClass = 'grade-a';
            else if (badgeLower.includes('grade b') || badgeLower === 'b') badgeClass = 'grade-b';
            else if (badgeLower.includes('grade c') || badgeLower === 'c') badgeClass = 'grade-c';
            // fallback: if it's something else (e.g., "Premium"), keep it uncolored
        }

        // Build the price HTML with optional strikethrough
        const priceHtml = p.oldPrice ? `
            <div class="price-wrapper">
                <span class="old-price">₦${p.oldPrice.toLocaleString()}</span>
                <span class="current-price">₦${p.price.toLocaleString()} <small>/ ${p.unit}</small></span>
            </div>
        ` : `
            <div class="price-wrapper">
                <span class="current-price">₦${p.price.toLocaleString()} <small>/ ${p.unit}</small></span>
            </div>
        `;

        return `
            <div class="product-card" 
                data-id="${p.id}"
                data-name="${p.name}"
                data-price="${p.price}"
                data-type="${p.type}"
                data-color="${p.color}"
                data-stock="${p.stock}">
                ${p.badge ? `<span class="product-badge badge-left ${badgeClass}">${p.badge}</span>` : ''}

                ${p.discount ? `<span class="product-badge badge-right discount">${p.discount}</span>` : ''}
                <a href="/products/product/${p.slug}/" class="product-link">
                    <img src="${p.image}" alt="${p.name}" class="product-img" loading="lazy" />
                    <div class="name">${p.name}</div>
                </a>
                <div class="variant">${p.variant}</div>
                ${priceHtml}
                <span class="stock-tag ${p.stock === 'in' ? 'in' : 'pre'}">
                    ${p.stock === 'in' ? '<i class="fas fa-circle"></i>' : '<i class="fas fa-clock"></i>'} ${p.stockLabel}
                </span>
                <button class="btn-add-dark" data-id="${p.id}">
                    <i class="fas fa-plus"></i> ${p.stock === 'pre' ? 'Pre-Order' : 'Add to Cart'}
                </button>
            </div>
        `;
    }).join('');

    resultCount.textContent = productsToRender.length;
}
// After defining renderProducts, add this:
document.addEventListener('click', function(e) {
    const btn = e.target.closest('.btn-add-dark');
    if (!btn) return;

    const productId = btn.dataset.id;
    if (!productId) return;

    // Call the global addToCart from cart.js
   // Call the global addToCart from cart.js
    window.addToCart(productId, 1)
        .then(() => {
            // ✅ Success – show toast
            alertSuccess('Added to cart! 🛒');
        })
        .catch(err => {
            // ❌ Error – show error toast
            alertError('Could not add item. Please try again.');
            console.error(err);
        });

        // Visual feedback (optional – you can keep it or replace with toast only)
        const orig = btn.innerHTML;
        btn.innerHTML = '<i class="fas fa-check"></i> Added!';
        btn.style.background = '#34D399';
        btn.style.color = '#0B170B';
        btn.style.borderColor = '#34D399';
        setTimeout(() => {
            btn.innerHTML = orig;
            btn.style.background = '';
            btn.style.color = '';
            btn.style.borderColor = '';
        }, 1200);
    
});

function getActiveFilters() {
    const checks = document.querySelectorAll('.filter-check:checked');
    const filters = { type: [], color: [], stock: [] };
    checks.forEach(cb => {
        const key = cb.dataset.filter;
        if (filters[key]) filters[key].push(cb.value);
    });
    return filters;
}

function filterProducts() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const activeFilters = getActiveFilters();

    const filtered = products.filter(p => {
        const searchStr = (p.name + ' ' + p.variant).toLowerCase();
        if (searchTerm && !searchStr.includes(searchTerm)) return false;
        if (activeFilters.type.length > 0 && !activeFilters.type.includes(p.type)) return false;
        if (activeFilters.color.length > 0 && !activeFilters.color.includes(p.color)) return false;
        if (activeFilters.stock.length > 0 && !activeFilters.stock.includes(p.stock)) return false;
        return true;
    });

    renderProducts(filtered);
    sortProducts();
}

function sortProducts() {
    const sortVal = document.getElementById('sortSelect').value;
    const cards = Array.from(grid.querySelectorAll('.product-card'));
    if (cards.length === 0) return;

    const parent = grid;
    const sortedCards = cards.sort((a, b) => {
        const nameA = a.dataset.name;
        const nameB = b.dataset.name;
        const priceA = parseFloat(a.dataset.price);
        const priceB = parseFloat(b.dataset.price);

        switch (sortVal) {
            case 'price-low':
                return priceA - priceB;
            case 'price-high':
                return priceB - priceA;
            case 'name-asc':
                return nameA.localeCompare(nameB);
            case 'name-desc':
                return nameB.localeCompare(nameA);
            default:
                return parseInt(a.dataset.id) - parseInt(b.dataset.id);
        }
    });

    sortedCards.forEach(card => parent.appendChild(card));
}

function clearAllFilters() {
    document.querySelectorAll('.filter-check').forEach(cb => cb.checked = true);
    searchInput.value = '';
    document.getElementById('sortSelect').value = 'default';
    filterProducts();
}

let cartCount = 0;
const badge = document.getElementById('cartCount');



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

document.addEventListener('DOMContentLoaded', () => {
    renderProducts(products);
    sortProducts();
});
// ---------- HERO CAROUSEL ----------
// ---------- HERO CAROUSEL (OPTIMIZED) ----------
document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.hero-slide');
    const dotsContainer = document.getElementById('carouselDots');
    const heroTitle = document.getElementById('heroTitle');
    const heroSubtitle = document.getElementById('heroSubtitle');
    let currentSlide = 0;
    let slideInterval;

    // --- Preload all images FIRST ---
    function preloadImages() {
        slides.forEach(slide => {
            const bg = slide.querySelector('.slide-bg');
            const url = bg.style.backgroundImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
            if (url && !url.startsWith('radial')) {
                const img = new Image();
                img.src = url;
            }
        });
    }
    preloadImages(); // <-- Preload BEFORE dots & autoplay

    // --- Create Dots ---
    slides.forEach((slide, index) => {
        const dot = document.createElement('button');
        dot.className = 'dot' + (index === 0 ? ' active' : '');
        dot.setAttribute('data-index', index);
        dot.addEventListener('click', () => goToSlide(index));
        dotsContainer.appendChild(dot);
    });
    const dots = dotsContainer.querySelectorAll('.dot');

    // --- Go to slide ---
    function goToSlide(index) {
        slides.forEach(s => s.classList.remove('active'));
        dots.forEach(d => d.classList.remove('active'));
        slides[index].classList.add('active');
        dots[index].classList.add('active');

        const slide = slides[index];
        const title = slide.getAttribute('data-title');
        const subtitle = slide.getAttribute('data-subtitle');
        if (title) {
            const hasItalic = heroTitle.innerHTML.includes('<i>');
            if (hasItalic && title.includes('perfect')) {
                const parts = title.split('perfect');
                heroTitle.innerHTML = `${parts[0]}<i>perfect</i>${parts[1] || ''}`;
            } else {
                heroTitle.textContent = title;
            }
        }
        if (subtitle) heroSubtitle.textContent = subtitle;
        currentSlide = index;
    }

    function nextSlide() {
        goToSlide((currentSlide + 1) % slides.length);
    }

    function startCarousel() {
        if (slideInterval) clearInterval(slideInterval);
        slideInterval = setInterval(nextSlide, 5500);
    }

    // --- Pause on hover ---
    const heroSection = document.querySelector('.shop-hero');
    heroSection.addEventListener('mouseenter', () => clearInterval(slideInterval));
    heroSection.addEventListener('mouseleave', startCarousel);

    // --- Start ---
    goToSlide(0);
    startCarousel();
});



// ========== FILTER TOGGLE ==========
document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('filterToggle');
    const filterOptions = document.getElementById('filterOptions');
    const icon = toggleBtn.querySelector('i');

    toggleBtn.addEventListener('click', function(e) {
        e.stopPropagation(); // prevent event from bubbling
        filterOptions.classList.toggle('open');
        icon.classList.toggle('open');
        // Change icon text if you want (optional)
        if (filterOptions.classList.contains('open')) {
            icon.className = 'fas fa-chevron-up';
        } else {
            icon.className = 'fas fa-chevron-down';
        }
    });

    // On desktop, ensure the filters are always visible and icon is down
    // We'll use a media query listener or just trust the CSS defaults.
    // If you want to handle resize to keep state consistent, you can, but the CSS default covers it.
});