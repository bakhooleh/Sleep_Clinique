        // Toggle sidebar on mobile
        function toggleSidebar() {
            document.getElementById('sidebar').classList.toggle('active');
        }

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(event) {
            const sidebar = document.getElementById('sidebar');
            const toggle = document.querySelector('.mobile-menu-toggle');
            
            if (window.innerWidth <= 768 && 
                !sidebar.contains(event.target) && 
                !toggle.contains(event.target) && 
                sidebar.classList.contains('active')) {
                sidebar.classList.remove('active');
            }
        });

        // Set current Persian date
        function setPersianDate() {
            const dateElements = document.querySelectorAll('.persian-date');
            const today = new Date().toLocaleDateString('fa-IR');
            dateElements.forEach(el => el.textContent = today);
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', function() {
            setPersianDate();
        });