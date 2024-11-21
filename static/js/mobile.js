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

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Feather icons
    feather.replace();

    // Touch feedback for all interactive elements
    const touchElements = document.querySelectorAll('.action-item, .journey-step, .card');
    
    touchElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.2s ease';
        }, { passive: true });

        element.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        }, { passive: true });
    });

    // Smooth scrolling for recommendation cards
    const recommendationContainer = document.querySelector('.recommendation-cards');
    if (recommendationContainer) {
        let isScrolling = false;
        let startX;
        let scrollLeft;

        recommendationContainer.addEventListener('touchstart', (e) => {
            isScrolling = true;
            startX = e.touches[0].pageX - recommendationContainer.offsetLeft;
            scrollLeft = recommendationContainer.scrollLeft;
        }, { passive: true });

        recommendationContainer.addEventListener('touchmove', (e) => {
            if (!isScrolling) return;
            const x = e.touches[0].pageX - recommendationContainer.offsetLeft;
            const walk = (x - startX) * 2;
            recommendationContainer.scrollLeft = scrollLeft - walk;
        }, { passive: true });

        recommendationContainer.addEventListener('touchend', () => {
            isScrolling = false;
        }, { passive: true });
    }

    // Handle back navigation gesture
    let touchStartX = 0;
    
    document.addEventListener('touchstart', (e) => {
        touchStartX = e.touches[0].clientX;
    }, { passive: true });

    document.addEventListener('touchend', (e) => {
        const touchEndX = e.changedTouches[0].clientX;
        const deltaX = touchEndX - touchStartX;

        if (deltaX > 100) { // Right swipe - go back
            window.history.back();
        }
    }, { passive: true });
});