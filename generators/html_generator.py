"""
HTML Generator - Generate HTML templates for web maps
"""

import html
from typing import Dict, List
from qgis.core import QgsMapLayer

from .base_generator import BaseGenerator


class HTMLGenerator(BaseGenerator):
    """Generator for HTML templates."""

    def __init__(self, config: Dict):
        """Initialize the HTML generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate HTML template.

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
            template_type = kwargs.get('template', 'basic')
            html = self._generate_template(template_type, layers)
            results['html'] = html
            results['success'] = True

        except Exception as e:
            results['errors'].append(f"HTML generation error: {str(e)}")

        return results

    def _generate_template(self, template_type: str, layers: List[QgsMapLayer]) -> str:
        """Generate HTML template based on type.

        :param template_type: Template type (basic, dashboard, storymap)
        :param layers: List of QGIS layers
        :returns: HTML string
        """
        if template_type == 'basic':
            return self._generate_basic_template(layers)
        elif template_type == 'dashboard':
            return self._generate_dashboard_template(layers)
        elif template_type == 'storymap':
            return self._generate_storymap_template(layers)
        else:
            return self._generate_basic_template(layers)

    def _get_data_scripts(self, layers: List[QgsMapLayer]) -> str:
        """Get script tags for preloaded layer JS data."""
        tags = []
        for layer in layers:
            lid = self.get_layer_id(layer)
            tags.append(f'    <script src="data/{lid}.js"></script>')
        return "\n".join(tags)

    def _generate_basic_template(self, layers: List[QgsMapLayer]) -> str:
        """Generate basic HTML template.

        :param layers: List of QGIS layers
        :returns: HTML string
        """
        title = html.escape(self.get_config_value('project.title', 'Web Map'))
        description = html.escape(self.get_config_value('project.description', ''))
        author = html.escape(self.get_config_value('project.author', ''))
        data_scripts = self._get_data_scripts(layers)

        html_content = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="{author}">
    <meta name="description" content="{description}">
    <title>{title}</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@600;700&display=swap" rel="stylesheet">

    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossorigin=""/>

    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <!-- Modern Floating Header -->
    <div class="map-floating-header">
        <div class="header-brand">
            <span class="brand-icon"><i class="fas fa-layer-group"></i></span>
            <div class="brand-text">
                <h1 class="map-title">{title}</h1>
                {f'<p class="map-subtitle">{description}</p>' if description else '<p class="map-subtitle">Carte Web Interactive QGIS</p>'}
            </div>
        </div>
    </div>

    <div id="map"></div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            crossorigin=""></script>

    <!-- Layer Data Scripts (offline file:// support) -->
{data_scripts}

    <!-- Custom JS -->
    <script src="js/app.js"></script>
</body>
</html>"""

        return html_content

    def _generate_dashboard_template(self, layers: List[QgsMapLayer]) -> str:
        """Generate dashboard HTML template.

        :param layers: List of QGIS layers
        :returns: HTML string
        """
        title = html.escape(self.get_config_value('project.title', 'Web Map Dashboard'))
        description = html.escape(self.get_config_value('project.description', ''))
        author = html.escape(self.get_config_value('project.author', ''))
        data_scripts = self._get_data_scripts(layers)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="{author}">
    <meta name="description" content="{description}">
    <title>{title}</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossorigin=""/>

    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="dashboard-container">
        <header class="dashboard-header">
            <h1>{title}</h1>
            <div id="statistics" class="stats-bar"></div>
        </header>

        <div class="dashboard-content">
            <main class="dashboard-main">
                <div id="map"></div>
            </main>
        </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            crossorigin=""></script>

    <!-- Layer Data Scripts -->
{data_scripts}

    <!-- Custom JS -->
    <script src="js/app.js"></script>
</body>
</html>"""

        return html_content

    def _generate_storymap_template(self, layers: List[QgsMapLayer]) -> str:
        """Generate story map HTML template.

        :param layers: List of QGIS layers
        :returns: HTML string
        """
        title = html.escape(self.get_config_value('project.title', 'Story Map'))
        description = html.escape(self.get_config_value('project.description', ''))
        author = html.escape(self.get_config_value('project.author', ''))
        data_scripts = self._get_data_scripts(layers)

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="author" content="{author}">
    <meta name="description" content="{description}">
    <title>{title}</title>

    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">

    <!-- Leaflet CSS -->
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
          crossorigin=""/>

    <!-- Font Awesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">

    <!-- Custom CSS -->
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="storymap-container">
        <div id="map"></div>

        <div class="storymap-sidebar">
            <header class="storymap-header">
                <h1>{title}</h1>
                <p>{description or "Application cartographique narrative interactive"}</p>
            </header>
            <div class="storymap-sections">
                <div class="storymap-section active" data-lat="0" data-lng="0" data-zoom="3">
                    <h2>Vue d'ensemble</h2>
                    <p>Bienvenue sur cette application cartographique interactive narrative.</p>
                </div>
            </div>
        </div>
    </div>

    <!-- Leaflet JS -->
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            crossorigin=""></script>

    <!-- Layer Data Scripts -->
{data_scripts}

    <!-- Custom JS -->
    <script src="js/app.js"></script>
</body>
</html>"""

        return html_content

    def validate(self) -> tuple:
        """Validate HTML generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        if not self.get_config_value('project.title'):
            errors.append("Project title is required")

        return (len(errors) == 0, errors)
