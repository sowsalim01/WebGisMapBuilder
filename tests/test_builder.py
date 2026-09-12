import os
import sys
import shutil
import unittest
from unittest.mock import MagicMock

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock qgis modules for headless CLI execution if running outside QGIS
if 'qgis' not in sys.modules:
    qgis_mock = MagicMock()
    qgis_core_mock = MagicMock()

    class MockMapLayer:
        VectorLayer = 0
        RasterLayer = 1
        PluginLayer = 2

    qgis_core_mock.QgsMapLayer = MockMapLayer
    sys.modules['qgis'] = qgis_mock
    sys.modules['qgis.core'] = qgis_core_mock
    sys.modules['qgis.PyQt'] = qgis_mock
    sys.modules['qgis.PyQt.QtCore'] = qgis_mock
    sys.modules['qgis.PyQt.QtGui'] = qgis_mock
    sys.modules['qgis.PyQt.QtWidgets'] = qgis_mock


class TestConfigManager(unittest.TestCase):
    """Test ConfigManager functionality."""

    def test_default_config(self):
        from core.config_manager import ConfigManager
        cm = ConfigManager()
        cfg = cm.get_config()

        self.assertIn('project', cfg)
        self.assertIn('map', cfg)
        self.assertIn('basemap', cfg)
        self.assertIn('theme', cfg)
        self.assertIn('ui', cfg)
        self.assertIn('export', cfg)

        # Check default UI controls
        self.assertTrue(cfg['ui'].get('show_layer_control'))
        self.assertTrue(cfg['ui'].get('show_scale_control'))
        self.assertTrue(cfg['ui'].get('show_legend'))

    def test_get_set_config(self):
        from core.config_manager import ConfigManager
        cm = ConfigManager()
        cm.set_config('project.title', 'Mon Beau Projet')
        self.assertEqual(cm.get_config('project.title'), 'Mon Beau Projet')

        cm.set_config('theme.primary_color', '#ff0000')
        self.assertEqual(cm.get_config('theme.primary_color'), '#ff0000')

    def test_themes_and_basemaps(self):
        from core.config_manager import ConfigManager
        cm = ConfigManager()
        themes = cm.get_available_themes()
        self.assertIn('professional', themes)
        self.assertIn('dark', themes)

        basemaps = cm.get_basemap_providers()
        self.assertIn('osm', basemaps)
        self.assertIn('carto_positron', basemaps)
        self.assertIn('esri_world', basemaps)


class TestLayerManager(unittest.TestCase):
    """Test LayerManager functionality."""

    def test_layer_config_defaults(self):
        from core.layer_manager import LayerManager
        lm = LayerManager()
        cfg = lm.get_layer_config('layer_123')

        self.assertTrue(cfg['visible'])
        self.assertEqual(cfg['opacity'], 1.0)
        self.assertEqual(cfg['min_zoom'], 0)
        self.assertEqual(cfg['max_zoom'], 22)

    def test_layer_config_update(self):
        from core.layer_manager import LayerManager
        lm = LayerManager()
        lm.set_layer_config('layer_123', {'display_name': 'Communes', 'opacity': 0.8})
        cfg = lm.get_layer_config('layer_123')

        self.assertEqual(cfg['display_name'], 'Communes')
        self.assertEqual(cfg['opacity'], 0.8)


class TestStyleManager(unittest.TestCase):
    """Test StyleManager conversions."""

    def test_color_and_styles(self):
        from core.style_manager import StyleManager
        sm = StyleManager()

        single_style = {
            'type': 'single',
            'geometry_type': 'Point',
            'style': {
                'color': '#ff0000',
                'stroke_color': '#000000',
                'size': 8,
                'opacity': 1.0
            }
        }
        js_code = sm.generate_leaflet_style(single_style)
        self.assertIn("fillColor: '#ff0000'", js_code)
        self.assertIn("radius: 8", js_code)

        point_func = sm.generate_leaflet_point_to_layer(single_style)
        self.assertIn("L.circleMarker", point_func)


class TestValidator(unittest.TestCase):
    """Test ProjectValidator."""

    def test_validate_config(self):
        from core.validator import ProjectValidator
        pv = ProjectValidator()

        # Missing required config
        bad_config = {'project': {}, 'map': {}}
        valid, errs, warns, info = pv.validate_project([], bad_config)
        self.assertFalse(valid)
        self.assertTrue(len(errs) > 0)


