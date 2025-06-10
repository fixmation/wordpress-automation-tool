
// Ensure consistent button alignment across all stages
document.addEventListener('DOMContentLoaded', function() {
    // Find all button containers
    const buttonContainers = document.querySelectorAll('.stage-container .d-flex.justify-content-center');
    
    // Apply consistent styling
    buttonContainers.forEach(container => {
        container.classList.add('gap-3', 'mt-3', 'mb-4');
        
        // Ensure buttons have consistent styling
        const buttons = container.querySelectorAll('.btn');
        buttons.forEach(button => {
            button.style.minWidth = '160px';
            button.style.height = '48px';
        });
    });
    
    // Convert any standalone buttons to the standard format
    const stageContainers = document.querySelectorAll('.stage-container');
    stageContainers.forEach(container => {
        const standaloneButtons = container.querySelectorAll('.btn:not(.d-flex .btn)');
        standaloneButtons.forEach(button => {
            // If button is not already in a flex container
            if (!button.closest('.d-flex')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'd-flex justify-content-center gap-3 mt-3 mb-4';
                button.parentNode.insertBefore(wrapper, button);
                wrapper.appendChild(button);
            }
        });
    });
});
