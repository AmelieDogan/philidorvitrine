window.addEventListener('DOMContentLoaded', () => {

    const lines = document.querySelectorAll('.logo-line');
    const baseHeights = [];
    const baseYPositions = [];
    const animations = [];

    // Stocker les hauteurs et positions Y de base
    lines.forEach(line => {
        baseHeights.push(parseFloat(line.getAttribute('height')));
        baseYPositions.push(parseFloat(line.getAttribute('y')));
    });

    // Créer des configurations d'animation différentes pour chaque rayon
    lines.forEach(() => {
        animations.push({
            speed: 0.01 + Math.random() * 0.02,             // Vitesse entre 0.03 et 0.06
            maxScale: 1.5 + Math.random() * 0.2,            // Scale maximum entre 2.2 et 2.6
            minScale: 1.0,                                   // Scale minimum fixe à 1.0 (taille de base)
            currentScale: 1.2 + Math.random() * 0.2,        // Position de départ entre 1.0 et 1.5
            direction: 1,                                    // Direction toujours vers l'extérieur
            pauseDuration: 30 + Math.random() * 40,         // Durée de pause aléatoire (30-70 frames)
            pauseCounter: 0,                                // Compteur pour la pause
            isPaused: false                                 // État de pause
        });
    });

    function animate() {
        lines.forEach((line, i) => {
            const animation = animations[i];
            const baseHeight = baseHeights[i];
            const baseY = baseYPositions[i];
            
            // Si en pause, décrémenter le compteur
            if (animation.isPaused) {
                animation.pauseCounter--;
                if (animation.pauseCounter <= 0) {
                    animation.isPaused = false;
                }
                return; // Ne pas animer pendant la pause
            }
            
            // Mettre à jour le scale en fonction de la direction et de la vitesse
            animation.currentScale += animation.speed * animation.direction;
            
            // Inverser la direction et déclencher une pause si nécessaire
            if (animation.currentScale >= animation.maxScale || animation.currentScale <= animation.minScale) {
                animation.direction *= -1;
                animation.isPaused = true;
                animation.pauseCounter = animation.pauseDuration;
                
                // S'assurer que le scale reste dans les limites
                animation.currentScale = Math.max(animation.minScale, 
                                               Math.min(animation.maxScale, animation.currentScale));
            }
            
            // Calculer la nouvelle hauteur
            const newHeight = baseHeight * animation.currentScale;
            
            // Pour l'extension vers l'extérieur uniquement :
            // - Garder le point central du rayon (baseY + baseHeight/2) fixe
            // - Étendre seulement vers l'extérieur du centre du logo
            const rayonCenter = baseY + baseHeight / 2;
            const logoCenter = 140; // Centre Y du logo
            
            // Déterminer si le rayon est au-dessus ou en dessous du centre
            const isAboveCenter = rayonCenter < logoCenter;
            
            // Calculer la nouvelle position Y
            let newY;
            if (isAboveCenter) {
                // Rayon au-dessus du centre : étendre vers le haut
                newY = rayonCenter - newHeight / 2;
                // Ajuster pour que l'extension se fasse uniquement vers l'extérieur (haut)
                newY = rayonCenter - newHeight + baseHeight / 2;
            } else {
                // Rayon en dessous du centre : étendre vers le bas
                newY = rayonCenter - baseHeight / 2;
            }
            
            // Appliquer les changements
            line.setAttribute('height', newHeight);
            line.setAttribute('y', newY);
        });
        
        requestAnimationFrame(animate);
    }

    // Démarrer l'animation
    animate();

    const logo = document.querySelector('.logo');
    const circle = document.querySelector('mask circle');

    logo.addEventListener('mouseenter', () => {
        lines.forEach((line, i) => {
            const enlargedHeight = baseHeights[i] * 1.8; // 3x plus long
            const baseHeight = baseHeights[i];
            const baseY = baseYPositions[i];
            
            const rayonCenter = baseY + baseHeight / 2;
            const logoCenter = 140;
            const isAboveCenter = rayonCenter < logoCenter;
            
            let newY;
            if (isAboveCenter) {
                newY = rayonCenter - enlargedHeight + baseHeight / 2;
            } else {
                newY = rayonCenter - baseHeight / 2;
            }
            
            line.setAttribute('height', enlargedHeight);
            line.setAttribute('y', newY);
        });

        if (circle) {
            circle.setAttribute('r', 58);
        }
    });

    logo.addEventListener('mouseleave', () => {
        lines.forEach((line, i) => {
            const originalHeight = baseHeights[i];
            const originalY = baseYPositions[i];
            
            line.setAttribute('height', originalHeight);
            line.setAttribute('y', originalY);
        });

        if (circle) {
            circle.setAttribute('r', 53);
        }
    });

});