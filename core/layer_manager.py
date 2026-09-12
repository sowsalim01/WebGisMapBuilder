"""
Layer Manager - Handle layer selection, configuration and validation
"""

from typing import Dict, List, Optional
from qgis.core import QgsMapLayer, QgsVectorLayer, QgsRasterLayer


class LayerManager:
    """Manager for handling QGIS layers in the web map building process."""

    SUPPORTED_LAYER_TYPES = [
        'Point',
        'Line',
        'Polygon',
        'Raster',
        'UnknownGeometry'
    ]

    def __init__(self):
        """Initialize the layer manager."""
        self.layer_configs = {}  # layer_id -> configuration dict

    def get_layer_config(self, layer_id: str, layer: Optional[QgsMapLayer] = None) -> Dict:
        """Get configuration for a specific layer.

        :param layer_id: Layer ID
        :param layer: Optional QgsMapLayer instance for intelligent defaults
        :returns: Layer configuration dictionary
        """
        if layer_id not in self.layer_configs:
            # Create intelligent default configuration
            display_name = layer.name() if layer else ''
            opacity = 1.0
            if layer and hasattr(layer, 'opacity'):
                opacity = float(layer.opacity())

            popup_fields = []
            if layer and layer.type() == QgsMapLayer.VectorLayer:
                for field in layer.fields():
                    fname = field.name()
                    alias = field.alias() if field.alias() else fname
                    popup_fields.append({
                        'name': fname,
                        'alias': alias,
                        'visible': True
                    })

            self.layer_configs[layer_id] = {
                'display_name': display_name,
                'visible': True,
                'opacity': opacity,
                'min_zoom': 0,
                'max_zoom': 22,
                'popup_enabled': True,
                'popup_fields': popup_fields,
                'label_field': None,
                'export_format': 'geojson',  # geojson, geojson_optimized
                'simplify': False,
                'simplify_tolerance': 0.0001,
                'z_index': 1
            }

        return self.layer_configs[layer_id]

    def set_layer_config(self, layer_id: str, config: Dict):
        """Set configuration for a specific layer.

        :param layer_id: Layer ID
        :param config: Configuration dictionary
        """
        if layer_id not in self.layer_configs:
            self.layer_configs[layer_id] = {}

        self.layer_configs[layer_id].update(config)

    def is_layer_supported(self, layer: QgsMapLayer) -> tuple:
        """Check if a layer is supported for web export.

        :param layer: QGIS map layer
        :returns: Tuple of (is_supported, reason)
        """
        # Check layer type
        if layer.type() == QgsMapLayer.VectorLayer:
            geometry_type = layer.geometryType()
            if geometry_type is None:
                return (False, "Layer has no geometry")

        elif layer.type() == QgsMapLayer.RasterLayer:
            # Raster layers are supported
            pass

        elif layer.type() == QgsMapLayer.PluginLayer:
            return (False, "Plugin layers are not supported")

        else:
            return (False, f"Layer type {layer.type()} is not supported")

        # Check if layer has a valid source
        if not layer.source():
            return (False, "Layer has no source")

        return (True, "")

    def get_layer_fields(self, layer: QgsMapLayer) -> List[Dict]:
        """Get field information for a vector layer.

        :param layer: QGIS map layer
        :returns: List of field information dictionaries
        """
        if layer.type() != QgsMapLayer.VectorLayer:
            return []

        fields = []
        vector_layer = layer

        for field in vector_layer.fields():
            field_info = {
                'name': field.name(),
                'type': field.type(),
                'type_name': field.typeName(),
                'length': field.length(),
                'precision': field.precision(),
                'comment': field.comment()
            }
            fields.append(field_info)

        return fields

    def estimate_export_size(self, layer: QgsMapLayer) -> Dict:
        """Estimate the export size for a layer.

        :param layer: QGIS map layer
        :returns: Dictionary with size estimation
        """
        if layer.type() != QgsMapLayer.VectorLayer:
            return {'estimated_size': 'Unknown', 'feature_count': 0}

        feature_count = layer.featureCount()

        # Rough estimation: 1KB per feature for simple geometries
        estimated_kb = feature_count * 1

        if estimated_kb < 1024:
            size_str = f"{estimated_kb} KB"
        elif estimated_kb < 1024 * 1024:
            size_str = f"{estimated_kb / 1024:.1f} MB"
        else:
            size_str = f"{estimated_kb / (1024 * 1024):.1f} GB"

        return {
            'estimated_size': size_str,
            'feature_count': feature_count,
            'recommended_format': self._recommend_format(feature_count)
        }

    def _recommend_format(self, feature_count: int) -> str:
        """Recommend export format based on feature count.

        :param feature_count: Number of features
        :returns: Recommended format string
        """
        if feature_count < 1000:
            return 'geojson'
        elif feature_count < 10000:
            return 'geojson_optimized'
        else:
            return 'service'  # Recommend using WMS/WFS

    def get_layer_export_options(self, layer: QgsMapLayer) -> List[str]:
        """Get available export options for a layer.

        :param layer: QGIS map layer
        :returns: List of available export format strings
        """
        options = []

        if layer.type() == QgsMapLayer.VectorLayer:
            options.extend(['geojson', 'geojson_optimized'])

            # Check if WMS is available
            if hasattr(layer, 'providerType'):
                provider = layer.providerType()
                if provider in ['wms', 'wfs']:
                    options.append(provider.upper())

        elif layer.type() == QgsMapLayer.RasterLayer:
            options.append('wms')

        return options if options else ['geojson']

    def clear_layer_configs(self):
        """Clear all layer configurations."""
        self.layer_configs = {}
