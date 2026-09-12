# WebGisMapBuilder

**Plugin QGIS professionnel pour créer des cartes web interactives modernes**

WebGisMapBuilder est un plugin QGIS puissant qui transforme vos projets QGIS en applications WebGIS professionnelles, modernes et interactives basées sur Leaflet.

![QGIS Plugin](https://img.shields.io/badge/QGIS-3.0+-blue)
![Python](https://img.shields.io/badge/Python-3.8+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Fonctionnalités principales

### 🎨 Templates Professionnels
- **Professional WebGIS** - Interface moderne avec sidebar, header, et panneaux avancés
- **Basic Map** - Carte plein écran avec panneaux de base
- **Dashboard** - Interface avec statistiques et carte
- **Story Map** - Carte narrative séquentielle

### 🗺️ Cartographie Interactive
- **Moteur Leaflet** - Carte web performante et légère
- **Fonds de carte multiples** - OpenStreetMap, CartoDB, ESRI, OpenTopoMap
- **Symbologie QGIS** - Conversion automatique des styles QGIS
- **Popups personnalisables** - Configuration des champs attributaires
- **Légende interactive** - Génération automatique depuis QGIS

### 🛠️ Outils Avancés
- **Recherche globale** - Recherche dans les couches et attributs
- **Filtres dynamiques** - Filtrage basé sur les attributs
- **Outils de mesure** - Distance et surface
- **Outils de dessin** - Points, lignes, polygones
- **Export GeoJSON** - Conversion automatique des couches

### 🎯 Interface Utilisateur
- **Mode sombre/clair** - Thème avec persistance
- **Design responsive** - Desktop, tablette, mobile
- **Sidebar rétractable** - Outils de cartographie
- **Panneau droit** - Gestion couches/légende/fonds
- **Popups élégants** - Design moderne et professionnel

## 📋 Prérequis

- **QGIS** 3.0 ou supérieur
- **Python** 3.8 ou supérieur
- **Connexion internet** (pour les bibliothèques CDN Leaflet)

## 🚀 Installation

### Via le dépôt de plugins QGIS

1. Ouvrez QGIS
2. Allez dans `Plugins` > `Gérer les extensions`
3. Recherchez "WebGisMapBuilder"
4. Cliquez sur `Installer le plugin`

### Installation manuelle

1. Téléchargez le plugin depuis le dépôt GitHub
2. Extrayez l'archive dans le dossier plugins QGIS :
   - **Windows**: `C:\Users\VOTRE_NOM\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Redémarrez QGIS
4. Activez le plugin dans `Plugins` > `Gérer les extensions`

## 📖 Utilisation

### Démarrage rapide

1. **Ouvrez un projet QGIS** avec vos couches
2. **Lancez le plugin** via `Plugins` > `WebGisMapBuilder` > `WebGisMap Builder`
3. **Configurez votre carte** :
   - Sélectionnez les couches à inclure
   - Configurez les champs de popup
   - Choisissez le template et le thème
   - Sélectionnez le fond de carte
4. **Prévisualisez** votre carte web
5. **Exportez** votre carte web

### Configuration des couches

#### Onglet "Couches"
- Cochez les couches à inclure dans l'export
- Réorganisez l'ordre des couches avec les boutons Monter/Descendre
- Configurez les propriétés (titre, visibilité, opacité, zoom)

#### Onglet "Style & Thème"
- Choisissez le template (Professional, Basic, Dashboard, Story Map)
- Sélectionnez le thème graphique (Professional, Dark, Minimal, etc.)
- Configurez le fond de carte par défaut

#### Onglet "Interactivité"
- Sélectionnez les champs à afficher dans les popups
- Activez/désactivez les contrôles de carte

#### Onglet "Prévisualisation"
- Générez un aperçu temporaire
- Testez l'interactivité avant export
- Ouvrez dans votre navigateur

#### Onglet "Exportation"
- Choisissez le format (Dossier Web, ZIP, Package Serveur)
- Sélectionnez le dossier de destination
- Exportez votre carte web

### Templates disponibles

#### Professional WebGIS (Recommandé)
Interface moderne et professionnelle avec :
- Header avec recherche globale
- Sidebar gauche avec outils
- Panneau droit avec onglets (Couches/Légende/Fonds)
- Mode sombre/clair
- Design responsive

#### Basic Map
Carte plein écran simple avec :
- Contrôles Leaflet de base
- Panneaux de couches et légende
- Popup standards

#### Dashboard
Interface analytique avec :
- Statistiques et KPI
- Graphiques et tableaux
- Carte intégrée

#### Story Map
Carte narrative avec :
- Sections séquentielles
- Navigation par étapes
- Contenu contextuel

## 🎨 Personnalisation

### Thèmes disponibles
- **Professional GIS** - Bleu ardoise & moderne
- **Dark GIS** - Thème sombre élégant
- **Minimal Clean** - Épuré blanc/gris
- **Light GIS** - Clair contemporain
- **Government** - Bleu officiel

### Fonds de carte
- **OpenStreetMap** - Standard
- **CartoDB Positron** - Fond clair épuré
- **CartoDB Dark** - Fond sombre
- **ESRI World Imagery** - Satellite
- **OpenTopoMap** - Relief

### Personnalisation CSS
Le template Professional utilise des variables CSS personnalisables :
```css
:root {
    --primary-color: #2c3e50;
    --secondary-color: #3498db;
    --bg-primary: #ffffff;
    --text-primary: #2c3e50;
}
```

## 📁 Structure de l'export

### Template Professional
```
WebMap_Export/
├── index.html                 # Page principale
├── assets/
│   ├── css/
│   │   └── professional.css   # Styles modernes
│   ├── js/
│   │   ├── config.js         # Configuration
│   │   ├── map.js            # Initialisation carte
│   │   ├── layers.js         # Gestion couches
│   │   ├── controls.js       # Contrôles carte
│   │   ├── search.js         # Recherche
│   │   ├── filters.js        # Filtres
│   │   ├── ui.js             # Interface
│   │   └── app.js            # Application
│   └── icons/                # Icônes
└── data/
    ├── layer1.geojson        # Données couches
    ├── layer2.geojson
    └── layer3.geojson
```

### Template Basic
```
WebMap_Export/
├── index.html                 # Page principale
├── css/
│   └── style.css             # Styles
├── js/
│   └── app.js                # JavaScript
└── data/
    ├── layer1.geojson
    └── layer2.geojson
```

## 🔧 Configuration avancée

### Configuration JavaScript
Le fichier `config.js` contient toute la configuration de la carte :
```javascript
const WebGISConfig = {
    project: {
        title: 'Ma Carte Web',
        description: 'Description du projet'
    },
    map: {
        center: [0, 0],
        zoom: 3,
        minZoom: 0,
        maxZoom: 20
    },
    basemap: {
        default: 'osm'
    }
};
```

### Performance
Pour les gros datasets :
- Utilisez le filtrage pour réduire les données
- Considérez l'utilisation de services WMS/WFS
- Optimisez les géométries complexes
- Utilisez l'indexation spatiale

## 🐛 Dépannage

### Erreurs courantes

#### Plugin ne se charge pas
- Vérifiez la compatibilité QGIS (version 3.0+)
- Vérifiez les permissions du dossier plugins
- Redémarrez QGIS après installation

#### Couches ne s'affichent pas
- Vérifiez que les couches sont visibles dans QGIS
- Vérifiez le système de coordonnées (WGS84 recommandé)
- Consultez les logs QGIS pour les erreurs

#### Export échoue
- Vérifiez les permissions du dossier de destination
- Assurez-vous d'avoir assez d'espace disque
- Vérifiez que les noms de fichiers ne contiennent pas de caractères spéciaux

#### Carte vide dans le navigateur
- Vérifiez la console du navigateur (F12)
- Assurez-vous que les fichiers GeoJSON sont présents
- Vérifiez les chemins relatifs dans le HTML

### Logs et debug
Les logs du plugin sont disponibles dans :
- **QGIS**: `Vue` > `Panneaux` > `Journal des messages`
- **Navigateur**: Console développeur (F12)

## 🤝 Contribution

Les contributions sont les bienvenues ! Pour contribuer :

1. Fork le projet
2. Créez une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour les détails.

## 👨‍💻 Auteurs

Mamadou SOW - sowsalim01@gmail.com

## 🙏 Remerciements

- **QGIS** - Plateforme SIG open source
- **Leaflet** - Bibliothèque cartographique JavaScript
- **Font Awesome** - Icônes modernes
- **Google Fonts** - Typographie professionnelle

## 📞 Support

Pour le support et les questions :
- **Issues GitHub** - Signalez des bugs et demandes de fonctionnalités
- **Documentation** - Consultez la documentation en ligne
- **Forum QGIS** - Communauté d'utilisateurs

## 🗺️ Roadmap

### Version future
- [ ] Support des tuiles vectorielles
- [ ] Intégration MapLibre GL
- [ ] Support WMS/WFS avancé
- [ ] Éditeur de style visuel
- [ ] Export vers serveurs cloud
- [ ] Templates personnalisables
- [ ] Support multi-langues

## 📚 Ressources

- [Documentation QGIS](https://docs.qgis.org/)
- [Documentation Leaflet](https://leafletjs.com/reference.html)
- [Tutoriels WebGIS](https://tutorials.webgis.org/)

---

**WebGisMapBuilder** - Transformez vos projets QGIS en cartes web professionnelles !

*Créé avec ❤️ pour la communauté SIG*