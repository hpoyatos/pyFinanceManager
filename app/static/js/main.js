document.addEventListener('DOMContentLoaded', () => {
    // Current date in topbar
    const dateEl = document.getElementById('current-date');
    if (dateEl) {
        const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        dateEl.textContent = new Date().toLocaleDateString('pt-BR', options);
    }

    // Theme toggle
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) {
        // Check saved theme
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            document.body.setAttribute('data-theme', savedTheme);
            updateThemeIcon(savedTheme);
        }

        themeBtn.addEventListener('click', () => {
            const currentTheme = document.body.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.body.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }

    function updateThemeIcon(theme) {
        const icon = themeBtn.querySelector('i');
        if (theme === 'dark') {
            icon.className = 'fa-solid fa-sun';
        } else {
            icon.className = 'fa-solid fa-moon';
        }
    }
});
