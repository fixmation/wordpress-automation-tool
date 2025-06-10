// Content Generation Script for WordPress Automation Tool
document.addEventListener('DOMContentLoaded', function() {
    // Initialize UI components
    initContentGenerationUI();

    // Initialize Stripe for subscription handling
    let stripe;
    if (typeof Stripe !== 'undefined' && stripePublishableKey) {
        stripe = Stripe(stripePublishableKey, { apiVersion: '2024-04-10' });
        console.log('Stripe initialized with key:', stripePublishableKey);
    } else {
        console.warn('Stripe is not properly initialized. Check if the Stripe key is provided.');
    }

    // Set up event listeners for generate content buttons
    setupGenerateContentButtons();

    // Set up event listeners for subscription buttons
    setupSubscriptionButtons();

    // Initialize Stripe subscription buttons
    initializeStripeSubscriptions();
    
    // Initialize quick content generation functionality
    initQuickContentGeneration();
    
    // Initialize quota refresh functionality
    initQuotaRefresh();
    
    // Initialize image upload functionality
    initImageUpload();
});

/**
 * Initialize UI components and check for existing generated content
 */
function initContentGenerationUI() {
    console.log('Current user plan:', currentUserPlan);

    // Load any existing generated content from session
    checkForExistingContent();

    // Ensure correct tabs are active based on user plan
    activateCorrectPlanTab();
}

/**
 * Check if content has already been generated and display it
 */
function checkForExistingContent() {
    // This would check session storage or make an API call to fetch previously generated content
    // For demonstration, we'll just check if additional_generated_content exists in the session

    // We would need to implement an endpoint to fetch this data
    fetch('/api/get_generated_content', {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.content) {
            // Display previously generated content
            displayGeneratedContent(data.content);
        }
    })
    .catch(error => {
        console.error('Error fetching generated content:', error);
    });
}

/**
 * Activate the appropriate tab based on user subscription
 */
function activateCorrectPlanTab() {
    // Default to basic plan tab
    let tabToActivate = document.getElementById('basic-tab');

    // If user has a higher tier plan, activate that tab
    if (currentUserPlan === 'professional' || currentUserPlan === 'premium') {
        tabToActivate = document.getElementById('professional-tab');
    }

    if (currentUserPlan === 'premium') {
        tabToActivate = document.getElementById('premium-tab');
    }

    // Activate the tab if it exists
    if (tabToActivate) {
        const tab = new bootstrap.Tab(tabToActivate);
        tab.show();
    }
}

/**
 * Set up event listeners for content generation buttons
 */
function setupGenerateContentButtons() {
    const generateButtons = document.querySelectorAll('.generate-content-btn');

    generateButtons.forEach(button => {
        button.addEventListener('click', function() {
            const plan = this.getAttribute('data-plan');
            generateContentForPlan(plan, this);
        });
    });
}

/**
 * Set up event listeners for subscription buttons
 */
function setupSubscriptionButtons() {
    const subscribeButtons = document.querySelectorAll('.subscribe-btn');

    subscribeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const plan = this.getAttribute('data-plan');
            const price = this.getAttribute('data-price');
            initiateStripeCheckout(plan, price, this);
        });
    });
}

/**
 * Helper function to get user's plan level
 * @returns {string} User's plan level (e.g., 'free', 'basic', 'professional', 'premium')
 */
function getUserPlanLevel() {
    // Replace this with actual logic to fetch user's plan from server or session storage
    return currentUserPlan || 'free';
}

/**
 * Show upgrade message to the user
 * @param {string} message - The upgrade message to display
 */
