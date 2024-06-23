document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const button = form.querySelector('button[type="submit"]');
            const spinner = button.querySelector('.spinner-border');
            const buttonText = button.querySelector('.button-text');
            
            spinner.classList.remove('d-none');
            buttonText.textContent = 'Processing...';
            button.disabled = true;
        });
    });
});

