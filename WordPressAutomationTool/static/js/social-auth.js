// Social authentication functionality for WordPress Automation Tool
document.addEventListener('DOMContentLoaded', function() {
    // Immediately apply fallback authentication since we're running in demo mode
    initFallbackAuth();
    
    function initFallbackAuth() {
        console.log('Initializing fallback authentication for all social providers');
        
        // Setup Google login buttons
        setupSocialButtons('.google-login', 'google');
        
        // Setup Facebook login buttons
        setupSocialButtons('.facebook-login', 'facebook');
        
        // Setup LinkedIn login buttons
        setupSocialButtons('.linkedin-login', 'linkedin');
        
        // Setup GitHub login buttons
        setupSocialButtons('.github-login', 'github');
    }
    
    // Setup click handlers for social buttons
    function setupSocialButtons(selector, provider) {
        const buttons = document.querySelectorAll(selector);
        if (buttons.length === 0) return;
        
        console.log(`Setting up ${provider} buttons:`, buttons.length);
        
        buttons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Show loading state
                const originalInnerHTML = this.innerHTML;
                
                // For Google button which has background image and hidden content
                if (provider === 'google') {
                    // Add a spinning overlay
                    this.style.position = 'relative';
                    const spinner = document.createElement('div');
                    spinner.className = 'spinner-overlay';
                    spinner.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                    spinner.style.position = 'absolute';
                    spinner.style.top = '0';
                    spinner.style.left = '0';
                    spinner.style.width = '100%';
                    spinner.style.height = '100%';
                    spinner.style.display = 'flex';
                    spinner.style.justifyContent = 'center';
                    spinner.style.alignItems = 'center';
                    spinner.style.backgroundColor = 'rgba(255,255,255,0.7)';
                    spinner.style.borderRadius = '8px';
                    this.appendChild(spinner);
                } else {
                    // For other buttons, replace content with spinner
                    this.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
                }
                
                this.disabled = true;
                
                console.log(`${provider} login button clicked`);
                
                // Simulate social login with delay for better UX
                setTimeout(() => {
                    // Process the simulated login
                    handleSimulatedLogin(provider);
                    
                    // Reset button state
                    if (provider === 'google') {
                        const spinner = this.querySelector('.spinner-overlay');
                        if (spinner) {
                            spinner.remove();
                        }
                    } else {
                        this.innerHTML = originalInnerHTML;
                    }
                    this.disabled = false;
                }, 1000);
            });
        });
    }
    
    // Handle simulated login process
    function handleSimulatedLogin(provider) {
        console.log(`Processing ${provider} login`);
        
        // Create a simulated user email based on provider
        const email = `${provider}_user_${Math.floor(Math.random() * 10000)}@example.com`;
        
        // Show authentication message
        const authMessage = document.createElement('div');
        authMessage.className = 'alert alert-info mt-3';
        authMessage.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>Authenticating with ${provider.charAt(0).toUpperCase() + provider.slice(1)}...`;
        
        // Find a good place to show the message
        const container = document.querySelector('.pricing-card') || 
                          document.querySelector('form') || 
                          document.body;
        container.appendChild(authMessage);
        
        // Redirect to the appropriate endpoint after a short delay
        setTimeout(() => {
            window.location.href = `/${provider}_login?email=${encodeURIComponent(email)}`;
        }, 1000);
    }
    
    // Show authentication error message
    function showError(message) {
        console.error(`Auth error: ${message}`);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger mt-3';
        errorDiv.innerHTML = `<i class="fas fa-exclamation-circle me-2"></i>${message}`;
        
        // Find a suitable place to show the error
        const container = document.querySelector('.pricing-card') || 
                          document.querySelector('form') || 
                          document.body;
        
        container.prepend(errorDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }
});