function showUpgradeMessage(message) {
    // Remove any existing upgrade messages
    const existingMessages = document.querySelectorAll('.upgrade-alert');
    existingMessages.forEach(msg => msg.remove());

    // Create new upgrade message
    const contentContainer = document.querySelector('.content-preview');
    const modalDiv = document.createElement('div');
    modalDiv.className = 'alert alert-warning alert-dismissible fade show upgrade-alert';
    modalDiv.innerHTML = `
        <h4 class="alert-heading">Subscription Required</h4>
        <p>${message}</p>
        <hr>
        <div class="subscription-options">
            <h5>Available Plans:</h5>
            <div class="d-flex justify-content-around flex-wrap gap-2">
                <button class="btn btn-primary subscribe-btn" data-plan="basic" data-price="9.99">
                    Basic Plan
                    <small class="d-block">$9.99/month</small>
                </button>
                <button class="btn btn-success subscribe-btn" data-plan="professional" data-price="19.99">
                    Professional Plan
                    <small class="d-block">$19.99/month</small>
                </button>
                <button class="btn btn-warning subscribe-btn" data-plan="premium" data-price="39.99">
                    Premium Plan
                    <small class="d-block">$39.99/month</small>
                </button>
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    if (contentContainer) {
        contentContainer.insertBefore(modalDiv, contentContainer.firstChild);
    }

    // Attach subscription handlers to new buttons
    modalDiv.querySelectorAll('.subscribe-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            initiateStripeCheckout(btn.getAttribute('data-plan'), btn.getAttribute('data-price'), btn);
        });
    });
}

/**
 * Generate content for the selected plan
 * @param {string} plan - The subscription plan type
 * @param {HTMLElement} buttonElement - The button that was clicked
 */
function generateContentForPlan(plan, buttonElement) {
    // Save original button state
    const originalButtonText = buttonElement.innerHTML;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
    buttonElement.disabled = true;

    // Check if user is trying to access higher tier features
    const planLevels = {
        'free': 0,
        'basic': 1,
        'professional': 2,
        'premium': 3
    };

    const userPlanLevel = getUserPlanLevel();

    if (planLevels[plan] > planLevels[userPlanLevel]) {
        buttonElement.innerHTML = originalButtonText;
        buttonElement.disabled = false;
        showUpgradeMessage(`Please upgrade to ${plan} plan to access these features`);
        return;
    }

    // First check if Gemini API is configured
    fetch('/api/check_gemini_api')
        .then(response => response.json())
        .then(data => {
            if (!data.configured) {
                alert('Gemini API key is required for content generation. Please configure it in the environment variables.');
                buttonElement.innerHTML = originalButtonText;
                buttonElement.disabled = false;
                return;
            }

            // Show loading state
            const contentContainer = document.getElementById(`${plan}-generated-content`);
            if (contentContainer) {
                contentContainer.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-spinner fa-spin me-2"></i>
                        Generating content with AI... This may take a moment.
                    </div>
                `;
                contentContainer.style.display = 'block';
            }

            // Set a timeout to handle long-running requests
            const timeoutDuration = 20000; // 20 seconds
            const timeoutId = setTimeout(() => {
                // Reset button state
                buttonElement.innerHTML = originalButtonText;
                buttonElement.disabled = false;

                if (contentContainer) {
                    contentContainer.innerHTML = `
                        <div class="alert alert-warning">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            Content generation is taking longer than expected. Our AI might be busy or there could be connectivity issues.
                            <button class="btn btn-sm btn-outline-warning ms-3" onclick="retryContentGeneration('${plan}', this.parentElement.parentElement)">
                                Try Again
                            </button>
                        </div>
                    `;
                }
            }, timeoutDuration);

            // Call API to generate content
            fetch('/generate_plan_content', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ plan: plan })
            })
            .then(response => response.json())
            .then(data => {
                // Clear timeout since we got a response
                clearTimeout(timeoutId);

                // Reset button state
                buttonElement.innerHTML = originalButtonText;
                buttonElement.disabled = false;

                if (data.success) {
                    // Track free trial content generation and show appropriate message
                    if (currentUserPlan === 'free') {
                        sessionStorage.setItem('freeTrialUsed', 'true');
                        showSuccessMessage(plan, true); // Pass true to indicate free trial usage
                    } else {
                        showSuccessMessage(plan, false);
                    }

                    // Display generated content
                    fetchAndDisplayContent(plan);
                } else {
                    // Show error message in the content container
                    if (contentContainer) {
                        contentContainer.innerHTML = `
                            <div class="alert alert-danger">
                                <i class="fas fa-exclamation-circle me-2"></i>
                                ${data.error || 'Failed to generate content. Please try again.'}
                                <button class="btn btn-sm btn-outline-danger ms-3" onclick="retryContentGeneration('${plan}', this.parentElement.parentElement)">
                                    Try Again
                                </button>
                            </div>
                        `;
                    }
                }
            })
            .catch(error => {
                // Clear timeout since we got a response (even if it's an error)
                clearTimeout(timeoutId);

                console.error('Error generating content:', error);
                buttonElement.innerHTML = originalButtonText;
                buttonElement.disabled = false;

                if (contentContainer) {
                    contentContainer.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-circle me-2"></i>
                            Error connecting to the server. Please check your internet connection and try again.
                            <button class="btn btn-sm btn-outline-danger ms-3" onclick="retryContentGeneration('${plan}', this.parentElement.parentElement)">
                                Try Again
                            </button>
                        </div>
                    `;
                }
            });
        })
        .catch(error => {
            console.error('Error checking API status:', error);
            buttonElement.innerHTML = originalButtonText;
            buttonElement.disabled = false;
        });
}

/**
 * Retry content generation after timeout or error
 * @param {string} plan - The subscription plan type
 * @param {HTMLElement} parentElement - The parent element of the retry button
 */
function retryContentGeneration(plan, parentElement) {
    parentElement.innerHTML = ''; // Clear existing message
    generateContentForPlan(plan, document.querySelector(`.generate-content-btn[data-plan="${plan}"]`));
}

/**
 * Fetch and display generated content for a plan
 * @param {string} plan - The subscription plan type
 */
function fetchAndDisplayContent(plan) {
    // Make an API call to get the generated content
    fetch('/api/get_generated_content?plan=' + plan, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success && data.content) {
            // Display the content in the appropriate section
            displayPlanContent(plan, data.content);
        } else {
            console.error('No content found for plan:', plan);
        }
    })
    .catch(error => {
        console.error('Error fetching content:', error);
    });

    // For demonstration purposes, we'll simulate a successful content fetch
    // and show the content container
    const contentContainer = document.getElementById(`${plan}-generated-content`);
    if (contentContainer) {
        contentContainer.style.display = 'block';

        // Populate with placeholder content
        populatePlaceholderContent(plan);
    }
}

/**
 * Display success message
 * @param {string} plan - The subscription plan type
 * @param {boolean} isFreeTrial - Whether this is a free trial generation
 */
function showSuccessMessage(plan, isFreeTrial = false) {
    const planLabels = {
        'basic': 'Basic',
        'professional': 'Professional',
        'premium': 'Premium'
    };

    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show';
    alertDiv.role = 'alert';

    if (isFreeTrial) {
        alertDiv.innerHTML = `
            <strong>Success!</strong> Your free trial content has been generated successfully.
            <hr>
            <p class="mb-0">This was your one-time free trial content generation. 
            To generate more content, please subscribe to one of our premium plans.</p>
            <div class="mt-3">
                <button class="btn btn-sm btn-outline-success me-2 subscribe-btn" data-plan="basic" data-price="9.99">
                    Upgrade to Basic
                </button>
                <button class="btn btn-sm btn-outline-success me-2 subscribe-btn" data-plan="professional" data-price="19.99">
                    Upgrade to Professional
                </button>
                <button class="btn btn-sm btn-outline-success subscribe-btn" data-plan="premium" data-price="39.99">
                    Upgrade to Premium
                </button>
            </div>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    } else {
        alertDiv.innerHTML = `
            <strong>Success!</strong> Your ${planLabels[plan] || plan} Plan content has been generated successfully.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    }

    // Get the content container where the alert should be inserted
    const contentContainer = document.getElementById(`${plan}-tab`);
    if (contentContainer) {
        contentContainer.prepend(alertDiv);

        // Automatically remove after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    } else {
        // Fall back to adding at the top of the page
        document.querySelector('.content-preview').prepend(alertDiv);
    }
}

/**
 * Initiate Stripe checkout process for a subscription
 * @param {string} plan - The plan type to subscribe to
 * @param {string} price - The price of the plan
 * @param {HTMLElement} buttonElement - The button that was clicked
 */
function initiateStripeCheckout(plan, price, buttonElement) {
    // Disable button and show loading state
    buttonElement.disabled = true;
    const originalText = buttonElement.innerHTML;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';

    // Remove any existing loading messages
    const existingLoadingMsgs = document.querySelectorAll('.loading-message');
    existingLoadingMsgs.forEach(msg => msg.remove());

    // Make request to server to create checkout session
    fetch('/create_checkout_session', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `plan=${plan}&price=${price}&display_currency=USD`
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.error || 'Payment processing error');
            });
        }
        return response.json();
    })
    .then(data => {
        console.log('Checkout session created:', data);

        if (data.url) {
            // Redirect to Stripe checkout
            console.log('Redirecting to:', data.url);
            window.location.href = data.url;

            // Add a fallback if redirection doesn't happen immediately
            setTimeout(function() {
                console.log('Fallback redirect needed');
                if (document.body.contains(loadingMsg)) {
                    loadingMsg.innerHTML = `
                        <p>If you are not automatically redirected, please click the button below:</p>
                        <a href="${data.url}" class="btn btn-primary">Go to Checkout</a>
                    `;
                }

                // Reset button after 5 seconds if user is still on the page
                setTimeout(function() {
                    if (buttonElement && document.body.contains(buttonElement)) {
                        buttonElement.disabled = false;
                        buttonElement.innerHTML = originalText;
                    }
                }, 5000);
            }, 3000);
        } else {
            throw new Error('No checkout URL received');
        }
    })
    .catch(error => {
        console.error('Payment error:', error);

        // Remove any loading messages
        const existingLoadingMsgs = document.querySelectorAll('.loading-message');
        existingLoadingMsgs.forEach(msg => msg.remove());

        // Add error message
        const errorMsg = document.createElement('div');
        errorMsg.className = 'alert alert-danger mt-3';
        errorMsg.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i>Error: ${error.message || 'Could not process payment'}`;

        const tabPane = document.querySelector(`#${plan}`);
        if (tabPane && tabPane.querySelector('.card-body')) {
            tabPane.querySelector('.card-body').appendChild(errorMsg);
        }

        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalText;

        // Remove error message after 5 seconds
        setTimeout(() => {
            if (errorMsg.parentNode) {
                errorMsg.parentNode.removeChild(errorMsg);
            }
        }, 5000);
    });
}

