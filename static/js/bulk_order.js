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

// ========== CART COUNTER (dummy) ==========
let cartCount = 0;
const badge = document.getElementById('cartCount');

// (Optional) Add to cart from this page – just a demo
// You could add a button, but for now it's just a placeholder.