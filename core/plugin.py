"""
Core plugin module - Main plugin logic and orchestration
"""

import os
from typing import Dict, List, Optional

from qgis.core import QgsProject, QgsMapLayer
from qgis.PyQt.QtCore import QObject, pyqtSignal


class WebGisMapBuilderCore(QObject):
    """Core plugin class that manages the web map building process."""

    # Signals for UI updates
    project_loaded = pyqtSignal()
    layers_changed = pyqtSignal(list)
    export_progress = pyqtSignal(int, str)
    export_complete = pyqtSignal(str)
    export_error = pyqtSignal(str)

    def __init__(self, iface):
        """Initialize the core plugin.

        :param iface: QGIS interface instance
        """
        super().__init__()
        self.iface = iface
        self.project = QgsProject.instance()
        self.selected_layers = []
        self.project_config = {}

    def load_current_project(self) -> Dict:
        """Load current QGIS project configuration.

        :returns: Dictionary containing project information
        """
        project_info = {
            'title': self.project.title(),
            'path': self.project.fileName(),
            'crs': self.project.crs().authid(),
            'layers': self.get_all_layers()
        }

        self.project_config = project_info
        self.project_loaded.emit()
        return project_info

    def get_all_layers(self) -> List[Dict]:
        """Get all layers from current project.

        :returns: List of layer information dictionaries
        """
        layers_info = []
        layers = self.project.mapLayers().values()

        for layer in layers:
            # Handle visibility with compatibility for different QGIS versions
            visible = False
            try:
                visible = layer.isVisible()
            except AttributeError:
                try:
                    visible = layer.itemVisibilityChecked()
                except AttributeError:
                    # Fallback to legend tree visibility
                    root = self.project.layerTreeRoot()
                    layer_tree_layer = root.findLayer(layer.id())
                    if layer_tree_layer:
                        visible = layer_tree_layer.isVisible()

            layer_info = {
                'id': layer.id(),
                'name': layer.name(),
                'type': layer.type(),
                'geometry_type': self._get_geometry_type(layer),
                'crs': layer.crs().authid(),
                'source': layer.source(),
                'visible': visible
            }
            layers_info.append(layer_info)

        return layers_info

    def _get_geometry_type(self, layer: QgsMapLayer) -> Optional[str]:
        """Get geometry type for vector layers.

        :param layer: QGIS map layer
        :returns: Geometry type string or None
        """
        if layer.type() == QgsMapLayer.VectorLayer:
            try:
                geom_type = layer.geometryType()
                type_map = {
                    0: 'Point',
                    1: 'Line',
                    2: 'Polygon',
                    3: 'UnknownGeometry',
                    4: 'NoGeometry'
                }
                return type_map.get(geom_type, 'Unknown')
            except:
                return 'Unknown'
        return None

    def select_layer(self, layer_id: str, selected: bool = True):
        """Select or deselect a layer for export.

        :param layer_id: Layer ID
        :param selected: Whether to select the layer
        """
        if selected and layer_id not in self.selected_layers:
            self.selected_layers.append(layer_id)
        elif not selected and layer_id in self.selected_layers:
            self.selected_layers.remove(layer_id)

        self.layers_changed.emit(self.selected_layers)

    def get_selected_layers(self) -> List[QgsMapLayer]:
        """Get selected layer objects.

        :returns: List of selected QgsMapLayer objects
        """
        layers = []
        project_layers = self.project.mapLayers()

        for layer_id in self.selected_layers:
            if layer_id in project_layers:
                layers.append(project_layers[layer_id])

        return layers

    def clear_selection(self):
        """Clear all selected layers."""
        self.selected_layers = []
        self.layers_changed.emit(self.selected_layers)

    def validate_project(self) -> tuple:
        """Validate current project for web export.

        :returns: Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check if project has layers
        if not self.project.mapLayers():
            errors.append("Project contains no layers")

        # Check if any layers are selected
        if not self.selected_layers:
            errors.append("No layers selected for export")

        # Check selected layers
        for layer in self.get_selected_layers():
            # Check CRS
            if layer.crs().isGeographic():
                errors.append(f"Layer '{layer.name()}' uses geographic CRS (WGS84)")

            # Check for large datasets
            if layer.type() == QgsMapLayer.VectorLayer:
                feature_count = layer.featureCount()
                if feature_count > 10000:
                    errors.append(
                        f"Layer '{layer.name()}' contains {feature_count} features. "
                        "Consider using a tile service or filtering data."
                    )

        return (len(errors) == 0, errors)

    def get_project_extent(self) -> Optional[Dict]:
        """Get the extent of selected layers.

        :returns: Dictionary with extent information or None
        """
        layers = self.get_selected_layers()
        if not layers:
            return None

        extent = layers[0].extent()
        for layer in layers[1:]:
            extent.combineExtentWith(layer.extent())

        return {
            'xmin': extent.xMinimum(),
            'ymin': extent.yMinimum(),
            'xmax': extent.xMaximum(),
            'ymax': extent.yMaximum(),
            'crs': layers[0].crs().authid()
        }
