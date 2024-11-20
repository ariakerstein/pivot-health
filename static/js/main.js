document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Handle file upload
    const fileUpload = document.querySelector('.file-upload');
    if (fileUpload) {
        fileUpload.addEventListener('change', function(e) {
            const fileName = e.target.files[0].name;
            const fileLabel = document.querySelector('.file-label');
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        });
    }

    // Animate recommendation cards on hover
    const recommendationCards = document.querySelectorAll('.recommendations .card');
    recommendationCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Handle onboarding task completion
    const taskButtons = document.querySelectorAll('.onboarding-tasks button');
    taskButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskItem = this.closest('.list-group-item');
            taskItem.classList.add('completed');
            this.textContent = 'Completed';
            this.disabled = true;
        });
    });
});
