document.addEventListener('DOMContentLoaded', function() {
    // Toggle mobile menu
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const nav = document.querySelector('nav');
    
    if (mobileMenuBtn && nav) {
        mobileMenuBtn.addEventListener('click', function() {
            nav.classList.toggle('show');
        });
    }
    
    // Handle favorite buttons
    document.querySelectorAll('.favorite-btn').forEach(btn => {
        btn.addEventListener('click', async function(e) {
            e.preventDefault();
            const recipeId = this.dataset.recipeId;
            const isFavorite = this.classList.contains('active');
            
            try {
                const response = await fetch(isFavorite ? 
                    `/remove_favorite/${recipeId}` : 
                    `/save_favorite/${recipeId}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
                
                if (response.ok) {
                    this.classList.toggle('active');
                    this.innerHTML = this.classList.contains('active') ? 
                        '<i class="fas fa-heart"></i> Saved' : 
                        '<i class="far fa-heart"></i> Save';
                }
            } catch (error) {
                console.error('Error:', error);
            }
        });
    });
    
    // Handle form submissions with fetch
    document.querySelectorAll('form.ajax-form').forEach(form => {
        form.addEventListener('submit', async function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
            submitBtn.disabled = true;
            
            try {
                const response = await fetch(this.action, {
                    method: this.method,
                    body: formData,
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    if (data.redirect) {
                        window.location.href = data.redirect;
                    } else {
                        // Handle success message
                        showFlashMessage('Operation successful!', 'success');
                    }
                } else {
                    showFlashMessage(data.error || 'An error occurred', 'error');
                }
            } catch (error) {
                showFlashMessage('Network error occurred', 'error');
            } finally {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            }
        });
    });
});

function showFlashMessage(message, type) {
    const flashContainer = document.createElement('div');
    flashContainer.className = `flash-message ${type}`;
    flashContainer.textContent = message;
    
    const main = document.querySelector('main');
    if (main) {
        main.prepend(flashContainer);
        
        setTimeout(() => {
            flashContainer.remove();
        }, 5000);
    }
}