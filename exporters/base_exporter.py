"""
Base Exporter - Abstract base class for all exporters
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from qgis.core import QgsMapLayer


class BaseExporter(ABC):
    """Abstract base class for web map exporters."""

    def __init__(self, config: Dict):
        """Initialize the exporter.

        :param config: Project configuration
        """
        self.config = config
        self.output_dir = None
        self.progress_callback = None

    def set_output_directory(self, output_dir: str):
        """Set the output directory for export.

        :param output_dir: Output directory path
        """
        self.output_dir = output_dir

    def set_progress_callback(self, callback):
        """Set callback function for progress updates.

        :param callback: Callback function
        """
        self.progress_callback = callback

    def _update_progress(self, value: int, message: str):
        """Update progress if callback is set.

        :param value: Progress value (0-100)
        :param message: Progress message
        """
        if self.progress_callback:
            self.progress_callback(value, message)

    @abstractmethod
    def export(self, layers: List[QgsMapLayer], **kwargs) -> Dict:
        """Export web map project.

        :param layers: List of QGIS layers
        :param kwargs: Additional exporter-specific parameters
        :returns: Dictionary with export results
        """
        pass

    @abstractmethod
    def validate(self) -> tuple:
        """Validate exporter configuration.

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

    def create_directory(self, directory: str) -> bool:
        """Create directory if it doesn't exist.

        :param directory: Directory path
        :returns: True if successful
        """
        import os
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
            return False

    def clean_filename(self, filename: str) -> str:
        """Clean filename for web usage.

        :param filename: Original filename
        :returns: Cleaned filename
        """
        import re
        cleaned = re.sub(r'[^\w\s-]', '', filename)
        cleaned = re.sub(r'[-\s]+', '_', cleaned)
        return cleaned.lower()
