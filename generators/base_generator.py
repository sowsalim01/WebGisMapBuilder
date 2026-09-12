"""
Base Generator - Abstract base class for all web map generators
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from qgis.core import QgsMapLayer


class BaseGenerator(ABC):
    """Abstract base class for web map generators."""

    def __init__(self, config: Dict):
        """Initialize the generator.

        :param config: Project configuration
        """
        self.config = config
        self.output_dir = None

    def set_output_directory(self, output_dir: str):
        """Set the output directory for generated files.

        :param output_dir: Output directory path
        """
        self.output_dir = output_dir

    @abstractmethod
    def generate(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Generate web map content.

        :param layers: List of QGIS layers
        :param kwargs: Additional generator-specific parameters
        :returns: Dictionary with generation results
        """
        pass

    @abstractmethod
    def validate(self) -> tuple:
        """Validate generator configuration.

        :returns: Tuple of (is_valid, error_messages)
        """
        pass

    def get_config_value(self, key_path: str, default=None):
        """Get configuration value by key path.

        :param key_path: Dot-separated key path
        :param default: Default value if key not found
        :returns: Configuration value
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def clean_filename(self, filename: str) -> str:
        """Clean filename for web usage.

        :param filename: Original filename
        :returns: Cleaned filename
        """
        # Remove special characters and spaces
        import re
        cleaned = re.sub(r'[^\w\s-]', '', filename)
        cleaned = re.sub(r'[-\s]+', '_', cleaned)
        return cleaned.lower()

    def get_layer_id(self, layer: QgsMapLayer) -> str:
        """Get a web-safe layer identifier.

        :param layer: QGIS map layer
        :returns: Web-safe layer ID
        """
        return self.clean_filename(layer.name())
