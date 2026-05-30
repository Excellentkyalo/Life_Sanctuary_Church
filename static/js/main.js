// static/js/main.js
// Life Sanctuary Church - JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Main.js loaded!');
    
    // ===== HAMBURGER MENU =====
    const hamburger = document.querySelector('.hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    console.log('Hamburger element:', hamburger);
    console.log('NavLinks element:', navLinks);
    
    if (hamburger && navLinks) {
        // Toggle menu on hamburger click
        hamburger.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle active class
            navLinks.classList.toggle('active');
            
            // Toggle hamburger icon (bars ↔ X)
            const icon = hamburger.querySelector('i');
            if (navLinks.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
            
            console.log('Menu toggled! Active:', navLinks.classList.contains('active'));
        });
        
        // Close menu when clicking a link
        const links = navLinks.querySelectorAll('a');
        links.forEach(function(link) {
            link.addEventListener('click', function() {
                navLinks.classList.remove('active');
                const icon = hamburger.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!hamburger.contains(e.target) && !navLinks.contains(e.target)) {
                navLinks.classList.remove('active');
                const icon = hamburger.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    // ===== MINISTRY TABS =====
    window.openTab = function(evt, tabName) {
        const card = evt.target.closest('.ministry-card');
        const tabContents = card.querySelectorAll('.tab-content');
        tabContents.forEach(function(content) {
            content.classList.remove('active');
            content.style.display = 'none';
        });
        
        const tabBtns = card.querySelectorAll('.tab-btn');
        tabBtns.forEach(function(btn) {
            btn.classList.remove('active');
        });
        
        const selectedTab = document.getElementById(tabName);
        if (selectedTab) {
            selectedTab.classList.add('active');
            selectedTab.style.display = 'block';
        }
        
        evt.currentTarget.classList.add('active');
    };
    
    // Initialize tabs
    document.querySelectorAll('.ministry-card').forEach(function(card) {
        const firstTabBtn = card.querySelector('.tab-btn');
        const firstTabContent = card.querySelector('.tab-content');
        if (firstTabBtn && firstTabContent) {
            card.querySelectorAll('.tab-content').forEach(function(content) {
                content.style.display = 'none';
            });
            firstTabContent.style.display = 'block';
            firstTabContent.classList.add('active');
            firstTabBtn.classList.add('active');
        }
    });
    
    // ===== NAVBAR SCROLL =====
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 100) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    console.log('All scripts ready!');
});