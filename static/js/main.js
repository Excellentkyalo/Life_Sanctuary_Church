// static/js/main.js

// --- 1. LOADER LOGIC ---
window.addEventListener('load', () => {
    const loader = document.getElementById('loader');
    // Wait for progress bar animation (2.5s) then fade out
    setTimeout(() => {
        loader.style.opacity = '0';
        setTimeout(() => {
            loader.style.display = 'none';
            initHeroAnim();
        }, 1000);
    }, 2500);
});

// --- 2. MINISTRY TABS LOGIC ---
function openTab(evt, tabName) {
    // Find the parent card of the clicked button
    const card = evt.currentTarget.closest('.ministry-card');
    // Hide all tab content within this card
    const tabContents = card.getElementsByClassName("tab-content");
    for (let i = 0; i < tabContents.length; i++) {
        tabContents[i].classList.remove("active");
    }
    // Remove active class from all buttons within this card
    const tabLinks = card.getElementsByClassName("tab-btn");
    for (let i = 0; i < tabLinks.length; i++) {
        tabLinks[i].classList.remove("active");
    }
    // Show the current tab and add active class to button
    document.getElementById(tabName).classList.add("active");
    evt.currentTarget.classList.add("active");
}

// --- 3. MOBILE MENU TOGGLE ---
const mobileMenu = document.querySelector('.mobile-menu');
const navLinks = document.querySelector('.nav-links');
const navLinksItems = document.querySelectorAll('.nav-links a');

if (mobileMenu) {
    mobileMenu.addEventListener('click', () => {
        mobileMenu.classList.toggle('active');
        navLinks.classList.toggle('active');
        // Prevent body scroll when menu is open
        document.body.style.overflow = navLinks.classList.contains('active') ? 'hidden' : 'auto';
    });
}

if (navLinksItems) {
    navLinksItems.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            navLinks.classList.remove('active');
            document.body.style.overflow = 'auto';
        });
    });
}

// Close menu when clicking outside
document.addEventListener('click', (e) => {
    if (mobileMenu && navLinks) {
        if (!mobileMenu.contains(e.target) && !navLinks.contains(e.target)) {
            mobileMenu.classList.remove('active');
            navLinks.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    }
});

// --- 4. GSAP ANIMATIONS ---
if (typeof gsap !== 'undefined') {
    gsap.registerPlugin(ScrollTrigger);
}

function initHeroAnim() {
    const fadeElements = document.querySelectorAll('.fade-in');
    fadeElements.forEach(element => {
        if (typeof gsap !== 'undefined') {
            gsap.fromTo(element,
                { opacity: 0, y: 50 },
                {
                    opacity: 1, y: 0, duration: 1, ease: "power3.out",
                    scrollTrigger: {
                        trigger: element,
                        start: "top 85%",
                        toggleActions: "play none none reverse"
                    }
                }
            );
        } else {
            element.classList.add('visible');
        }
    });
}

// Navbar scroll effect
const navbar = document.querySelector('.navbar');
if (navbar) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 100) {
            navbar.style.background = 'rgba(45, 27, 78, 0.98)';
            navbar.style.padding = '0.8rem 5%';
        } else {
            navbar.style.background = 'rgba(45, 27, 78, 0.95)';
            navbar.style.padding = '1rem 5%';
        }
    });
}

// Counter animation for ministry stats
const counters = document.querySelectorAll('.stat-number');
if (typeof gsap !== 'undefined') {
    counters.forEach(counter => {
        const target = parseInt(counter.innerText);
        const suffix = counter.innerText.replace(/[0-9]/g, '');
        gsap.fromTo(counter,
            { innerHTML: 0 },
            {
                innerHTML: target,
                duration: 2,
                snap: { innerHTML: 1 },
                scrollTrigger: { trigger: counter, start: "top 85%" },
                onUpdate: function() {
                    counter.innerHTML = Math.ceil(this.targets()[0].innerHTML) + suffix;
                }
            }
        );
    });
}

// Handle window resize
let resizeTimer;
window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
        // Reset nav on resize if needed
        if (window.innerWidth > 968) {
            if (navLinks) navLinks.classList.remove('active');
            if (mobileMenu) mobileMenu.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    }, 250);
});