$(document).ready(function() {
    $('#dataTable').DataTable();

    const darkModeToggle = document.getElementById('darkModeToggle');
    const icon = darkModeToggle.querySelector('i');
    const body = document.body;

    // Check localStorage for dark mode setting
    if (localStorage.getItem('darkMode') === 'enabled') {
        body.classList.add('dark-mode');
        icon.classList.remove('bi-moon');
        icon.classList.add('bi-sun');
    }

    darkModeToggle.addEventListener('click', () => {
        body.classList.toggle('dark-mode');
        if (body.classList.contains('dark-mode')) {
            localStorage.setItem('darkMode', 'enabled');
            icon.classList.remove('bi-moon');
            icon.classList.add('bi-sun');
        } else {
            localStorage.setItem('darkMode', 'disabled');
            icon.classList.remove('bi-sun');
            icon.classList.add('bi-moon');
        }
    });
});
