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