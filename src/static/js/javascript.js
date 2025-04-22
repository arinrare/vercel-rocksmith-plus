document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const hamburger = document.querySelector('.hamburger');
    const nav = document.querySelector('.main-nav');
    const bandForm = document.getElementById('bandForm');
    const genreForm = document.getElementById('genreForm');
    const showBandForm = document.getElementById('showBandForm');
    const showGenreForm = document.getElementById('showGenreForm');

    // Track selected genres
    let selectedGenres = new Set();

    // Mobile Navigation
    hamburger.addEventListener('click', () => {
        nav.classList.toggle('active');
        hamburger.classList.toggle('active');
    });

    // Initialize forms
    genreForm.classList.add('inactive');

    // Form switching handlers
    showBandForm.addEventListener('click', () => {
        bandForm.hidden = false;
        genreForm.hidden = true;
        showBandForm.classList.add('active');
        showGenreForm.classList.remove('active');
        bandForm.classList.remove('inactive');
        genreForm.classList.add('inactive');
    });
 
    showGenreForm.addEventListener('click', () => {
        bandForm.hidden = true;
        genreForm.hidden = false;
        showGenreForm.classList.add('active');
        showBandForm.classList.remove('active');
        genreForm.classList.remove('inactive');
        bandForm.classList.add('inactive');
    });

    // Genre selection management
    function updateGenreOptions(currentSelect = null) {
        const allSelects = document.querySelectorAll('#genreForm select');
        
        selectedGenres.clear();
        allSelects.forEach(select => {
            if (select !== currentSelect && select.value) {
                selectedGenres.add(select.value);
            }
        });

        allSelects.forEach(select => {
            Array.from(select.options).forEach(option => {
                if (option.value) {
                    if (select.value === option.value) {
                        option.disabled = false;
                    } else {
                        option.disabled = selectedGenres.has(option.value);
                    }
                }
            });
        });
    }

    // Add band input handler
    document.getElementById('addBand').addEventListener('click', () => {
        const template = document.querySelector('.band-input').cloneNode(true);
        template.querySelector('input').value = '';
        const selects = template.querySelectorAll('select');
        selects.forEach(select => select.value = '');
        template.querySelector('.remove-btn').hidden = false;
        document.getElementById('bandInputs').appendChild(template);
    });

    // Add genre input handler
    document.getElementById('addGenre').addEventListener('click', () => {
        const template = document.querySelector('.genre-input').cloneNode(true);
        const newSelect = template.querySelector('select');
        newSelect.value = '';
        template.querySelector('input').value = '';
        template.querySelector('.remove-btn').hidden = false;
        
        // Add change listener to new select
        newSelect.addEventListener('change', () => updateGenreOptions(newSelect));
        
        document.getElementById('genreInputs').appendChild(template);
        updateGenreOptions();
    });

    // Initialize genre select listeners
    document.querySelectorAll('#genreForm select').forEach(select => {
        select.addEventListener('change', () => updateGenreOptions(select));
    });

    // Remove button handler
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('remove-btn')) {
            const element = e.target.closest('.band-input, .genre-input');
            if (element) {
                element.remove();
                updateGenreOptions();
            }
        }
    });

    // Form submission handlers
    bandForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(bandForm);
        // TODO: Handle band form submission
        console.log('Band form submitted');
    });

    genreForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const formData = new FormData(genreForm);
        // TODO: Handle genre form submission
        console.log('Genre form submitted');
    });
});