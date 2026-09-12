"""
WebGisMapBuilder - Interactive Web Map Builder for QGIS

A professional QGIS plugin for creating modern, interactive web maps
from QGIS projects and layers.
"""

import os
import platform

from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import Qgis, QgsProject


class WebGisMapBuilder:
    """QGIS Plugin Implementation for WebGisMapBuilder."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.locale = QSettings().value('locale/userLocale')[0:2] if QSettings().contains('locale/userLocale') else 'en'

        # Initialize translation
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WebGisMapBuilder_{}.qm'.format(self.locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare plugin attributes
        self.plugin_name = 'WebGisMapBuilder'
        self.plugin_name_clean = 'WebGisMapBuilder'
        self.actions = []
        self.menu = self.tr(u'&WebGisMapBuilder')
        self.toolbar = self.iface.addToolBar(u'WebGisMapBuilder')
        self.toolbar.setObjectName(self.plugin_name_clean)

        # Check if plugin was started the first time in current QGIS session
        self.first_start = True

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        self.add_action(
            icon_path,
            text=self.tr(u'WebGisMap Builder'),
            callback=self.run,
            parent=self.iface.mainWindow(),
            is_checkable=False
        )

        # Will be set to False in run()
        self.first_start = True

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        pass

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginFromMenu(
                self.tr(u'&WebGisMapBuilder'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def run(self):
        """Run method that performs all the real work"""
        # Create the dialog with elements (after translation) and keep reference
        # only if it's the first time
        if self.first_start:
            from .ui.main_dialog import WebGisMapBuilderDialog
            self.dlg = WebGisMapBuilderDialog(self.iface)

        # show the dialog
        self.dlg.show()
        self.first_start = False

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None,
        is_checkable=False
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/icon.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.
        :type whats_this: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param is_checkable: Flag indicating whether the action is checkable.
        :type is_checkable: bool

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """
        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        action.setCheckable(is_checkable)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def tr(self, message):
        """Get the translation for a string using Qt translation system."""
        return QCoreApplication.translate('WebGisMapBuilder', message)


def classFactory(iface):
    """Load WebGisMapBuilder class from file WebGisMapBuilder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    return WebGisMapBuilder(iface)
