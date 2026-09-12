"""
Professional HTML Generator - Generate modern WebGIS HTML templates
"""

import html
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class ProfessionalHTMLGenerator(BaseGenerator):
    """Generator for professional WebGIS HTML templates."""

    def __init__(self, config: Dict):
        """Initialize the professional HTML generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate professional HTML template.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with generation results
        """
        results = {
            'success': False,
            'html': '',
            'errors': []
        }

        try:
            html_content = self._generate_professional_template(layers)
            results['html'] = html_content
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"Professional HTML generation error: {str(e)}")

        return results

    def _generate_professional_template(self, layers: List[QgsMapLayer]) -> str:
        """Generate professional WebGIS HTML template.

        :param layers: List of QGIS layers
        :returns: HTML string
        """
        title = html.escape(self.get_config_value('project.title', 'WebGIS Professional'))
        description = html.escape(self.get_config_value('project.description', ''))
        author = html.escape(self.get_config_value('project.author', ''))
        author_row = f"""<div class="list-group-item d-flex justify-content-between align-items-center py-2">
                            <span class="text-muted"><i class="fas fa-user-pen me-2"></i>Auteur</span>
                            <span class="fw-semibold">{author}</span>
                        </div>""" if author else ""

        data_scripts = self._get_data_scripts(layers)
        layer_count = len(layers)

        html_content = f"""<!DOCTYPE html>
<html lang="fr" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="{author}">
    <meta name="description" content="{description}">
    <title>{title}</title>

    <!-- Google Fonts: Inter & Outfit -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">

    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" crossorigin="anonymous">

    <!-- Bootstrap Icons & Font Awesome -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossorigin=""/>

    <!-- Leaflet Draw CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.css"/>

    <!-- Leaflet Measure CSS -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet-measure/3.1.0/leaflet-measure.css"/>

    <!-- Custom WebGIS CSS -->
    <link rel="stylesheet" href="assets/css/professional.css">
</head>
<body>
    <!-- Header -->
    <header class="webgis-header">
        <div class="header-left">
            <div class="logo">
                <div class="logo-icon-wrap">
                    <i class="fas fa-layer-group"></i>
                </div>
                <div class="logo-text-wrap">
                    <span class="logo-brand">WebGIS Studio</span>
                    <span class="logo-badge">Pro</span>
                </div>
            </div>
            <div class="project-info">
                <h1 class="project-title">{title}</h1>
                <p class="project-subtitle">Portail SIG Interactif QGIS</p>
            </div>
        </div>

        <div class="header-center">
            <div class="search-container">
                <i class="fas fa-search search-icon"></i>
                <input type="text" class="search-input" placeholder="Rechercher un attribut, un lieu, une entité..." id="global-search" autocomplete="off">
                <span class="search-badge d-none d-md-inline">Recherche</span>
                <div class="search-results" id="search-results"></div>
            </div>
        </div>

        <div class="header-right">
            <button class="header-btn" id="theme-toggle" title="Basculer Mode Clair / Sombre">
                <i class="fas fa-moon"></i>
            </button>
            <button class="header-btn" id="fullscreen-btn" title="Mode Plein Écran">
                <i class="fas fa-expand"></i>
            </button>
            <button class="header-btn" id="help-btn" title="Informations sur le projet" data-bs-toggle="modal" data-bs-target="#infoModal">
                <i class="fas fa-info-circle"></i>
            </button>
        </div>
    </header>

    <!-- Main Container -->
    <div class="webgis-container">
        <!-- Left Sidebar -->
        <aside class="sidebar" id="sidebar">
            <div class="sidebar-toggle" id="sidebar-toggle" title="Réduire / Agrandir le menu">
                <i class="fas fa-chevron-left"></i>
            </div>

            <nav class="sidebar-nav">
                <div class="nav-item active" data-tool="map" title="Navigation Carte">
                    <i class="fas fa-map"></i>
                    <span class="nav-label">Carte</span>
                </div>
                <div class="nav-item" data-tool="search" title="Recherche">
                    <i class="fas fa-search"></i>
                    <span class="nav-label">Recherche</span>
                </div>
                <div class="nav-item" data-tool="filters" title="Couches & Filtres">
                    <i class="fas fa-sliders-h"></i>
                    <span class="nav-label">Gestion</span>
                </div>
                <div class="nav-item" data-tool="location" title="Ma Géolocalisation">
                    <i class="fas fa-crosshairs"></i>
                    <span class="nav-label">Localisation</span>
                </div>
                <div class="nav-item" data-tool="measure" title="Outils de Mesure">
                    <i class="fas fa-ruler-combined"></i>
                    <span class="nav-label">Mesures</span>
                </div>
                <div class="nav-item" data-tool="draw" title="Outils de Dessin">
                    <i class="fas fa-pencil-ruler"></i>
                    <span class="nav-label">Dessin</span>
                </div>
                <div class="nav-item" data-tool="print" title="Imprimer la Carte">
                    <i class="fas fa-print"></i>
                    <span class="nav-label">Imprimer</span>
                </div>
                <div class="nav-item" data-tool="share" title="Partager le Lien">
                    <i class="fas fa-share-nodes"></i>
                    <span class="nav-label">Partager</span>
                </div>
            </nav>
        </aside>

        <!-- Map Container -->
        <main class="map-container">
            <div id="map"></div>

            <!-- Map Controls Floating Overlay -->
            <div class="map-controls">
                <div class="control-group">
                    <button class="control-btn" id="zoom-in" title="Zoom avant">
                        <i class="fas fa-plus"></i>
                    </button>
                    <button class="control-btn" id="zoom-out" title="Zoom arrière">
                        <i class="fas fa-minus"></i>
                    </button>
                    <button class="control-btn" id="home" title="Vue initiale du projet">
                        <i class="fas fa-home"></i>
                    </button>
                </div>

                <div class="control-group">
                    <button class="control-btn" id="locate" title="Me localiser (GPS)">
                        <i class="fas fa-location-crosshairs"></i>
                    </button>
                    <button class="control-btn" id="measure-distance" title="Mesurer une distance">
                        <i class="fas fa-ruler-horizontal"></i>
                    </button>
                    <button class="control-btn" id="measure-area" title="Mesurer une surface">
                        <i class="fas fa-draw-polygon"></i>
                    </button>
                </div>
            </div>

            <!-- Coordinates & Scale Display -->
            <div class="coordinates-display" id="coordinates">
                <span class="coord-badge"><i class="fas fa-location-dot me-1"></i><span id="lat-display">Lat: 0.00000</span>, <span id="lng-display">Lon: 0.00000</span></span>
            </div>
        </main>

        <!-- Right Panel (Glassmorphism Studio Panel) -->
        <aside class="right-panel" id="right-panel">
            <div class="panel-toggle" id="panel-toggle" title="Masquer / Afficher le panneau">
                <i class="fas fa-chevron-right"></i>
            </div>

            <div class="panel-tabs">
                <button class="tab-btn active" data-tab="layers">
                    <i class="fas fa-layer-group"></i>
                    <span>Couches</span>
                    <span class="badge bg-primary-subtle text-primary rounded-pill ms-1">{layer_count}</span>
                </button>
                <button class="tab-btn" data-tab="legend">
                    <i class="fas fa-list-check"></i>
                    <span>Légende</span>
                </button>
                <button class="tab-btn" data-tab="basemaps">
                    <i class="fas fa-map-location-dot"></i>
                    <span>Fonds</span>
                </button>
            </div>

            <div class="panel-content">
                <!-- Layers Tab -->
                <div class="tab-pane active" id="layers-tab">
                    <div class="panel-section-header">
                        <span class="section-title"><i class="fas fa-layer-group text-primary me-2"></i>Couches Cartographiques</span>
                        <span class="section-desc">Activez, ajustez l'opacité ou zoomez sur chaque donnée</span>
                    </div>
                    <div class="layer-list" id="layer-list">
                        <!-- Layers populated dynamically -->
                    </div>
                </div>

                <!-- Legend Tab -->
                <div class="tab-pane" id="legend-tab">
                    <div class="panel-section-header">
                        <span class="section-title"><i class="fas fa-list-check text-primary me-2"></i>Légende des Couches</span>
                        <span class="section-desc">Symboles et classes extraits directement de QGIS</span>
                    </div>
                    <div class="legend-content" id="legend-content">
                        <!-- Legend populated dynamically -->
                    </div>
                </div>

                <!-- Basemaps Tab -->
                <div class="tab-pane" id="basemaps-tab">
                    <div class="panel-section-header">
                        <span class="section-title"><i class="fas fa-globe text-primary me-2"></i>Fond de Plan</span>
                        <span class="section-desc">Sélectionnez le fond cartographique adapté</span>
                    </div>
                    <div class="basemap-grid" id="basemap-grid">
                        <!-- Basemaps populated dynamically -->
                    </div>
                </div>
            </div>
        </aside>
    </div>

    <!-- Bootstrap 5 Info / About Modal -->
    <div class="modal fade" id="infoModal" tabindex="-1" aria-labelledby="infoModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content glass-modal border-0 shadow-lg">
                <div class="modal-header border-0 pb-0">
                    <div class="d-flex align-items-center gap-2">
                        <div class="modal-logo-icon">
                            <i class="fas fa-map-marked-alt text-primary fs-4"></i>
                        </div>
                        <div>
                            <h5 class="modal-title fw-bold m-0" id="infoModalLabel">{title}</h5>
                            <small class="text-muted">WebGIS Interactive Map</small>
                        </div>
                    </div>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Fermer"></button>
                </div>
                <div class="modal-body py-3">
                    <p class="text-secondary small mb-3">{description or "Application cartographique web moderne générée depuis un projet QGIS."}</p>
                    
                    <div class="list-group list-group-flush rounded-3 border mb-3 small">
                        {author_row}
                        <div class="list-group-item d-flex justify-content-between align-items-center py-2">
                            <span class="text-muted"><i class="fas fa-layer-group me-2"></i>Nombre de couches</span>
                            <span class="badge bg-primary rounded-pill">{layer_count}</span>
                        </div>
                        <div class="list-group-item d-flex justify-content-between align-items-center py-2">
                            <span class="text-muted"><i class="fas fa-code-branch me-2"></i>Technologies</span>
                            <span class="fw-semibold">Leaflet 1.9, Bootstrap 5, GeoJSON</span>
                        </div>
                    </div>
                </div>
                <div class="modal-footer border-0 pt-0">
                    <button type="button" class="btn btn-primary btn-sm px-4 rounded-pill" data-bs-dismiss="modal">Fermer</button>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap 5 Bundle JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" crossorigin="anonymous"></script>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            crossorigin=""></script>

    <!-- Leaflet Draw JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet.draw/1.0.4/leaflet.draw.js"></script>

    <!-- Leaflet Measure JS -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet-measure/3.1.0/leaflet-measure.js"></script>

    <!-- Layer Data Scripts (offline file:// support) -->
{data_scripts}

    <!-- Custom WebGIS JS Modules -->
    <script src="assets/js/config.js"></script>
    <script src="assets/js/map.js"></script>
    <script src="assets/js/layers.js"></script>
    <script src="assets/js/controls.js"></script>
    <script src="assets/js/search.js"></script>
    <script src="assets/js/filters.js"></script>
    <script src="assets/js/ui.js"></script>
    <script src="assets/js/app.js"></script>
</body>
</html>"""

        return html_content

    def _get_data_scripts(self, layers: List[QgsMapLayer]) -> str:
        """Get script tags for preloaded layer JS data."""
        tags = []
        for layer in layers:
            lid = self.get_layer_id(layer)
            tags.append(f'    <script src="data/{lid}.js"></script>')
        return "\n".join(tags)

    def validate(self) -> tuple:
        """Validate professional HTML generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.get_config_value('project.title'):
            errors.append("Project title is required")

        return (len(errors) == 0, errors)