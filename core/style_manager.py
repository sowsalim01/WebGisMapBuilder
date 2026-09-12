"""
Style Manager - Convert QGIS styles to web map styles (Leaflet, etc.)
"""

from typing import Dict, List, Optional, Any
from qgis.core import QgsMapLayer, QgsVectorLayer, QgsSingleSymbolRenderer, QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer, QgsRuleBasedRenderer
from qgis.PyQt.QtGui import QColor


class StyleManager:
    """Manager for converting QGIS styles to web map styles."""

    def __init__(self):
        """Initialize the style manager."""
        self.style_cache = {}  # layer_id -> converted style

    def convert_layer_style(self, layer: QgsMapLayer) -> Dict:
        """Convert QGIS layer style to web map style format.

        :param layer: QGIS map layer
        :returns: Dictionary containing web map style configuration
        """
        if layer.id() in self.style_cache:
            return self.style_cache[layer.id()]

        if layer.type() != QgsMapLayer.VectorLayer:
            # Raster layers have different styling
            style = {
                'type': 'raster',
                'opacity': layer.opacity() / 255.0 if hasattr(layer, 'opacity') else 1.0
            }
        else:
            vector_layer = layer
            renderer = vector_layer.renderer()

            if renderer is None:
                style = self._create_default_style(vector_layer)
            else:
                style = self._convert_renderer(renderer, vector_layer)

        self.style_cache[layer.id()] = style
        return style

    def _convert_renderer(self, renderer, layer: QgsVectorLayer) -> Dict:
        """Convert QGIS renderer to web map style.

        :param renderer: QGIS renderer
        :param layer: Vector layer
        :returns: Web map style dictionary
        """
        if isinstance(renderer, QgsSingleSymbolRenderer):
            return self._convert_single_symbol(renderer, layer)
        elif isinstance(renderer, QgsCategorizedSymbolRenderer):
            return self._convert_categorized(renderer, layer)
        elif isinstance(renderer, QgsGraduatedSymbolRenderer):
            return self._convert_graduated(renderer, layer)
        elif isinstance(renderer, QgsRuleBasedRenderer):
            return self._convert_rule_based(renderer, layer)
        else:
            return self._create_default_style(layer)

    def _convert_single_symbol(self, renderer: QgsSingleSymbolRenderer, layer: QgsVectorLayer) -> Dict:
        """Convert single symbol renderer to web style.

        :param renderer: Single symbol renderer
        :param layer: Vector layer
        :returns: Web map style dictionary
        """
        symbol = renderer.symbol()
        return {
            'type': 'single',
            'geometry_type': self._get_geometry_type(layer),
            'style': self._convert_symbol(symbol)
        }

    def _convert_categorized(self, renderer: QgsCategorizedSymbolRenderer, layer: QgsVectorLayer) -> Dict:
        """Convert categorized renderer to web style.

        :param renderer: Categorized renderer
        :param layer: Vector layer
        :returns: Web map style dictionary
        """
        categories = []
        for category in renderer.categories():
            category_style = {
                'value': category.value(),
                'label': category.label(),
                'style': self._convert_symbol(category.symbol())
            }
            categories.append(category_style)

        return {
            'type': 'categorized',
            'geometry_type': self._get_geometry_type(layer),
            'field': renderer.classAttribute(),
            'categories': categories
        }

    def _convert_graduated(self, renderer: QgsGraduatedSymbolRenderer, layer: QgsVectorLayer) -> Dict:
        """Convert graduated renderer to web style.

        :param renderer: Graduated renderer
        :param layer: Vector layer
        :returns: Web map style dictionary
        """
        ranges = []
        for range_obj in renderer.ranges():
            range_style = {
                'min': range_obj.lowerValue(),
                'max': range_obj.upperValue(),
                'label': range_obj.label(),
                'style': self._convert_symbol(range_obj.symbol())
            }
            ranges.append(range_style)

        return {
            'type': 'graduated',
            'geometry_type': self._get_geometry_type(layer),
            'field': renderer.classAttribute(),
            'ranges': ranges
        }

    def _convert_rule_based(self, renderer: QgsRuleBasedRenderer, layer: QgsVectorLayer) -> Dict:
        """Convert rule-based renderer to web style.

        :param renderer: Rule-based renderer
        :param layer: Vector layer
        :returns: Web map style dictionary
        """
        rules = []
        root_rule = renderer.rootRule()

        def process_rule(rule, depth=0):
            rule_info = {
                'filter': rule.filterExpression(),
                'label': rule.label(),
                'style': self._convert_symbol(rule.symbol()) if rule.symbol() else None,
                'children': []
            }

            for child_rule in rule.children():
                rule_info['children'].append(process_rule(child_rule, depth + 1))

            return rule_info

        for rule in root_rule.children():
            rules.append(process_rule(rule))

        return {
            'type': 'rule-based',
            'geometry_type': self._get_geometry_type(layer),
            'rules': rules
        }

    def _convert_symbol(self, symbol) -> Dict:
        """Convert QGIS symbol to web map symbol format.

        :param symbol: QGIS symbol
        :returns: Web map symbol dictionary
        """
        if symbol is None:
            return {}

        symbol_dict = {
            'color': self._convert_color(symbol.color()),
            'opacity': symbol.opacity()
        }

        # Handle size/width based on symbol type
        if hasattr(symbol, 'size'):
            symbol_dict['size'] = symbol.size()
        elif hasattr(symbol, 'width'):
            symbol_dict['size'] = symbol.width()

        # Handle outline/stroke
        if hasattr(symbol, 'symbolLayers'):
            for layer in symbol.symbolLayers():
                if hasattr(layer, 'strokeColor'):
                    symbol_dict['stroke_color'] = self._convert_color(layer.strokeColor())
                if hasattr(layer, 'strokeWidth'):
                    symbol_dict['stroke_width'] = layer.strokeWidth()
                if hasattr(layer, 'strokeStyle'):
                    symbol_dict['stroke_style'] = layer.strokeStyle()

        return symbol_dict

    def _convert_color(self, color: QColor) -> str:
        """Convert QColor to CSS color string.

        :param color: QColor object
        :returns: CSS color string
        """
        if color is None:
            return '#000000'

        return color.name()

    def _get_geometry_type(self, layer: QgsVectorLayer) -> str:
        """Get geometry type string for a vector layer.

        :param layer: Vector layer
        :returns: Geometry type string
        """
        geom_type = layer.geometryType()
        type_map = {
            0: 'Point',
            1: 'Line',
            2: 'Polygon',
            3: 'Unknown',
            4: 'None'
        }
        return type_map.get(geom_type, 'Unknown')

    def _create_default_style(self, layer: QgsVectorLayer) -> Dict:
        """Create default style for a layer.

        :param layer: Vector layer
        :returns: Default style dictionary
        """
        geom_type = self._get_geometry_type(layer)

        default_styles = {
            'Point': {
                'color': '#3388ff',
                'radius': 6,
                'stroke_color': '#000000',
                'stroke_width': 1
            },
            'Line': {
                'color': '#3388ff',
                'weight': 3,
                'opacity': 1.0
            },
            'Polygon': {
                'color': '#3388ff',
                'fill_color': '#3388ff',
                'fill_opacity': 0.5,
                'stroke_color': '#000000',
                'stroke_width': 2
            }
        }

        return {
            'type': 'single',
            'geometry_type': geom_type,
            'style': default_styles.get(geom_type, {})
        }

    def clear_cache(self):
        """Clear the style cache."""
        self.style_cache = {}

    def generate_leaflet_style(self, layer_style: Dict) -> str:
        """Generate Leaflet style JavaScript code.

        :param layer_style: Web map style dictionary
        :returns: JavaScript style code
        """
        if layer_style.get('type') == 'single':
            return self._generate_leaflet_single_style(layer_style)
        elif layer_style.get('type') == 'categorized':
            return self._generate_leaflet_categorized_style(layer_style)
        elif layer_style.get('type') == 'graduated':
            return self._generate_leaflet_graduated_style(layer_style)
        else:
            return '{}'

    def _generate_leaflet_single_style(self, style: Dict) -> str:
        """Generate Leaflet single symbol style.

        :param style: Style dictionary
        :returns: JavaScript style code
        """
        symbol = style.get('style', {})
        geom_type = style.get('geometry_type', 'Point')

        if geom_type == 'Point':
            return f"""{{
                radius: {symbol.get('size', 6)},
                fillColor: '{symbol.get('color', '#3388ff')}',
                color: '{symbol.get('stroke_color', '#000000')}',
                weight: {symbol.get('stroke_width', 1)},
                opacity: {symbol.get('opacity', 1.0)},
                fillOpacity: {symbol.get('opacity', 0.8)}
            }}"""
        elif geom_type == 'Line':
            return f"""{{
                color: '{symbol.get('color', '#3388ff')}',
                weight: {symbol.get('size', 3)},
                opacity: {symbol.get('opacity', 1.0)}
            }}"""
        elif geom_type == 'Polygon':
            return f"""{{
                fillColor: '{symbol.get('color', '#3388ff')}',
                weight: {symbol.get('stroke_width', 2)},
                color: '{symbol.get('stroke_color', '#000000')}',
                opacity: {symbol.get('opacity', 1.0)},
                fillOpacity: {symbol.get('opacity', 0.5)}
            }}"""

        return '{}'

    def _generate_leaflet_categorized_style(self, style: Dict) -> str:
        """Generate Leaflet categorized style function.

        :param style: Style dictionary
        :returns: JavaScript style function code
        """
        field = style.get('field', '')
        categories = style.get('categories', [])

        style_cases = []
        for cat in categories:
            cat_style = self._generate_leaflet_single_style({
                'type': 'single',
                'geometry_type': style.get('geometry_type'),
                'style': cat.get('style', {})
            })
            style_cases.append(f"case '{cat['value']}': return {cat_style};")

        style_function = f"""function(feature) {{
        var value = feature.properties['{field}'];
        switch(value) {{
            {chr(10).join(style_cases)}
            default: return {{}};
        }}
    }}"""

        return style_function

    def _generate_leaflet_graduated_style(self, style: Dict) -> str:
        """Generate Leaflet graduated style function.

        :param style: Style dictionary
        :returns: JavaScript style function code
        """
        field = style.get('field', '')
        ranges = style.get('ranges', [])

        style_cases = []
        for range_obj in ranges:
            range_style = self._generate_leaflet_single_style({
                'type': 'single',
                'geometry_type': style.get('geometry_type'),
                'style': range_obj.get('style', {})
            })
            style_cases.append(
                f"case (value >= {range_obj['min']} && value <= {range_obj['max']}): "
                f"return {range_style};"
            )

        style_function = f"""function(feature) {{
        var value = feature.properties['{field}'];
        switch(true) {{
            {chr(10).join(style_cases)}
            default: return {{}};
        }}
    }}"""

        return style_function

    def generate_leaflet_point_to_layer(self, style: Dict) -> str:
        """Generate Leaflet pointToLayer function code.

        :param style: Style dictionary
        :returns: JavaScript pointToLayer function code
        """
        geom_type = style.get('geometry_type', 'Point')
        if geom_type != 'Point':
            return ""

        style_type = style.get('type', 'single')
        if style_type == 'single':
            single_style = self._generate_leaflet_single_style(style)
            return f"""function(feature, latlng) {{
        return L.circleMarker(latlng, {single_style});
    }}"""
        elif style_type in ['categorized', 'graduated']:
            style_fn = self.generate_leaflet_style(style)
            return f"""function(feature, latlng) {{
        var styleFn = {style_fn};
        return L.circleMarker(latlng, styleFn(feature));
    }}"""

        return """function(feature, latlng) {
        return L.circleMarker(latlng, { radius: 6, fillColor: '#3388ff', color: '#000000', weight: 1, opacity: 1, fillOpacity: 0.8 });
    }"""

    def extract_legend_items(self, layer: QgsMapLayer) -> List[Dict]:
        """Extract legend items (labels, colors, geometry types) from a layer.

        :param layer: QGIS map layer
        :returns: List of dicts with label, color, type
        """
        items = []
        if layer.type() != QgsMapLayer.VectorLayer:
            items.append({
                'label': layer.name(),
                'color': '#888888',
                'type': 'raster'
            })
            return items

        vector_layer = layer
        geom_type = self._get_geometry_type(vector_layer)
        renderer = vector_layer.renderer()

        if renderer is None:
            items.append({'label': vector_layer.name(), 'color': '#3388ff', 'type': geom_type})
            return items

        if isinstance(renderer, QgsSingleSymbolRenderer):
            color = '#3388ff'
            if renderer.symbol():
                color = self._convert_color(renderer.symbol().color())
            items.append({
                'label': vector_layer.name(),
                'color': color,
                'type': geom_type
            })
        elif isinstance(renderer, QgsCategorizedSymbolRenderer):
            for cat in renderer.categories():
                c_color = '#3388ff'
                if cat.symbol():
                    c_color = self._convert_color(cat.symbol().color())
                label = cat.label() if cat.label() else str(cat.value())
                items.append({
                    'label': label,
                    'color': c_color,
                    'type': geom_type,
                    'value': str(cat.value())
                })
        elif isinstance(renderer, QgsGraduatedSymbolRenderer):
            for r in renderer.ranges():
                r_color = '#3388ff'
                if r.symbol():
                    r_color = self._convert_color(r.symbol().color())
                items.append({
                    'label': r.label(),
                    'color': r_color,
                    'type': geom_type,
                    'min': r.lowerValue(),
                    'max': r.upperValue()
                })
        else:
            items.append({'label': vector_layer.name(), 'color': '#3388ff', 'type': geom_type})

        return items
