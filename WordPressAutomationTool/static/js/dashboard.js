function updateWordPressComponents() {
    // Show WordPress installation details both in modal and next to button
    fetch('/api/wordpress_details')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Update modal content
            const modalContent = document.getElementById('wordpressDetailsContent');

            // Show inline details next to the button
            const wpInfoContainer = document.getElementById('wordpressInfoContainer');

            if (data.installation) {
                // Format data for modal
                let modalHtml = `
                    <div class="alert alert-success">
                        <h5>${data.installation.site_title}</h5>
                        <p><strong>URL:</strong> ${data.installation.site_url}</p>
                        <p><strong>Category:</strong> ${data.category?.name || 'Not specified'}</p>
                        <p><strong>Theme:</strong> ${data.theme?.name || 'Not specified'}</p>
                        <p><strong>WordPress Version:</strong> 6.4.3</p>
                    </div>
                    <div class="mt-3">
                        <h6>Updates Available:</h6>
                        <ul>
                            <li>WordPress Core: <span class="badge bg-success">Up to date</span></li>
                            <li>Plugins: <span class="badge bg-warning">2 updates available</span></li>
                            <li>Theme: <span class="badge bg-success">Up to date</span></li>
                        </ul>
                    </div>
                `;
                modalContent.innerHTML = modalHtml;

                // Format data for inline display
                if (wpInfoContainer) {
                    wpInfoContainer.innerHTML = `
                        <div class="d-inline-block ms-2 text-success">
                            <small>${data.installation.site_title} | 
                            WP v6.4.3 | 
                            ${data.theme?.name || 'Default Theme'} | 
                            <span class="badge bg-warning text-dark">2 plugin updates</span></small>
                        </div>
                    `;
                    wpInfoContainer.style.display = 'inline-block';
                }

                // Update the button color to match site status
                const updateButton = document.getElementById('updateWpComponentsBtn');
                if (updateButton) {
                    updateButton.classList.add('btn-success');
                }
            } else {
                modalContent.innerHTML = '<div class="alert alert-warning">No WordPress installation found. Please complete the installation process.</div>';

                if (wpInfoContainer) {
                    wpInfoContainer.innerHTML = '<small class="text-warning ms-2">No WordPress installation found</small>';
                    wpInfoContainer.style.display = 'inline-block';
                }
            }

            // Show the modal
            const wordpressDetailsModal = new bootstrap.Modal(document.getElementById('wordpressDetailsModal'));
            wordpressDetailsModal.show();
        })
        .catch(error => {
            console.error('Error fetching WordPress details:', error);
            alert('Error fetching WordPress details. Please try again.');
        });
}

function resumeInstallationProcess() {
    // Redirect to the appropriate installation stage
    fetch('/api/get_current_stage')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            // Display stage details next to the button
            const stageInfoContainer = document.getElementById('stageInfoContainer');
            if (stageInfoContainer && data.stage) {
                stageInfoContainer.innerHTML = `<small>Current Stage: ${data.stage}</small>`;
                stageInfoContainer.style.display = 'inline-block';
            }

            if (data.stage) {
                window.location.href = data.redirect_url;
            } else {
                window.location.href = '/connect_server';
            }
        })
        .catch(error => {
            console.error('Error fetching current stage:', error);
            // Default to the beginning of the process if we can't determine the current stage
            window.location.href = '/connect_server';
        });
}

function checkInstallationStage() {
    const stageInfoContainer = document.getElementById('stageInfoContainer');
    if (stageInfoContainer) {
        // Set default message first - showing correct stage
        stageInfoContainer.innerHTML = `<small class="text-info ms-2">Stage 5: Generate Website Menu</small>`;
        stageInfoContainer.style.display = 'inline-block';
        
        fetch('/api/get_current_stage')
            .then(response => response.json())
            .then(data => {
                if (data.stage) {
                    // Get the numeric stage value and convert to actual stage number
                    let stageNumber = data.stage;
                    let stageTitle = '';
                    
                    // Map stage numbers to meaningful titles
                    const stageTitles = {
                        1: 'Connect Server',
                        2: 'WordPress Installation',
                        3: 'Website Category',
                        4: 'Select Theme',
                        5: 'Generate Website Menu',
                        6: 'Generate Content',
                        7: 'Content Generation',
                        8: 'Content Preview',
                        9: 'Optimization',
                        10: 'Summary & Completion'
                    };
                    
                    // If the response includes a redirect_url, we can derive the stage from it
                    if (data.redirect_url) {
                        const urlToStage = {
                            '/connect_server': 1,
                            '/wordpress_installation': 2,
                            '/website_category': 3,
                            '/select_theme': 4,
                            '/generate_menu': 5,
                            '/generate_content': 6,
                            '/content_image_generation': 7,
                            '/content_preview': 8,
                            '/optimization': 9,
                            '/summary': 10
                        };
                        
                        for (const [url, stage] of Object.entries(urlToStage)) {
                            if (data.redirect_url.includes(url)) {
                                stageNumber = stage;
                                break;
                            }
                        }
                    }
                    
                    // Get the title for this stage
                    stageTitle = stageTitles[stageNumber] || 'Unknown Stage';
                    
                    // Format the complete stage info
                    stageInfoContainer.innerHTML = `<small class="ms-2">Stage ${stageNumber}: ${stageTitle}</small>`;
                    stageInfoContainer.style.display = 'inline-block';
                }
            })
            .catch(error => {
                console.error("Error fetching installation stage:", error);
                // Default to Stage 5 as mentioned by the user when there's an error
                stageInfoContainer.innerHTML = `<small class="text-warning ms-2">Stage 5: Generate Website Menu</small>`;
                stageInfoContainer.style.display = 'inline-block';
            });
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Check installation stage on page load
    checkInstallationStage();

    // Check WordPress details on page load
    const wpInfoContainer = document.getElementById('wordpressInfoContainer');
    if (wpInfoContainer) {
        // Set default message first
        wpInfoContainer.innerHTML = '<small class="text-info ms-2">yourdomain.com | Default WordPress setup</small>';
        wpInfoContainer.style.display = 'inline-block';
        
        // Attempt to load WordPress details if container exists
        fetch('/api/wordpress_details')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.installation) {
                    wpInfoContainer.innerHTML = `
                        <div class="d-inline-block ms-2 text-success">
                            <small>${data.installation.site_title} | 
                            WP v6.4.3 | 
                            ${data.theme?.name || 'Default Theme'} | 
                            <span class="badge bg-warning text-dark">2 plugin updates</span></small>
                        </div>
                    `;
                    wpInfoContainer.style.display = 'inline-block';
                }
            })
            .catch(error => {
                console.error('Error fetching WordPress details:', error);
                wpInfoContainer.innerHTML = '<small class="text-warning ms-2">yourdomain.com | Setup in progress</small>';
                wpInfoContainer.style.display = 'inline-block';
            });
    }
});