/**
 * Display content for a specific plan
 * @param {string} plan - The subscription plan type
 * @param {object} content - The content object from the API
 */
function displayPlanContent(plan, content) {
    // Show the content container
    const contentContainer = document.getElementById(`${plan}-generated-content`);
    if (!contentContainer) return;

    contentContainer.style.display = 'block';

    // Populate content based on plan type
    switch(plan) {
        case 'basic':
            // Populate basic plan content
            if (content.blog_post) {
                document.querySelector('.blog-post-content').innerHTML = `
                    <div class="content-preview-text">${content.blog_post}</div>
                    <div class="d-flex justify-content-end mt-3">
                        <button class="btn btn-sm btn-success sync-to-wp" data-content-type="post" data-plan="basic" data-content-key="blog_post">
                            <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                        </button>
                    </div>
                `;
            }
            if (content.about_page) {
                document.querySelector('.about-page-content').innerHTML = `
                    <div class="content-preview-text">${content.about_page}</div>
                    <div class="d-flex justify-content-end mt-3">
                        <button class="btn btn-sm btn-success sync-to-wp" data-content-type="page" data-plan="basic" data-content-key="about_page">
                            <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                        </button>
                    </div>
                `;
            }
            if (content.contact_page) {
                document.querySelector('.contact-page-content').innerHTML = `
                    <div class="content-preview-text">${content.contact_page}</div>
                    <div class="d-flex justify-content-end mt-3">
                        <button class="btn btn-sm btn-success sync-to-wp" data-content-type="page" data-plan="basic" data-content-key="contact_page">
                            <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                        </button>
                    </div>
                `;
            }
            break;

        case 'professional':
            // Populate professional plan content
            if (content.blog_posts) {
                let blogPostsHtml = '<div class="content-preview-text">';
                content.blog_posts.forEach((post, index) => {
                    blogPostsHtml += `
                        <div class="mb-4">
                            <h4>Blog Post ${index + 1}</h4>
                            <div>${post}</div>
                            <div class="d-flex justify-content-end mt-2">
                                <button class="btn btn-sm btn-success sync-to-wp" data-content-type="post" data-plan="professional" data-content-key="blog_posts" data-index="${index}">
                                    <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                                </button>
                            </div>
                        </div>
                    `;
                });
                blogPostsHtml += '</div>';
                document.querySelector('.blog-posts-content').innerHTML = blogPostsHtml;
            }
            if (content.all_pages) {
                let pagesHtml = '<div class="content-preview-text">';
                for (const [pageName, pageContent] of Object.entries(content.all_pages)) {
                    pagesHtml += `
                        <div class="mb-4">
                            <h4>${pageName}</h4>
                            <div>${pageContent}</div>
                            <div class="d-flex justify-content-end mt-2">
                                <button class="btn btn-sm btn-success sync-to-wp" data-content-type="page" data-plan="professional" data-content-key="all_pages" data-page-name="${pageName}">
                                    <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                                </button>
                            </div>
                        </div>
                    `;
                }
                pagesHtml += '</div>';
                document.querySelector('.all-pages-content').innerHTML = pagesHtml;
            }
            if (content.seo_content) {
                let seoHtml = '<div class="content-preview-text">';
                for (const [seoType, seoContent] of Object.entries(content.seo_content)) {
                    seoHtml += `<h4>${seoType.replace('_', ' ').toUpperCase()}</h4><div>${seoContent}</div>`;
                }
                seoHtml += '</div>';
                document.querySelector('.seo-content').innerHTML = seoHtml;
            }
            if (content.social_media) {
                let socialHtml = '<div class="content-preview-text">';
                for (const [platform, socialContent] of Object.entries(content.social_media)) {
                    socialHtml += `<h4>${platform.toUpperCase()}</h4><div>${socialContent}</div>`;
                }
                socialHtml += '</div>';
                document.querySelector('.social-media-content').innerHTML = socialHtml;
            }
            break;

        case 'premium':
            // Populate premium plan content
            if (content.blog_posts) {
                let blogPostsHtml = '<div class="content-preview-text">';
                content.blog_posts.forEach((post, index) => {
                    blogPostsHtml += `
                        <div class="mb-4">
                            <h4>Blog Post ${index + 1}</h4>
                            <div>${post}</div>
                            <div class="d-flex justify-content-end mt-2">
                                <button class="btn btn-sm btn-success sync-to-wp" data-content-type="post" data-plan="premium" data-content-key="blog_posts" data-index="${index}">
                                    <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                                </button>
                            </div>
                        </div>
                    `;
                });
                blogPostsHtml += '</div>';
                document.querySelector('.premium-blog-posts-content').innerHTML = blogPostsHtml;
            }
            if (content.custom_templates) {
                let templatesHtml = '<div class="content-preview-text">';
                for (const [templateName, templateContent] of Object.entries(content.custom_templates)) {
                    templatesHtml += `<h4>${templateName.replace('_', ' ').toUpperCase()}</h4><div>${templateContent}</div>`;
                }
                templatesHtml += '</div>';
                document.querySelector('.custom-templates-content').innerHTML = templatesHtml;
            }
            if (content.multi_language) {
                let langHtml = '<div class="content-preview-text">';
                for (const [language, langContent] of Object.entries(content.multi_language)) {
                    langHtml += `<h4>${language.toUpperCase()}</h4><div>${langContent}</div>`;
                }
                langHtml += '</div>';
                document.querySelector('.multi-language-content').innerHTML = langHtml;
            }
            if (content.advanced_seo) {
                let advSeoHtml = '<div class="content-preview-text">';
                for (const [seoType, seoContent] of Object.entries(content.advanced_seo)) {
                    advSeoHtml += `<h4>${seoType.replace('_', ' ').toUpperCase()}</h4><div>${seoContent}</div>`;
                }
                advSeoHtml += '</div>';
                document.querySelector('.advanced-seo-content').innerHTML = advSeoHtml;
            }
            break;
    }
    
    // Add event listeners to sync buttons
    const syncButtons = document.querySelectorAll('.sync-to-wp');
    syncButtons.forEach(button => {
        button.addEventListener('click', function() {
            syncContentToWordPress(this);
        });
    });
}

