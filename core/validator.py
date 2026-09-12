"""
Validator - Validate projects and configurations before export
"""

from typing import Dict, List, Tuple
from qgis.core import QgsMapLayer, QgsVectorLayer


class ProjectValidator:
    """Validator for web map projects."""

    def __init__(self):
        """Initialize the validator."""
        self.warnings = []
        self.errors = []
        self.info = []

    def validate_project(self, layers: List[QgsMapLayer], config: Dict) -> Tuple[bool, List[str], List[str], List[str]]:
        """Validate a complete web map project.

        :param layers: List of selected QGIS layers
        :param config: Project configuration
        :returns: Tuple of (is_valid, errors, warnings, info)
        """
        self.warnings = []
        self.errors = []
        self.info = []

        # Validate configuration
        self._validate_config(config)

        # Validate layers
        self._validate_layers(layers)

        # Validate CRS consistency
        self._validate_crs(layers)

        # Validate data size
        self._validate_data_size(layers)

        # Validate layer configurations
        self._validate_layer_configs(layers, config)

        is_valid = len(self.errors) == 0
        return (is_valid, self.errors, self.warnings, self.info)

    def _validate_config(self, config: Dict):
        """Validate project configuration.

        :param config: Project configuration
        """
        # Check required fields
        if not config.get('project', {}).get('title'):
            if 'project' not in config or not isinstance(config['project'], dict):
                config['project'] = {}
            config['project']['title'] = "WebGIS Map"
            self.warnings.append("Project title was missing, automatically defaulted to 'WebGIS Map'")

        # Check map configuration
        map_config = config.get('map', {})
        center = map_config.get('center')
        if not center or not isinstance(center, list) or len(center) != 2:
            self.errors.append("Invalid map center coordinates")

        zoom = map_config.get('zoom')
        if zoom is None or not isinstance(zoom, int) or zoom < 0 or zoom > 22:
            self.errors.append("Invalid map zoom level")

        # Check basemap
        basemap = config.get('basemap', {})
        if not basemap.get('url'):
            self.errors.append("Basemap URL is missing")

        # Check export format
        export_format = config.get('export', {}).get('format')
        if export_format not in ['web', 'zip', 'server']:
            self.errors.append(f"Invalid export format: {export_format}")

    def _validate_layers(self, layers: List[QgsMapLayer]):
        """Validate selected layers.

        :param layers: List of QGIS layers
        """
        if not layers:
            self.errors.append("No layers selected for export")
            return

        self.info.append(f"Selected {len(layers)} layer(s)")

        for layer in layers:
            # Check layer source
            if not layer.source():
                self.warnings.append(f"Layer '{layer.name()}' has no source")

            # Check layer type
            if layer.type() == QgsMapLayer.PluginLayer:
                self.errors.append(f"Layer '{layer.name()}' is a plugin layer and is not supported")

            # Check for memory layers
            if layer.source().startswith('memory'):
                self.warnings.append(f"Layer '{layer.name()}' is a memory layer and may not persist")

    def _validate_crs(self, layers: List[QgsMapLayer]):
        """Validate CRS consistency across layers.

        :param layers: List of QGIS layers
        """
        if not layers:
            return

        crs_list = [layer.crs().authid() for layer in layers]
        unique_crs = set(crs_list)

        if len(unique_crs) > 1:
            self.warnings.append(
                f"Layers use different CRS: {', '.join(unique_crs)}. "
                "This may cause display issues in the web map."
            )

        # Inform about reprojection to EPSG:4326 for Leaflet
        non_wgs84 = [crs for crs in unique_crs if crs != 'EPSG:4326']
        if non_wgs84:
            self.info.append(
                f"Layers in {', '.join(non_wgs84)} will be automatically reprojected to EPSG:4326 (WGS84) for Leaflet."
            )
        else:
            self.info.append("All layers are already in EPSG:4326 (WGS84).")

    def _validate_data_size(self, layers: List[QgsMapLayer]):
        """Validate data size and provide recommendations.

        :param layers: List of QGIS layers
        """
        total_features = 0
        large_layers = []

        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                feature_count = layer.featureCount()
                total_features += feature_count

                if feature_count > 10000:
                    large_layers.append((layer.name(), feature_count))

        if total_features > 50000:
            self.warnings.append(
                f"Total feature count ({total_features}) is very large. "
                "Consider using a tile service or filtering data."
            )

        for layer_name, count in large_layers:
            if count > 100000:
                self.errors.append(
                    f"Layer '{layer_name}' contains {count} features. "
                    "This will likely cause performance issues. "
                    "Use a tile service or filter the data."
                )
            else:
                self.warnings.append(
                    f"Layer '{layer_name}' contains {count} features. "
                    "Consider optimization or using a tile service."
                )

    def _validate_layer_configs(self, layers: List[QgsMapLayer], config: Dict):
        """Validate layer-specific configurations.

        :param layers: List of QGIS layers
        :param config: Project configuration
        """
        # Check if any layers have popup configurations
        has_popups = False
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer_config = config.get('layers', {}).get(layer.id(), {})
                if layer_config.get('popup_fields'):
                    has_popups = True
                    break

        if not has_popups:
            self.info.append("No popup fields configured. Users won't see attribute information.")

        # Check for label fields
        has_labels = False
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                layer_config = config.get('layers', {}).get(layer.id(), {})
                if layer_config.get('label_field'):
                    has_labels = True
                    break

        if not has_labels:
            self.info.append("No label fields configured. Features won't have labels in the web map.")

    def validate_geojson(self, geojson_data: Dict) -> Tuple[bool, List[str]]:
        """Validate GeoJSON data.

        :param geojson_data: GeoJSON dictionary
        :returns: Tuple of (is_valid, errors)
        """
        errors = []

        if not isinstance(geojson_data, dict):
            errors.append("GeoJSON must be a dictionary")
            return (False, errors)

        # Check required fields
        if 'type' not in geojson_data:
            errors.append("GeoJSON missing 'type' field")

        if geojson_data.get('type') == 'FeatureCollection':
            if 'features' not in geojson_data:
                errors.append("FeatureCollection missing 'features' field")
            elif not isinstance(geojson_data['features'], list):
                errors.append("'features' must be a list")

        elif geojson_data.get('type') == 'Feature':
            if 'geometry' not in geojson_data:
                errors.append("Feature missing 'geometry' field")
            if 'properties' not in geojson_data:
                errors.append("Feature missing 'properties' field")

        return (len(errors) == 0, errors)

    def validate_html_template(self, template_content: str) -> Tuple[bool, List[str]]:
        """Validate HTML template content.

        :param template_content: HTML template string
        :returns: Tuple of (is_valid, errors)
        """
        errors = []

        if not template_content:
            errors.append("Template content is empty")
            return (False, errors)

        # Check for required template placeholders
        required_placeholders = [
            '{{title}}',
            '{{layers}}',
            '{{basemap}}'
        ]

        for placeholder in required_placeholders:
            if placeholder not in template_content:
                errors.append(f"Template missing required placeholder: {placeholder}")

        return (len(errors) == 0, errors)

    def get_validation_report(self) -> str:
        """Generate a formatted validation report.

        :returns: Formatted validation report string
        """
        report_lines = []

        if self.errors:
            report_lines.append("ERRORS:")
            for error in self.errors:
                report_lines.append(f"  ❌ {error}")
            report_lines.append("")

        if self.warnings:
            report_lines.append("WARNINGS:")
            for warning in self.warnings:
                report_lines.append(f"  ⚠️  {warning}")
            report_lines.append("")

        if self.info:
            report_lines.append("INFO:")
            for info in self.info:
                report_lines.append(f"  ℹ️  {info}")
            report_lines.append("")

        if not self.errors and not self.warnings and not self.info:
            report_lines.append("✅ Project validation passed successfully")

        return "\n".join(report_lines)

    def clear(self):
        """Clear validation results."""
        self.warnings = []
        self.errors = []
        self.info = []
