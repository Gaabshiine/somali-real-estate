document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent the form from submitting immediately

    // Get the submit button and modify its HTML to show the spinner
    var submitButton = document.getElementById('submitButton');
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Please wait...';
    submitButton.disabled = true;  // Disable the button to prevent multiple submits

    // Programmatically submit the form immediately
    setTimeout(() => {
        this.submit();  // This refers to the form
    });
});