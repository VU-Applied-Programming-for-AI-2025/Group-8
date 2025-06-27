/*=============== SHOW MENU ===============*/
const navMenu = document.getElementById('nav-menu'),
    navToggle = document.getElementById('nav-toggle'),
    navClose = document.getElementById('nav-close')

/*===== MENU SHOW =====*/
/* Validate if constant exists */
if (navToggle) {
    navToggle.addEventListener('click', () => {
        navMenu.classList.add('show-menu')
    })
}

/*===== MENU HIDDEN =====*/
/* Validate if constant exists */
if (navClose) {
    navClose.addEventListener('click', () => {
        navMenu.classList.remove('show-menu')
    })
}

/*=============== REMOVE MENU MOBILE ===============*/
const navLink = document.querySelectorAll('.nav__link')

function linkAction() {
    const navMenu = document.getElementById('nav-menu')
    // When we click on each nav__link, we remove the show-menu class
    navMenu.classList.remove('show-menu')
}
navLink.forEach(n => n.addEventListener('click', linkAction))

/*=============== GSAP ANIMATION ===============*/
// Ensure TweenMax (GSAP v2) library is loaded before this script.
// If you are using GSAP v3, the syntax will be slightly different (gsap.from, gsap.to, etc.)

// Animations for the home section elements
TweenMax.from('.home__title', 1, { delay: .2, opacity: 0, y: 20, ease: Expo.easeInOut });
TweenMax.from('.home__description', 1, { delay: .3, opacity: 0, y: 20, ease: Expo.easeInOut });
TweenMax.from('.home__button', 1, { delay: .4, opacity: 0, y: 20, ease: Expo.easeInOut });
TweenMax.from('.home__liquid', 1, { delay: .7, opacity: 0, y: 200, ease: Expo.easeInOut });
TweenMax.from('.home__juice', 1, { delay: 1.2, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__apple1', 1, { delay: 1.5, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__apple2', 1, { delay: 1.6, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__leaf:nth-child(1)', 2, { delay: 1.3, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__leaf:nth-child(2)', 2, { delay: 1.4, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__leaf:nth-child(3)', 2, { delay: 1.5, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__leaf:nth-child(4)', 2, { delay: 1.6, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__leaf:nth-child(5)', 2, { delay: 1.7, opacity: 0, y: -800, ease: Expo.easeInOut });
TweenMax.from('.home__leaf:nth-child(6)', 2, { delay: 1.8, opacity: 0, y: -800, ease: Expo.easeInOut });
// These apply to the input within the home section
TweenMax.from('.home__input', 1, { delay: .4, opacity: 0, y: 20, ease: Expo.easeInOut });
TweenMax.from('.home__form', 1, { delay: .4, opacity: 0, y: 20, ease: Expo.easeInOut });


document.addEventListener('DOMContentLoaded', () => {
    // JavaScript for custom accordion (if not using Bootstrap)
    const accordionButtons = document.querySelectorAll('.custom-accordion .accordion-button');

    accordionButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-bs-target');
            const targetCollapse = document.querySelector(targetId);
            const isCollapsed = button.classList.contains('collapsed');

            // Close all other open accordion items
            document.querySelectorAll('.custom-accordion .accordion-collapse.show').forEach(openCollapse => {
                if (openCollapse !== targetCollapse) {
                    openCollapse.classList.remove('show');
                    openCollapse.previousElementSibling.querySelector('.accordion-button').classList.add('collapsed');
                    openCollapse.previousElementSibling.querySelector('.accordion-button').setAttribute('aria-expanded', 'false');
                }
            });

            // Toggle current accordion item
            if (isCollapsed) {
                targetCollapse.classList.add('show');
                button.classList.remove('collapsed');
                button.setAttribute('aria-expanded', 'true');
            } else {
                targetCollapse.classList.remove('show');
                button.classList.add('collapsed');
                button.setAttribute('aria-expanded', 'false');
            }
        });
    });

    // Smooth scrolling for anchor links (if not handled by another library/framework)
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Timeline progress animation (simple version)
    const timelineSection = document.querySelector('.timeline-section');
    const timelineProgress = document.querySelector('.list-progress .inner');

    if (timelineSection && timelineProgress) {
        const observerOptions = {
            root: null,
            rootMargin: '0px',
            threshold: 0.1 // When 10% of the section is visible
        };

        const observer = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Animate progress bar to 100% when section enters viewport
                    timelineProgress.style.height = '100%';
                    timelineProgress.style.transition = 'height 1.5s ease-out';
                    observer.unobserve(entry.target); // Stop observing once animated
                } else {
                    // Reset height when not in view (optional, if you want it to re-animate on scroll back)
                    // timelineProgress.style.height = '0%';
                }
            });
        }, observerOptions);

        observer.observe(timelineSection);
    }

    // --- NEW: Search Bar Toggle Logic ---
    const searchIconWrapper = document.getElementById('searchIconWrapper');
    const searchForm = document.getElementById('searchForm');

    if (searchIconWrapper && searchForm) {
        searchIconWrapper.addEventListener('click', (event) => {
            event.stopPropagation(); // Prevent click from bubbling up to document and immediately closing
            searchForm.classList.toggle('active');
            // Optional: focus on the input field when it opens
            if (searchForm.classList.contains('active')) {
                searchForm.querySelector('.search-input').focus();
            }
        });

        // Close search form if clicked outside
        document.addEventListener('click', (event) => {
            // Check if the click was outside both the icon and the form
            if (!searchIconWrapper.contains(event.target) && !searchForm.contains(event.target)) {
                searchForm.classList.remove('active');
            }
        });

        // Prevent clicks inside the form from closing it (important for input/button interaction)
        searchForm.addEventListener('click', (event) => {
            event.stopPropagation();
        });
    }
});