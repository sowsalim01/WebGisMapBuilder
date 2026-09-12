"""
Configuration Manager - Handle project configuration and settings
"""

import json
import logging
import os
from typing import Dict, Optional

from qgis.core import QgsProject

log = logging.getLogger(__name__)


class ConfigManager:
    """Manager for handling web map project configuration."""

    DEFAULT_CONFIG = {
        'project': {
            'title': 'WebGIS Map',
            'description': '',
            'author': '',
            'version': '1.0'
        },
        'map': {
            'center': [0, 0],
            'zoom': 2,
            'min_zoom': 0,
            'max_zoom': 18,
            'bounds': None
        },
        'basemap': {
            'provider': 'osm',
            'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            'attribution': '© OpenStreetMap contributors',
            'max_zoom': 19
        },
        'template': 'professional',  # professional, basic, dashboard, storymap
        'theme': {
            'name': 'professional',
            'primary_color': '#2c3e50',
            'secondary_color': '#3498db',
            'font_family': 'Arial, sans-serif',
            'panel_background': '#ffffff',
            'panel_opacity': 0.95
        },
        'ui': {
            'show_zoom_control': True,
            'show_scale_control': True,
            'show_layer_control': True,
            'show_attribution': True,
            'show_fullscreen': True,
            'show_mouse_position': True,
            'show_legend': True,
            'show_search': True
        },
        'export': {
            'format': 'web',  # web, zip, server
            'output_dir': '',
            'include_data': True,
            'export_js_fallback': True,  # Generate var json_xxx in data/xxx.js for offline file:// support
            'optimize_images': True,
            'minify_js': False,
            'minify_css': False
        },
        'advanced': {
            'custom_css': '',
            'custom_js': '',
            'external_libraries': []
        }
    }

    def __init__(self):
        """Initialize the configuration manager."""
        self.config = self.DEFAULT_CONFIG.copy()
        self.config_file = None

    def load_config(self, config_path: str) -> bool:
        """Load configuration from a JSON file.

        :param config_path: Path to configuration file
        :returns: True if successful, False otherwise
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)

            # Merge with default config to ensure all keys exist
            self.config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
            self.config_file = config_path
            return True

        except Exception as e:
            print(f"Error loading config: {e}")
            return False

    def save_config(self, config_path: Optional[str] = None) -> bool:
        """Save configuration to a JSON file.

        :param config_path: Path to save configuration (uses current config_file if None)
        :returns: True if successful, False otherwise
        """
        if config_path is None:
            config_path = self.config_file

        if config_path is None:
            return False

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            self.config_file = config_path
            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """Merge loaded config with default config.

        :param default: Default configuration
        :param loaded: Loaded configuration
        :returns: Merged configuration
        """
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value

        return result

    def get_config(self, key_path: str = '') -> Dict:
        """Get configuration value by key path.

        :param key_path: Dot-separated key path (e.g., 'map.center')
        :returns: Configuration value or dictionary
        """
        if not key_path:
            return self.config

        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return self.DEFAULT_CONFIG

        return value

    def set_config(self, key_path: str, value: any):
        """Set configuration value by key path.

        :param key_path: Dot-separated key path (e.g., 'map.center')
        :param value: Value to set
        """
        keys = key_path.split('.')
        config = self.config

        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        config[keys[-1]] = value

    def reset_config(self):
        """Reset configuration to default values."""
        self.config = self.DEFAULT_CONFIG.copy()

    def load_from_qgis_project(self):
        """Load basic configuration from current QGIS project."""
        project = QgsProject.instance()

        # Set project title (with fallbacks to baseName and default)
        title = project.title() or project.baseName() or "WebGIS Map"
        self.set_config('project.title', title)

        # Get project extent for map bounds reprojected to EPSG:4326
        layers = list(project.mapLayers().values())
        if layers:
            try:
                from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform
                wgs84 = QgsCoordinateReferenceSystem('EPSG:4326')
                total_extent = None

                for layer in layers:
                    if not layer.isValid():
                        continue
                    ext = layer.extent()
                    if ext.isEmpty() or ext.isNull():
                        continue
                    try:
                        if layer.crs() != wgs84:
                            ct = QgsCoordinateTransform(layer.crs(), wgs84, project)
                            ext_wgs = ct.transformBoundingBox(ext)
                        else:
                            ext_wgs = ext

                        if total_extent is None:
                            total_extent = ext_wgs
                        else:
                            total_extent.combineExtentWith(ext_wgs)
                    except Exception as e:  # noqa: BLE001
                        log.warning("Could not transform extent for layer '%s': %s", layer.name(), e)

                if total_extent and not total_extent.isEmpty():
                    center = total_extent.center()
                    # Leaflet center is [lat, lng] = [y, x]
                    self.set_config('map.center', [center.y(), center.x()])
                    self.set_config('map.bounds', [
                        [total_extent.yMinimum(), total_extent.xMinimum()],
                        [total_extent.yMaximum(), total_extent.xMaximum()]
                    ])

                    # Calculate appropriate zoom level based on degree span
                    max_span = max(total_extent.width(), total_extent.height())
                    if max_span > 60:
                        zoom = 3
                    elif max_span > 20:
                        zoom = 5
                    elif max_span > 5:
                        zoom = 7
                    elif max_span > 1:
                        zoom = 9
                    elif max_span > 0.2:
                        zoom = 12
                    elif max_span > 0.05:
                        zoom = 14
                    else:
                        zoom = 16

                    self.set_config('map.zoom', zoom)
            except Exception as e:
                print(f"Error calculating project extent: {e}")

    def get_basemap_providers(self) -> Dict[str, Dict]:
        """Get available basemap providers.

        :returns: Dictionary of basemap providers
        """
        return {
            'osm': {
                'name': 'OpenStreetMap',
                'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                'attribution': '© OpenStreetMap contributors',
                'max_zoom': 19
            },
            'carto_positron': {
                'name': 'CartoDB Positron',
                'url': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
                'attribution': '© OpenStreetMap contributors © CARTO',
                'max_zoom': 20
            },
            'carto_dark': {
                'name': 'CartoDB Dark',
                'url': 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                'attribution': '© OpenStreetMap contributors © CARTO',
                'max_zoom': 20
            },
            'esri_world': {
                'name': 'ESRI World Imagery',
                'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                'attribution': '© Esri',
                'max_zoom': 17
            },
            'opentopomap': {
                'name': 'OpenTopoMap',
                'url': 'https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
                'attribution': '© OpenStreetMap contributors © SRTM',
                'max_zoom': 17
            }
        }

    def get_available_themes(self) -> Dict[str, Dict]:
        """Get available UI themes.

        :returns: Dictionary of themes
        """
        return {
            'professional': {
                'name': 'Professional GIS',
                'primary_color': '#2c3e50',
                'secondary_color': '#3498db',
                'font_family': 'Arial, sans-serif',
                'panel_background': '#ffffff',
                'panel_opacity': 0.95
            },
            'minimal': {
                'name': 'Minimal',
                'primary_color': '#333333',
                'secondary_color': '#666666',
                'font_family': 'Helvetica, sans-serif',
                'panel_background': '#ffffff',
                'panel_opacity': 1.0
            },
            'dark': {
                'name': 'Dark',
                'primary_color': '#1a1a1a',
                'secondary_color': '#4a4a4a',
                'font_family': 'Arial, sans-serif',
                'panel_background': '#2a2a2a',
                'panel_opacity': 0.95
            },
            'light': {
                'name': 'Light',
                'primary_color': '#f8f9fa',
                'secondary_color': '#e9ecef',
                'font_family': 'Arial, sans-serif',
                'panel_background': '#ffffff',
                'panel_opacity': 1.0
            },
            'government': {
                'name': 'Government',
                'primary_color': '#003366',
                'secondary_color': '#0055a4',
                'font_family': 'Georgia, serif',
                'panel_background': '#f5f5f5',
                'panel_opacity': 0.95
            }
        }

    def validate_config(self) -> tuple:
        """Validate current configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check required fields
        if not self.get_config('project.title'):
            errors.append("Project title is required")

        # Check map configuration
        center = self.get_config('map.center')
        if not isinstance(center, list) or len(center) != 2:
            errors.append("Map center must be a list of two coordinates")

        zoom = self.get_config('map.zoom')
        if not isinstance(zoom, int) or zoom < 0 or zoom > 22:
            errors.append("Map zoom must be an integer between 0 and 22")

        # Check basemap
        basemap_url = self.get_config('basemap.url')
        if not basemap_url:
            errors.append("Basemap URL is required")

        return (len(errors) == 0, errors)
