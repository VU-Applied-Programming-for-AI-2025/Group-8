document.addEventListener('DOMContentLoaded', function() {
    const authForm = document.querySelector('.auth-form');
    const registerForm = document.querySelector('.register-form');
    
    if (authForm) {
        authForm.addEventListener('submit', function(e) {
            const username = this.querySelector('input[name="username"]').value.trim();
            const password = this.querySelector('input[name="password"]').value.trim();
            
            if (!username || !password) {
                e.preventDefault();
                showError('Please fill in all fields');
            }
        });
    }
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                showError('Please fill in all required fields');
            }
        });
    }
});

function showError(message) {
    let errorDiv = document.querySelector('.error-message');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        const form = document.querySelector('.auth-form') || document.querySelector('.register-form');
        form.prepend(errorDiv);
    }
    
    errorDiv.textContent = message;
}