/**
 * Sync content to WordPress
 * @param {HTMLElement} buttonElement - The sync button element
 */
function syncContentToWordPress(buttonElement) {
    // Save original button state
    const originalText = buttonElement.innerHTML;
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Syncing...';
    
    // Get content data from attributes
    const contentType = buttonElement.getAttribute('data-content-type'); // post, page
    const plan = buttonElement.getAttribute('data-plan');
    const contentKey = buttonElement.getAttribute('data-content-key');
    const index = buttonElement.getAttribute('data-index');
    const pageName = buttonElement.getAttribute('data-page-name');
    
    // Get the content from session storage or fetch it
    fetch('/api/get_generated_content?plan=' + plan, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success && !data.content) {
            throw new Error('No content available to sync');
        }
        
        let contentToSync = '';
        let contentTitle = '';
        
        // Extract the content based on plan and content key
        if (plan === 'basic') {
            contentToSync = data.content[contentKey];
            contentTitle = contentKey === 'blog_post' ? 'Blog Post' : 
                          contentKey === 'about_page' ? 'About Us' : 'Contact Us';
        } else if (plan === 'professional' || plan === 'premium') {
            if (contentKey === 'blog_posts' && index) {
                contentToSync = data.content[contentKey][index];
                contentTitle = `Blog Post ${parseInt(index) + 1}`;
            } else if (contentKey === 'all_pages' && pageName) {
                contentToSync = data.content[contentKey][pageName];
                contentTitle = pageName;
            }
        }
        
        if (!contentToSync) {
            throw new Error('Failed to retrieve content for syncing');
        }
        
        // Prepare content data for API
        const contentData = {
            title: contentTitle,
            content: contentToSync,
            status: 'draft' // Default to draft
        };
        
        // Send to WordPress API
        return fetch('/api/sync_wordpress_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content_type: contentType,
                content_data: contentData,
                plan: plan
            })
        });
    })
    .then(response => response.json())
    .then(result => {
        if (!result.success) {
            throw new Error(result.error || 'Failed to sync content to WordPress');
        }
        
        // Show success message
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show';
        notification.innerHTML = `
            <strong>Success!</strong> Content synced to WordPress.
            <p class="mb-0 small">Status: ${result.content_status}</p>
            ${result.content_url ? `<p class="mb-0 small"><a href="${result.content_url}" target="_blank">View Content</a></p>` : ''}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert notification after the button
        buttonElement.parentNode.parentNode.appendChild(notification);
        
        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalText;
        
        // Auto-dismiss notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    })
    .catch(error => {
        console.error('Error syncing content:', error);
        
        // Show error message
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger alert-dismissible fade show';
        notification.innerHTML = `
            <strong>Error!</strong> ${error.message || 'Failed to sync content to WordPress'}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        // Insert notification after the button
        buttonElement.parentNode.parentNode.appendChild(notification);
        
        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalText;
        
        // Auto-dismiss notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    });
}

/**
 * Populate placeholder content for demonstration purposes
 * @param {string} plan - The subscription plan type
 */
function populatePlaceholderContent(plan) {
    switch(plan) {
        case 'basic':
            // Simulate basic plan content
            document.querySelector('.blog-post-content').innerHTML = `
                <div class="content-preview-text">
                    <h3>The Ultimate Guide to [Category] Success</h3>
                    <p>In today's competitive market, standing out in the [Category] industry requires innovation, dedication, and a deep understanding of customer needs. This comprehensive guide explores the essential strategies that successful [Category] businesses implement to thrive in 2024 and beyond.</p>
                    <p>First, we'll examine the current trends shaping the industry. Then, we'll dive into actionable steps you can take to elevate your business above the competition. Whether you're just starting out or looking to grow an established [Category] business, these insights will provide valuable direction.</p>
                    <p>Read on to discover the secrets of [Category] success that industry leaders don't want you to know!</p>
                </div>
            `;
            document.querySelector('.about-page-content').innerHTML = `
                <div class="content-preview-text">
                    <h3>About Our [Category] Business</h3>
                    <p>Founded in 2015, our [Category] business has been at the forefront of innovation and excellence in the industry. Our journey began with a simple mission: to provide exceptional [Category] solutions that transform the way our clients operate.</p>
                    <p>Our team of experienced professionals brings together decades of combined expertise in [Category] services. We pride ourselves on our customer-first approach, ensuring that every client receives personalized attention and tailored solutions to meet their unique needs.</p>
                    <p>What sets us apart is our unwavering commitment to quality, innovation, and integrity. We believe in building lasting relationships with our clients based on trust, transparency, and exceptional results.</p>
                </div>
            `;
            document.querySelector('.contact-page-content').innerHTML = `
                <div class="content-preview-text">
                    <h3>Contact Us</h3>
                    <p>We're here to answer any questions you may have about our [Category] services. Reach out to us and we'll respond as soon as possible.</p>
                    <div style="margin: 20px 0;">
                        <strong>Email:</strong> info@yourcompany.com<br>
                        <strong>Phone:</strong> (555) 123-4567<br>
                        <strong>Address:</strong> 123 Business Avenue, Enterprise City, State 12345
                    </div>
                    <p>Hours of Operation:</p>
                    <ul>
                        <li>Monday - Friday: 9:00 AM - 6:00 PM</li>
                        <li>Saturday: 10:00 AM - 4:00 PM</li>
                        <li>Sunday: Closed</li>
                    </ul>
                </div>
            `;
            break;

        case 'professional':
            // Simulate professional plan content with abbreviated content
            document.querySelector('.blog-posts-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>Blog Post 1: 7 Essential Tips for [Category] Success</h4>
                    <p>Introduction to proven strategies for [Category] businesses...</p>
                    <h4>Blog Post 2: How to Choose the Right [Category] Solution</h4>
                    <p>A guide to selecting the perfect [Category] solution for your needs...</p>
                    <h4>Blog Post 3: The Future of [Category] Technology</h4>
                    <p>Exploring upcoming trends and innovations in the [Category] industry...</p>
                    <h4>Blog Post 4: Case Study: [Category] Transformation</h4>
                    <p>How one business revolutionized their operations with our [Category] solutions...</p>
                    <h4>Blog Post 5: [Category] Best Practices for 2024</h4>
                    <p>Stay ahead of the competition with these industry-leading practices...</p>
                </div>
            `;
            document.querySelector('.all-pages-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>Home Page</h4>
                    <p>Welcome to the premier destination for [Category] solutions...</p>
                    <h4>Services Page</h4>
                    <p>Comprehensive overview of our [Category] services and packages...</p>
                    <h4>Portfolio Page</h4>
                    <p>Showcase of our successful [Category] projects and case studies...</p>
                    <h4>Testimonials Page</h4>
                    <p>What our clients say about our exceptional [Category] solutions...</p>
                </div>
            `;
            document.querySelector('.seo-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>META DESCRIPTIONS</h4>
                    <p>Optimized meta descriptions for all pages to improve search visibility...</p>
                    <h4>KEYWORDS</h4>
                    <p>Researched keywords relevant to [Category] industry for maximum SEO impact...</p>
                    <h4>HEADINGS</h4>
                    <p>SEO-optimized H1, H2, and H3 headings for improved page structure...</p>
                </div>
            `;
            document.querySelector('.social-media-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>FACEBOOK</h4>
                    <p>Engaging Facebook post templates for promoting [Category] services...</p>
                    <h4>TWITTER</h4>
                    <p>Concise Twitter content templates with relevant hashtags...</p>
                    <h4>INSTAGRAM</h4>
                    <p>Visual-focused Instagram content ideas with caption templates...</p>
                </div>
            `;
            break;

        case 'premium':
            // Simulate premium plan content with abbreviated content
            document.querySelector('.premium-blog-posts-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>Blog Post 1: [Premium Content]</h4>
                    <p>Premium level article about [Category] innovation...</p>
                    <h4>Blog Post 2: [Premium Content]</h4>
                    <p>In-depth analysis of [Category] market trends...</p>
                    <h4>Blog Post 3: [Premium Content]</h4>
                    <p>Expert guide to advanced [Category] strategies...</p>
                    <p><em>...12 more premium blog posts available</em></p>
                </div>
            `;
            document.querySelector('.custom-templates-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>PRODUCT TEMPLATE</h4>
                    <p>Professional template for showcasing [Category] products with customizable sections...</p>
                    <h4>SERVICE TEMPLATE</h4>
                    <p>Detailed service description template with benefits, features, and call-to-action...</p>
                    <h4>EVENT TEMPLATE</h4>
                    <p>Event announcement template with registration details and promotional elements...</p>
                </div>
            `;
            document.querySelector('.multi-language-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>ENGLISH</h4>
                    <p>Primary English content for all website sections...</p>
                    <h4>SPANISH</h4>
                    <p>Professional Spanish translations of all website content...</p>
                    <h4>FRENCH</h4>
                    <p>Accurate French translations with cultural adaptations...</p>
                </div>
            `;
            document.querySelector('.advanced-seo-content').innerHTML = `
                <div class="content-preview-text">
                    <h4>SCHEMA MARKUP</h4>
                    <p>Structured data markup to enhance search engine understanding of content...</p>
                    <h4>CANONICAL TAGS</h4>
                    <p>Strategy for handling duplicate content with canonical URL implementation...</p>
                    <h4>INTERNAL LINKING</h4>
                    <p>Comprehensive internal linking structure to improve site architecture...</p>
                </div>
            `;
            break;
    }
}

// Initialize Stripe subscription buttons
function initializeStripeSubscriptions() {
    const subscribeButtons = document.querySelectorAll('.subscribe-btn');

    if (subscribeButtons.length > 0) {
        console.log('Found subscription buttons:', subscribeButtons.length);

        // Add event listeners to subscription buttons
        subscribeButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();
                const plan = this.dataset.plan;
                const price = this.dataset.price;
                console.log(`Subscribe button clicked for ${plan} plan at $${price}`);
                initiateStripeCheckout(plan, price, this);
            });
        });
    }
}

// Initialize quick content generation functionality
function initQuickContentGeneration() {
    const generateBtn = document.getElementById('generate-quick-content');
    const contentType = document.getElementById('content-type');
    const contentTopic = document.getElementById('content-topic');
    const resultContainer = document.getElementById('quick-content-result');
    
    if (!generateBtn || !contentType || !contentTopic || !resultContainer) return;
    
    generateBtn.addEventListener('click', function() {
        // Validate input
        if (!contentTopic.value.trim()) {
            resultContainer.innerHTML = `
                <div class="alert alert-warning">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Please enter a topic or keywords for your content
                </div>
            `;
            return;
        }
        
        // Show loading state
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generating...';
        
        resultContainer.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-spinner fa-spin me-2"></i>
                Generating ${contentType.value.replace('_', ' ')}... This may take a moment.
            </div>
        `;
        
        // Make request to generate content
        fetch('/api/generate_quick_content', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                content_type: contentType.value,
                topic: contentTopic.value
            })
        })
        .then(response => response.json())
        .then(data => {
            // Reset button state
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Quick Content';
            
            if (data.success) {
                // Display the generated content
                resultContainer.innerHTML = `
                    <div class="card">
                        <div class="card-header bg-success text-white d-flex justify-content-between align-items-center">
                            <span>Generated ${contentType.value.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</span>
                            <button class="btn btn-sm btn-outline-light" onclick="copyToClipboard('generated-content-text')">
                                <i class="fas fa-copy"></i>
                            </button>
                        </div>
                        <div class="card-body">
                            <div id="generated-content-text">${data.content}</div>
                        </div>
                        <div class="card-footer">
                            <button class="btn btn-sm btn-success sync-to-wp" data-content-type="${contentType.value}" data-content="${encodeURIComponent(data.content)}">
                                <i class="fas fa-sync-alt me-2"></i>Sync to WordPress
                            </button>
                        </div>
                    </div>
                `;
                
                // Update quota display
                refreshQuotaDisplay();
                
                // Add event listener to sync button
                resultContainer.querySelector('.sync-to-wp').addEventListener('click', function() {
                    const button = this;
                    const contentToSync = decodeURIComponent(button.getAttribute('data-content'));
                    const contentTypeValue = button.getAttribute('data-content-type');
                    
                    syncQuickContentToWordPress(contentTypeValue, contentToSync, button);
                });
            } else {
                // Show error message
                resultContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle me-2"></i>
                        ${data.error || 'Failed to generate content. Please try again.'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Error generating content:', error);
            
            // Reset button state and show error
            generateBtn.disabled = false;
            generateBtn.innerHTML = '<i class="fas fa-magic me-2"></i>Generate Quick Content';
            
            resultContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-circle me-2"></i>
                    Error connecting to the server. Please check your internet connection and try again.
                </div>
            `;
        });
    });
    
    // Setup copy to clipboard functionality
    window.copyToClipboard = function(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const text = element.innerText;
        
        // Create temporary element
        const tempElement = document.createElement('textarea');
        tempElement.value = text;
        document.body.appendChild(tempElement);
        
        // Select and copy
        tempElement.select();
        document.execCommand('copy');
        
        // Clean up
        document.body.removeChild(tempElement);
        
        // Show feedback
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.textContent = 'Copied to clipboard!';
        document.body.appendChild(notification);
        
        // Remove after 2 seconds
        setTimeout(() => {
            notification.remove();
        }, 2000);
    };
}

// Sync quick content to WordPress
function syncQuickContentToWordPress(contentType, content, buttonElement) {
    // Save original button state
    const originalText = buttonElement.innerHTML;
    buttonElement.disabled = true;
    buttonElement.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Syncing...';
    
    // Prepare title based on content type
    let contentTitle = '';
    switch (contentType) {
        case 'blog_post':
            contentTitle = content.split('\n')[0].replace(/<[^>]*>/g, '').substring(0, 50); // Use first line as title
            break;
        case 'product_description':
            contentTitle = 'Product Description';
            break;
        case 'seo_meta':
            contentTitle = 'SEO Meta Description';
            break;
        case 'social_post':
            contentTitle = 'Social Media Post';
            break;
        default:
            contentTitle = 'Generated Content';
    }
    
    // Prepare the post data
    const postData = {
        content_type: contentType === 'blog_post' ? 'post' : 'page',
        content_data: {
            title: contentTitle,
            content: content,
            status: 'draft'
        }
    };
    
    // Send to WordPress API
    fetch('/api/sync_wordpress_content', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(result => {
        if (!result.success) {
            throw new Error(result.error || 'Failed to sync content to WordPress');
        }
        
        // Show success message
        const cardFooter = buttonElement.parentNode;
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-success mt-2 mb-0';
        notification.innerHTML = `
            <i class="fas fa-check-circle me-2"></i>
            Content synced to WordPress as a draft.
            ${result.content_url ? `<a href="${result.content_url}" target="_blank" class="ms-2">View Content</a>` : ''}
        `;
        
        cardFooter.appendChild(notification);
        
        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalText;
        
        // Auto-dismiss notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    })
    .catch(error => {
        console.error('Error syncing content:', error);
        
        // Show error message
        const cardFooter = buttonElement.parentNode;
        
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger mt-2 mb-0';
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle me-2"></i>
            ${error.message || 'Failed to sync content to WordPress'}
        `;
        
        cardFooter.appendChild(notification);
        
        // Reset button
        buttonElement.disabled = false;
        buttonElement.innerHTML = originalText;
        
        // Auto-dismiss notification after 5 seconds
        setTimeout(() => {
            notification.remove();
        }, 5000);
    });
}

// Initialize quota refresh functionality
function initQuotaRefresh() {
    const refreshBtn = document.getElementById('refresh-quota');
    if (!refreshBtn) return;
    
    refreshBtn.addEventListener('click', function() {
        // Show loading state
        const originalText = this.innerHTML;
        this.disabled = true;
        this.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i> Refreshing...';
        
        // Call API to get updated quota
        refreshQuotaDisplay()
            .then(() => {
                // Reset button
                this.disabled = false;
                this.innerHTML = originalText;
            })
            .catch(error => {
                console.error('Error refreshing quota:', error);
                // Reset button
                this.disabled = false;
                this.innerHTML = originalText;
            });
    });
}

// Refresh the quota display
function refreshQuotaDisplay() {
    return new Promise((resolve, reject) => {
        fetch('/api/get_content_quota')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update the quota display
                    const planType = data.plan_type || 'free';
                    const used = data.used || 0;
                    const total = data.total || 1;
                    const remaining = total - used;
                    const percentUsed = (used / total) * 100;
                    
                    // Find the badge and progress bar
                    const badge = document.querySelector('.subscription-usage-card .badge');
                    const progressBar = document.querySelector('.subscription-usage-card .progress-bar');
                    
                    if (badge && progressBar) {
                        // Update the badge
                        badge.textContent = `${remaining}/${total} remaining`;
                        
                        // Update progress bar
                        progressBar.style.width = `${percentUsed}%`;
                        progressBar.setAttribute('aria-valuenow', percentUsed);
                        
                        // Resolve the promise
                        resolve();
                    } else {
                        reject(new Error('Quota display elements not found'));
                    }
                } else {
                    reject(new Error(data.error || 'Failed to fetch quota'));
                }
            })
            .catch(error => {
                console.error('Error fetching quota:', error);
                reject(error);
            });
    });
}

// Initialize image upload functionality
function initImageUpload() {
    const imageUploadBtn = document.getElementById('upload-images-btn');
    const imageInput = document.getElementById('wp-images');
    const imageCountDisplay = document.getElementById('image-count-display');
    const uploadProgress = document.getElementById('upload-progress');
    const uploadResult = document.getElementById('upload-result');
    const uploadedImagesContainer = document.getElementById('uploaded-images-container');

    if (!imageUploadBtn || !imageInput) return;

    // Update the file count display when files are selected
    imageInput.addEventListener('change', function() {
        const fileCount = this.files.length;
        imageCountDisplay.textContent = fileCount === 0 
            ? 'No files selected' 
            : `${fileCount} file${fileCount === 1 ? '' : 's'} selected`;
            
        // Validate against plan limits
        let maxAllowed = 1; // Default for free plan
        const userPlan = currentUserPlan || 'free';
        
        if (userPlan === 'basic') maxAllowed = 5;
        else if (userPlan === 'professional') maxAllowed = 15;
        else if (userPlan === 'premium') maxAllowed = 30;
        
        if (fileCount > maxAllowed) {
            uploadResult.innerHTML = `<div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Your ${userPlan} plan allows a maximum of ${maxAllowed} image uploads. Please select fewer images.
            </div>`;
            imageUploadBtn.disabled = true;
        } else {
            uploadResult.innerHTML = '';
            imageUploadBtn.disabled = false;
        }
    });

    // Handle the upload when the button is clicked
    imageUploadBtn.addEventListener('click', function() {
        if (imageInput.files.length === 0) {
            uploadResult.innerHTML = `<div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Please select at least one image to upload.
            </div>`;
            return;
        }

        // Prepare form data
        const formData = new FormData();
        for (let i = 0; i < imageInput.files.length; i++) {
            formData.append('images', imageInput.files[i]);
        }
        formData.append('alt_text', document.getElementById('alt-text').value || '');

        // Show progress bar
        uploadProgress.classList.remove('d-none');
        const progressBar = uploadProgress.querySelector('.progress-bar');
        progressBar.style.width = '0%';
        progressBar.setAttribute('aria-valuenow', 0);
        
        // Disable the upload button during upload
        imageUploadBtn.disabled = true;
        imageUploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';

        // Make the API request
        fetch('/api/upload_wordpress_media', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Failed to upload images');
                });
            }
            return response.json();
        })
        .then(data => {
            // Upload complete, update UI
            progressBar.style.width = '100%';
            progressBar.setAttribute('aria-valuenow', 100);
            
            uploadResult.innerHTML = `<div class="alert alert-success">
                <i class="fas fa-check-circle me-2"></i>
                Successfully uploaded ${data.uploaded_count} image${data.uploaded_count === 1 ? '' : 's'} to WordPress.
            </div>`;
            
            // Display the uploaded images
            if (data.images && data.images.length > 0) {
                let imagesHtml = '';
                data.images.forEach(image => {
                    imagesHtml += `
                        <div class="col-md-4 col-sm-6">
                            <div class="card h-100">
                                <img src="${image.url}" class="card-img-top" alt="${image.alt || 'Uploaded image'}">
                                <div class="card-body">
                                    <h5 class="card-title text-truncate">${image.filename}</h5>
                                    <p class="card-text small text-muted">ID: ${image.id}</p>
                                </div>
                            </div>
                        </div>
                    `;
                });
                uploadedImagesContainer.innerHTML = imagesHtml;
            }
            
            // Reset form
            setTimeout(() => {
                uploadProgress.classList.add('d-none');
                imageUploadBtn.disabled = false;
                imageUploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload to WordPress';
            }, 1500);
        })
        .catch(error => {
            console.error('Error uploading images:', error);
            
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', 0);
            
            uploadResult.innerHTML = `<div class="alert alert-danger">
                <i class="fas fa-exclamation-circle me-2"></i>
                ${error.message || 'Error uploading images. Please try again.'}
            </div>`;
            
            // Reset button
            uploadProgress.classList.add('d-none');
            imageUploadBtn.disabled = false;
            imageUploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload to WordPress';
        });
    });
}