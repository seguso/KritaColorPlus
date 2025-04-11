# -----------------------------------------------------------------------------
# PyKritaToolKit
# Copyright (C) 2019-2022 - Grum999
# -----------------------------------------------------------------------------
# SPDX-License-Identifier: GPL-3.0-or-later
#
# https://spdx.org/licenses/GPL-3.0-or-later.html
# -----------------------------------------------------------------------------
# A Krita plugin framework
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# The ekrita_tools module provides extended classes and method for Krita
#
# Main classes from this module
#
# - EKritaToolsId:
#       Provides tools identifiers
#
# - EKritaToolsCategory
#       Provides tools categories
#
# - EKritaTools:
#       Provides methods for quick access to tools
#
# -----------------------------------------------------------------------------

from krita import *

from PyQt5.QtWidgets import (
        QWidget,
        QToolButton,
        QDockWidget
    )

from PyQt5.QtCore import (
        QObject,
        QSignalMapper,
        pyqtSignal as Signal
    )



# -----------------------------------------------------------------------------

class EInvalidValue(Exception):
    """An invalid value has been provided"""
    pass


class EKritaToolsId:
    """Tools Id

    Id is normally the same for QAction and QToolButton
    """
    SVG_SELECT =           'InteractionTool'
    SVG_TEXT =             'SvgTextTool'
    SVG_PATH =             'PathTool'
    SVG_CALLIGRAPHY =      'KarbonCalligraphyTool'

    TFM_TRANSFORM =        'KisToolTransform'
    TFM_MOVE =             'KritaTransform/KisToolMove'
    TFM_CROP =             'KisToolCrop'

    PAINT_BRUSH =          'KritaShape/KisToolBrush'
    PAINT_LINE =           'KritaShape/KisToolLine'
    PAINT_RECTANGLE =      'KritaShape/KisToolRectangle'
    PAINT_ELLIPSE =        'KritaShape/KisToolEllipse'
    PAINT_POLYGON =        'KisToolPolygon'
    PAINT_POLYLINE =       'KisToolPolyline'
    PAINT_PATH =           'KisToolPath'
    PAINT_PENCIL =         'KisToolPencil'
    PAINT_DYNAMIC_BRUSH =  'KritaShape/KisToolDyna'
    PAINT_MULTI_BRUSH =    'KritaShape/KisToolMultiBrush'

    FILL_GRADIENT =        'KritaFill/KisToolGradient'
    FILL_COLORSAMPLER =    'KritaSelected/KisToolColorSampler'
    FILL_COLORMASK =       'KritaShape/KisToolLazyBrush'
    FILL_SMARTPATCH =      'KritaShape/KisToolSmartPatch'
    FILL_BUCKET =          'KritaFill/KisToolFill'
    FILL_ENCLOSEFILL =     'KisToolEncloseAndFill'

    HELPER_ASSISTANT =     'KisAssistantTool'
    HELPER_MEASURE =       'KritaShape/KisToolMeasure'
    HELPER_REFIMG =        'ToolReferenceImages'

    SELECT_RECTANGLE =     'KisToolSelectRectangular'
    SELECT_ELLIPSE =       'KisToolSelectElliptical'
    SELECT_POLYGON =       'KisToolSelectPolygonal'
    SELECT_OUTLINE =       'KisToolSelectOutline'
    SELECT_CONTIGUOUS =    'KisToolSelectContiguous'
    SELECT_SIMILAR =       'KisToolSelectSimilar'
    SELECT_PATH =          'KisToolSelectPath'
    SELECT_MAGNETIC =      'KisToolSelectMagnetic'

    VIEW_ZOOM =            'ZoomTool'
    VIEW_PAN =             'PanTool'


class EKritaToolsCategory:
    """Categories to classify tools"""
    SVG =       'vector'
    TFM =       'transform'
    PAINT =     'paint'
    FILL =      'fill'
    HELPER =    'helper'
    SELECT =    'selection'
    VIEW =      'view'


