// Fonction pour les accordéons
document.addEventListener("DOMContentLoaded", function () {
  const accordions = document.querySelectorAll(".accordeon");

  accordions.forEach((acc) => {
    const header = acc.querySelector(".header");

    if (header) {
      header.addEventListener("click", () => {
        acc.classList.toggle("active");
      });
    }
  });
});

// Fonction pour initialiser la pagination
function initializePagination() {
    const paginationContainers = document.querySelectorAll('.pagination-container');
    
    paginationContainers.forEach(container => {
        const totalItems = parseInt(container.dataset.totalItems);
        const itemsPerPage = 7;
        const totalPages = Math.ceil(totalItems / itemsPerPage);
        let currentPage = 1;
        
        const list = container.querySelector('.paginated-list');
        const items = list.querySelectorAll('li');
        const prevBtn = container.querySelector('[data-action="prev"]');
        const nextBtn = container.querySelector('[data-action="next"]');
        const currentPageSpan = container.querySelector('.current-page');
        const totalPagesSpan = container.querySelector('.total-pages');
        
        // Fonction pour afficher une page spécifique
        function showPage(pageNumber) {
            currentPage = pageNumber;
            
            // Masquer tous les éléments
            items.forEach(item => {
                item.style.display = 'none';
            });
            
            // Afficher les éléments de la page courante
            items.forEach((item, index) => {
                const itemPage = Math.ceil((index + 1) / itemsPerPage);
                if (itemPage === currentPage) {
                    item.style.display = 'list-item';
                }
            });
            
            // Mettre à jour les contrôles
            currentPageSpan.textContent = currentPage;
            prevBtn.disabled = currentPage === 1;
            nextBtn.disabled = currentPage === totalPages;
            
            // Ajouter/retirer les classes CSS pour le style
            prevBtn.classList.toggle('disabled', currentPage === 1);
            nextBtn.classList.toggle('disabled', currentPage === totalPages);
        }
        
        // Gestionnaires d'événements pour les boutons
        prevBtn.addEventListener('click', () => {
            if (currentPage > 1) {
                showPage(currentPage - 1);
            }
        });
        
        nextBtn.addEventListener('click', () => {
            if (currentPage < totalPages) {
                showPage(currentPage + 1);
            }
        });
        
        // Initialiser la première page
        showPage(1);
    });
}

// Initialiser la pagination au chargement de la page
document.addEventListener('DOMContentLoaded', initializePagination);

// Réinitialiser la pagination si le contenu change dynamiquement
function reinitializePagination() {
    initializePagination();
}