//Search
document.addEventListener('DOMContentLoaded', function() {
    const searchIconWrapper = document.getElementById('searchIconWrapper');
    const searchForm = document.getElementById('searchForm');
    const searchInput = searchForm.querySelector('.search-input');
    const searchButton = searchForm.querySelector('.search-button');

    searchIconWrapper.addEventListener('click', function() {
        searchForm.classList.toggle('active');
        if (searchForm.classList.contains('active')) {
            searchInput.focus(); // Focus the input when it becomes active
        } else {
            searchInput.value = ''; // Clear input when collapsing
        }
    });

    // Optional: Hide search form if clicked outside (if desired)
    document.addEventListener('click', function(event) {
        if (!searchForm.contains(event.target) && !searchIconWrapper.contains(event.target)) {
            searchForm.classList.remove('active');
            searchInput.value = ''; // Clear input when collapsing
        }
    });
});

// How it works
document.addEventListener('DOMContentLoaded', function() {
    const timeline = document.getElementById('vertical-scrollable-timeline');
    const progressDiv = timeline.querySelector('.list-progress .inner'); // This is the div that will actually fill
    const timelineItems = timeline.querySelectorAll('li');

    function updateProgressBar() {
        const timelineRect = timeline.getBoundingClientRect();
        const viewportHeight = window.innerHeight;

        // Calculate how much of the timeline section is visible
        let visibleHeight = 0;
        if (timelineRect.top < 0 && timelineRect.bottom > 0) {
            visibleHeight = Math.min(viewportHeight, timelineRect.height + timelineRect.top);
        } else if (timelineRect.top >= 0 && timelineRect.top < viewportHeight) {
            visibleHeight = viewportHeight - timelineRect.top;
        } else if (timelineRect.top < 0 && timelineRect.bottom > viewportHeight) {
            visibleHeight = viewportHeight;
        }

        // Calculate progress percentage based on scroll
        let scrollProgress = 0;
        if (timelineRect.height > 0) {
            scrollProgress = (visibleHeight / timelineRect.height) * 100;
            // Cap progress at 100% and ensure it doesn't go below 0
            scrollProgress = Math.max(0, Math.min(100, scrollProgress));
        }

        // Apply the progress to the inner div height
        progressDiv.style.height = scrollProgress + '%';

        // Animate timeline items as they come into view
        timelineItems.forEach(item => {
            const itemRect = item.getBoundingClientRect();
            // If the item's top is within the viewport and its bottom is also within (or below) the viewport
            if (itemRect.top < window.innerHeight && itemRect.bottom > 0) {
                item.classList.add('in-view');
            } else {
                item.classList.remove('in-view'); // Optional: remove class if it scrolls out of view
            }
        });
    }

    // Call on scroll and initial load
    window.addEventListener('scroll', updateProgressBar);
    updateProgressBar(); // Initial call to set the state on page load
});


/* Toggle between adding and removing the "responsive" class to topnav when the user clicks on the icon */
function myFunction() {
    var x = document.getElementById("myNavLeft");
    if (x.className === "nav-left") {
        x.className += " responsive";
    } else {
        x.className = "nav-left";
    }
}