class EKritaTools:
    """Tools definition"""

    class EKritaToolNotifier(QObject):
        toolChanged = Signal(str, bool)

    __TOOLS = {
        EKritaToolsId.SVG_SELECT: {
            'label': i18n('Select Shapes Tool'),
            'category': EKritaToolsCategory.SVG,
            'widget': None
            },
        EKritaToolsId.SVG_TEXT: {
            'label': i18n('Text Tool'),
            'category': EKritaToolsCategory.SVG,
            'widget': None
            },
        EKritaToolsId.SVG_PATH: {
            'label': i18n('Edit Shapes Tool'),
            'category': EKritaToolsCategory.SVG,
            'widget': None
            },
        EKritaToolsId.SVG_CALLIGRAPHY: {
            'label': i18n('Calligraphy'),
            'category': EKritaToolsCategory.SVG,
            'widget': None
            },

        EKritaToolsId.TFM_TRANSFORM: {
            'label': i18n('Transform a layer or a selection'),
            'category': EKritaToolsCategory.TFM,
            'widget': None
            },
        EKritaToolsId.TFM_MOVE: {
            'label': i18n('Move a layer'),
            'category': EKritaToolsCategory.TFM,
            'widget': None
            },
        EKritaToolsId.TFM_CROP: {
            'label': i18n('Crop the image to an area'),
            'category': EKritaToolsCategory.TFM,
            'widget': None
            },

        EKritaToolsId.PAINT_BRUSH: {
            'label': i18n("Freehand Brush Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_LINE: {
            'label': i18n("Line Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_RECTANGLE: {
            'label': i18n("Rectangle Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_ELLIPSE: {
            'label': i18n("Ellipse Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_POLYGON: {
            'label': i18n("Polygon Tool: Shift-mouseclick ends the polygon."),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_POLYLINE: {
            'label': i18n("Polyline Tool: Shift-mouseclick ends the polyline."),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_PATH: {
            'label': i18n("Bezier Curve Tool: Shift-mouseclick ends the curve."),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_PENCIL: {
            'label': i18n("Freehand Path Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_DYNAMIC_BRUSH: {
            'label': i18n("Dynamic Brush Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },
        EKritaToolsId.PAINT_MULTI_BRUSH: {
            'label': i18n("Multibrush Tool"),
            'category': EKritaToolsCategory.PAINT,
            'widget': None
            },

        EKritaToolsId.FILL_GRADIENT: {
            'label': i18n('Draw a gradient.'),
            'category': EKritaToolsCategory.FILL,
            'widget': None
            },
        EKritaToolsId.FILL_COLORSAMPLER: {
            'label': i18n('Sample a colour from the image or current layer'),
            'category': EKritaToolsCategory.FILL,
            'widget': None
            },
        EKritaToolsId.FILL_COLORMASK: {
            'label': i18n('Colourise Mask Tool'),
            'category': EKritaToolsCategory.FILL,
            'widget': None
            },
        EKritaToolsId.FILL_SMARTPATCH: {
            'label': i18n('Smart Patch Tool'),
            'category': EKritaToolsCategory.FILL,
            'widget': None
            },
        EKritaToolsId.FILL_BUCKET: {
            'label': i18n('Fill a contiguous area of colour with a colour, or fill a selection.'),
            'category': EKritaToolsCategory.FILL,
            'widget': None
            },
        EKritaToolsId.FILL_ENCLOSEFILL: {
            'label': i18n('Enclose and Fill Tool'),
            'category': EKritaToolsCategory.FILL,
            'widget': None
            },

        EKritaToolsId.HELPER_ASSISTANT: {
            'label': i18n('Assistant Tool'),
            'category': EKritaToolsCategory.HELPER,
            'widget': None
            },
        EKritaToolsId.HELPER_MEASURE: {
            'label': i18n('Measure the distance between two points'),
            'category': EKritaToolsCategory.HELPER,
            'widget': None
            },
        EKritaToolsId.HELPER_REFIMG: {
            'label': i18n('Reference Images Tool'),
            'category': EKritaToolsCategory.HELPER,
            'widget': None
            },

        EKritaToolsId.SELECT_RECTANGLE: {
            'label': i18n('Rectangular Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_ELLIPSE: {
            'label': i18n('Elliptical Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_POLYGON: {
            'label': i18n('Polygonal Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_OUTLINE: {
            'label': i18n('Freehand Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_CONTIGUOUS: {
            'label': i18n('Contiguous Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_SIMILAR: {
            'label': i18n('Similar Colour Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_PATH: {
            'label': i18n('Bezier Curve Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },
        EKritaToolsId.SELECT_MAGNETIC: {
            'label': i18n('Magnetic Curve Selection Tool'),
            'category': EKritaToolsCategory.SELECT,
            'widget': None
            },

        EKritaToolsId.VIEW_ZOOM: {
            'label': i18n('Zoom Tool'),
            'category': EKritaToolsCategory.VIEW,
            'widget': None
            },
        EKritaToolsId.VIEW_PAN: {
            'label': i18n('Pan Tool'),
            'category': EKritaToolsCategory.VIEW,
            'widget': None
            }
        }

    __notifier = None
    __toolbox = None
    __signalMapper = QSignalMapper()

    notifier = EKritaToolNotifier()

    @staticmethod
    def init():
        """Initialise static class"""
        def __toolChanged(id):
            """tool has been changed, emit signal"""
            EKritaTools.notifier.toolChanged.emit(id, EKritaTools.__TOOLS[id]['widget'].isChecked())

        def __windowCreated():
            """Executed when a Krita window is created"""
            if EKritaTools.__toolbox is None:

                EKritaTools.__toolbox = Krita.instance().activeWindow().qwindow().findChild(QDockWidget, 'ToolBox')

                EKritaTools.__signalMapper.mapped[str].connect(__toolChanged)

                for id in list(EKritaTools.__TOOLS.keys()):
                    toolButton = EKritaTools.__toolbox.findChild(QToolButton, id)
                    if toolButton:
                        EKritaTools.__TOOLS[id]['widget'] = toolButton
                        toolButton.toggled.connect(EKritaTools.__signalMapper.map)
                        EKritaTools.__signalMapper.setMapping(toolButton, id)

        if EKritaTools.__toolbox is None:
            EKritaTools.toolChanged = Signal(str, bool)
            EKritaTools.__notifier = Krita.instance().notifier()

            EKritaTools.__notifier.setActive(True)
            EKritaTools.__notifier.windowCreated.connect(__windowCreated)

    @staticmethod
    def list(filter=None):
        """Return list of available tools Id

        If given, `filter` is EKritaToolsCategory value or a list of EKritaToolsCategory values
        In this case, only tools matching given category are returned

        if given `filter` is not valid, return empty list
        """
        if filter is None:
            return list(EKritaTools.__TOOLS.keys())
        else:
            if isinstance(filter, str):
                # convert to list
                filter = [filter]
            if isinstance(filter, (list, tuple)):
                return [id for id in list(EKritaTools.__TOOLS.keys()) if EKritaTools.__TOOLS[id]['category'] in filter]
        return []

    @staticmethod
    def get(id):
        """Return tool definition for given id

        returned definition is a dictionnary with following keys:
            'label': <str>, translated label for tool
            'category': <str>, group for tool
            'widget': <QWidget>, widget for tool
        """
        try:
            return EKritaTools.__TOOLS[id]
        except Exception:
            raise EInvalidValue("Given `id` is not valid")

    @staticmethod
    def name(id):
        """Return tool label definition for given id"""
        try:
            return EKritaTools.__TOOLS[id]['label']
        except Exception:
            raise EInvalidValue("Given `id` is not valid")

    @staticmethod
    def category(id):
        """Return tool category definition for given id"""
        try:
            return EKritaTools.__TOOLS[id]['category']
        except Exception:
            raise EInvalidValue("Given `id` is not valid")

    @staticmethod
    def current(filter=None):
        """return id of current tool

        If given, `filter` is EKritaToolsCategory value or a list of EKritaToolsCategory values
        In this case, id is returned for tools for which category is matching given filter; Otherwise return None

        if given `filter` is not valid, return None
        """
        for id in EKritaTools.list(filter):
            toolButton = EKritaTools.__TOOLS[id]['widget']
            if toolButton and toolButton.isChecked():
                return id
        return None

    @staticmethod
    def setCurrent(id):
        """Set current paint tool from given `id`"""
        if id in EKritaTools.__TOOLS and id != EKritaTools.current():
            Krita.instance().action(id).trigger()


# -------------------------------------------------------------------------------------
# initialise module
EKritaTools.init()