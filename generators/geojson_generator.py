"""
GeoJSON Generator - Export QGIS layers to GeoJSON format
"""

import json
import os
from typing import Dict, List, Optional
from qgis.core import QgsMapLayer, QgsVectorLayer, QgsProject, QgsCoordinateTransformContext

from .base_generator import BaseGenerator


class GeoJSONGenerator(BaseGenerator):
    """Generator for GeoJSON export."""

    def __init__(self, config: Dict):
        """Initialize the GeoJSON generator.

        :param config: Project configuration
        """
        super().__init__(config)

    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate GeoJSON files from QGIS layers.

        :param layers: List of QGIS layers
        :param kwargs: Additional parameters
        :returns: Dictionary with generation results
        """
        results = {
            'success': False,
            'files': [],
            'errors': []
        }

        if self.output_dir is None:
            results['errors'].append("Output directory not set")
            return results

        try:
            # Create data directory
            data_dir = os.path.join(self.output_dir, 'data')
            os.makedirs(data_dir, exist_ok=True)

            # Export each layer
            for layer in layers:
                if layer.type() == QgsMapLayer.VectorLayer:
                    file_result = self._export_layer_to_geojson(layer, data_dir)
                    if file_result['success']:
                        results['files'].append(file_result['file'])
                    else:
                        results['errors'].extend(file_result['errors'])
                else:
                    results['errors'].append(f"Layer '{layer.name()}' is not a vector layer")

            results['success'] = len(results['errors']) == 0

        except Exception as e:
            results['errors'].append(f"GeoJSON generation error: {str(e)}")

        return results

    def _export_layer_to_geojson(self, layer: QgsVectorLayer, output_dir: str) -> Dict:
        """Export a single layer to GeoJSON and JS files with EPSG:4326 reprojection.

        :param layer: QGIS vector layer
        :param output_dir: Output directory
        :returns: Dictionary with export results
        """
        result = {
            'success': False,
            'file': '',
            'js_file': '',
            'errors': []
        }

        try:
            from qgis.core import QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry

            # Generate filename
            layer_id = self.get_layer_id(layer)
            geojson_filename = f"{layer_id}.geojson"
            geojson_filepath = os.path.join(output_dir, geojson_filename)
            js_filename = f"{layer_id}.js"
            js_filepath = os.path.join(output_dir, js_filename)

            # Get layer configuration
            layer_config = self.get_config_value(f'layers.{layer.id()}', {})
            if not layer_config:
                layer_config = self.get_config_value(f'layers.{layer_id}', {})

            # Prepare coordinate transformation to WGS84 (EPSG:4326)
            src_crs = layer.crs()
            dest_crs = QgsCoordinateReferenceSystem('EPSG:4326')
            transform = None
            need_transform = False

            if src_crs.isValid() and src_crs.authid() != 'EPSG:4326':
                transform = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance())
                need_transform = transform.isValid()

            # Export to GeoJSON dict
            geojson_data = self._layer_to_geojson(layer, layer_config, transform, need_transform)

            # Write GeoJSON file
            with open(geojson_filepath, 'w', encoding='utf-8') as f:
                json.dump(geojson_data, f, ensure_ascii=False)

            # Write JS variable file for offline / file:// local support
            with open(js_filepath, 'w', encoding='utf-8') as f:
                json_str = json.dumps(geojson_data, ensure_ascii=False)
                f.write(f"var json_{layer_id} = {json_str};\n")

            result['success'] = True
            result['file'] = geojson_filepath
            result['js_file'] = js_filepath

        except Exception as e:
            result['errors'].append(f"Error exporting layer '{layer.name()}': {str(e)}")

        return result

    def _layer_to_geojson(self, layer: QgsVectorLayer, layer_config: Dict, transform=None, need_transform=False) -> Dict:
        """Convert QGIS layer to GeoJSON format reprojected to EPSG:4326.

        :param layer: QGIS vector layer
        :param layer_config: Layer configuration
        :param transform: Optional QgsCoordinateTransform
        :param need_transform: Boolean flag
        :returns: GeoJSON dictionary
        """
        geojson = {
            'type': 'FeatureCollection',
            'name': layer.name(),
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'
                }
            },
            'features': []
        }

        # Get popup / export fields
        export_fields = []
        popup_fields = layer_config.get('popup_fields', [])
        if popup_fields:
            for pf in popup_fields:
                if isinstance(pf, dict) and pf.get('visible', True):
                    export_fields.append(pf.get('name'))
                elif isinstance(pf, str):
                    export_fields.append(pf)

        if not export_fields:
            # Export all fields if none specified
            export_fields = [field.name() for field in layer.fields()]

        # Export features
        for feature in layer.getFeatures():
            geojson_feature = self._feature_to_geojson(feature, export_fields, transform, need_transform)
            if geojson_feature:
                geojson['features'].append(geojson_feature)

        return geojson

    def _feature_to_geojson(self, feature, export_fields: List[str], transform=None, need_transform=False) -> Optional[Dict]:
        """Convert QGIS feature to GeoJSON feature with optional reprojection.

        :param feature: QGIS feature
        :param export_fields: List of field names to export
        :param transform: Optional QgsCoordinateTransform
        :param need_transform: Boolean
        :returns: GeoJSON feature dictionary
        """
        try:
            from qgis.core import QgsGeometry

            geometry = feature.geometry()
            if geometry is None or geometry.isNull() or geometry.isEmpty():
                return None

            geom = QgsGeometry(geometry)
            if need_transform and transform:
                res = geom.transform(transform)
                if res != 0:
                    pass

            geom_json = json.loads(geom.asJson()) if hasattr(geom, 'asJson') else geom.asJsonObject()

            # Extract properties
            properties = {}
            for field_name in export_fields:
                if field_name in feature.fields().names():
                    value = feature[field_name]
                    if value is None:
                        value = ''
                    elif not isinstance(value, (int, float, str, bool)):
                        value = str(value)
                    properties[field_name] = value

            return {
                'type': 'Feature',
                'geometry': geom_json,
                'properties': properties
            }

        except Exception as e:
            return None

    def _optimize_geojson(self, geojson_data: Dict, simplify_tolerance: float) -> Dict:
        """Optimize GeoJSON data by simplifying geometries.

        :param geojson_data: GeoJSON dictionary
        :param simplify_tolerance: Simplification tolerance
        :returns: Optimized GeoJSON dictionary
        """
        # This is a placeholder for geometry simplification
        # In a full implementation, you would use a library like shapely or topojson
        # For now, we'll just return the original data
        return geojson_data

    def estimate_file_size(self, layer: QgsVectorLayer) -> Dict:
        """Estimate the file size for a layer's GeoJSON export.

        :param layer: QGIS vector layer
        :returns: Dictionary with size estimation
        """
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
            'recommended': self._get_recommendation(feature_count)
        }

    def _get_recommendation(self, feature_count: int) -> str:
        """Get recommendation based on feature count.

        :param feature_count: Number of features
        :returns: Recommendation string
        """
        if feature_count < 1000:
            return "GeoJSON export is suitable"
        elif feature_count < 10000:
            return "Consider enabling simplification"
        else:
            return "Consider using a tile service or filtering data"

    def validate(self) -> tuple:
        """Validate GeoJSON generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        if self.output_dir is None:
            errors.append("Output directory not set")

        return (len(errors) == 0, errors)
