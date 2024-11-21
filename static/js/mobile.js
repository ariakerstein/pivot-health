document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Add touch feedback to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.2s';
        });

        card.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });

    // Handle pull-to-refresh
    let touchStart = 0;
    let touchEnd = 0;

    document.addEventListener('touchstart', function(e) {
        touchStart = e.touches[0].clientY;
    });

    document.addEventListener('touchend', function(e) {
        touchEnd = e.changedTouches[0].clientY;
        handleSwipe();
    });

    function handleSwipe() {
        const swipeDistance = touchEnd - touchStart;
        if (swipeDistance > 100 && window.scrollY === 0) {
            location.reload();
        }
    }

    // Add smooth scrolling to internal links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
});

// Add mobile-specific gesture handling
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', function(e) {
    touchStartX = e.touches[0].clientX;
});

document.addEventListener('touchend', function(e) {
    touchEndX = e.changedTouches[0].clientX;
    handleHorizontalSwipe();
});

function handleHorizontalSwipe() {
    const swipeDistance = touchEndX - touchStartX;
    const menu = document.getElementById('mobileMenu');
    const bsMenu = bootstrap.Offcanvas.getInstance(menu);
    
    // Swipe right to open menu
    if (swipeDistance > 100 && !menu.classList.contains('show')) {
        bsMenu.show();
    }
    // Swipe left to close menu
    else if (swipeDistance < -100 && menu.classList.contains('show')) {
        bsMenu.hide();
    }
}