class TestGenerators(unittest.TestCase):
    """Test HTML and CSS generators."""

    def test_html_generator(self):
        from core.config_manager import ConfigManager
        from generators.html_generator import HTMLGenerator

        cm = ConfigManager()
        cm.set_config('project.title', 'Test Map')
        gen = HTMLGenerator(cm.get_config())

        res = gen.generate([], template='basic')
        self.assertTrue(res['success'])
        self.assertIn('Test Map', res['html'])
        self.assertIn('leaflet.js', res['html'])
        self.assertIn('id="map"', res['html'])

    def test_css_generator(self):
        from core.config_manager import ConfigManager
        from generators.css_generator import CSSGenerator

        cm = ConfigManager()
        gen = CSSGenerator(cm.get_config())
        res = gen.generate([], template='basic')

        self.assertTrue(res['success'])
        self.assertIn('#map', res['css'])
        self.assertIn('.leaflet-popup-content', res['css'])
        self.assertIn('.leaflet-legend-box', res['css'])

    def test_js_generator_legend(self):
        from core.config_manager import ConfigManager
        from generators.js_generator import JavaScriptGenerator

        cm = ConfigManager()
        cm.set_config('ui.show_legend', True)
        gen = JavaScriptGenerator(cm.get_config())

        legend_data = [
            {
                'layer_name': "L'Étendue des Forêts",
                'items': [
                    {'label': 'Feuillus', 'color': '#22c55e', 'type': 'Polygon'},
                    {'label': 'Résineux', 'color': '#15803d', 'type': 'Polygon'}
                ]
            }
        ]
        legend_code = gen._generate_legend_code(legend_data)
        self.assertIn('leaflet-legend-box', legend_code)
        self.assertIn('Feuillus', legend_code)
        self.assertIn('div.innerHTML =', legend_code)



class TestExporters(unittest.TestCase):
    """Test full exporter workflows."""

    def test_web_exporter(self):
        import tempfile
        import shutil
        from core.config_manager import ConfigManager
        from exporters.web_exporter import WebExporter
        from exporters.zip_exporter import ZipExporter

        temp_dir = os.path.join(tempfile.gettempdir(), 'webgismap_test_export')
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        cm = ConfigManager()
        cm.set_config('project.title', 'Export Test Map')

        exporter = WebExporter(cm.get_config())
        exporter.set_output_directory(temp_dir)

        res = exporter.export([])
        self.assertTrue(res['success'], f"Export failed with errors: {res.get('errors')}")
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'index.html')))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'assets', 'css', 'professional.css')))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'assets', 'js', 'app.js')))

        # Check that no hardcoded author appears when author is not configured
        with open(os.path.join(temp_dir, 'index.html'), 'r', encoding='utf-8') as f:
            index_html = f.read()
        self.assertNotIn('Mamadou', index_html)

        # Check fitMapToBounds in JS files
        with open(os.path.join(temp_dir, 'assets', 'js', 'map.js'), 'r', encoding='utf-8') as f:
            map_js = f.read()
        self.assertIn('fitMapToBounds', map_js)

        with open(os.path.join(temp_dir, 'assets', 'js', 'layers.js'), 'r', encoding='utf-8') as f:
            layers_js = f.read()
        self.assertIn('indexFeature', layers_js)
        self.assertIn('fitMapToBounds', layers_js)

        with open(os.path.join(temp_dir, 'assets', 'js', 'search.js'), 'r', encoding='utf-8') as f:
            search_js = f.read()
        self.assertIn('indexFeature', search_js)

        # Test basic template export explicitly
        basic_dir = os.path.join(tempfile.gettempdir(), 'webgismap_test_basic')
        if os.path.exists(basic_dir):
            shutil.rmtree(basic_dir)
        exporter_basic = WebExporter(cm.get_config())
        exporter_basic.set_output_directory(basic_dir)
        res_basic = exporter_basic.export([], template='basic')
        self.assertTrue(res_basic['success'], f"Basic export failed: {res_basic.get('errors')}")
        self.assertTrue(os.path.exists(os.path.join(basic_dir, 'css', 'style.css')))
        self.assertTrue(os.path.exists(os.path.join(basic_dir, 'js', 'app.js')))
        shutil.rmtree(basic_dir)

        # Test ZIP exporter
        zip_exporter = ZipExporter(cm.get_config())
        zip_exporter.set_output_directory(temp_dir)
        zip_res = zip_exporter.export([])
        self.assertTrue(zip_res['success'], f"ZIP export failed with errors: {zip_res.get('errors')}")
        self.assertTrue(os.path.exists(zip_res['output_file']))

        # Cleanup
        shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main()
