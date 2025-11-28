# Association Website

Ce projet est un site web moderne et professionnel destiné à présenter une association, ses projets et son impact sur la communauté.

## Structure du Projet

```
association_website/
├── css/
│   └── style.css
├── js/
│   └── script.js
├── images/
│   └── (placeholder pour les images)
└── index.html
```

## Fonctionnalités

- Design responsive adapté à tous les appareils
- Présentation de l'association et de sa mission
- Galerie de projets avec système de filtrage
- Statistiques d'impact avec animation
- Témoignages avec slider interactif
- Section actualités
- Formulaire de contact
- Carte interactive Google Maps
- Effet de parallaxe et animations au défilement

## Personnalisation

### Images

Pour personnaliser le site, vous devez ajouter vos propres images dans le dossier `images/`. Voici les images nécessaires :

- `hero-bg.jpg` - Image d'arrière-plan de la bannière d'accueil
- `team.jpg` - Photo de l'équipe pour la section "Qui sommes-nous"
- `support-bg.jpg` - Image d'arrière-plan pour la section "Nous soutenir"
- `projet1.jpg` à `projet6.jpg` - Images pour les projets
- `news1.jpg` à `news3.jpg` - Images pour les actualités
- `testimonial1.jpg` à `testimonial3.jpg` - Photos des personnes témoignant

### API Google Maps

Pour que la carte Google Maps fonctionne correctement, vous devez :

1. Obtenir une clé API Google Maps sur [Google Cloud Platform](https://console.cloud.google.com/)
2. Remplacer `API_KEY` dans le script à la fin du fichier `index.html` par votre clé API

```html
<script async defer src="https://maps.googleapis.com/maps/api/js?key=VOTRE_CLÉ_API&callback=initMap"></script>
```

### Coordonnées de l'association

Dans le fichier `js/script.js`, mettez à jour les coordonnées GPS de l'association :

```javascript
const associationLocation = { lat: 48.8566, lng: 2.3522 }; // Remplacer par vos coordonnées
```

## Améliorations futures possibles

- Ajout d'une section blog avec articles complets
- Intégration d'un système de dons en ligne
- Galerie de photos avec lightbox
- Calendrier d'événements interactif
- Espace membre/bénévole
- Version multilingue

## Technologies utilisées

- HTML5
- CSS3 (avec variables CSS pour la personnalisation)
- JavaScript (ES6+)
- Google Maps API
- Font Awesome (pour les icônes)
- Google Fonts (Montserrat et Poppins)

## Crédits

Ce site a été créé pour présenter de manière professionnelle les activités d'une association fictive.
