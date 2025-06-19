const lines = document.querySelectorAll('.logo-line');
const baseHeights = [];
const animations = [];

// Stocker les hauteurs de base et créer des configurations d'animation différentes pour chaque rayon
lines.forEach(() => {
    // Paramètres aléatoires différents pour chaque rayon
    animations.push({
        speed: 0.005 + Math.random() * 0.015,  // Vitesse entre 0.005 et 0.02
        maxScale: 1.2 + Math.random() * 0.4,   // Scale maximum entre 1.2 et 1.6
        minScale: 0.7 + Math.random() * 0.2,   // Scale minimum entre 0.7 et 0.9
        currentScale: 0.8 + Math.random() * 0.4, // Position de départ différente
        direction: Math.random() > 0.5 ? 1 : -1  // Direction initiale aléatoire
    });
});

// Récupérer les hauteurs de base
lines.forEach(line => {
    baseHeights.push(parseFloat(line.getAttribute('height')));
});

function animate() {
    lines.forEach((line, i) => {
        const animation = animations[i];
        const baseHeight = baseHeights[i];
        
        // Mettre à jour le scale en fonction de la direction et de la vitesse
        animation.currentScale += animation.speed * animation.direction;
        
        // Inverser la direction si nécessaire
        if (animation.currentScale >= animation.maxScale || animation.currentScale <= animation.minScale) {
            animation.direction *= -1;
        }
        
        // Calculer la nouvelle hauteur et position
        const newHeight = baseHeight * animation.currentScale;
        
        // Appliquer les changements
        line.setAttribute('height', newHeight);
        line.setAttribute('y', 140 - newHeight / 2);
    });
    
    requestAnimationFrame(animate);
}

// Démarrer l'animation
animate();