// Progress tracking functionality
const Progress = {
    // Save current stage progress
    saveProgress: async function(stage, data = {}) {
        try {
            const response = await fetch('/api/save_progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ stage, data })
            });
            
            if (!response.ok) {
                throw new Error('Failed to save progress');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error saving progress:', error);
            throw error;
        }
    },
    
    // Resume from last saved stage
    resumeProgress: async function() {
        try {
            const response = await fetch('/api/resume_progress');
            
            if (!response.ok) {
                throw new Error('Failed to retrieve progress');
            }
            
            const progress = await response.json();
            return progress;
        } catch (error) {
            console.error('Error retrieving progress:', error);
            throw error;
        }
    }
};

// Auto-save progress when stage changes
document.addEventListener('DOMContentLoaded', function() {
    const progressBar = document.querySelector('.progress-bar');
    if (progressBar) {
        const currentStage = parseInt(progressBar.getAttribute('aria-valuenow') / 10);
        const stageData = {};
        
        // Collect form data if present
        const form = document.querySelector('form');
        if (form) {
            const formData = new FormData(form);
            for (let [key, value] of formData.entries()) {
                stageData[key] = value;
            }
        }
        
        // Always save progress, even if form is empty
        Progress.saveProgress(currentStage, stageData).catch(console.error);
    }
});
// Resume progress on page load
window.addEventListener('load', async function() {
    try {
        const progress = await Progress.resumeProgress();
        
        // Redirect to last stage if on earlier stage
        const currentStage = document.querySelector('.progress-bar') ? 
            parseInt(document.querySelector('.progress-bar').getAttribute('aria-valuenow') / 10) : 1;
            
        if (progress.current_stage > currentStage) {
            const stageUrls = {
                1: '/connect_server',
                2: '/wordpress_installation',
                3: '/website_category',
                4: '/select_theme',
                5: '/generate_menu',
                6: '/generate_content',
                7: '/content_image_generation',
                8: '/content_preview',
                9: '/optimization',
                10: '/summary'
            };
            
            if (stageUrls[progress.current_stage]) {
                window.location.href = stageUrls[progress.current_stage];
            }
        }
        
        // Populate form data if available
        if (progress.stage_data) {
            const form = document.querySelector('form');
            if (form) {
                Object.entries(progress.stage_data).forEach(([key, value]) => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input) {
                        input.value = value;
                    }
                });
            }
        }
    } catch (error) {
        console.error('Error resuming progress:', error);
    }
});