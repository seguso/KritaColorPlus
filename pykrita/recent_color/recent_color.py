# TODO TODO pick color stops creating layers
# TODO when changing color via the selector, then press mix, it didn't start new layer, because it erases all
# TODO when using C on reference, add layer to real image.
# TODO when chanign opacity of reference, do it on real image
# todo pick color via button does not reset opacity of layer

from . mouseMonitor import MouseMonitor
from PyQt5.QtWidgets import QTreeView
from PyQt5.QtCore import Qt, QModelIndex, QItemSelectionModel
import pprint
import time
from . import globals as g

# Throttling for debug logs

from .whichtool import EKritaTools, EKritaToolsId  # Import the necessary classes
from .brush_cycler import brush_cycler  # Import the brush cycler instance
from .brush_list_widget import BrushListDialog  # Import the brush list dialog
from .slider import KritaStyleSlider # Import the new slider


from .rgb import rgb, rgbOfColorArray,colorArrayOfRgb, colorArray255_3_OfRgb


from krita import *

from krita import (
    Krita,)

from pathlib import Path

from PyQt5.QtCore import (
    Qt,
    QObject,
    QEvent,
    QPointF,
    QRect,
    QTimer,
    pyqtSignal)  # Added pyqtSignal

from PyQt5.QtGui import (
    QTransform,
    QPainter,
    QBrush,
    QColor,
    QPolygonF,
    QInputEvent,
    QKeyEvent,
    QCursor)

from PyQt5.QtWidgets import (
    QWidget,
    QMdiArea,
    QTextEdit,
    QAbstractScrollArea,
    QAction, QMenu,
    QLabel,           # Added QLabel
    QHBoxLayout,      # Added QHBoxLayout
    # Added QVBoxLayout (already used but good to be explicit)
    QVBoxLayout,
    # Added QPushButton (already used but good to be explicit)
    QPushButton,
    QDockWidget       # Added QDockWidget back
    )

from typing import List, Tuple, Optional, Sequence, Union # Add Union


# from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os
import os.path
import time
import datetime
import xml
import math
import json
import queue
from typing import List, Any, Optional  # Add List, Any, Optional

from .spectral import *

def arrEqual(a1, a2):
    return (int(a1[0] * 255.0) == int(a2[0] * 255.0) and
            int(a1[1] * 255.0) == int(a2[1] * 255.0) and
            int(a1[2] * 255.0) == int(a2[2] * 255.0))


# Helper function to sample a pixel and return [R, G, B] 0-255
# Returns None if sampling fails
def sample_pixel_rgb0255(document, x, y):
    try:
        # Ensure coordinates are integers
        ix, iy = int(x), int(y)

        # Basic boundary check (pixelData might also handle this)
        doc_width = document.width()
        doc_height = document.height()
        if ix < 0 or iy < 0 or ix >= doc_width or iy >= doc_height:
             log(f"Warning: Sample point ({ix}, {iy}) out of bounds ({doc_width}x{doc_height})")
             # Decide how to handle out-of-bounds: return None, black, or clamp coordinates
             # Clamping might be reasonable:
             ix = max(0, min(ix, doc_width - 1))
             iy = max(0, min(iy, doc_height - 1))
             # return None # Option 1: Skip this pixel
             # return [0.0, 0.0, 0.0] # Option 2: Treat as black

        pixBytes = document.pixelData(ix, iy, 1, 1)
        if not pixBytes:
            log(f"Warning: pixelData returned empty for ({ix}, {iy})")
            return None # Or return a default color like black [0, 0, 0]

        # Convert bytes to QColor
        # Assuming RGBA8888 or RGBA64 based on previous code context
        # Note: Krita's internal format might vary, adjust if needed
        if len(pixBytes) == 4: # Assuming RGBA8888
            imageData = QImage(pixBytes, 1, 1, QImage.Format_RGBA8888)
        elif len(pixBytes) == 8: # Assuming RGBA64
             imageData = QImage(pixBytes, 1, 1, QImage.Format_RGBA64)
        # Add handling for other formats if necessary, e.g., grayscale
        # elif len(pixBytes) == 1: # Example: Grayscale
        #     imageData = QImage(pixBytes, 1, 1, QImage.Format_Grayscale8)
        #     gray_val = imageData.pixelColor(0, 0).blackF() * 255.0
        #     return [gray_val, gray_val, gray_val]
        else:
            log(f"Warning: unsupported pixelData len {len(pixBytes)} at ({ix}, {iy})")
            return None # Or return a default color

        pixelC: QColor = imageData.pixelColor(0, 0)
        # Return as [R, G, B] list (Note: QColor uses RGB order)
        # Ensure values are floats 0-255 for spectral_mix
        return [float(pixelC.red()), float(pixelC.green()), float(pixelC.blue())]
    except Exception as e:
        log(f"Error sampling pixel at ({x}, {y}): {e}")
        return None # Return None on any error


# Helper function to blend a list of colors [[R,G,B], ...] using spectral_mix
# Assumes colors are lists of floats [0-255]
# Define the expected type for a single color: List of 3 numbers (int or float)
ColorType = List[Union[float, int]]
# Define the input type: List containing optional colors
InputColorsType = List[Optional[ColorType]]

def blend_colors_spectral(colors: InputColorsType) -> ColorType:
    """
    Blends a list of colors using spectral mixing.

    Args:
        colors: A list where each element is either None or a list of 3 numbers
                (int or float) representing RGB values [0-255].

    Returns:
        A list of 3 numbers representing the blended RGB color.

    Raises:
        TypeError: If the input is not a list, or if any element (that is not None)
                   is not a list of 3 numbers (int or float).
        ValueError: If the input list is empty or contains only None values after validation.
    """
    if not isinstance(colors, list):
        raise TypeError(f"Input must be a list, but got {type(colors).__name__}")

    validated_colors: List[ColorType] = []
    for i, color in enumerate(colors):
        if color is None:
            continue # Skip None values as intended by original filter

        if not isinstance(color, list) or len(color) != 3:
            raise TypeError(f"Element at index {i} must be a list of 3 numbers or None, but got {type(color).__name__} with length {len(color) if isinstance(color, list) else 'N/A'}")

        for j, component in enumerate(color):
            if not isinstance(component, (int, float)):
                raise TypeError(f"Color component at index {i}[{j}] must be an int or float, but got {type(component).__name__}")

        validated_colors.append(color) # Add the validated color

    if not validated_colors:
        raise ValueError("Cannot blend empty list or list containing only None values.")

    if len(validated_colors) == 1:
        # If only one valid color, return it directly
        log("solo uno")
        return validated_colors[0]

    # Start with the first valid color
    # Start with the first valid color
    blended_color = validated_colors[0]

    # log(f"i validi sono {len(validated_colors)}")
    # Sequentially mix in the remaining valid colors
    for i in range(1, len(validated_colors)):
        # The weight 't' for spectral_mix represents the proportion of the *new* color
        # being added to the current blend. For the (i+1)-th color overall (index i),
        # its weight in the final mix should be 1/(i+1).
        t = 1.0 / (float(i) + 1.0)
        # Call spectral_mix directly, using the correct variable name
        blended_color = spectral_mix(blended_color, validated_colors[i], t)

    # The final blended_color is already in [R, G, B] format (0-255)
    return blended_color



def toggleAutoMixing():

    if g.g_auto_mix_enabled:

        g.g_auto_mix_enabled = False
        g.g_actionAutoMix.setChecked(False)

        # you probably disabled auto-mixing in order to manually change the fg color (= target color). but the color selector has probably changed. so reset it to the current target
        if g.g_virtual_fg_color_rgb is not None:
            setFgColor(g.g_virtual_fg_color_rgb)
        g.g_auto_mix_ignore_this_color_in_onfgcolorchanged = None



        quickMessage("Disabled auto-mixing")

        g.g_btn_auto_mix.setChecked(False)
    else:
        quickMessage("Enabled auto-mixing")
        g.g_auto_mix_enabled = True
        g.g_btn_auto_mix.setChecked(True)
        g.g_actionAutoMix.setChecked(True)


def toggleDirtyBrush():

    if g.g_dirty_brush_overall_enabled:

        g.g_dirty_brush_overall_enabled = False
        g.g_actionDirtyBrush.setChecked(False)

        quickMessage("Disabled dirty brush")

        g.g_btn_dirty_brush.setChecked(False)
    else:
        quickMessage("Enabled dirty brush")
        g.g_dirty_brush_overall_enabled = True
        g.g_btn_dirty_brush.setChecked(True)
        g.g_actionDirtyBrush.setChecked(True)


def log(s):
    g.printCount += 1
    print(f"{g.printCount}: {s}\n\n")

# --- Custom Widget for Clickable Color Squares ---


class ClickableColorLabel(QLabel):
    """ A QLabel that displays a color and emits a signal when clicked. """
    clicked = pyqtSignal(QColor)

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(32, 32)
        self.setStyleSheet(
            f"background-color: {self._color.name()}; border: 1px solid black;")
        self.setToolTip(f"Color: {self._color.name()}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # log(f"ClickableColorLabel clicked: emitting color {self._color.name()}")
            self.clicked.emit(self._color)
        super().mousePressEvent(event)

# --- Docker Definition ---
# Note: Removed duplicate class definition below


class HelloDocker(DockWidget):
    def __init__(self):
        super().__init__()
        g.g_docker_instance = self  # Store instance globally
        self.setWindowTitle("ColorPlus")
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)

        mainLayout = QVBoxLayout()
        mainWidget.setLayout(mainLayout)

        # Color History has been moved to a separate docker

        # active color

        layoutHorizColorAndDry = QHBoxLayout()
        mainLayout.addLayout(layoutHorizColorAndDry)

        btnDry = QPushButton("Dry paper", mainWidget)
        layoutHorizColorAndDry.addWidget(btnDry)
        font = btnDry.font()
        font.setPixelSize(15)
        btnDry.setFont(font)
        btnDry.setMinimumHeight(50)

        btnDry.clicked.connect(lambda: dryPaper())

        g.lblActiveColor = QLabel()
        g.lblActiveColor.setToolTip("Current foreground color")
        layoutHorizColorAndDry.addWidget(g.lblActiveColor)
        # lblActiveColor.setStyleSheet("background-color: red")
        g.lblActiveColor.setMinimumHeight(45)
        g.lblActiveColor.setMinimumWidth(65)

        # # mix layout
        layoutHorizMix = QHBoxLayout()
        mainLayout.addLayout(layoutHorizMix)

   
        g.g_slider_mix = KritaStyleSlider(mainWidget, "Mix level")
        g.g_slider_mix.setToolTip("Mix level")
        layoutHorizMix.addWidget(g.g_slider_mix)
        # Set initial value (0.0-1.0 range)
        g.g_slider_mix.setValue(g.g_how_much_canvas_to_pick)
        g.g_slider_mix.valueChanged.connect(self.mixLevelValueChanged)

        # auto-mix layout

        layoutHorizAutoMix = QHBoxLayout()
        mainLayout.addLayout(layoutHorizAutoMix)

        # auto-mix button

        g.g_btn_auto_mix = QPushButton("Auto-mix color", mainWidget)
        g.g_btn_auto_mix.setCheckable(True)
        layoutHorizAutoMix.addWidget(g.g_btn_auto_mix)
        g.g_btn_auto_mix.clicked.connect(toggleAutoMixing)
        # g.g_btn_auto_mix.setMinimumHeight(60)

        font = g.g_btn_auto_mix.font()
        font.setPixelSize(15)
        g.g_btn_auto_mix.setFont(font)

        # auto-mix level

        g.g_slider_auto_mix_level = KritaStyleSlider(mainWidget, "Auto-mix level")
        g.g_slider_auto_mix_level.setToolTip("Auto-mix level")
        layoutHorizAutoMix.addWidget(g.g_slider_auto_mix_level)
        # Set initial value (0.0-1.0 range)
        g.g_slider_auto_mix_level.setValue(g.g_auto_mix__how_much_canvas_to_pick)
        g.g_slider_auto_mix_level.valueChanged.connect(
            self.autoMixLevelValueChanged)

        # dirty brush layout
        layoutHorizDirtyBrush = QHBoxLayout()
        mainLayout.addLayout(layoutHorizDirtyBrush)

        # dirty brush button
        g.g_btn_dirty_brush = QPushButton("Dirty brush", mainWidget)
        g.g_btn_dirty_brush.setCheckable(True)
        layoutHorizDirtyBrush.addWidget(g.g_btn_dirty_brush)
        g.g_btn_dirty_brush.clicked.connect(toggleDirtyBrush)
        # g.g_btn_dirty_brush.setMinimumHeight(60)

        font = g.g_btn_dirty_brush.font()
        font.setPixelSize(15)
        g.g_btn_dirty_brush.setFont(font)

        # dirty brush level
        g.g_slider_dirty_brush_level = KritaStyleSlider(mainWidget, "Dirty brush level")
        g.g_slider_dirty_brush_level.setToolTip("Dirty brush level")
        layoutHorizDirtyBrush.addWidget(g.g_slider_dirty_brush_level)
        # Set initial value (map 0.04-0.5 range to 0.0-1.0)
        initial_dirty_value = (g.g_dirty_brush_level - 0.04) / 0.46
        g.g_slider_dirty_brush_level.setValue(max(0.0, min(1.0, initial_dirty_value))) # Clamp value
        g.g_slider_dirty_brush_level.valueChanged.connect(
            self.dirtyBrushLevelValueChanged)
            
        # mix radius layout
        layoutHorizMixRadius = QHBoxLayout()
        mainLayout.addLayout(layoutHorizMixRadius)
        
        # mix radius button (replacing static label)
        g.g_btn_mix_radius = QPushButton("Mix radius", mainWidget)
        g.g_btn_mix_radius.setCheckable(True)
        g.g_btn_mix_radius.setChecked(g.g_mix_radius_enabled)
        layoutHorizMixRadius.addWidget(g.g_btn_mix_radius)
        font = g.g_btn_mix_radius.font()
        font.setPixelSize(15)
        g.g_btn_mix_radius.setFont(font)
        # g.g_btn_mix_radius.setMinimumHeight(60)
        g.g_btn_mix_radius.clicked.connect(self.toggleMixRadiusEnabled)
        
        # mix radius dial
        g.g_slider_mix_radius = KritaStyleSlider(mainWidget, "Mix radius")
        g.g_slider_mix_radius.setToolTip("Mix radius in pixels (0-20)")
        layoutHorizMixRadius.addWidget(g.g_slider_mix_radius)
        # Set initial value (map 0-20 range to 0.0-1.0)
        initial_radius_value = g.g_mix_radius / 20.0 if g.g_mix_radius is not None else 0.0
        g.g_slider_mix_radius.setValue(max(0.0, min(1.0, initial_radius_value))) # Clamp value
        g.g_slider_mix_radius.valueChanged.connect(self.mixRadiusValueChanged)

        # Brush cycler layout
        layoutHorizBrushCycler = QHBoxLayout()
        mainLayout.addLayout(layoutHorizBrushCycler)
        
        # Brush cycler button
        g.g_btn_brush_cycler = QPushButton("Cycle brushes", mainWidget)
        g.g_btn_brush_cycler.setCheckable(True)
        layoutHorizBrushCycler.addWidget(g.g_btn_brush_cycler)
        g.g_btn_brush_cycler.clicked.connect(self.toggleBrushCycler)
        # g.g_btn_brush_cycler.setMinimumHeight(60)
        
        # Set initial tooltip
        if brush_cycler.brush_list:
            g.g_btn_brush_cycler.setToolTip(f"Cycle brushes (enabled: {brush_cycler.enabled}, {len(brush_cycler.brush_list)} brushes)")
        else:
            g.g_btn_brush_cycler.setToolTip("Cycle brushes (no brushes in list)")
        
        # font = g.g_btn_brush_cycler.font()
        # # font.setPixelSize(14)
        # g.g_btn_brush_cycler.setFont(font)
        
        # Button to add current brush to cycle list
        btnAddBrush = QPushButton("+", mainWidget)
        btnAddBrush.setToolTip("Add current brush to cycle list")
        layoutHorizBrushCycler.addWidget(btnAddBrush)
        btnAddBrush.clicked.connect(self.addCurrentBrushToCycleList)
        # btnAddBrush.setMinimumHeight(60)
        btnAddBrush.setMaximumWidth(40)
        
        # Button to edit brush list
        btnEditBrushList = QPushButton("Edit List", mainWidget)
        btnEditBrushList.setToolTip("View and edit brush cycle list")
        layoutHorizBrushCycler.addWidget(btnEditBrushList)
        btnEditBrushList.clicked.connect(self.showBrushListEditor)
        # btnEditBrushList.setMinimumHeight(60)
        
        # pick color button
        # self.buttonPickColor = QPushButton("Pick color", mainWidget)

        # self.buttonPickColor.setMinimumHeight(50)
        # self.buttonPickColor.setCheckable(True)
        # font = self.buttonPickColor.font()
        # font.setPixelSize(20)
        # self.buttonPickColor.setFont(font)

        # # mainLayout.addWidget(self.buttonPickColor) # non lo voglio, prende spazio

        # self.buttonPickColor.clicked.connect(self.pickColorClicked) # quindi non lo connetto
        # g.g_btn_pick_color = self.buttonPickColor

    # Color History functionality has been moved to ColorHistoryDocker class

    def leaveEvent(self, event):
        pass
        # log("Mouse left the dock widget")

        # label = QLabel("Hello", self)
        # self.setWidget(label)
        # self.label = label

    def autoMixLevelValueChanged(self, value): # Changed 'level' to 'value' (float 0.0-1.0)
        # log(f"autoMixLevelValueChanged {value}")

        g.g_auto_mix__how_much_canvas_to_pick = value # Use the float value directly

        Krita.instance().writeSetting("colorPlus", "g.g_auto_mix__how_much_canvas_to_pick",
                                      str(g.g_auto_mix__how_much_canvas_to_pick))

        quickMessage(
            f"Changed auto-mixing to {round(g.g_auto_mix__how_much_canvas_to_pick * 100.0)} %")
            
    def dirtyBrushLevelValueChanged(self, value): # Changed 'level' to 'value' (float 0.0-1.0)
        # Convert slider value (0.0-1.0) to the desired range (0.04-0.5)
        g.g_dirty_brush_level = 0.04 + value * 0.46
        
        Krita.instance().writeSetting("colorPlus", "g.g_dirty_brush_level",
                                      str(g.g_dirty_brush_level))
        
        quickMessage(
            f"Changed dirty brush level to {round(g.g_dirty_brush_level * 100.0)} %")
            
    def mixRadiusValueChanged(self, value): # Changed 'level' to 'value' (float 0.0-1.0)
        # Convert slider value (0.0-1.0) to the desired range (0-20 pixels)
        g.g_mix_radius = value * 20.0
        
        Krita.instance().writeSetting("colorPlus", "g.g_mix_radius",
                                      str(g.g_mix_radius))
        
        quickMessage(
            f"Changed mix radius to {round(g.g_mix_radius)} pixels")
            
    def toggleMixRadiusEnabled(self):
        # Inverte lo stato della variabile g_mix_radius_enabled
        g.g_mix_radius_enabled = not g.g_mix_radius_enabled
        
        # Aggiorna lo stato del pulsante
        g.g_btn_mix_radius.setChecked(g.g_mix_radius_enabled)
        
        # Salva lo stato nelle impostazioni di Krita per renderlo persistente
        Krita.instance().writeSetting("colorPlus", "g.g_mix_radius_enabled",
                                     "1" if g.g_mix_radius_enabled else "0")
        
        # Mostra un messaggio all'utente
        quickMessage(f"{'Enabled' if g.g_mix_radius_enabled else 'Disabled'} mix radius")

    
    def mixLevelValueChanged(self, value): # Changed 'level' to 'value' (float 0.0-1.0)

        g.g_how_much_canvas_to_pick = value # Use the float value directly

        Krita.instance().writeSetting("colorPlus", "g.g_how_much_canvas_to_pick",
                                      str(g.g_how_much_canvas_to_pick))

        quickMessage(
            f"Changed mixing level to {round(g.g_how_much_canvas_to_pick * 100.0)} %")

    def toggleBrushCycler(self):
        """Toggle brush cycling on/off"""
        is_enabled = brush_cycler.toggle_enabled()
        g.g_btn_brush_cycler.setChecked(is_enabled)
        
        # Update the tooltip
        self.updateBrushCyclerButton()
        
        if is_enabled:
            # Check if we have brushes in the list
            if not brush_cycler.brush_list:
                # Try to add current brush if list is empty
                if brush_cycler.add_current_brush():
                    quickMessage("Enabled brush cycling with current brush")
                    # Update tooltip again since brush list changed
                    self.updateBrushCyclerButton()
                else:
                    quickMessage("Enabled brush cycling, but no brushes in list. Add brushes with + button.")
            else:
                quickMessage(f"Enabled brush cycling with {len(brush_cycler.brush_list)} brushes")
        else:
            quickMessage("Disabled brush cycling")
    
    def addCurrentBrushToCycleList(self):
        """Add the current brush to the cycle list"""
        if brush_cycler.add_current_brush():
            quickMessage(f"Added current brush to cycle list. Total: {len(brush_cycler.brush_list)}")
            # Update the tooltip to reflect the new brush count
            self.updateBrushCyclerButton()
        else:
            quickMessage("Could not add current brush to cycle list")
    
    def showBrushListEditor(self):
        """Show the brush list editor dialog"""
        dialog = BrushListDialog(Krita.instance().activeWindow().qwindow())
        dialog.brush_list_widget.brushListChanged.connect(self.updateBrushCyclerButton)
        dialog.exec_()
    
    def updateBrushCyclerButton(self):
        """Update the brush cycler button state based on the current brush list"""
        # Update the button state based on whether cycling is enabled and brushes exist
        g.g_btn_brush_cycler.setChecked(brush_cycler.enabled)
        
        # Update the tooltip to show the number of brushes
        if brush_cycler.brush_list:
            g.g_btn_brush_cycler.setToolTip(f"Cycle brushes (enabled: {brush_cycler.enabled}, {len(brush_cycler.brush_list)} brushes)")
        else:
            g.g_btn_brush_cycler.setToolTip("Cycle brushes (no brushes in list)")
    
    def canvasChanged(self, canvas):
        # self.label.setText("Hellodocker: canvas changed");
        pass


def get_layer_model():
    app = Krita.instance()
    kis_layer_box = next(
        (d for d in app.dockers() if d.objectName() == 'KisLayerBox'), None)
    view = kis_layer_box.findChild(QTreeView, 'listLayers')
    return view.model(), view.selectionModel()

# Helper function to recursively get all visible paint layers in top-down order
def get_all_layers(node):
    layers = []
    if not node:
        return layers
    for child in node.childNodes():
        # Check if child is visible
        if child.visible():
             if child.type() == 'paintlayer':
                 layers.append(child)
             elif child.type() == 'grouplayer':
                 # Recursively add layers from the group, maintaining order.
                 layers.extend(get_all_layers(child))
    return layers


# forcedPos deve essere relativo al centro del document, non assoluto
def getColorUnderCursorOrAtPos(forcedPos: Optional['xy'] = None, ignore_bottom_layer: bool = False) -> Optional[rgb]:
    # forcedPos is of type xy
    application = Krita.instance()
    document = application.activeDocument()

    if document:
        win = application.activeWindow()
        center = QPointF(0.5 * document.width(), 0.5 * document.height())

        if forcedPos is None:
            # questo dà la posizione da (-docwt/2, -docht/2) a (docwt/2, docht/2)
            p = get_cursor_in_document_coords()
            # per cui aggiungo metà della larghezza documento e metà altezza. così è nel range (0, 0) -- (docwt, docht)
            doc_pos = p + center
            doc_posxy = xyOfQpoint(doc_pos)  # passo a intero
        else:
            doc_posxy = xy(forcedPos.x + int(round(center.x())),
                           forcedPos.y + int(round(center.y())))

        # log(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')

        # parentNode = document.activeNode().parentNode()

        # fgCol = None
        # if pretendLastLayerIsFgColor:

            # if win is not None:
            # view = win.activeView()
            # if view is not None:
            # fg = view.foregroundColor()
            # comp = fg.components()

            # fgCol = rgb( int  (comp[0] * 255.0), int  (comp[1] * 255.0), int  (comp[2] * 255.0), 1)
            # else:
            # return None

        if True:  # parentNode is not None:

            # brothers = parentNode.childNodes()
            # colors = []

            # #costruisco colors
            # for curLayer in brothers:

            # if curLayer.uniqueId() == document.activeNode().uniqueId() and skipCurrentLayer:
            # #print ("salto cur layer")
            # continue

            # if curLayer.uniqueId() == document.activeNode().uniqueId() and pretendLastLayerIsFgColor :

            # layerOpac = curLayer.opacity() # tra  0 e 255

            # paintingOp01 = win.activeView().paintingOpacity()
            # # log(f"opacity = {paintingOp}")
            # colors.append( rgb(fgCol.r, fgCol.g, fgCol.b, int(layerOpac * paintingOp01)))

            # else:

            # pixelBytes = curLayer.pixelData(doc_posxy.x, doc_posxy.y, 1, 1)

            # imageData = QImage(pixelBytes, 1, 1, QImage.Format_RGBA8888)
            # pixelC = imageData.pixelColor(0,0)

            # # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
            # # if curLayer.uniqueId() == document.activeNode().uniqueId():
            # # correzMul = 1.0
            # # else:
            # layerOpac = curLayer.opacity() # tra  0 e 255
            # correzMul = float(layerOpac) /  255.0

            # #log(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")

            # colors.append(  rgb(pixelC.red(),  pixelC.green(),  pixelC.blue(),  pixelC.alpha() * correzMul ))

            # #creo il colore composito dei layer. questo è il bgcolor
            # bgColor = calcolaCompositeColor(colors)

            # --- New logic block starts ---
            if ignore_bottom_layer:
                # Need QImage for layer pixel reading
                try:
                    # Import needed for QImage creation from bytes
                    from PyQt5.QtGui import QImage
                except ImportError:
                    # Log error or notify user? Fallback might be best.
                    print("KritaColorPlus Error: Could not import PyQt5.QtGui.QImage. Cannot ignore bottom layer.")
                    # Fall through to default behavior without QImage
                    pass
                else: # Proceed only if import succeeded
                    all_layers = get_all_layers(document.rootNode())
                    # log(f"trovati {len(all_layers)} layer") # Revert logging
                    # Layers are ordered top-to-bottom

                    if len(all_layers) > 1: # Only proceed if there's more than one layer
                        found_opaque_pixel_above_bottom = False
                        # Iterate through all layers except the last one (bottom layer)
                        # Iterate from index 1 (skip background at 0) to the end
                        # se volessi il pixel di quello topmost, dovrei iterare in ordine inverso. ma qui voglio solo sapere se ce n'e' uno opaco a parte il bg.
                        for i in range(1, len(all_layers)): 
                            curLayer = all_layers[i]
                            try:
                                # Ensure coordinates are integers
                                x, y = int(doc_posxy.x), int(doc_posxy.y)
                                # Basic bounds check using document dimensions; layer dimensions might differ
                                if 0 <= x < document.width() and 0 <= y < document.height():
                                    pixelBytes = curLayer.pixelData(x, y, 1, 1)
                                    if pixelBytes: # Check if pixelData returned valid bytes
                                        imageData = None
                                        # Use formats consistent with later checks
                                        if len(pixelBytes) == 4:
                                            imageData = QImage(pixelBytes, 1, 1, QImage.Format_RGBA8888)
                                        elif len(pixelBytes) == 8:
                                            imageData = QImage(pixelBytes, 1, 1, QImage.Format_RGBA64)
                                        # Add more formats if needed based on Krita's layer types

                                        if imageData:
                                            pixelC = imageData.pixelColor(0, 0)
                                            # Check alpha channel (alpha() is 0-255)
                                            if pixelC.alpha() > 0:
                                                found_opaque_pixel_above_bottom = True
                                                # log(f"trovato opaco sul layer: {curLayer.name()}")
                                                break # Found one, no need to check further layers
                                else: #coordinate out of bounds for this layer or pixelData empty, treat as transparent
                                    log("getColorUnderCursorOrAtPos coordinate out of bounds")

                            except Exception as e:
                                # Log error or handle cases where pixelData fails for a layer
                                # print(f"Error reading pixel data for layer {curLayer.name()}: {e}")
                                pass # Continue to next layer

                        # After checking all layers (except bottom): if none were opaque, return None
                        if not found_opaque_pixel_above_bottom:
                            return None
                    # If only 1 layer, or if an opaque pixel was found above the bottom layer,
                    # fall through to the default composite color logic below.

            # --- New logic block ends ---

            doc_pos = doc_posxy # Use the calculated integer coordinates

            # 3 or 6 bytes depending on the image format
            # Get composite pixel data (Default behavior or fallback)
            try:
                # Need QImage for composite pixel reading too
                from PyQt5.QtGui import QImage
                pixBytes = document.pixelData(int(doc_pos.x), int(doc_pos.y), 1, 1)
            except ImportError:
                 print("KritaColorPlus Error: Could not import PyQt5.QtGui.QImage. Cannot get pixel color.")
                 return None
            except Exception as e:
                # Handle potential errors during composite pixel data retrieval
                # print(f"Error getting composite pixel data at {doc_pos.x},{doc_pos.y}: {e}")
                return None

            if not pixBytes: # Handle case where pixelData returns empty bytes (e.g., outside canvas)
                 return None

            # byte_values = [str(int.from_bytes(byte, 'big')) for byte in pixBytes]
            # concatenated_string = '-'.join(byte_values)

            # log(f'Dati letti: {concatenated_string}')

            # ora ho i byte (3 o 6 byte). devo convertirli in colore Qt
            if len(pixBytes) == 4:
                imageData = QImage(pixBytes, 1, 1, QImage.Format_RGBA8888)
            elif len(pixBytes) == 8:
                imageData = QImage(pixBytes, 1, 1, QImage.Format_RGBA64)
            else:
                # Log warning instead of raising exception? Or return None?
                # print(f"Warning: unsupported composite pixelData length {len(pixBytes)} at {doc_pos.x},{doc_pos.y}")
                return None # Return None if format is unexpected

            if not imageData:
                 # This case might happen if QImage fails for some reason
                 return None

            pixelC = imageData.pixelColor(0, 0)

            # e ora da colore qt a colore mio
            # Convert QColor to internal rgb format, preserving alpha from the composite pixel
            # Krita QColor components (red, green, blue, alpha) are int 0-255
            # Assuming the rgb class expects floats 0-255 for r,g,b and alpha.
            mergedColor = rgb(float(pixelC.red()), float(pixelC.green()), float(pixelC.blue()), float(pixelC.alpha()))

            bgColor = mergedColor

            # log(f"color under cursor  = {bgColor.toString()}")
            return bgColor
        else:
            return None
    else:
        return None


def dryPaper(showMessage=True):

    # log(f"dry paper called showMessage = {showMessage}")
    application = Krita.instance()
    currentDoc = application.activeDocument()
    if currentDoc is None:

        return None
    else:
        activeLayer = currentDoc.activeNode()

        if g.g_blur_on_dry:
            application.action('selectopaque').trigger()
            currentDoc.waitForDone()  # action needs to finish before continuing
            selectionStroke = currentDoc.selection()
            blurFilter = application.filter('gaussian blur')
            blurFilter.setProperty('level', 50)
            blurFilter.setProperty('radius', 50)

        parentNode = activeLayer.parentNode()
        rootNode = currentDoc.rootNode() # Get the document root node
        newLa = None

        # Check if the parent is the document root
        is_top_level = (parentNode == rootNode)

        if is_top_level:
            # log("dry paper called. Layer is top-level. Creating new group.")
            # Create a new group layer at the top level
            newGroup = currentDoc.createGroupLayer("Dry Paper auto-group")
            # Find the index of the active layer to insert the group above it
            try:
                # Insert the new group *before* the active layer
                rootNode.addChildNode(newGroup, activeLayer)
            except Exception as e: # Catch potential errors more broadly
                 log(f"Error adding group before active layer: {e}. Adding to top.")
                 # Fallback if adding before fails (e.g., activeLayer not direct child)
                 rootNode.addChildNode(newGroup, None)

            # Set the new group as the parent for the wet layer
            parentNode = newGroup
            # Optional: Move the active layer into the new group
            # parentNode.addChildNode(activeLayer, None) # This changes layer structure
        elif parentNode is not None:
            # log(f"dry paper called. parent = {parentNode}")
            pass
        else:
            # log("dry paper called. parentNode is None. This shouldn't happen for active layers.")
            parentNode = None # Ensure parentNode is None if it started as None

        if parentNode: # Proceed if we have a valid parent (original or new group)
            oldOpacity = activeLayer.opacity()

            # activeLayer.mergeDown() # Keep this commented out for now
            # currentDoc.waitForDone()

            newLa = currentDoc.createNode("Wet_area", "paintLayer")
            newLa.setOpacity(oldOpacity)

            # Add the new layer *above* the active layer within the parent group
            try:
                children = parentNode.childNodes()
                idx = children.index(activeLayer)
                beforeNode = None
                if idx + 1 < len(children):
                    beforeNode = children[idx + 1]
                # Insert the new layer *before* the node that was originally after activeLayer
                parentNode.addChildNode(newLa, beforeNode)
            except ValueError: # Handle case where activeLayer might have been moved or not found
                 # Fallback if activeLayer not found (e.g., if moved) or parent is new group
                 parentNode.addChildNode(newLa, None) # Add to top if index not found

            currentDoc.setActiveNode(newLa) # Make the new layer active

            if g.g_blur_on_dry and selectionStroke:
                # Apply blur to the original layer *after* creating the new one
                # Ensure the original layer is active for the filter
                currentDoc.setActiveNode(activeLayer)
                blurFilter.apply(selectionStroke, 0, 0)
                currentDoc.waitForDone()
                currentDoc.deselect()
                # Set active node back to the new layer
                currentDoc.setActiveNode(newLa)

            if g.g_set_spectral_blend_mode_when_creating_layer:
                # log("setting over spectral")
                newLa.setBlendingMode("over spectral")

            if g.g_blur_on_dry:
                # al layer precedente ad activeLayer, applica il blur
                for layerPrima in parentNode.childNodes()[: -2]:

                    # log(f"applicando blur a  {layerPrima.name()}:{selectionStroke.x()}, {selectionStroke.y()}, {selectionStroke.width()},{selectionStroke.height()}")

                    selFuori = Selection()
                    selFuori.select(selectionStroke.x(), selectionStroke.y(
                    ), selectionStroke.width(), selectionStroke.height(), 255)
                    selFuori.subtract(selectionStroke)

                    currentDoc.setSelection(selFuori)
                    selFuori.copy(layerPrima)

                    blurFilter.apply(layerPrima, selectionStroke.x(), selectionStroke.y(
                    ), selectionStroke.width(), selectionStroke.height())

                    currentDoc.setSelection(None)
                    # paste è bacata, non posso usarlo
                    # selFuori.paste(layerPrima, selectionStroke.x() + 20  , selectionStroke.y() + 20 ) # copia il pezzo che non doveva essere blurred

                    currentDoc.setActiveNode(layerPrima)
                    Krita.instance().action('edit_paste').trigger()

                    currentDoc.waitForDone()  # action needs to finish before continuing

                    # ora ci devo

                currentDoc.refreshProjection()
                currentDoc.setSelection(None)
                # currentDoc.setSelection(None)

            g.g_opacity_decided_for_layer = False

            # currentDoc.setActiveNode(newLa)

            # currentDoc.refreshProjection() # tenta di agggirare il bug di quickmessage a tutto schermo
            # currentDoc.waitForDone()
        else:
            messageBox(
                "In order to call \"Dry paper\", the current layer needs to have a parent group")
            showMessage = False
            # newLa = currentDoc.createNode("Wet_area", "paintLayer")
            # newLa.setOpacity(50.0 * 255.0 / 100.0)
            # root.addChildNode(newLa, None)

        # test blur

        if showMessage:
            # log("dry paper called message")
            quickMessage("Dry paper")
            # application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), timeMessage, 1)

        return newLa


def node_to_index(node, model):
    path = list()
    while node and (node.index() >= 0):
        path.insert(0, node.index())
        node = node.parentNode()

    index = QModelIndex()
    for i in path:
        last_row = model.rowCount(index) - 1
        index = model.index(last_row - i, 0, index)
    return index


def update_label_from_virtual_color():
    r = g.g_virtual_fg_color_rgb.r
    # Use a different name for the local variable
    green_val = g.g_virtual_fg_color_rgb.g
    b = g.g_virtual_fg_color_rgb.b
    g.lblActiveColor.setStyleSheet(
        f"background-color: rgb({b}, {green_val}, {r})")  # Use the new variable name


def index_to_node(index, document):
    if not index.isValid():
        raise RuntimeError('Invalid index')
    model = index.model()
    path = list()
    while index.isValid():
        last_row = model.rowCount(index.parent()) - 1
        path.insert(0, last_row - index.row())
        index = index.parent()

    node = None
    children = document.topLevelNodes()
    for i in path:
        node = children[i]
        children = node.childNodes()
    return node


class AutoFocusSetter(QObject):

    # Q_OBJECT
    # ...
    # # protected
    # eventFilter = bool(QObject obj, QEvent event)

    def eventFilter(self, obj, event):

        # log(f"event {g.event_lookup.get(str(event.type()), 'sconosciuto')}")

        if event.type() == QEvent.Enter:
            # log(f"enter")
            # log(f"enter color selector ")

            # if isinstance(obj, QDockWidget):
            # log(f"enter dock widget {obj.objectName()} ")

            # if obj.type() == QMdiSubWindow:
            if isinstance(obj, QMdiSubWindow):
                # log(f"debug - enter subwindow")

                wi = Krita.instance().activeWindow()
                q_win = wi.qwindow()
                mdi_area = q_win.findChild(QMdiArea)
                mdi_area.setActiveSubWindow(obj)

                subwin = obj
                isAlwaysOnTop = True if subwin.windowFlags() & Qt.WindowStaysOnTopHint else False

                # if the color has just been changed manually, create a new layer

                if g.g_color_changed_from_selector_probably:

                    curLayerId = Krita.instance().activeDocument().activeNode().uniqueId()
                    # print (f"debug - color changed probably. curnode =  {curLayerId}")
                    # pprint.plog(g.g_layer_is_dirty)

                    if (curLayerId in g.g_layer_is_dirty):  # if cur layer is dirty
                        l_color_changed_from_selector = True
                    else:
                        l_color_changed_from_selector = False

                    # questo era bacato! a volte era uguale. lo commento. così crea layer anche se esco e rientro dal canvas, ma può essere comodo invece che premere D per rafforzare.
                    # TODO aggiungi controllo "se il layer attuale è dirty"
                    # if g.g_virtual_fg_color_rgb.equals(g.g_virtual_color_used_last_rgb):
                        # l_color_changed_from_selector = False
                    # else:
                        # l_color_changed_from_selector = True
                else:
                    l_color_changed_from_selector = False

                # log ("debug 1")

                # Use the new flag to check if color changed *since last leave*
                if ( not isAlwaysOnTop and l_color_changed_from_selector and 
                            g.g_color_changed_since_last_leave 
                            and (not g.g_auto_mix_enabled or g.g_auto_mix_paused) and g.g_multi_layer_mode):

                    # log ("debug 2 creating layer")
                    newLa = dryPaper(False)

                    # reenable dirty brush

                    if g.g_dirty_brush_overall_enabled:
                        g.g_dirty_brush_currently_on = True

                    # devo anche resettare opacità di default

                    document = Krita.instance().activeDocument()
                    if g.g_auto_reset_opacity_on_pick == 1 and document is not None:
                        newLa.setOpacity(
                            int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))

                        document.refreshProjection()

                    # Flag is now reset on Leave event, no need to reset here
                    g.g_color_changed_from_selector_probably = False

                    if g.g_diminishing_opacity:
                        g.g_auto_mix__how_much_canvas_to_pick = 1.0

                        val099 = round(
                            g.g_auto_mix__how_much_canvas_to_pick * 100.0) - 1
                        g.g_dial_auto_mix_level.setValue(val099)

                # if I am entering a window that is not always on top (the part "and not isalwaysontop" is there to attemp to fix a bug: auto-mix sometimes stops pausing when you hover the color picker)
                if g.g_auto_mix_paused and not isAlwaysOnTop:
                    g.g_auto_mix_paused = False

                # obj.activateWindow()

        if event.type() == QEvent.Leave:
            # log(f"leave")

            # logic: if the mouse leaver an always-on-top window, focus the first window that's not always on top.
            if isinstance(obj, QMdiSubWindow):
                # Reset the flag when leaving the canvas
                g.g_color_changed_since_last_leave = False
                # log(f"leave {obj} ")

                wi = Krita.instance().activeWindow()

                subwin = obj
                isAlwaysOnTop = True if subwin.windowFlags() & Qt.WindowStaysOnTopHint else False

                if isAlwaysOnTop:  # if mouse left an always-on-top window:
                    # print ("is always-on-top")

                    subwins = wi.qwindow().findChild(QMdiArea).subWindowList()
                    for su in subwins:
                        curIsAlw = False if su.windowFlags() & Qt.WindowStaysOnTopHint else True
                        if curIsAlw:

                            # focus this one
                            q_win = wi.qwindow()
                            mdi_area = q_win.findChild(QMdiArea)
                            mdi_area.setActiveSubWindow(su)

                            break

                            print("focusing first window that's not always on top")
                else:
                    # mouse left a normal window. possibly it entered the color picker. So pause automixing, so you can use the picker

                    if g.g_auto_mix_enabled:
                        g.g_auto_mix_paused = True
                        # log("pausing automix")

                        # qui vorrei resettare il picker al colore originario. ma se lo faccio succede un meccanismo perverso. scatta setFgColor.
                        # o meglio scatta onFgColorChanged.
                        # quindi il motore si segna che il fg color e' cambiato DOPO che hai fatto leave. e quindi quando rifai enter ti crea un nuovo layer, 
                        # anche se tu non hai davvero cambiato colore. lui crede che tu nel picker abbia cambiato colore. perche' hai fatto questo
                        # setFgColor. Quindi in qualche modo devi far capire a onFgColorChanged che non conta.

                        g.g_auto_mix_ignore_this_color_in_onfgcolorchanged = g.g_virtual_fg_color_rgb
                        
                        if g.g_virtual_fg_color_rgb is not None:
                            setFgColor(g.g_virtual_fg_color_rgb)

                    else:
                        g.g_auto_mix_ignore_this_color_in_onfgcolorchanged = None
                        pass
                        # log("leave, doing nothing, auto mix disabled")

        # if event.type() == QEvent.MouseMove:
            # print (f"mousemove")
            # #col = getColorUnderCursorOrAtPos()

        # if event.type() == QEvent.HoverMove:
            # print (f"hover mousemove")
            # #col = getColorUnderCursorOrAtPos()

        # if event.type() == QEvent.GraphicsSceneMouseMove:
            # print (f"GraphicsSceneMouseMove")
            # #col = getColorUnderCursorOrAtPos()

        # if event.type() == QEvent.GraphicsSceneHoverMove:
            # print (f"GraphicsSceneHoverMove")
            # #col = getColorUnderCursorOrAtPos()

        # QEvent.MouseButtonRelease non è affidabile, a volte smette di scattare:
        if event.type() == QEvent.Paint:

            # log("- paint event detected ma ignorato, non scatta sempre");

            pass

        if event.type() == QEvent.MouseButtonRelease:
            # non scatta piu
            # log(">>>>>>>>>mouse button release")
            pass

        if event.type() == QEvent.MouseButtonPress:
            # non scatta piu
            # log(">>>>>>>>mouse buttonpress")

            pass

        return False  # non scarta l'evento

        # return QObject.eventFilter(obj, event)

        # if event.type() == QEvent.KeyPress:
        # log(f"keypress")
        # keyEvent = QKeyEvent(event)
        # qDebug("Ate key press %d", keyEvent.key())
        # return True
        # else:
        # # standard event processing
        # return QObject.eventFilter(obj, event)

# log(Krita.instance().filters())


def setFgColor(col: rgb):
    # log("setFgColor")

    app = Krita.instance()
    win = app.activeWindow()
    if win is not None:
        view = win.activeView()
        if view is not None:
            fg = view.foregroundColor()
            comp = fg.components()
            # log(f"fg color = {comp}")

            comp[0] = (col.r/255.0)
            comp[1] = (col.g / 255.0)
            comp[2] = (col.b / 255.0)

            fg.setComponents(comp)

            view.setForeGroundColor(fg)


def QPointHash(qp):
    return f"{qp.x()}-{qp.y()}"


def setFgColorEqualToColorOfLastStrokeAfterOpacityAdjust():

    if g.g_last_coord_mouse_up is None:
        log("error g.g_last_coord_mouse_up is none")

    else:
        fr = queue.Queue(0)  # maxsize = means infinite

        fr.put(xyOfQpoint(g.g_last_coord_mouse_up))
        visited = {}
        count = 0
        foundColors = []

        while True:
            curPos = fr.get()
            hashCurPos = curPos.toString()

            if hashCurPos in visited:
                continue

            visited[hashCurPos] = 1

            col = getColorUnderCursorOrAtPos(forcedPos=curPos)

            # , skipCurrentLayer = True  no longer possible
            colExcludingLast = getColorUnderCursorOrAtPos(forcedPos=curPos)

            if not col.equals(colExcludingLast):
                # log(f"found color at {curPos}. color is {col.toString()}, col excluding curlayer is {colExcludingLast.toString()}")
                foundColors.append(col)

            # se ho trovato 8 colori, faccio la media ed esco. TODO prendere invece il più numeroso
            if len(foundColors) == 8:
                media = foundColors[0]
                for m in foundColors:
                    media = m.average(media)
                col = media
                break

            # cerchiamo anche intorno. espando frontiera
            st = 2

            fr.put(xy(curPos.x + st, curPos.y))
            fr.put(xy(curPos.x - st, curPos.y))
            fr.put(xy(curPos.x, curPos.y - st))
            fr.put(xy(curPos.x, curPos.y + st))

            # se dopo un po' non sono riuscito, termino
            count += 1

            if count > 2500:
                log("esco dal loop senza successo")
                quickMessage("errore, colore non trovato")
                break

        setFgColor(col)

        newLa = dryPaper(False)

        newLa.setOpacity(
            int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))

        application = Krita.instance()
        currentDoc = application.activeDocument()
        if currentDoc is not None:
            currentDoc.refreshProjection()



class Dict2Class(object):

    def __init__(self, my_dict):

        for key in my_dict:
            setattr(self, key, my_dict[key])


def messageBox(txt):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setText(txt)
    # msg.setInformativeText()
    msg.setWindowTitle("ColorPlus")
    # msg.setDetailedText("The details are as follows:")
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()


def minimize_views():
    """
    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiArea.html
    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiSubWindow.html
    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QWidget.showMinimized
    """
    app = Krita.instance()
    win = app.activeWindow()
    q_win = win.qwindow()
    mdi_area = q_win.findChild(QMdiArea)
    for sub_win in mdi_area.subWindowList():
        sub_win.showMinimized()


def set_active_view_stay_on_top(new_state):
    """
    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiArea.html
    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QMdiSubWindow.html
    https://doc.qt.io/qtforpython-5/PySide2/QtWidgets/QWidget.html#PySide2.QtWidgets.PySide2.QtWidgets.QWidget.setWindowFlag
    """
    app = Krita.instance()
    win = app.activeWindow()
    q_win = win.qwindow()
    mdi_area = q_win.findChild(QMdiArea)
    sub_win = mdi_area.activeSubWindow()
    sub_win.setWindowFlag(Qt.WindowStaysOnTopHint, new_state)


def quickMessage(msg, timeMessage=360):
    application = Krita.instance()
    application.activeWindow().activeView().showFloatingMessage(
        msg, QIcon(), timeMessage, 1)


def rgbOfManagedColor(c):
    co = c.components()
    return rgb(float(co[0] * 255.0), float(co[1] * 255.0), float(co[2] * 255.0), 255.0)


class xy:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def toString(self):
        return f"{self.x}-{self.y}"


def xyOfQpoint(q):
    return xy(int(round(q.x())),  int(round(q.y())))

    # def log(self, msg):
    # log(f"{msg}:   r:{self.r}, g:{self.g}, b:{self.b} ,a:{self.a}")


def get_q_view(view):
    window = view.window()
    q_window = window.qwindow()
    q_stacked_widget = q_window.centralWidget()
    q_mdi_area = q_stacked_widget.findChild(QMdiArea)
    for v, q_mdi_view in zip(window.views(), q_mdi_area.subWindowList()):
        if v == view:
            return q_mdi_view.widget()


def calcolaCompositeColor(colors):
    mergedColor = None
    for col in colors:
        # col.log("cur color")
        if mergedColor is None:
            mergedColor = col
            # mergedColor.log("setto merged color")
        else:
            a = float(col.a) / 255.0
            # print (f"a = {a}")
            invA = (1.0 - a)
            # print (f"invA = {invA}")
            mergedColor = rgb(mergedColor.r * invA + col.r * a,
                              mergedColor.g * invA + col.g * a,
                              mergedColor.b * invA + col.b * a,
                              255.0)
            # mergedColor.log("merged color")
    return mergedColor


def get_q_canvas(q_view):
    if q_view is None:
        return None

    scroll_area = q_view.findChild(QAbstractScrollArea)
    viewport = scroll_area.viewport()
    for child in viewport.children():
        cls_name = child.metaObject().className()
        if cls_name.startswith('Kis') and ('Canvas' in cls_name):
            return child


def mixFgColorWithBgColor_normalLogic(createLayer=False, clearCurLayer=False, deleteCurLayer=False):

    app = Krita.instance()
    win = app.activeWindow()
    if win is not None:
        view = win.activeView()
        if view is not None:
            document = view.document()
            if document:
                center = QPointF(0.5 * document.width(),
                                 0.5 * document.height())
                p = get_cursor_in_document_coords()

                doc_pos = p + center  # float
                # log(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')

                # parentNode = document.activeNode().parentNode()

                if True:  # parentNode is not None:

                    # brothers = parentNode.childNodes()
                    # colors = []

                    # 3 or 6 bytes depending on the image format
                    pixBytes = document.pixelData(
                        int(doc_pos.x()), int(doc_pos.y()), 1, 1)

                    # byte_values = [str(int.from_bytes(byte, 'big')) for byte in pixBytes]
                    # concatenated_string = '-'.join(byte_values)

                    # log(f'Dati letti: {concatenated_string}')

                    # ora ho i byte (3 o 6 byte). devo convertirli in colore Qt
                    if len(pixBytes) == 4:
                        imageData = QImage(
                            pixBytes, 1, 1, QImage.Format_RGBA8888)
                    elif len(pixBytes) == 8:
                        imageData = QImage(
                            pixBytes, 1, 1, QImage.Format_RGBA64)
                    else:
                        raise f"unsupported len {len(pixBytes)}"

                    pixelC = imageData.pixelColor(0, 0)

                    # e ora da colore qt a colore mio
                    mergedColor = rgb(float(pixelC.red()),  float(
                        pixelC.green()),  float(pixelC.blue()), 255.0)

                    # log(f'pixel risulta: {mergedColor.r}  {mergedColor.g} {mergedColor.b}')

                    # # I build colors[]
                    # for curLayer in brothers:
                    # # If this is the current layer and it is transparent, I skip this layer, because I only want to pick from layers below it.  Why? Because you typically use the mix shortcut when the stroke you just made is wrong, and it needs to be more similar to the background layer. But then, you want to be able to click on the stroke you just did and pick the color BELOW it.
                    # # the exception is if I've switched to single-layer mode, aka temp_switched_to_100_previous_opac
                    # if curLayer.uniqueId() != document.activeNode().uniqueId() or curLayer.opacity() == 255 or g.g_temp_switched_to_100_previous_opac is not None:

                    # pixelBytes = curLayer.pixelData( int(round(doc_pos.x())), int(round(doc_pos.y())), 1, 1)

                    # imageData = QImage(pixelBytes, 1, 1, QImage.Format_RGBA8888)
                    # pixelC = imageData.pixelColor(0,0)

                    # # if this is the current layer and it is trasparent, this means you are mixing from a stroke you just did. Then consider it not transparent. So the next stroke will be almost identical to the previous stroke
                    # if curLayer.uniqueId() == document.activeNode().uniqueId():
                    # correzMul = 1.0
                    # else:
                    # layerOpac = curLayer.opacity() # between 0 and 255
                    # correzMul = float(layerOpac) /  255.0

                    # #log(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")

                    # colors.append(  rgb(pixelC.red(),  pixelC.green(),  pixelC.blue(),  pixelC.alpha() * correzMul ))

                    if False:  # len(colors) == 0: # there was only the fg layer
                        quickMessage(
                            f"Cannot mix: could not find background layers to pick from. ")
                    else:
                        # creo il colore composito dei layer. questo è il bgcolor
                        bgColor = mergedColor  # calcolaCompositeColor(colors)
                        # bgColor.log("bgColor")

                        fg = view.foregroundColor()
                        comp = fg.components()

                        if len(comp) == 4:

                            canv = g.g_how_much_canvas_to_pick

                            # BEGIN mix color the old way (non spectral)

                            # fgMul = 1.0 - canv
                            # comp[0] = comp[0] * fgMul + (bgColor.r / 255.0)  * canv
                            # comp[1] = comp[1] * fgMul + (bgColor.g / 255.0)  * canv
                            # comp[2] = comp[2] * fgMul + (bgColor.b  / 255.0)  * canv
                            # end

                            # begin mix colors spectral, bgr
                            fgMul = 1.0 - canv
                            sb = comp[0] * 255.0
                            sg = comp[1] * 255.0
                            sr = comp[2] * 255.0

                            db = bgColor.r
                            dg = bgColor.g
                            dr = bgColor.b

                            resultColor = spectral_mix(
                                [sr, sg, sb], [dr, dg, db], fgMul)
                            # resultColor is [r,g,b]. copy back to bgr:

                            comp[0] = resultColor[2] / 255.0
                            comp[1] = resultColor[1] / 255.0
                            comp[2] = resultColor[0] / 255.0

                            # END

                            # begin mix colors spectral, rgb
                            # fgMul = 1.0 - canv
                            # sr = comp[0]
                            # sg = comp[1]
                            # sb = comp[2]

                            # dr = bgColor.r / 255.0
                            # dg = bgColor.g / 255.0
                            # db = bgColor.b / 255.0

                            # resultColor = mixRGB(sr, sg, sb, fgMul, dr, dg, db)

                            # comp[0] = resultColor[0]
                            # comp[1] = resultColor[1]
                            # comp[2] = resultColor[2]

                            # END

                            fg.setComponents(comp)

                            # g.g_ultimo_colore_vero_settato_dall_utente = comp # ricorda che questo e' un colore vero

                            view.setForeGroundColor(fg)

                            # setto anche il virtual fg color al result del mix

                            # log("g_virtual_fg_color_rgb = mix 2")
                            g.g_virtual_fg_color_rgb = rgb(
                                comp[0] * 255.0, comp[1] * 255.0, comp[2] * 255.0, 255.0)
                            update_label_from_virtual_color()

                            if g.g_diminishing_opacity:
                                g.g_auto_mix__how_much_canvas_to_pick = 1.0

                                val099 = round(
                                    g.g_auto_mix__how_much_canvas_to_pick * 100.0) - 1
                                g.g_dial_auto_mix_level.setValue(val099)

                            quickMessage(
                                f"Picked {round(canv * 100)}%  color from the canvas.")

                            # 1) if I mixed because the color is wrong, i.e. I made a mistake, then erase the mistake
                            if clearCurLayer:

                                if g.g_multi_layer_mode:

                                    app.action('selectopaque').trigger()
                                    document.waitForDone()  # action needs to finish before continuing
                                    app.action(
                                        'fill_selection_foreground_color').trigger()
                                    app.action('deselect').trigger()

                            if deleteCurLayer:
                                document.activeNode().remove()

                            # 2) if I didn't make a mistake, I just want to fade the current color, then create a new layer
                            if createLayer and g.g_multi_layer_mode:
                                # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
                                if g.g_temp_switched_to_100_previous_opac is None:
                                    newLa = dryPaper(showMessage=False)

                                    # if active layer opacity < 70, set to 70

                                    if g.g_auto_reset_opacity_on_pick == 1 and document is not None:
                                        newLa.setOpacity(
                                            int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))

                                        document.refreshProjection()

                            # messaggio

                        elif len(comp) == 2:
                            messageBox(
                                " Your foreground color is currently grayscale. In order to use \"Mix\", please set your foreground color to an RGB color first.")
                        else:
                            messageBox(
                                "In order to use \"Mix\", please set your foreground color to an RGB color first.")


def get_transform(view):
    def _offset(scroller):
        mid = (scroller.minimum() + scroller.maximum()) / 2.0
        return -(scroller.value() - mid)
    canvas = view.canvas()
    document = view.document()
    q_view = get_q_view(view)
    if q_view is not None:
        area = q_view.findChild(QAbstractScrollArea)
        zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
        transform = QTransform()
        transform.translate(
            _offset(area.horizontalScrollBar()),
            _offset(area.verticalScrollBar()))
        transform.rotate(canvas.rotation())
        transform.scale(zoom, zoom)
        return transform
    else:
        return None


def get_cursor_in_document_coords():
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view.document():
        q_view = get_q_view(view)
        q_canvas = get_q_canvas(q_view)
        transform = get_transform(view)
        if transform is not None:
            transform_inv, _ = transform.inverted()
            global_pos = QCursor.pos()
            local_pos = q_canvas.mapFromGlobal(global_pos)
            center = q_canvas.rect().center()
            return transform_inv.map(local_pos - QPointF(center))
        else:
            return None

# from PyQt5.QtCore import (
        # Qt,)

# from PyQt5.QtWidgets import (
        # QTextEdit,
        # QTableView)


def listEqual(l1, l2):
    if (len(l1) == len(l2) and len(l1) == sum([1 for i, j in zip(l1, l2) if i == j])):
        return True
    else:
        return False

# import numpy as np

# def rgb2hsv(rgb):
    # """ convert RGB to HSV color space

    # :param rgb: np.ndarray
    # :return: np.ndarray
    # """

    # rgb = rgb.astype('float')
    # maxv = np.amax(rgb, axis=2)
    # maxc = np.argmax(rgb, axis=2)
    # minv = np.amin(rgb, axis=2)
    # minc = np.argmin(rgb, axis=2)

    # hsv = np.zeros(rgb.shape, dtype='float')
    # hsv[maxc == minc, 0] = np.zeros(hsv[maxc == minc, 0].shape)
    # hsv[maxc == 0, 0] = (((rgb[..., 1] - rgb[..., 2]) * 60.0 / (maxv - minv + np.spacing(1))) % 360.0)[maxc == 0]
    # hsv[maxc == 1, 0] = (((rgb[..., 2] - rgb[..., 0]) * 60.0 / (maxv - minv + np.spacing(1))) + 120.0)[maxc == 1]
    # hsv[maxc == 2, 0] = (((rgb[..., 0] - rgb[..., 1]) * 60.0 / (maxv - minv + np.spacing(1))) + 240.0)[maxc == 2]
    # hsv[maxv == 0, 1] = np.zeros(hsv[maxv == 0, 1].shape)
    # hsv[maxv != 0, 1] = (1 - minv / (maxv + np.spacing(1)))[maxv != 0]
    # hsv[..., 2] = maxv

    # return hsv


# def hsv2rgb(hsv):
    # """ convert HSV to RGB color space

    # :param hsv: np.ndarray
    # :return: np.ndarray
    # """

    # hi = np.floor(hsv[..., 0] / 60.0) % 6
    # hi = hi.astype('uint8')
    # v = hsv[..., 2].astype('float')
    # f = (hsv[..., 0] / 60.0) - np.floor(hsv[..., 0] / 60.0)
    # p = v * (1.0 - hsv[..., 1])
    # q = v * (1.0 - (f * hsv[..., 1]))
    # t = v * (1.0 - ((1.0 - f) * hsv[..., 1]))

    # rgb = np.zeros(hsv.shape)
    # rgb[hi == 0, :] = np.dstack((v, t, p))[hi == 0, :]
    # rgb[hi == 1, :] = np.dstack((q, v, p))[hi == 1, :]
    # rgb[hi == 2, :] = np.dstack((p, v, t))[hi == 2, :]
    # rgb[hi == 3, :] = np.dstack((p, q, v))[hi == 3, :]
    # rgb[hi == 4, :] = np.dstack((t, p, v))[hi == 4, :]
    # rgb[hi == 5, :] = np.dstack((v, p, q))[hi == 5, :]

    # return rgb


class Window:
    x = 10
    y = 20
    wt = 30
    ht = 40
    name = "file.kra"
    isMaximized = False
    isMinimized = False
    isAlwaysOnTop = False
    fullPath = ""


class PluginState:
    windows: List[Any] = []  # Add type hint


# def onTimerDebug():
    # application = Krita.instance()
    # # currentDoc = application.activeDocument()
    # # if currentDoc is not None:
    # # log(f"x offset: {currentDoc.xOffset()}")

    # wi = Krita.instance().activeWindow()
    # subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

    # # fullPaths = []
    # # for wi in Krita.instance().windows():
    # # log(f"wi = {wi}  title = {wi.qwindow().windowTitle()}")
    # # for vi in wi.views():
    # # log(f"view filename {vi.document().fileName()}")
    # # fullPaths.append(vi.document().fileName())

    # windows = []
    # for su in subwins:

    # log(f"parent = {su.parent()}, par par = {su.parent().parent()}")
    # tit = su.windowTitle().replace(" *", "")

    # #path = [ fp for fp in fullPaths if fp.endswith(tit) ] [0]
    # log(f"window {tit}, position {su.pos()}")
    # newWin = Window()
    # newWin.x = su.pos().x()
    # newWin.y = su.pos().y()
    # newWin.wt = su.size().width()
    # newWin.ht = su.size().height()
    # #newWin.fullPath = path
    # newWin.title = tit
    # newWin.isMaximized = True if su.windowState() & Qt.WindowMaximized else False
    # newWin.isMinimized = True if su.windowState() & Qt.WindowMinimized else False
    # newWin.isAlwaysOnTop = True if su.windowFlags() & Qt.WindowStaysOnTopHint else False
    # windows.append(newWin)

    # js = json.dumps([ w.__dict__ for w in windows] )

    # log(f"dump json = {js}")


monitor = MouseMonitor()


def handle_click(widget):
    if monitor.is_krita_canvas(widget):
        # log("Click sul canvas di Krita!")

        g.g_last_coord_mouse_down = get_cursor_in_document_coords()

        if g.g_auto_mixing_just_once_logic:
            g.g_auto_mixing_just_once_now_on = False

        if g.g_dirty_brush_currently_on and g.g_dirty_brush_overall_enabled:
            application = Krita.instance()
            win = application.activeWindow()
            if win is not None:
                view = win.activeView()
                if view is not None:
                    fg = view.foregroundColor()  # tipo ManagedColor, valori da 0 a 1
                    document = Krita.instance().activeDocument()

                    if document is not None:
                        # Get cursor position using the provided method
                        doc_pos = None # Initialize doc_pos
                        try:
                            # Calculate document center
                            center = QPointF(0.5 * document.width(), 0.5 * document.height())
                            # Get cursor relative to center (assuming get_cursor_in_document_coords exists)
                            p = get_cursor_in_document_coords()
                            if p is not None:
                                # Add center offset to get absolute document coordinates (0,0 top-left)
                                doc_pos = p + center # QPointF
                            else:
                                log("Error: get_cursor_in_document_coords() returned None.")
                        except Exception as e:
                            log(f"Error calculating document position: {e}")
                            # doc_pos remains None

                        if doc_pos:
                            cx = doc_pos.x()
                            cy = doc_pos.y()


                            if not g.g_mix_radius_enabled:
                                #niente radius
                                
                                g.g_color_on_down_dirty_brush = getColorUnderCursorOrAtPos()
                                # log (f"niente mix radius per dirty. color on down = {g.g_color_on_down_dirty_brush.toString()}")
                            else:
                                radius = float(g.g_mix_radius) # Ensure radius is float, read from globals

                                # Define the 5 sample points
                                sample_points = [
                                    # (cx, cy),             # Center non lo metto piu
                                    (cx, cy - radius),    # Up
                                    (cx, cy + radius),    # Down
                                    (cx - radius, cy),    # Left
                                    (cx + radius, cy)     # Right
                                ]

                                # Sample the colors at these points using the new helper
                                sampled_colors_rgb = []
                                for px, py in sample_points:
                                    # Assuming sample_pixel_rgb is defined and handles coordinates correctly
                                    color = sample_pixel_rgb0255(document, px, py)
                                    sampled_colors_rgb.append(color) # Appends color [R,G,B] or None

                                # Blend the sampled colors using the new helper (handles None values)
                                # Result is [R, G, B] 0-255
                                # Assuming blend_colors_spectral is defined
                                final_canvas_color_rgb = blend_colors_spectral(sampled_colors_rgb)
                                # Fallback logic if blending fails
                                if not final_canvas_color_rgb:
                                    log("Warning: Blending failed (e.g., all samples out of bounds/errors). Falling back to center pixel.")
                                    # Fallback: try center pixel
                                    final_canvas_color_rgb = sample_pixel_rgb0255(document, cx, cy)

                                
                              
                                    
                                # Convert R,G,B to float as per rgb class expectation
                                g.g_color_on_down_dirty_brush = rgb(float(final_canvas_color_rgb[0] * 255.0), float(final_canvas_color_rgb[1] * 255.0), float(final_canvas_color_rgb[2] * 255.0), 255.0)
                                # log(f"Dirty brush down color set via sampling: {g.g_color_on_down_dirty_brush}")
                                
                        else:
                            log("Could not get document position for dirty brush sampling.")
                            g.g_color_on_down_dirty_brush = None # Or a default color
                    else:
                        log("No active document found for dirty brush sampling.")
                        g.g_color_on_down_dirty_brush = None # Or a default color

    else:
        # log(f"Click su: {widget}")
        pass


def handle_release(widget): # bm_released  bm_mousereleased bm_mousebuttonreleased bm_mouseup
    if monitor.is_krita_canvas(widget):

        # log("mouse released on canvas")

        # ********************************
        # 1)  aggiorna la color history
        #

        # --- Check if the current tool is a brush tool using whichtool.py ---
        current_tool_id = EKritaTools.current()

        if not current_tool_id:
            # log("Could not determine current tool ID.")
            return  # Exit if tool ID couldn't be determined

        # Define the list of brush tool IDs using constants from EKritaToolsId
        brush_tool_ids = [
            EKritaToolsId.PAINT_BRUSH,
            EKritaToolsId.PAINT_PENCIL,
            # EKritaToolsId.PAINT_AIRBRUSH, # Note: Airbrush seems not defined in whichtool.py's EKritaToolsId
            EKritaToolsId.PAINT_DYNAMIC_BRUSH,
            # Smart Patch is listed under FILL but acts like a brush
            EKritaToolsId.FILL_SMARTPATCH,
            # EKritaToolsId.PAINT_CLONE_BRUSH # Note: Clone brush seems not defined
            EKritaToolsId.PAINT_MULTI_BRUSH,
            # Add any other relevant IDs from EKritaToolsId if needed
        ]

        if current_tool_id not in brush_tool_ids:
            # History changed due to another action (new layer, filter, etc.)
            # log(f"History changed, but current tool ({current_tool_id}) is not a brush. Ignoring.")
            return  # Exit the function if it's not a brush stroke
        # --- End of tool check ---
        
        # Cycle to next brush if brush cycler is enabled
        if brush_cycler.enabled and brush_cycler.brush_list:
            brush_cycler.cycle_to_next_brush()

        # If it is a brush tool, proceed with the original logic:

        # log(f"\n--- _on_history_was_made (Stroke {self.counter}, Tool: {current_tool_name}) ---")
        # Get globals (original code continues here)
        # Get the actual foreground color from Krita
        krita_fg_color = Krita.instance().activeWindow().activeView().foregroundColor()
        # Get color components (usually [R, G, B, A] as floats 0.0-1.0)
        components = krita_fg_color.components()


        def aggiorna_history_aggiungendo(aComponents):
            # Convert Krita components (0-1 float, RGBA) to our rgb class format (0-255 float, BGR internally)
            # Note: The rgb class stores B in self.r and R in self.b internally.
            actual_color_rgb = rgb(r=aComponents[0] * 255.0,  # Blue component (index 2) * 255 for rgb.r
                                   # Green component (index 1) * 255 for rgb.g
                                   g=aComponents[1] * 255.0,
                                   # Red component (index 0) * 255 for rgb.b
                                   b=aComponents[2] * 255.0,
                                   a=aComponents[3] * 255.0)  # Alpha component (index 3) * 255 for rgb.a

            # Use the actual color for the stroke
            stroke_color = actual_color_rgb.clone()


            # log(f"  Stroke Color (g.g_virtual_fg_color_rgb): {stroke_color.toString() if stroke_color else 'None'}")
            # log(f"  Before Update: Index = {g.g_color_history_index}, History = {[c.toString() for c in g.g_last_virtual_colors_used]}")

            if stroke_color is not None:
                stroke_color_clone = stroke_color.clone()
                # log(f"  Processing stroke color {stroke_color_clone.toString()}")

                # Use a temporary list to avoid modifying while iterating if needed, though list comprehension handles this.
                # original_count = len(g.g_last_virtual_colors_used)

                # Remove all existing instances of the color using list comprehension
                g.g_last_virtual_colors_used = [
                    c for c in g.g_last_virtual_colors_used if not c.equals(stroke_color_clone)]
                
                # removed_count = original_count - len(g.g_last_virtual_colors_used)
                # if removed_count > 0:
                #     log(f"  Removed {removed_count} existing instance(s) of {stroke_color_clone.toString()}.")

                # Add the new/current color to the beginning (most recent)
                g.g_last_virtual_colors_used.insert(0, stroke_color_clone)
                # log(f"  Added color {stroke_color_clone.toString()} to beginning. History size: {len(g.g_last_virtual_colors_used)}")

                # Trim list to max_history, keeping the newest items (at the start)
                max_history = 40  # TODO: Consider making this configurable
                if len(g.g_last_virtual_colors_used) > max_history:
                    g.g_last_virtual_colors_used = g.g_last_virtual_colors_used[:max_history]
                    # log(f"  History trimmed to {max_history} items.")

                # Always reset the history index after a stroke adds/moves a color
                g.g_color_history_index = 0
                # log(f"  Reset g_color_history_index to 0.")

            # Update the absolute last color tracker (always, inside try)
            # g.g_virtual_color_used_last_rgb = stroke_color

            # aggiorna la history

            # Aggiorna il dock widget della cronologia colori
            if g.g_color_history_docker_instance:
                g.g_color_history_docker_instance.update_color_history_ui()

            update_label_from_virtual_color()


        if g.g_dirty_brush_color_to_ignore is not None and arrEqual(components, g.g_dirty_brush_color_to_ignore):
            # non aggiorno la history visuale, perche' e' un colore generato dal dirty brush
            # log(f"colore ignorato {components}")
            pass

        elif g.g_auto_mix_color_to_ignore is not None and arrEqual(components, g.g_auto_mix_color_to_ignore):
            # non aggiorno la history visuale, perche' e' un colore generato dall'automix
            # log(f"aggiorna history : colore ignorato , generato da automix {components}")

            # non aggiungo alla history il colore fasullo dell'automixing, ma devo aggiungere quello vero selezionato dall'utente
            # che e' sicuramente il virtual color! perche' devo riportarlo in testa alla history.
            # if g.g_ultimo_colore_vero_settato_dall_utente is not None:
            
            aggiorna_history_aggiungendo(colorArrayOfRgb( g.g_virtual_fg_color_rgb))
                        
        else:
            # log(f"mouse release : colore non ignorato {components} : aggiungo alla history")

            # e' arrivato un colore diverso, quindi l'ha settato l'utente da picker
            g.g_dirty_brush_color_to_ignore = None
            g.g_auto_mix_color_to_ignore = None

            aggiorna_history_aggiungendo(components)

            

        
            # else:
            #     log("  Warning: Docker instance not found in globals (g.g_docker_instance). UI not updated.")
            # log(f"  After Update: Index = {g.g_color_history_index}, History = {[c.toString() for c in g.g_last_virtual_colors_used]}")

        # ********************************
        #

        
        g.g_last_coord_mouse_up = get_cursor_in_document_coords()

        # remember layer is dirty

        g.g_layer_is_dirty[Krita.instance().activeDocument().activeNode().uniqueId()] = True
        # log(f"setting layer dirty {Krita.instance().activeDocument().activeNode().uniqueId()}")

        if g.g_auto_dry_each_stroke and g.g_multi_layer_mode:
            newLa = dryPaper(showMessage=False)

        if g.g_diminishing_opacity:
            g.g_auto_mix__how_much_canvas_to_pick = g.g_auto_mix__how_much_canvas_to_pick * 0.9

            val099 = round(g.g_auto_mix__how_much_canvas_to_pick * 100.0) - 1
            g.g_dial_auto_mix_level.setValue(val099)

            # if g.g_auto_mix__how_much_canvas_to_pick > 1.0:
            # g.g_auto_mix__how_much_canvas_to_pick = 1.0

        # mouse released: sporca se dirty brush

        if g.g_dirty_brush_currently_on and g.g_dirty_brush_overall_enabled:  # qui siamo in mousereleased
            application = Krita.instance()
            win = application.activeWindow()
            if win is not None:
                view = win.activeView()
                if g.g_color_on_down_dirty_brush is None:
                    # log("g_color_on_down_dirty_brush is none. skippo logica dirty")
                    pass

                if view is not None and g.g_color_on_down_dirty_brush is not None:

                    g.g_virtual_fg_color_rgb_previous_when_dirty_brush_on = g.g_virtual_fg_color_rgb.clone()

                    fg = view.foregroundColor()  # tipo ManagedColor, valori da 0 a 1
            # log(f"fg  = {fg}")

                    # fg2 = rgbOfManagedColor(fg) # valori da 0 a 255

                    # global g.g_virtual_fg_color_rgb
                    # g.g_virtual_fg_color_rgb = fg2

                    # non riesco aprendere il colore precedente
                    # bgColor = getColorUnderCursorOrAtPos(True) # skippo current layer altrimenti prende il fg attuale

                    # average between color when mouse down and color when mouse up

                    # bgColor.average( g.g_color_on_down_dirty_brush)
                    bgColorAverage = g.g_color_on_down_dirty_brush

                    # Mix using spectral_mix instead of linear interpolation
                    #canv = 0.12  # Amount of background color to mix in

                    # Get components (assuming 0.0-1.0 range from Krita API)
                    fg_comp_orig = fg.components()

                    # Prepare colors for spectral_mix (expects 0-255 integer lists)
                    fg_rgb_255 = [int(c * 255) for c in fg_comp_orig[0:3]]
                    # Assuming .r, .g, .b are 0-255
                    bg_rgb_255 = [bgColorAverage.r,
                                  bgColorAverage.g, bgColorAverage.b]

                    # Perform spectral mixing
                    mixed_rgb_255 = spectral_mix(fg_rgb_255, bg_rgb_255, g.g_dirty_brush_level)

                    # Convert result back to 0.0-1.0 for setComponents
                    mixed_comp_float = [c / 255.0 for c in mixed_rgb_255]

                    # Create new component list, preserving original alpha if present
                    new_comp = list(fg_comp_orig)  # Create a mutable copy
                    new_comp[0] = mixed_comp_float[0]
                    new_comp[1] = mixed_comp_float[1]
                    new_comp[2] = mixed_comp_float[2]
                    new_comp[3] = 1.0

                    g.g_dirty_brush_color_to_ignore = new_comp
                    # log(f"setto color to ignore = {new_comp}")

                    fg.setComponents(new_comp)

                    view.setForeGroundColor(fg)

                    # log("g_virtual_fg_color_rgb dirty")

                    # g.g_virtual_fg_color_rgb = rgb( float  (new_comp[0] * 255.0), float  (new_comp[1] * 255.0), float  (new_comp[2] * 255.0), 255.0)

                    # update_label_from_virtual_color()

    else:
        # log(f"Rilascio 2 su: {widget}")
        pass


monitor.mouseClicked.connect(handle_click)
monitor.mouseReleased.connect(handle_release)


class MyExtension(Extension):

    def __init__(self, parent):  # bm_init
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)

        self.inited = False

        self.counter = 0

        self.qdock = QDockWidget()

        multi_layer_mode_str = Krita.instance().readSetting(
            "colorPlus", "g.g_multi_layer_mode", "1")
        g.g_multi_layer_mode = multi_layer_mode_str == "1"

        g.g_auto_reset_opacity_on_pick_level = float(Krita.instance().readSetting(
            "colorPlus", "g.g_auto_reset_opacity_on_pick_level", "68.0"))

        # g.g_mix_auto_clears_cur_layer = Krita.instance().readSetting("colorPlus", "g.g_mix_auto_clears_cur_layer","1")

        g.g_auto_mix__how_much_canvas_to_pick = float(Krita.instance().readSetting(
            "colorPlus", "g.g_auto_mix__how_much_canvas_to_pick", "0.5"))

        g.g_auto_mixing_target_distance = float(Krita.instance().readSetting(
            "colorPlus", "g.g_auto_mixing_target_distance", "40.0"))

        g.g_auto_reset_opacity_on_pick = int(Krita.instance().readSetting(
            "colorPlus", "g.g_auto_reset_opacity_on_pick", "0"))

        strHowMuch = Krita.instance().readSetting(
            "colorPlus", "g.g_how_much_canvas_to_pick", "0.45")
        g.g_how_much_canvas_to_pick = float(strHowMuch)

        g.g_auto_opacity_max_distance = int(Krita.instance().readSetting(
            "colorPlus", "g.g_auto_opacity_max_distance", "40"))
            
        g.g_dirty_brush_level = float(Krita.instance().readSetting(
            "colorPlus", "g.g_dirty_brush_level", "0.12"))
            
        g.g_mix_radius = float(Krita.instance().readSetting(
            "colorPlus", "g.g_mix_radius", "0.0"))
            
        # Carica lo stato di g_mix_radius_enabled dalle impostazioni
        g.g_mix_radius_enabled = Krita.instance().readSetting(
            "colorPlus", "g.g_mix_radius_enabled", "0") == "1"

        # dev values , only read when timer is active
        g.g_virtual_fg_color_rgb = None  # di tipo rgb

        g.g_color_history_index = -1  # New

        g.g_auto_focus = Krita.instance().readSetting(
            "colorPlus", "g.g_auto_focus", "true")

        self.mix_radius = 1  # pixel

        g.g_temp_switched_to_100_previous_opac = None

        g.g_temp_switched_to_25_previous_opac = None

        self.mixing_target_distance = 20.0

        self.correct_color_for_transparency = True

        # self.timerDebug = QTimer()
        # self.timerDebug.timeout.connect(onTimerDebug)
        # self.timerDebug.start(2000)

        # creo il timer per il mixing
        self.timerMixon = QTimer()
        self.timerMixon.timeout.connect(self.mixOnTimer)
        self.timerMixon.start(40)

        # creo il timer
        # self.timerEnumRes = QTimer()
        # self.timerEnumRes.timeout.connect(self.enumResources)
        # self.timerEnumRes.start(2000)

        # creo il timer per il colore
        # self.timer2 = QTimer()
        # self.timer2.timeout.connect(self.updateColorUnderMouse)
        # self.timer2.start(40)

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.saveWindowPositions)
        # self.timer.start(2000)

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.mergeOnTimer)
        # self.timer.start(4000)

        home = str(Path.home())

        home = os.getenv('APPDATA')

        self.plugin_state_dir = f"{home}/plugin_krita_color_plus"

        self.filePathWindowState = f"{self.plugin_state_dir}/windowPositions.txt"

        self.windows_with_autofocus = []
        self.ef_autofocus = AutoFocusSetter(self)

        if not os.path.exists(self.plugin_state_dir):

            os.mkdir(self.plugin_state_dir)

        Krita.instance().notifier().windowCreated.connect(self.onWindowCreated)
        Krita.instance().notifier().viewCreated.connect(self.onViewOpenedEvent)
        Krita.instance().notifier().imageCreated.connect(self.onDocCreated)

        self.timer = QTimer()
        self.timer.timeout.connect(self.updateAutoFocus)
        self.timer.start(1000)

        # Register the main ColorPlus docker
        Application.addDockWidgetFactory(DockWidgetFactory(
            "hello", DockWidgetFactoryBase.DockRight, HelloDocker))

        # Register the Color History docker
        from .color_history_docker import ColorHistoryDocker
        Application.addDockWidgetFactory(DockWidgetFactory(
            "colorhistory", DockWidgetFactoryBase.DockRight, ColorHistoryDocker))

        log(f"init ok. home = {home}")

    def updateAutoFocus(self):

        wi = Krita.instance().activeWindow()
        if wi is not None:
            subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

            if g.g_auto_focus == "true":
                for su in subwins:
                    if su not in self.windows_with_autofocus:
                        # log(f"installing autofocus for window {su}")
                        su.installEventFilter(self.ef_autofocus)
                        self.windows_with_autofocus.append(su)
            else:
                for su in subwins:
                    if su in self.windows_with_autofocus:
                        # log(f"uninstalling autofocus for window {su}")
                        su.removeEventFilter(self.ef_autofocus)
                        self.windows_with_autofocus.remove(su)

    def onViewOpenedEvent(openedView):

        # log(f"view opened {openedView}")

        g.allBrushPresets = Krita.instance().resources('paintoppresets')
        # for k,v in allBrushPresets.items():
        # print (f"key {k}")

        # openedView.updateAutoFocus()

    def onDocCreated(openedDoc):

        # log(f"doc created{openedDoc}")

        g.allBrushPresets = Krita.instance().resources('paintoppresets')
        # log(f"all brush presets = {allBrushPresets.size()}")

        # openedView.updateAutoFocus()

    def onFgColorChanged(self):

        
        # this is fired several times when the user changes a color via the color selector.
        # So I can't add a layer here, because I would add hundreds of layers. So I don't do anything,
        # but mark it dirty via g.g_color_changed_from_selector_probably.

        # capisci se è davvero cambiato, dato che questa callback è inaffidabile e viene chiamata anche se entro ed esco dal selector senza cliccare
        # serve per la logica che crea new layer
        

        # log(f"fg color changed event: {g.countColorChanged}")

        g.countColorChanged += 1

        # otherwise it is the auto-mixing timer that changed the color. ignore
    

        # the color has been changed manually, not by auto-mix

        # devo settare questo colore come target per l'auto-mixing
        view = Krita.instance().activeWindow().activeView()
        if view is not None:
            fg: Optional[ManagedColor] = view.foregroundColor()
            if fg is not None:
                # components() likely returns Tuple[float, float, float, float] for RGBA
                # il ManagedColor si usa cosi'
                comp: Sequence[float] = fg.components()
                if len(comp) == 4:  # Assuming RGBA

                    newColorRgb = rgbOfColorArray(comp)

                    if (not g.g_auto_mix_enabled or g.g_auto_mix_paused):
                        if g.g_auto_mix_color_to_ignore is not None and arrEqual(g.g_auto_mix_color_to_ignore, comp):
                            pass
                        elif g.g_dirty_brush_color_to_ignore is not None and arrEqual(g.g_dirty_brush_color_to_ignore, comp):
                            pass
                        else:
                            # e' un colore settato davvero dall'utente. ricordalo
                            # g.g_ultimo_colore_vero_settato_dall_utente = comp

                            g.g_color_changed_from_selector_probably = True
                            

                            

                            # Use the new utility function for conversion
                            

                            # log(f"g_virtual_fg_color_rgb = onfgcolorchanged cioe' {mergedColor.toString()}, orig = {comp[0]}, {comp[1]}, {comp[2]}")

                            # print(f"setto target per automixing {newColorRgb}")
                            g.g_virtual_fg_color_rgb = newColorRgb  # lo memorizzo. diventa il target dell'automixing

                            update_label_from_virtual_color()

                            # log(f"setting last_color_picked = {g.g_virtual_fg_color_rgb.toString()}")
                        

                    #cruciale altrimenti l'automix crea nuovi layer quando vai sul selector e torni sul canvas.
                    if not g.g_auto_mix_ignore_this_color_in_onfgcolorchanged or not g.g_auto_mix_ignore_this_color_in_onfgcolorchanged.equals(newColorRgb):
                        g.g_color_changed_since_last_leave = True
                        
                else:
                    log("err1")

            else:
                log("err2")

        
        # Set the flag indicating color has changed since the last leave event

       
    def onWindowCreated(self):  # called by framework
        # log("on window created  ")

        # self.currentColor = [255,255,255,0]
        # self.previousColor = [255,255,20,0]
        # self.inited = False

        app = Krita.instance()

        # non affidabile, scatta troppo spesso
        # history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
        # kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
        # s_model = kis_undo_view.selectionModel()
        # s_model.currentChanged.connect(self._on_history_was_made)

        # start listening to color changes via color selector
        colorSelectorNg = next(
            (d for d in app.dockers() if d.objectName() == 'ColorSelectorNg'), None)
        # log(f"type of color selector = {type(colorSelectorNg)}")
        for child in colorSelectorNg.findChildren(QObject):
            meta = child.metaObject()
            if meta.className() in {
                'KisColorSelectorRing', 'KisColorSelectorTriangle',
                    'KisColorSelectorSimple', 'KisColorSelectorWheel'}:
                sig = getattr(child, 'update')
                sig.connect(self.onFgColorChanged)

        # non si riesce a mettere un event filter sul color selector. gli eventi non arrivano...
        # event_filter = EventFilter(colorSelectorNg)
        # colorSelectorNg.installEventFilter(event_filter)

        self.inited = True
        print("swap: initialized")

        log("on window created : ok")

    def setup(self):  # called by framework
        log("setup called")

    def saveWindowPositions(self):
        wi = Krita.instance().activeWindow()
        subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

        fullPaths = []
        for wi in Krita.instance().windows():
            log(f"wi = {wi}  title = {wi.qwindow().windowTitle()}")
            for vi in wi.views():
                log(f"view filename {vi.document().fileName()}")
                fullPaths.append(vi.document().fileName())

        windows = []
        for su in subwins:
            tit = su.windowTitle().replace(" *", "")

            path = [fp for fp in fullPaths if fp.endswith(tit)][0]
            log(f"window {tit}, position {su.pos()}")
            newWin = Window()
            newWin.x = su.pos().x()
            newWin.y = su.pos().y()
            newWin.wt = su.size().width()
            newWin.ht = su.size().height()
            newWin.fullPath = path
            newWin.title = tit
            newWin.isMaximized = True if su.windowState() & Qt.WindowMaximized else False
            newWin.isMinimized = True if su.windowState() & Qt.WindowMinimized else False
            newWin.isAlwaysOnTop = True if su.windowFlags() & Qt.WindowStaysOnTopHint else False
            windows.append(newWin)

        js = json.dumps([w.__dict__ for w in windows])

        with open(self.filePathWindowState, 'w+') as f:
            f.write(js)
        log(f"dump json = {js}")

        return js

    # def restoreWindowPositionsOld(self): #relies on sessions to open the files

        # #restore last saved window state
        # f = open(self.filePathWindowState)
        # windows = json.load(f)
        # log(f"roba letta: {windows}")

        # f.close()

        # wi = Krita.instance().activeWindow()
        # subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

        # for w in windows:
        # w2 = Dict2Class(w)
        # log(f"titolo = {w2.title}, x = {w2.x}")

        # for su in subwins:
        # tit = su.windowTitle().replace(" *", "")
        # if tit == w2.title:
        # # devo settare questa finestra come era
        # if w2.isMaximized: # se era massimizzata
        # su.setWindowState(su.windowState() | Qt.WindowMaximized)  # la massimizzo
        # else:
        # su.setWindowState(su.windowState() & ~Qt.WindowMaximized)  # tolgo lo stato maximixed

        # if w2.isAlwaysOnTop : # se era always on top
        # su.setWindowFlags(su.windowFlags() | Qt.WindowStaysOnTopHint)  # la metto on top
        # else:
        # su.setWindowFlags(su.windowFlags() & ~Qt.WindowStaysOnTopHint)  # tolgo lo stato on top

        # su.move( w2.x, w2.y)
        # su.resize(w2.wt, w2.ht)

    def restoreWindowPositions(self):

        # restore last saved window state
        try:
            f = open(self.filePathWindowState)
            windows = json.load(f)
            log(f"roba letta: {windows}")

            f.close()

            wi = Krita.instance().activeWindow()
            subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

            # sort the windows so that the always on top is restored first, otherwise if it's last you don't see the correct layers in the layer list, after I do setActiveSubWindow below.

            def sortFun(wi):
                w2 = Dict2Class(wi)
                if w2.isAlwaysOnTop:
                    return -1
                else:
                    return 1

            windows.sort(key=sortFun)
            log(f"sorted: {windows}")

            # open all files in the correct order
            for w in windows:
                w2 = Dict2Class(w)
                log(f"titolo = {w2.title}, x = {w2.x}. opening document: {w2.fullPath}")

                alreadyOpen = False
                for su in subwins:
                    tit = su.windowTitle().replace(" *", "")
                    if tit == w2.title:
                        alreadyOpen = True

                if not alreadyOpen:
                    doc = Krita.instance().openDocument(w2.fullPath)
                    Krita.instance().activeWindow().addView(doc)

            # all needed files are open. Set attributes, like maximized and always on top

            # subwins have changed. reload them
            subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

            for w in windows:
                w2 = Dict2Class(w)
                log(f"titolo = {w2.title}, x = {w2.x}")

                for su in subwins:
                    tit = su.windowTitle().replace(" *", "")
                    if tit == w2.title:
                        # devo settare questa finestra come era
                        if w2.isMaximized:  # se era massimizzata
                            # la massimizzo
                            su.setWindowState(
                                su.windowState() | Qt.WindowMaximized)
                        else:
                            # tolgo lo stato maximixed
                            su.setWindowState(
                                su.windowState() & ~Qt.WindowMaximized)

                        if w2.isMinimized:
                            su.setWindowState(
                                su.windowState() | Qt.WindowMinimized)
                        else:
                            su.setWindowState(
                                su.windowState() & ~Qt.WindowMinimized)

                        if w2.isAlwaysOnTop:  # se era always on top
                            # la metto on top
                            su.setWindowFlags(
                                su.windowFlags() | Qt.WindowStaysOnTopHint)
                        else:
                            # tolgo lo stato on top
                            su.setWindowFlags(
                                su.windowFlags() & ~Qt.WindowStaysOnTopHint)

                        su.move(w2.x, w2.y)
                        su.resize(w2.wt, w2.ht)

            # I activate any window that is not on top and not minimized. this still leaves the layers of the wrong window in the layer list, therefore I sorted them previously
            for su in subwins:
                flags = su.windowFlags()

                stayOnTop = False
                if su.windowFlags() & Qt.WindowStaysOnTopHint:
                    stayOnTop = True
                else:
                    stayOnTop = False

                isMinimized = False
                if su.windowState() & Qt.WindowMinimized:
                    isMinimized = True
                else:
                    isMinimized = False

                if not isMinimized and not stayOnTop:

                    q_win = wi.qwindow()
                    mdi_area = q_win.findChild(QMdiArea)
                    mdi_area.setActiveSubWindow(su)
                    su.activateWindow()  # test

            # subwins = window.qwindow().findChild(QMdiArea).subWindowList()
            # for su in subwins:

            # application = Krita.instance()
            # currentDoc = application.activeDocument()
            # currentDoc.refreshProjection()           #altrimenti non si aggiorna

        except FileNotFoundError:
            messageBox(
                f"The file where the window state is stored was not found: \n\n{self.filePathWindowState } \n\nYou need to save the windows state first. Then the file will be created.")

    # def setup(self):

            # self.currentColor = [0,0,0,0]
            # self.previousColor = [0,0,0,0]
            # self.inited = False

            # log("LastColor setup ok")

    def switchToLastColor(self):  # bm_previouscolor
        """Switches color based on history, handling consecutive presses vs. first press after paint."""

        # log("--- switchToLastColor ---")
        # log(f"Before Switch: Index = {g.g_color_history_index}, History = {[c.toString() for c in g.g_last_virtual_colors_used]}")

        try:
            acView = Krita.instance().activeWindow().activeView()
            if acView is None:
                log("  Abort: No active view.")
                return


            # eccezione: forse invece di andare a previous color devo fare clean brush
            if g.g_dirty_brush_color_to_ignore is not None:
                quickMessage("Clean brush")
                setFgColor(g.g_virtual_fg_color_rgb)
                g.g_dirty_brush_color_to_ignore = None
                return


            num_colors = len(g.g_last_virtual_colors_used)
            if num_colors == 0:  # Need at least one color to select from
                log("  Abort: No colors in history.")
                quickMessage("No colors in history.")
                return



            


            # Calculate the next index by incrementing (moving towards older colors: 0 -> 1 -> 2...)
            # g_color_history_index = 0 represents the most recent color.
            next_index = g.g_color_history_index + 1

            # log(f"  Current index: {g.g_color_history_index}. Trying next index: {next_index}")


            # Update virtual color and Krita's foreground color

            # Check if the next index is within the list bounds
            if next_index < num_colors:
                g.g_color_history_index = next_index  # Update the global index
                target_color = g.g_last_virtual_colors_used[g.g_color_history_index]
                # log(f"g_virtual_fg_color_rgb = last color cioe' {target_color.toString()}")
                # Set the virtual foreground color
                g.g_virtual_fg_color_rgb = target_color.clone()
                # log(f"  Switched to color at index {g.g_color_history_index}: {target_color.toString()}")
            else:
                # Index is out of bounds (tried to go past the oldest color)
                # log(f"  Reached end of history. No change. Index remains {g.g_color_history_index}")
                quickMessage("Reached oldest color in history.")
                # Do not wrap around, do not change color

            

            update_label_from_virtual_color()

            col: ManagedColor = acView.foregroundColor()
            comp = col.components()

            comp[0] = (g.g_virtual_fg_color_rgb.r / 255.0)
            comp[1] = (g.g_virtual_fg_color_rgb.g / 255.0)
            comp[2] = (g.g_virtual_fg_color_rgb.b / 255.0)
            comp[3] = 1.0

            col.setComponents(comp)
            
            acView.setForeGroundColor(col)
            # log(f"  Set FG Color to: {g.g_virtual_fg_color_rgb.toString()}")

            # DO NOT reorder the list.
            acView.showFloatingMessage(f"Switched color (History pos {g.g_color_history_index})", QIcon(), g.timeMessage, 1)
            # log(f"After Switch: Index = {g.g_color_history_index}, History = {[c.toString() for c in g.g_last_virtual_colors_used]}")

            # --- Optional: Layer creation logic (kept from original) ---

            document = acView.document()
            if document is not None:
                activeNode = document.activeNode()
                if activeNode is not None:
                    parentNode = activeNode.parentNode()
                    if parentNode is not None:
                        if g.g_temp_switched_to_100_previous_opac is None and g.g_multi_layer_mode:
                            newLa = dryPaper(showMessage=False)
                            if newLa is not None and g.g_auto_reset_opacity_on_pick == 1:

                                newLa.setOpacity(
                                    int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))
                                document.refreshProjection()
            # --- End Optional Layer Logic ---

        except IndexError:
            quickMessage(
                "Error accessing color history (Index out of bounds).")
            g.g_color_history_index = -1  # Reset index on error
            log(f"IndexError in switchToLastColor (Index was {g.g_color_history_index}), resetting index to -1.")
            import traceback
            traceback.print_exc()
        except Exception as e:
            if 'acView' in locals() and acView is not None:
                acView.showFloatingMessage(
                    f"Error switching color: {e}.", QIcon(), g.timeMessage * 2, 1)
            log(f"Error in switchToLastColor: {e}")
            import traceback
            traceback.print_exc()
            g.g_color_history_index = -1  # Reset index on other errors too
            log("Resetting index to -1 due to exception.")
        except Exception as e:
            acView.showFloatingMessage(
                f"error {e}.", QIcon(), g.timeMessage * 2, 1)
            log("errore trovato in swap:")
            log(e)

    def toggle_100_opac(self):
        application = Krita.instance()
        currentDoc = application.activeDocument()
        if currentDoc is not None:
            activeLayer = currentDoc.activeNode()
            curOpac = activeLayer.opacity()

            if g.g_temp_switched_to_100_previous_opac is None:
                newLa = dryPaper(False)

                activeLayer = newLa
                # currentDoc = application.activeDocument()
                # currentDoc.waitForDone()
                # activeLayer = currentDoc.activeNode()

                if g.g_temp_switched_to_25_previous_opac is not None:
                    g.g_temp_switched_to_100_previous_opac = g.g_temp_switched_to_25_previous_opac
                    g.g_temp_switched_to_25_previous_opac = None
                else:
                    g.g_temp_switched_to_100_previous_opac = activeLayer.opacity()

                activeLayer.setOpacity(255)

                # the brush opacity becomes equal to the layer opacityfg = view.foregroundColor()

                # view  = Krita.instance().activeWindow().activeView()

                # newPaintingOp = self.temp_switched_to_100_previous_opac / 255.0
                # log(f"setting new painting op = {newPaintingOp}")
                # view.setPaintingOpacity(newPaintingOp)

                quickMessage(
                    f"Temporarily set 100% opacity. Press again to restore. debug. mix-paused = {g.g_auto_mix_paused}")
            else:
                newLa = dryPaper(False)

                # currentDoc = application.activeDocument()
                activeLayer = newLa  # currentDoc.activeNode()
                activeLayer.setOpacity(g.g_temp_switched_to_100_previous_opac)

                quickMessage(
                    f"Restored {round (g.g_temp_switched_to_100_previous_opac * 100.0 / 255.0)}  opacity. debug. mix-paused = {g.g_auto_mix_paused}")

                # view  = Krita.instance().activeWindow().activeView()
                # view.setPaintingOpacity(1.0)

                g.g_temp_switched_to_100_previous_opac = None

    def toggle_25_opac(self):
        application = Krita.instance()
        currentDoc = application.activeDocument()
        if currentDoc is not None:
            activeLayer = currentDoc.activeNode()
            curOpac = activeLayer.opacity()

            if g.g_temp_switched_to_25_previous_opac is None:
                activeLayer = dryPaper(False)

                if g.g_temp_switched_to_100_previous_opac is not None:
                    g.g_temp_switched_to_25_previous_opac = g.g_temp_switched_to_100_previous_opac
                    g.g_temp_switched_to_100_previous_opac = None
                else:
                    g.g_temp_switched_to_25_previous_opac = activeLayer.opacity()

                activeLayer.setOpacity(int(25.0 * 255.0 / 100.0))

                quickMessage(
                    f"Temporarily set 25% opacity. Press again to restore.")
            else:
                activeLayer = dryPaper(False)
                activeLayer.setOpacity(g.g_temp_switched_to_25_previous_opac)

                quickMessage(
                    f"Restored {round (g.g_temp_switched_to_25_previous_opac * 100.0 / 255.0)}  opacity")

                g.g_temp_switched_to_25_previous_opac = None

    # Note: Updated signature to accept arguments from currentChanged signal

    # def mixOldSingleLayer(self):
            # app = Krita.instance()
            # win = app.activeWindow()
            # if win is not None:
                # view = win.activeView()
                # if view is not None:
            # document = view.document()
            # if document:
                # center = QPointF(0.5 * document.width(), 0.5 * document.height())
                # p = get_cursor_in_document_coords()
                # if p is not None:
                # doc_pos = p + center
                # log(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')

                # self.pixelBytes = document.activeNode().pixelData(doc_pos.x(), doc_pos.y(), 1, 1)

                # self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                # self.pixelC = self.imageData.pixelColor(0,0)
                # log(f"color under cursor = {self.pixelC.red()}, {self.pixelC.green()}, {self.pixelC.blue()}")

                # fg = view.foregroundColor()
                # comp = fg.components()
                # log(f"fg color = {comp}")

                # canv = 0.5 #I pick half color from canvas
                # fgMul = 1.0 - canv
                # comp[0] = comp[0] * fgMul + (self.pixelC.red() / 255.0)  * canv
                # comp[1] = comp[1] * fgMul + (self.pixelC.green() / 255.0)  * canv
                # comp[2] = comp[2] * fgMul + (self.pixelC.blue()  / 255.0)  * canv

                # fg.setComponents(comp)

                # view.setForeGroundColor(fg)

    # Never used. this mixing logic makes sense when the current color is mostly correct, and you only want to introduce a small variation. In practice it is useless.

    def mixFgColorWithBgColor_maxDistanceLogic(self):
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            view = win.activeView()
            if view is not None:
                document = view.document()
                if document:
                    center = QPointF(0.5 * document.width(),
                                     0.5 * document.height())
                    p = get_cursor_in_document_coords()

                    doc_pos = p + center

                    # log(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')

                    parentNode = document.activeNode().parentNode()

                    if parentNode is not None:

                        brothers = parentNode.childNodes()
                        colors = []

                        # costruisco colors
                        for curLayer in brothers:

                            self.pixelBytes = curLayer.pixelData(
                                doc_pos.x(), doc_pos.y(), 1, 1)

                            self.imageData = QImage(
                                self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                            self.pixelC = self.imageData.pixelColor(0, 0)

                            # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                            if curLayer.uniqueId() == document.activeNode().uniqueId():
                                correzMul = 1.0
                            else:
                                layerOpac = curLayer.opacity()  # tra  0 e 255
                                correzMul = float(layerOpac) / 255.0

                            # log(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")

                            colors.append(rgb(self.pixelC.red(),  self.pixelC.green(
                            ),  self.pixelC.blue(),  self.pixelC.alpha() * correzMul))

                        # creo il colore composito dei layer. questo è il bgcolor
                        bgColor = calcolaCompositeColor(colors)
                        # bgColor.log("bgColor")

                        # setto il fg color uguale a merged color mischiato con il fg
                        fg = view.foregroundColor()  # tipo ManagedColor, valori da 0 a 1
                        log(f"fg  = {fg}")

                        fg2 = rgbOfManagedColor(fg)  # valori da 0 a 255
                        fg2.log("fg2")

                        comp = fg.components()
                        log(f"fg color = {comp}")

                        dist = fg2.distance(bgColor)
                        log(f"distance = {dist}")

                        curDist = None
                        picked50 = False

                        # calcola curFg
                        if dist <= self.mixing_target_distance:
                            # i colori sono molto vicini. fai 50%
                            curMul = 0.5
                            curFg = rgb(fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                        fg2.g * curMul + bgColor.g *
                                        (1.0 - curMul),
                                        fg2.b * curMul + bgColor.b *
                                            (1.0 - curMul),
                                        255)
                            curDist = dist
                            picked50 = True
                        else:  # i colori sono lontani. avvicina poco a poco finché la distanza del curFg dall'origFg non diventa > target

                            stepMul = 0.001

                            curMul = 0.0

                            while True:

                                curFg = rgb(fg2.r * curMul + bgColor.r * (1.0 - curMul),
                                            fg2.g * curMul + bgColor.g *
                                            (1.0 - curMul),
                                            fg2.b * curMul + bgColor.b *
                                                (1.0 - curMul),
                                            255)

                                curDist = curFg.distance(fg2)

                                log(
                                    f"iterando. mul  = {curMul}, dist  tra {curFg.toString()} e {fg2.toString()} = {curDist}. ")

                                if curDist <= self.mixing_target_distance:
                                    break

                                curMul += stepMul

                            picked50 = False

                        # canv = howMuchCanvas # pick half color from canvas

                        comp[0] = curFg.r / 255.0
                        comp[1] = curFg.g / 255.0
                        comp[2] = curFg.b / 255.0

                        # fgMul = 1.0 - canv
                        # comp[0] = comp[0] * fgMul + (bgColor.r / 255.0)  * canv
                        # comp[1] = comp[1] * fgMul + (bgColor.g / 255.0)  * canv
                        # comp[2] = comp[2] * fgMul + (bgColor.b  / 255.0)  * canv

                        fg.setComponents(comp)

                        view.setForeGroundColor(fg)

                        # setto anche il virtual fg color al result del mix
                        log("g_virtual_fg_color_rgb mixando")
                        g.g_virtual_fg_color_rgb = rgb(
                            int(comp[0] * 255.0), int(comp[1] * 255.0), int(comp[2] * 255.0), 1)
                        update_label_from_virtual_color()

                        # messaggio
                        if picked50:
                            view.showFloatingMessage(
                                f"Picked 50% because distance was small ({round(curDist)})", QIcon(), g.timeMessage, 1)
                        else:
                            view.showFloatingMessage(
                                f"Picked a bit of color from canvas. Distance: {round(curDist)}", QIcon(), g.timeMessage, 1)

    def acceptCurrentColorAndStopDirty(self, clearCurLayer=True):

        if g.g_dirty_brush_overall_enabled:
            g.g_dirty_brush_currently_on = False

        # reset previous color, because the dirty brush has already changed items
        if g.g_dirty_brush_overall_enabled:
            setFgColor(g.g_virtual_fg_color_rgb_previous_when_dirty_brush_on)

        if clearCurLayer and g.g_temp_switched_to_100_previous_opac is None:
            app = Krita.instance()
            win = app.activeWindow()
            if win is not None:
                view = win.activeView()
                if view is not None:
                    document = view.document()
                    if document:

                        app = Krita.instance()
                        app.action('clear').trigger()
                        document.waitForDone()  # action needs to finish before continuing

        quickMessage("Accept color and stop dirty brush")

    def updateColorUnderMouse(self):
        # log("updateColorUnderMouse")
        self.colorUnderMouse = getColorUnderCursorOrAtPos()
        # if col is not None:
        # log(f"update color under mouse: {col.toString()}")

    def enumResources(self):
        log("enum resources")
        # log( Krita.instance().resources('paintoppresets') )

        g.allBrushPresets = Krita.instance().resources('preset')
        log(f"resources: {g.allBrushPresets}")

        # allBrushPresets = Krita.instance().resources('paintoppresets')
        for k, v in g.allBrushPresets.items():
            print(f"key {k}")

    def mixOnTimer(self):  #bm_automix

        if g.g_virtual_fg_color_rgb is None or not g.g_auto_mix_enabled or g.g_auto_mix_paused or (g.g_auto_mixing_just_once_logic and not g.g_auto_mixing_just_once_now_on):
            return

        # log("timer 2")
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            view = win.activeView()
            if view is not None:
                document = view.document()
                if document:
                    # center = QPointF(0.5 * document.width(),
                    #                  0.5 * document.height())
                    p = get_cursor_in_document_coords()
                    if p is None:
                        print("aborted mixOnTimer")
                        return

                    # doc_posPiuCenter = p + center


                      
                    # doc_pos = xyOfQpoint(doc_pos)
                    # log(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')

                    # parentNode = document.activeNode().parentNode()

                    if not g.g_mix_radius_enabled:
                        
                        
                        maybeColorRgb255 : Optional[rgb] = getColorUnderCursorOrAtPos(ignore_bottom_layer=True)
                        colorRgb255: rgb = g.g_virtual_fg_color_rgb if maybeColorRgb255 is None else maybeColorRgb255
                  
                      
                        # e ora da colore qt a colore mio
                        bgColor255 = colorRgb255
                      
                     
                        # vecchia logia senza radius
                        canv = g.g_auto_mix__how_much_canvas_to_pick

                        fgMul = 1.0 - canv

                   

                        # begin mix colors spectral, bgr
                        fgMul = 1.0 - canv
                        sb = g.g_virtual_fg_color_rgb.r
                        sg = g.g_virtual_fg_color_rgb.g
                        sr = g.g_virtual_fg_color_rgb.b

                        db = bgColor255.r
                        dg = bgColor255.g
                        dr = bgColor255.b

                        resultColor = spectral_mix(
                            [sr, sg, sb], [dr, dg, db], # sono valori 0 255
                            fgMul)
                        # resultColor is [r,g,b]. copy back to bgr:


                        fg = view.foregroundColor()
                        comp = fg.components()

                        comp[0] = resultColor[2] / 255.0
                        comp[1] = resultColor[1] / 255.0
                        comp[2] = resultColor[0] / 255.0

                        # END


                        fg.setComponents(comp)

                        g.g_auto_mix_color_to_ignore = comp

                        view.setForeGroundColor(fg)


                    else:  # con mixing radius

                       

                        # === New 4-point sampling logic ===
                        # cx_c = doc_posPiuCenter.x()
                        # cy_c = doc_posPiuCenter.y()

                        cx_p = p.x()
                        cy_p = p.y()
                        radius = float(g.g_mix_radius) # Ensure radius is float, read from globals

                        # Define the 5 sample points
                        sample_pointsxy = [
                            xy(cx_p, cy_p - radius),    # Up
                            xy(cx_p, cy_p + radius),    # Down
                            xy(cx_p - radius, cy_p),    # Left
                            xy(cx_p + radius, cy_p)     # Right
                        
                        ]
                        # sample_points = [
                        #     # (cx, cy),             # Center non lo metto piu
                        #     (cx_c, cy_c - radius),    # Up
                        #     (cx_c, cy_c + radius),    # Down
                        #     (cx_c - radius, cy_c),    # Left
                        #     (cx_c + radius, cy_c)     # Right
                        
                        # ]

                        # current_time = time.time()
                        # if current_time - g.last_log_time_sample_points > 1.0:
                        #     log(f"Sample points: {sample_pointsxy}") # DEBUG
                            

                        # Sample the colors at these points using the new helper
                        sampled_colors_arr255 = []
                        for p in sample_pointsxy:
                            maybeColorRgb255 : Optional[rgb] = getColorUnderCursorOrAtPos(forcedPos=p, ignore_bottom_layer=True)
                            colorRgb255: rgb = g.g_virtual_fg_color_rgb if maybeColorRgb255 is None else maybeColorRgb255

                            rgbArr = colorArray255_3_OfRgb(colorRgb255)
                            sampled_colors_arr255.append(rgbArr) # Appends color [R,G,B] or None
                        
                        # for (px,py) in sample_points:

                        #     color = sample_pixel_rgb0255(document, px, py)
                        #     sampled_colors_rgbarr.append(color) # Appends color [R,G,B] or None

                            
                        
                        # if current_time - g.last_log_time_sample_points > 1.0:
                        #     log(f"Sampled colors RGB array: {sampled_colors_arr255}") # DEBUG
                        

                        # Blend the sampled colors using the new helper (handles None values)
                        # Result is [R, G, B] 0-255
                        final_canvas_color_rgb = blend_colors_spectral(sampled_colors_arr255)
                        
                        # if current_time - g.last_log_time_sample_points > 1.0:
                        #     log(f"Final canvas color RGB: {final_canvas_color_rgb}") # DEBUG
                            


                        # g.last_log_time_sample_points = current_time

                        # We no longer need the single 'mergedColor' object for the primary mixing path.
                        # The final mixing logic later will use final_canvas_color_rgb directly.
                        # However, some other code paths might still expect mergedColor.
                        # Let's create an rgb object from the final blend for potential compatibility.
                        # Note: spectral_mix returns [R, G, B], rgb expects R, G, B args.
                        # Also, rgb uses 0-255 range, which matches final_canvas_color_rgb.
                        if not final_canvas_color_rgb:
                             # Handle case where blending failed (e.g., all samples out of bounds/errors)
                             log("Error: Could not determine final canvas color from sampling. Falling back.")
                             # Fallback: try center pixel first
                             final_canvas_color_rgb = sample_pixel_rgb0255(document, cx_c, cy_c)
                             
                        # === End of 5-point sampling logic ===

                     

                        # setto il fg color uguale a merged color mischiato con il memorizzato (non con il fg)

                        fg = view.foregroundColor()
                        comp = fg.components()

                      


                        

                        # BEGIN mix colors old way
                        # comp[0] = (g.g_virtual_fg_color_rgb.r/255.0) * fgMul + (mergedColor.r / 255.0)  * canv
                        # comp[1] = (g.g_virtual_fg_color_rgb.g / 255.0) * fgMul + (mergedColor.g / 255.0)  * canv
                        # comp[2] = (g.g_virtual_fg_color_rgb.b / 255.0) * fgMul + (mergedColor.b  / 255.0)  * canv

                        # END

                        # begin mix colors spectral: Foreground vs Blended Canvas Color
                        # 'canv' (g.g_auto_mix__how_much_canvas_to_pick) is the weight of the canvas color (color2)
                        # spectral_mix's 't' parameter is the weight of color2.
                        t_mix = g.g_auto_mix__how_much_canvas_to_pick # Weight of the blended canvas color in the final mix

                        # Foreground color (color1) - Ensure it's [R, G, B] 0-255 list
                        # g.g_virtual_fg_color_rgb stores R, G, B as floats 0-255
                        fg_color_rgb = [
                            float(g.g_virtual_fg_color_rgb.r),
                            float(g.g_virtual_fg_color_rgb.g),
                            float(g.g_virtual_fg_color_rgb.b)
                        ]

                        # Blended canvas color (color2) - Already [R, G, B] 0-255 list
                        # from final_canvas_color_rgb calculated earlier (or fallback)
                        canvas_blend_rgb = final_canvas_color_rgb # This is guaranteed to be a list [R,G,B]

                        # Perform the final spectral mix
                        # spectral_mix(color1, color2, t) where t is weight of color2
                        try:
                            final_mixed_color_rgb = spectral_mix(
                                fg_color_rgb, canvas_blend_rgb, t_mix)
                        except Exception as e:
                            log(f"Error during final spectral mix: {e}")
                            # Fallback if final mix fails: use original fg color
                            final_mixed_color_rgb = fg_color_rgb


                        # final_mixed_color_rgb is [R, G, B] 0-255.
                        # Convert back to Krita's component format (0.0-1.0)
                        # Assuming 'comp' expects BGR order based on original code comp[0]=res[2]/255
                        # Check if final_mixed_color_rgb is valid before division
                        
                        comp[0] = final_mixed_color_rgb[0] / 255.0 # Blue
                        comp[1] = final_mixed_color_rgb[1] / 255.0 # Green
                        comp[2] = final_mixed_color_rgb[2] / 255.0 # Red
                    

                        # END spectral mix

                        # comp[0] =  (mergedColor.r / 255.0)
                        # comp[1] =  (mergedColor.g / 255.0)
                        # comp[2] = (mergedColor.b  / 255.0)

                        fg.setComponents(comp)

                        g.g_auto_mix_color_to_ignore = comp

                        view.setForeGroundColor(fg)

    # def mixSmall(self):
        # return self.mix(0.66)  #0.66 from canvas

    # def mixBig(self):
        # return self.mix( 0.33)  #0.33 from canvas

    def pickColorFun(self, showMessage=True): #bm_pick

        # log("pick called")
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            # log("pick called 1")
            view = win.activeView()
            if view is not None:
                # log("pick called 2")
                document = view.document()
                if document:
                    # log("pick called 3")
                    center = QPointF(0.5 * document.width(),
                                     0.5 * document.height())
                    p = get_cursor_in_document_coords()
                    doc_pos = p + center

                    # 3 or 6 bytes depending on the image format
                    pixBytes = document.pixelData(
                        int(doc_pos.x()), int(doc_pos.y()), 1, 1)

                    # byte_values = [str(int.from_bytes(byte, 'big')) for byte in pixBytes]
                    # concatenated_string = '-'.join(byte_values)

                    # log(f'Dati letti: {concatenated_string}')

                    # ora ho i byte (3 o 6 byte). devo convertirli in colore Qt
                    if len(pixBytes) == 4:
                        imageData = QImage(
                            pixBytes, 1, 1, QImage.Format_RGBA8888)
                    elif len(pixBytes) == 8:
                        imageData = QImage(
                            pixBytes, 1, 1, QImage.Format_RGBA64)
                    else:
                        raise f"unsupported len {len(pixBytes)}"

                    pixelC = imageData.pixelColor(0, 0)

                    # e ora da colore qt a colore mio
                    mergedColor = rgb(float(pixelC.red()),  float(
                        pixelC.green()),  float(pixelC.blue()), 255.0)

                    # log(f'pixel risulta: {mergedColor.r}  {mergedColor.g} {mergedColor.b}')

                    # parentNode = document.activeNode().parentNode()

                    if True:  # parentNode is not None:
                        # log("pick called 4")
                        # brothers = parentNode.childNodes()
                        # colors = []

                        # #costruisco colors
                        # for curLayer in brothers:
                        # #log(f"pixel bytes = {self.pixelBytes}")
                        # self.pixelBytes = curLayer.pixelData(int (round(doc_pos.x())), int(round(doc_pos.y())), 1, 1)

                        # self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                        # self.pixelC = self.imageData.pixelColor(0,0) # valori tra 0 e 255
                        # #log(f"pixel color  = {self.pixelC.name()}")  # .name() lo stampa in modo leggibile

                        # # devo correggere l'alpha del pixel con l'alpha del layer. ma non lo correggo se il layer è quello attuale, che è trasparente. così la pennellata successiva si vede uguale
                        # # if curLayer.uniqueId() == document.activeNode().uniqueId():
                        # # correzMul = 1.0
                        # # else:
                        # layerOpac = curLayer.opacity() # tra  0 e 255
                        # correzMul = float(layerOpac) /  255.0

                        # #log(f"pick: color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha() }, a corretto = {self.pixelC.alpha() * correzMul}")

                        # colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() * correzMul ))

                        # #creo il colore composito

                        # mergedColor = calcolaCompositeColor(colors);
                        # print (f"picked color: {mergedColor.toString()}")

                        # if self.correct_color_for_transparency:
                        # #risaturiamo in modo tale che la somma resti uguale
                        # sommaOld = mergedColor.r + mergedColor.g + mergedColor.b

                        # # deve essere uguale a mul * curLayerOpac01 * (mergedColor.r + mergedColor.g + mergedColor.b)

                        # curLayerOpac01 =  float (document.activeNode().opacity()) / 255.0  #tra 0 e 1

                        # # # formula: mulA è tale che (merged.a * mulA) * curLayerOpac =  merged.a  => mul = 1 / curlayeropac
                        # # log(f"  curLayerOpac01 = {curLayerOpac01}, newr = {mergedColor.r / curLayerOpac01 },    newg = {mergedColor.g / curLayerOpac01 },    newb = {mergedColor.b / curLayerOpac01}")
                        # # # newR * curLayerOpac01 = merged.r
                        # mergedColor = rgb(   min (255, mergedColor.r / curLayerOpac01 ),    min(255,mergedColor.g / curLayerOpac01 ),    min(255, mergedColor.b / curLayerOpac01 ),  255)

                        log("g_virtual_fg_color_rgb = mergedcolor")
                        g.g_virtual_fg_color_rgb = mergedColor  # lo memorizzo come target
                        update_label_from_virtual_color()

                        # importante: non aggiungerlo alla coda,  perché poi scatta lo stesso l'aggiunta alla coda con colore leggermente diverso, non so perche'. se non fai niente funziona.
                        # # aggiungo alla lista solo se non è già in coda (stranamente è necessario)
                        # if g.g_virtual_fg_color_rgb is None:
                        # pass
                        # if len(g.g_last_virtual_colors_used) > 0:
                        # if g.g_last_virtual_colors_used[-1].equals(g.g_virtual_fg_color_rgb):
                        # pass
                        # else:
                        # g.g_last_virtual_colors_used.append(g.g_virtual_fg_color_rgb.clone())
                        # else:
                        # g.g_last_virtual_colors_used.append(g.g_virtual_fg_color_rgb.clone())

                        # setto il fg color uguale a merged color
                        fg = view.foregroundColor()
                        comp = fg.components()

                        # wrokaround in case your fg color is [1,1], which means greyscale
                        log(f"fg color = {comp}")

                        if len(comp) == 4:

                            comp[0] = (mergedColor.r / 255.0)
                            comp[1] = (mergedColor.g / 255.0)
                            comp[2] = (mergedColor.b / 255.0)

                            log(f"fg color after = {comp}")

                            fg.setComponents(comp)

                            # g.g_ultimo_colore_vero_settato_dall_utente = comp # ricorda che questo e' un colore vero

                            view.setForeGroundColor(fg)

                            if g.g_auto_mixing_just_once_logic:
                                g.g_auto_mixing_just_once_now_on = True

                            if g.g_diminishing_opacity:
                                g.g_auto_mix__how_much_canvas_to_pick = 1.0

                                val099 = round(
                                    g.g_auto_mix__how_much_canvas_to_pick * 100.0) - 1
                                g.g_dial_auto_mix_level.setValue(val099)

                            # messaggio
                            if showMessage:
                                view.showFloatingMessage(
                                    "Pick color", QIcon(), g.timeMessage, 1)
                        elif len(comp) == 2:
                            messageBox(
                                " Your foreground color is currently grayscale. In order to use \"pick\", please set your foreground color to an RGB color first.")
                        else:
                            messageBox(
                                "In order to use pick, please set your foreground color to an RGB color first.")

    def increaseMixing(self):

        g.g_how_much_canvas_to_pick += g.g_mixing_step
        if g.g_how_much_canvas_to_pick > 1.0:
            g.g_how_much_canvas_to_pick = 1.0

        Krita.instance().writeSetting("colorPlus", "g.g_how_much_canvas_to_pick",
                                      str(g.g_how_much_canvas_to_pick))

        quickMessage(
            f"Increased mixing to {round(g.g_how_much_canvas_to_pick* 100.0)}%")

    def decreaseMixing(self):

        g.g_how_much_canvas_to_pick -= g.g_mixing_step
        if g.g_how_much_canvas_to_pick < 0.0:
            g.g_how_much_canvas_to_pick = 0.0

        Krita.instance().writeSetting("colorPlus", "g.g_how_much_canvas_to_pick",
                                      str(g.g_how_much_canvas_to_pick))

        quickMessage(
            f"Decreased mixing to {round(g.g_how_much_canvas_to_pick * 100.0)}%")

    def increaseAutoMixing(self):

        if g.g_auto_mixing_uses_distance_logic:
            g.g_auto_mixing_target_distance += g.g_auto_mixing_distance_step
            if g.g_auto_mixing_target_distance > 255.0:
                g.g_auto_mixing_target_distance = 255.0

            Krita.instance().writeSetting("colorPlus", "g.g_auto_mixing_target_distance",
                                          str(g.g_auto_mixing_target_distance))

            quickMessage(
                f"Increased auto-mixing distance to {round(g.g_auto_mixing_target_distance )}")

        else:
            g.g_auto_mix__how_much_canvas_to_pick += g.g_mixing_step
            if g.g_auto_mix__how_much_canvas_to_pick > 1.0:
                g.g_auto_mix__how_much_canvas_to_pick = 1.0

            Krita.instance().writeSetting("colorPlus", "g.g_auto_mix__how_much_canvas_to_pick",
                                          str(g.g_auto_mix__how_much_canvas_to_pick))

            quickMessage(
                f"Increased auto-mixing to {round(g.g_auto_mix__how_much_canvas_to_pick * 100.0)} %")

    def decreaseAutoMixing(self):

        if g.g_auto_mixing_uses_distance_logic:
            g.g_auto_mixing_target_distance -= g.g_auto_mixing_distance_step
            if g.g_auto_mixing_target_distance < 0.0:
                g.g_auto_mixing_target_distance = 0.0

            Krita.instance().writeSetting("colorPlus", "g.g_auto_mixing_target_distance",
                                          str(g.g_auto_mixing_target_distance))

            quickMessage(
                f"Decreased auto-mixing distance to {round(g.g_auto_mixing_target_distance)}")

        else:
            g.g_auto_mix__how_much_canvas_to_pick -= g.g_mixing_step
            if g.g_auto_mix__how_much_canvas_to_pick < 0.0:
                g.g_auto_mix__how_much_canvas_to_pick = 0.0

            Krita.instance().writeSetting("colorPlus", "g.g_auto_mix__how_much_canvas_to_pick",
                                          str(g.g_auto_mix__how_much_canvas_to_pick))

            quickMessage(
                f"Decreased auto-mixing to {round(g.g_auto_mix__how_much_canvas_to_pick * 100.0)}%")

    def increaseAutoResetOpacityOnPick(self):

        g.g_auto_reset_opacity_on_pick_level += 5.0
        if g.g_auto_reset_opacity_on_pick_level >= 100.0:
            g.g_auto_reset_opacity_on_pick_level = 100.0

        Krita.instance().writeSetting("colorPlus", "g.g_auto_reset_opacity_on_pick_level",
                                      str(g.g_auto_reset_opacity_on_pick_level))

        quickMessage(
            f"Increased default opacity to {round(g.g_auto_reset_opacity_on_pick_level)}%")

    def decreaseAutoResetOpacityOnPick(self):

        g.g_auto_reset_opacity_on_pick_level -= 5.0
        if g.g_auto_reset_opacity_on_pick_level <= 0.0:
            g.g_auto_reset_opacity_on_pick_level = 0.0

        Krita.instance().writeSetting("colorPlus", "g.g_auto_reset_opacity_on_pick_level",
                                      str(g.g_auto_reset_opacity_on_pick_level))

        quickMessage(
            f"Decreased default opacity to {round(g.g_auto_reset_opacity_on_pick_level)}%")

    # def increasemixing_targetLogic(self):
        # self.mixing_target_distance += g.g_step_mixing_target_distance
        # if self.mixing_target_distance > 255.0:
        # self.mixing_target_distance = 255.0

        # quickMessage(f"Increased mixing. Target distance from fg color: {round(self.mixing_target_distance )}")

    # def decreasemixing_targetLogic(self):
        # self.mixing_target_distance -= g.g_step_mixing_target_distance
        # if self.mixing_target_distance < 0.0:
        # self.mixing_target_distance = 0.0

        # quickMessage(f"Decreased mixing. Target distance from fg color: {round(self.mixing_target_distance)}")

    def increaseLayerOpacity(self):

        # dryPaper() # conviene, perche' tanto significa che i segni precedenti non si vedono.

        application = Krita.instance()
        currentDoc = application.activeDocument()

        if g.g_auto_dry_each_stroke:
            parentNode = currentDoc.activeNode().parentNode()
            if parentNode is not None:
                activeLayer = parentNode.childNodes()[-2]
            else:
                activeLayer = currentDoc.activeNode()
        else:
            activeLayer = currentDoc.activeNode()

        curOpac = activeLayer.opacity()

        if curOpac <= 12.0 * 255.0 / 100.0:
            stepOpacity = g.g_normal_step_layer_opacity / 2.0
        else:
            stepOpacity = g.g_normal_step_layer_opacity

        newOpac = curOpac + stepOpacity

        if newOpac > 255:
            newOpac = 255
        activeLayer.setOpacity(int(newOpac))

        currentDoc.refreshProjection()  # altrimenti non si aggiorna

        # #aggiro bug di setopacity
        # parentNode = activeLayer.parentNode()
        # if parentNode is not None:
        # newLa = activeLayer.clone()
        # activeLayer.remove()
        # parentNode.addChildNode(newLa, None)

        application.activeWindow().activeView().showFloatingMessage(
            f"Increased layer opacity to {round(newOpac * 100.0 / 255.0)}", QIcon(), g.timeMessage, 1)

    def increaseAutoOpacityMaxDistance(self):

        g.g_auto_opacity_max_distance += 5

        if g.g_auto_opacity_max_distance > 255:
            g.g_auto_opacity_max_distance = 255

        Krita.instance().writeSetting(
            "colorPlus", "g.g_auto_opacity_max_distance", g.g_auto_opacity_max_distance)

        quickMessage(
            f"Increased max distance to {g.g_auto_opacity_max_distance}")

    def decreaseAutoOpacityMaxDistance(self):

        g.g_auto_opacity_max_distance -= 5

        if g.g_auto_opacity_max_distance <= 0:
            g.g_auto_opacity_max_distance = 0

        Krita.instance().writeSetting(
            "colorPlus", "g.g_auto_opacity_max_distance", g.g_auto_opacity_max_distance)
        quickMessage(
            f"Decreased max distance to {g.g_auto_opacity_max_distance}")

    def decreaseLayerOpacity(self):

        # application = Krita.instance()
        # currentDoc = application.activeDocument()
        # activeLayer = currentDoc.activeNode()
        # blurFilter = application.filter('gaussian blur')
        # blurFilter.apply(activeLayer, 0, 0, 3000, 2000)

        # self.dryPaper() # conviene, perche' tanto significa che i segni precedenti non si vedono.

        application = Krita.instance()
        currentDoc = application.activeDocument()
        if g.g_auto_dry_each_stroke:
            parentNode = currentDoc.activeNode().parentNode()
            if parentNode is not None:
                activeLayer = parentNode.childNodes()[-2]
            else:
                activeLayer = currentDoc.activeNode()
        else:
            activeLayer = currentDoc.activeNode()

        curOpac = activeLayer.opacity()

        if curOpac <= 20.0 * 255.0 / 100.0:
            stepOpacity = g.g_normal_step_layer_opacity / 2.0
        else:
            stepOpacity = g.g_normal_step_layer_opacity

        newOpac = curOpac - stepOpacity

        if newOpac < 0:
            newOpac = 0
        activeLayer.setOpacity(int(newOpac))

        currentDoc.refreshProjection()  # altrimenti non si aggiorna

        # #aggiro bug di setopacity
        # parentNode = activeLayer.parentNode()
        # if parentNode is not None:
        # newLa = activeLayer.clone()
        # activeLayer.remove()
        # parentNode.addChildNode(newLa, None)

        application.activeWindow().activeView().showFloatingMessage(
            f"Decreased layer opacity to { round(newOpac * 100.0 / 255.0)}", QIcon(), g.timeMessage, 1)

    def grum(self, currentSelection, currentLayer, application):
        currentDoc = application.activeDocument()

        if currentDoc is not None:
            # currentSelection = currentDoc.selection()

            if currentSelection is not None:
                # currentLayer = currentDoc.activeNode()

                if currentLayer is not None and currentLayer.type() == 'paintlayer':
                    blurFilter = application.filter('gaussian blur')

                    tmpDoc = Krita.instance().createDocument(currentDoc.width(),
                                                             currentDoc.height(),
                                                             'tmpDoc',
                                                             currentDoc.colorModel(),
                                                             currentDoc.colorDepth(),
                                                             currentDoc.colorProfile(),
                                                             currentDoc.resolution())

                    tmpLayer = tmpDoc.createNode('tmpLayer', 'paintlayer')
                    tmpLayer.setPixelData(currentLayer.pixelData(currentSelection.x(),
                                                                 currentSelection.y(),
                                                                 currentSelection.width(),
                                                                 currentSelection.height()),
                                          currentSelection.x(),
                                          currentSelection.y(),
                                          currentSelection.width(),
                                          currentSelection.height())

                    tmpFilterMask = tmpDoc.createFilterMask(
                        'tmpFilterMask', blurFilter, currentSelection)
                    tmpLayer.addChildNode(tmpFilterMask, None)

                    tmpDoc.rootNode().addChildNode(tmpLayer, None)

                    currentLayer.setPixelData(tmpLayer.projectionPixelData(currentSelection.x(),
                                                                           currentSelection.y(),
                                                                           currentSelection.width(),
                                                                           currentSelection.height()),
                                              currentSelection.x(),
                                              currentSelection.y(),
                                              currentSelection.width(),
                                              currentSelection.height())

                    currentDoc.refreshProjection()

                    tmpDoc.close()

    def dryPaperWithMessage(self):
        dryPaper(True)

    def dryPaperOldWithMerge(self, showMessage=True):

        # log(f"dry paper called showMessage = {showMessage}")
        application = Krita.instance()
        currentDoc = application.activeDocument()
        activeLayer = currentDoc.activeNode()

        # application.action('selectopaque').trigger()
        # currentDoc.waitForDone () # action needs to finish before continuing
        # selectionStroke = currentDoc.selection()

        parentNode = activeLayer.parentNode()
        newLa = None
        if parentNode is not None:
            # log("dry paper called1")
            oldOpacity = activeLayer.opacity()
            activeLayer.mergeDown()
            currentDoc.waitForDone()

            root = currentDoc.rootNode()
            newLa = currentDoc.createNode("Wet_area", "paintLayer")
            newLa.setOpacity(oldOpacity)

            backgroundLayer = parentNode.childNodes()[0]

            parentNode.addChildNode(newLa, None)

            g.g_opacity_decided_for_layer = False

            # currentDoc.setActiveNode(newLa)
            # currentDoc.refreshProjection()
            # currentDoc.waitForDone()

        else:

            newLa = currentDoc.createNode("Wet_area", "paintLayer")
            newLa.setOpacity(50.0 * 255.0 / 100.0)
            root.addChildNode(newLa, None)

            g.g_opacity_decided_for_layer = False

        # test blur

        if showMessage:
            log("dry paper called message")
            quickMessage("Dry paper")
            # application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), g.timeMessage, 1)

        return newLa

    # does not work. cannot set the active layer after merging down.
    def mergeOnTimer(self):
        # log(f"dry paper called showMessage = {showMessage}")
        application = Krita.instance()
        currentDoc = application.activeDocument()
        if currentDoc is not None:
            activeLayer = currentDoc.activeNode()
            if activeLayer is not None:

                # application.action('selectopaque').trigger()
                # currentDoc.waitForDone () # action needs to finish before continuing
                # selectionStroke = currentDoc.selection()

                parentNode = activeLayer.parentNode()

                if parentNode is not None:

                    children = parentNode.childNodes()
                    if len(children) > 3:

                        # skip the background which has opacity 100%. but follow the order from closest to bg to farthest
                        lastLayer = children[1]

                        lastLayer.mergeDown()
                        currentDoc.waitForDone()
                        # merged all layers. Create a new one and set opacity
                        # currentDoc.setActiveNode(children[-1])

                        quickMessage("auto dry layer")

                        # setActiveNode does not work. Workaround is:
                        children = parentNode.childNodes()
                        target_node = children[1]
                        model, s_model = get_layer_model()
                        index = node_to_index(target_node, model)
                        print(f"index is {index}")

                        s_model.setCurrentIndex(
                            index, QItemSelectionModel.Select)

                        # currentDoc.setActiveNode(children[1])

    def mergeCleanup(self):
        # log(f"dry paper called showMessage = {showMessage}")
        application = Krita.instance()
        currentDoc = application.activeDocument()
        activeLayer = currentDoc.activeNode()

        # application.action('selectopaque').trigger()
        # currentDoc.waitForDone () # action needs to finish before continuing
        # selectionStroke = currentDoc.selection()

        parentNode = activeLayer.parentNode()
        newLa = None
        if parentNode is not None:
            # log("dry paper called1")
            oldOpacity = activeLayer.opacity()

            while True:
                children = parentNode.childNodes()
                if len(children) <= 1:
                    break

                # skip the background which has opacity 100%. but follow the order from closest to bg to farthest
                lastLayer = children[1]

                lastLayer.mergeDown()

            # merged all layers. Create a new one and set opacity

            currentDoc.waitForDone()

            if g.g_multi_layer_mode:
                # root = currentDoc.rootNode()
                newLa = currentDoc.createNode("Wet_area", "paintLayer")
                newLa.setOpacity(oldOpacity)

                if g.g_set_spectral_blend_mode_when_creating_layer:
                    # log("setting over spectral")
                    newLa.setBlendingMode("over spectral")

                # backgroundLayer = parentNode.childNodes()[0]

                parentNode.addChildNode(newLa, None)

        else:
            messageBox(
                "In order to call \"Cleanup layers\", the current layer needs to have a parent group")
            showMessage = False
            # newLa = currentDoc.createNode("Wet_area", "paintLayer")
            # newLa.setOpacity(50.0 * 255.0 / 100.0)
            # root.addChildNode(newLa, None)
            newLa = None

        # test blur

        log("cleanup layers called message")
        quickMessage("Cleanup layers")
        # application.activeWindow().activeView().showFloatingMessage("Dry paper", QIcon(), timeMessage, 1)

        return newLa

    def manualResetLayerOpacityToDefault(self):

        application = Krita.instance()
        document = application.activeDocument()

        if document is not None:
            document.activeNode().setOpacity(
                int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))  # bm_djiwejdie

            document.refreshProjection()

            quickMessage(
                f"Reset layer opacity to default ({round(g.g_auto_reset_opacity_on_pick_level )}%)")

    def dryPaperAndPick(self):
        log("dry paper and pick")

        # non funziona se inverto l'ordine... non capisco perche'
        self.pickColorFun(False)

        # find if there is a parent node
        hasParentNode = False
        app = Krita.instance()
        document = None
        win = app.activeWindow()
        if win is not None:
            # log("pick called 1")
            view = win.activeView()
            if view is not None:
                # log("pick called 2")
                document = view.document()
                if document:

                    # could be root node, so I need to do parent again
                    parentNode = document.activeNode().parentNode()

                    if parentNode is not None:
                        pa = parentNode.parentNode()
                        if pa is not None:
                            log(
                                f"has parent node. document file {document.fileName()}. parentNode = {parentNode.name()}")
                            hasParentNode = True

        # I don't want to add a layer if I'm picking from the mixing palette, or if I've switched to 100 percent opacity mode
        if g.g_temp_switched_to_100_previous_opac is None and hasParentNode and g.g_multi_layer_mode:
            newLa = dryPaper(showMessage=False)

            # if active layer opacity < 70, set to 70

            if g.g_auto_reset_opacity_on_pick == 1 and document is not None and g.g_temp_switched_to_25_previous_opac is None:
                # bm_djiwejdie
                newLa.setOpacity(
                    int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))

                document.refreshProjection()

            quickMessage("Dry paper and pick color")
        elif g.g_temp_switched_to_100_previous_opac is not None and hasParentNode:
            # non faccio dry, ma devo cmq resettare l'opacità del layer attuale

            if g.g_auto_reset_opacity_on_pick == 1 and document is not None:
                document.activeNode().setOpacity(
                    int(g.g_auto_reset_opacity_on_pick_level * 255.0 / 100.0))  # bm_djiwejdie

                document.refreshProjection()

        else:
            # useless to dry paper because I am at 100% opacity
            quickMessage("Picked color")

    # def dryPaperAndMix(self):
        # log("dry paper and mix")

        # #non funziona se inverto l'ordine... non capisco perche'
        # self.mixFgColorWithBgColor_normalLogic()

        # if self.temp_switched_to_100_previous_opac is None:
            # self.dryPaper(showMessage = False)
            # #quickMessage("Dry paper and mix color")
        # else:
            # #useless to dry paper because I am at 100% opacity
            # pass
            # #quickMessage("Picked color")

    def onEnter(self):
        log(f"enter event")

    def createActions(self, window):

        action = window.createAction("LastColor", "Switch to last used color")
        action.triggered.connect(self.switchToLastColor)

        # action2 = window.createAction("MixColorBig", "MixColorBig")
        # action2.triggered.connect(self.mixBig)

        # action2 = window.createAction("MixColorSmall", "MixColorSmall")
        # action2.triggered.connect(self.mixSmall)

        actionMixW = window.createAction(
            "MixColorBecauseWrong", "Mix color because current color is wrong (also clears current layer)")
        actionMixW.triggered.connect(lambda: mixFgColorWithBgColor_normalLogic(
            clearCurLayer=True, createLayer=False))

        actionMixC = window.createAction(
            "MixColorBecauseWantNew", "Mix color because you want to fade out (also creates new layer)")
        actionMixC.triggered.connect(lambda: mixFgColorWithBgColor_normalLogic(
            clearCurLayer=False, createLayer=True))

        # actionMixSmall = window.createAction("MixColorSmall", "Pick some color from canvas, but no more than a given distance")
        # actionMixSmall.triggered.connect(self.mixFgColorWithBgColor_maxDistanceLogic)

        actionPickAndDry = window.createAction(
            "DryPaperAndPick", "Pick color under cursor and dry the paper")
        actionPickAndDry.triggered.connect(self.dryPaperAndPick)

        actionPick = window.createAction(
            "PickColor", "Pick color under cursor")
        actionPick.triggered.connect(self.pickColorFun)

        actionDryPaper = window.createAction(
            "LayerMergeDownAndNew", "Dry the paper (create new layer and set opacity)")
        actionDryPaper.triggered.connect(self.dryPaperWithMessage)

        actionViewFullScreen = window.createAction(
            "ViewSingleWindow", "Hide always on top windows and go fullscreen")
        actionViewFullScreen.triggered.connect(minimizeOnTopAndViewFullScreen)

        actionIncreaseLO = window.createAction(
            "IncreaseLayerOpacity", "Increase current layer opacity")
        actionIncreaseLO.setShortcut("S")
        actionIncreaseLO.triggered.connect(self.increaseLayerOpacity)

        actiondeclo = window.createAction(
            "DecreaseLayerOpacity", "Decrease current layer opacity")
        actiondeclo.setShortcut("A")
        actiondeclo.triggered.connect(self.decreaseLayerOpacity)

        # actionIncreaseAO = window.createAction("IncreaseMaxDistanceAutoOpacity", "Increase max distance for auto opacity")
        # actionIncreaseAO.triggered.connect(self.increaseAutoOpacityMaxDistance)

        # actiondecao = window.createAction("DecreaseMaxDistanceAutoOpacity", "Decrease max distance for auto opacity")
        # actiondecao.triggered.connect(self.decreaseAutoOpacityMaxDistance)

        actionincmi = window.createAction(
            "IncreaseMixing", "Increase mixing level (amount of color you pick from canvas when mixing)")
        actionincmi.triggered.connect(self.increaseMixing)

        actiondecmi = window.createAction(
            "DecreaseMixing", "Decrease mixing level (amount of color you pick from canvas when mixing)")
        actiondecmi.triggered.connect(self.decreaseMixing)

        # global g.g_mix_auto_clears_cur_layer
        # actionmixClear = window.createAction("MixClearCurrentLayer", "Mixing color auto-clears current layer")
        # actionmixClear.setCheckable(True)
        # actionmixClear.setChecked(g.g_mix_auto_clears_cur_layer == "1")
        # actionmixClear.triggered.connect(self.toggleMixClearsCurrentLayer)

        actioninaro = window.createAction(
            "IncreaseAutoResetOpacityOnPick", "Increase default layer opacity")
        actioninaro.setShortcut("w")
        actioninaro.triggered.connect(self.increaseAutoResetOpacityOnPick)

        actiondearo = window.createAction(
            "DecreaseAutoResetOpacityOnPick", "Decrease default layer opacity")
        actiondearo.setShortcut("q")
        actiondearo.triggered.connect(self.decreaseAutoResetOpacityOnPick)

        actionSave = window.createAction(
            "saveWindowPositions", "Save state and position of all windows")
        actionSave.setShortcut("Ctrl+Shift+F")
        actionSave.triggered.connect(self.saveWindowPositions)

        actionRestore = window.createAction(
            "restoreWindowPositions", "Restore state and position of all windows")
        actionRestore.setShortcut("Ctrl+Shift+R")
        actionRestore.triggered.connect(self.restoreWindowPositions)

        actionToggle100 = window.createAction(
            "toggle100PercOpacity", "Toggle 100% layer opacity")
        # actionToggle100.setShortcut("f")
        actionToggle100.triggered.connect(self.toggle_100_opac)

        actionToggle25 = window.createAction(
            "toggle25PercOpacity", "Toggle 25% layer opacity")

        actionToggle25.triggered.connect(self.toggle_25_opac)

        actionToggleMc = window.createAction(
            "cleanupLayers", "Cleanup (merge all temp layers)")
        actionToggleMc.triggered.connect(self.mergeCleanup)

        self.actionAutoFocus = window.createAction(
            "autoFocus", "Autofocus windows on mouse over")
        self.actionAutoFocus.setCheckable(True)
        self.actionAutoFocus.setChecked(g.g_auto_focus == "true")
        self.actionAutoFocus.triggered.connect(toggleAutoFocus)

        self.actionAutoResOpPick = window.createAction(
            "toggleAutoResetOpacityOnPick", "Auto-reset layer opacity to default on color pick")
        self.actionAutoResOpPick.setCheckable(True)
        self.actionAutoResOpPick.setChecked(
            g.g_auto_reset_opacity_on_pick == 1)
        self.actionAutoResOpPick.triggered.connect(
            toggleAutoResetOpacityOnPick)

        self.actionSingleLayerMode = window.createAction(
            "toggleSingleLayerMode", "Single-layer mode (don't auto create layers for watercolor effect)")
        self.actionSingleLayerMode.setCheckable(True)
        self.actionSingleLayerMode.setChecked(not g.g_multi_layer_mode)
        self.actionSingleLayerMode.triggered.connect(toggleMultiLayerMode)

        self.actionAcceptColorAndStop = window.createAction(
            "acceptCurrentColorAndStopDirty", "Accept current color and stop dirty brush")
        self.actionAcceptColorAndStop.triggered.connect(
            lambda: self.acceptCurrentColorAndStopDirty(clearCurLayer=True))

        self.manualResOpPick = window.createAction(
            "manualResetLayerOpacityToDefault", "Reset layer opacity to default now")
        # self.manualResOpPick.setShortcut("v")
        self.manualResOpPick.triggered.connect(
            self.manualResetLayerOpacityToDefault)

        setFgColorEqualToColorOfLastStroke = window.createAction(
            "acceptCurrentColor", "accept current layer color")
        setFgColorEqualToColorOfLastStroke.triggered.connect(
            setFgColorEqualToColorOfLastStrokeAfterOpacityAdjust)
        setFgColorEqualToColorOfLastStroke.setShortcut("v")

        main_menu = window.qwindow().menuBar()
        custom_menu = main_menu.addMenu("ColorPlus")

        custom_menu.addAction(self.actionAutoFocus)
        custom_menu.addAction(self.actionSingleLayerMode)

        custom_menu.addSeparator()
        custom_menu.addAction(actionViewFullScreen)

        g.g_auto_mix_enabled = False
        g.g_actionAutoMix = window.createAction(
            "toggleAutoMixing", "Auto mixing (each stroke picks a bit of color from the background)")
        g.g_actionAutoMix.setCheckable(True)
        g.g_actionAutoMix.setShortcut("r")
        g.g_actionAutoMix.triggered.connect(toggleAutoMixing)
        
        g.g_dirty_brush_overall_enabled = False
        g.g_actionDirtyBrush = window.createAction(
            "toggleDirtyBrush", "Dirty brush (simulates a brush that gets dirty with previous colors)")
        g.g_actionDirtyBrush.setCheckable(True)
        g.g_actionDirtyBrush.setShortcut("d")
        g.g_actionDirtyBrush.triggered.connect(toggleDirtyBrush)
        
        # Add brush cycler action
        g.g_actionBrushCycler = window.createAction(
            "toggleBrushCycler", "Cycle brushes (automatically change brush after each stroke)")
        g.g_actionBrushCycler.setCheckable(True)
        g.g_actionBrushCycler.setShortcut("b")
        g.g_actionBrushCycler.triggered.connect(lambda: g.g_docker_instance.toggleBrushCycler())

        self.actionIncAutoMix = window.createAction(
            "increaseAutoMixing", "Increase auto-mixing (amount of bg color you pick at each stroke)")
        self.actionIncAutoMix.setShortcut("shift+w")
        self.actionIncAutoMix.triggered.connect(self.increaseAutoMixing)

        self.actionDecAutoMix = window.createAction(
            "decreaseAutoMixing", "Decrease auto-mixing (amount of bg color you pick at each stroke)")
        self.actionDecAutoMix.setShortcut("shift+q")
        self.actionDecAutoMix.triggered.connect(self.decreaseAutoMixing)

        custom_menu.addSeparator()
        custom_menu.addAction(g.g_actionAutoMix)
        custom_menu.addAction(self.actionIncAutoMix)
        custom_menu.addAction(self.actionDecAutoMix)
        custom_menu.addAction(g.g_actionDirtyBrush)
        custom_menu.addAction(g.g_actionBrushCycler)

        custom_menu.addSeparator()
        custom_menu.addAction(actionDryPaper)

        custom_menu.addAction(actionToggleMc)

        custom_menu.addSeparator()
        custom_menu.addAction(actionRestore)
        custom_menu.addAction(actionSave)

        custom_menu.addSeparator()
        custom_menu.addAction(actionPick)
        custom_menu.addAction(actionPickAndDry)

        custom_menu.addSeparator()
        custom_menu.addAction(self.actionAutoResOpPick)
        custom_menu.addAction(actioninaro)
        custom_menu.addAction(actiondearo)
        custom_menu.addAction(self.manualResOpPick)

        custom_menu.addSeparator()

        custom_menu.addAction(actionIncreaseLO)
        custom_menu.addAction(actiondeclo)
        custom_menu.addSeparator()
        # custom_menu.addAction(actionmixClear)
        custom_menu.addAction(actionMixW)
        custom_menu.addAction(actionMixC)

        custom_menu.addAction(actionincmi)
        custom_menu.addAction(actiondecmi)

        custom_menu.addSeparator()

        custom_menu.addAction(actionToggle100)
        custom_menu.addAction(actionToggle25)


def minimizeOnTopAndViewFullScreen():
    app = Krita.instance()

    # log(f"windows = {app.windows()}")
    # log(f"active window title = {app.activeWindow().qwindow().windowTitle()}")

    wi = app.activeWindow()

    # for wi in app.windows():
    # log(f"---------")
    # log(f"window title = {wi.qwindow().windowTitle()}")
    # log(f"wi views = {wi.views()}")
    # print (f"wi subwindows = {wi.qwindow().findChild(QMdiArea).subWindowList()}")

    subwins = wi.qwindow().findChild(QMdiArea).subWindowList()

    # vedi se c'è una finestra always on top
    thereIsOnTop = False
    for su in subwins:
        # flags = su.windowFlags()
        if su.windowFlags() & Qt.WindowStaysOnTopHint:
            thereIsOnTop = True

    # vedi se c'è una finestra massimizzata
    thereIsMaximized = False
    for su in subwins:
        # flags = su.windowFlags()
        if su.windowState() & Qt.WindowMaximized:
            print(f"trovata finestra massimiz {su.windowTitle()}")
            thereIsMaximized = True

    # cerca di capire in che stato siamo.

    act = app.action('view_show_canvas_only')
    siamoInStatoNormale = not act.isChecked()

    # old logic: se c'è una window on top non minimizzata, siamo in stato normale. altrimenti siamo in stato view full screen
    # siamoInStatoNormale = False
    # if thereIsOnTop :
    # for su in subwins:
    # #flags = su.windowFlags()

    # stayOnTop = False
    # if su.windowFlags() & Qt.WindowStaysOnTopHint:
    # stayOnTop = True

    # else:
    # stayOnTop = False

    # isMinimized = False
    # if su.windowState() & Qt.WindowMinimized:
    # isMinimized = True
    # else:
    # isMinimized = False

    # if stayOnTop and not isMinimized:
    # siamoInStatoNormale = True
    # else:
    # # non ci sono finestre on top. come faccio a capire se siamo in stato normale? vediamo se non esiste una finestra massimizzata
    # print ( "non ci sono finestre on top")

    log(f"siamo in stato normale: {siamoInStatoNormale}")

    if siamoInStatoNormale:
        # devo minimizzare le on top e massimizzare la prima delle non-on-top

        for su in subwins:
            flags = su.windowFlags()

            stayOnTop = False
            if su.windowFlags() & Qt.WindowStaysOnTopHint:
                stayOnTop = True
            else:
                stayOnTop = False

            if stayOnTop:
                # è una finestra di reference: minimizzala
                su.setWindowState(su.windowState() | Qt.WindowMinimized)
            else:
                # è è una finestra normal: massimizza
                # su.setWindowState(su.windowState() & ~Qt.WindowMinimized)

                su.setWindowState(su.windowState() |
                                  Qt.WindowMaximized)  # la massimizzo

        # ora nascondo i docker
        app.action('view_show_canvas_only').trigger()
        app.activeDocument().waitForDone()  # action needs to finish before continuing

        # workaround per mancanza di fit to page
        app.action('zoom_to_100pct').trigger()
        app.activeDocument().waitForDone()  # action needs to finish before continuing

        app.action('toggle_zoom_to_fit').trigger()
        app.activeDocument().waitForDone()  # action needs to finish before continuing

    else:
        # devo tornare in stato normale, quindi alle on top devo togliere il minimized e alle normali devo togliere il maximized

        for su in subwins:
            flags = su.windowFlags()

            stayOnTop = False
            if su.windowFlags() & Qt.WindowStaysOnTopHint:
                stayOnTop = True
            else:
                stayOnTop = False

            if stayOnTop:
                # è una finestra di reference: togli il minimized
                su.setWindowState(su.windowState() & ~Qt.WindowMinimized)
            else:
                # è è una finestra normal: togli il massimizza
                # tolgo lo stato maximixed
                su.setWindowState(su.windowState() & ~Qt.WindowMaximized)

        # ora ri-mostro i docker (richiamando la stessa action)
        app.action('view_show_canvas_only').trigger()
        app.activeDocument().waitForDone()  # action needs to finish before continuing


def toggleAutoFocus():
    if g.g_auto_focus == "true":

        g.g_auto_focus = "false"
    else:

        g.g_auto_focus = "true"

    Krita.instance().writeSetting("colorPlus", "g.g_auto_focus", g.g_auto_focus)


def toggleAutoResetOpacityOnPick():

    if g.g_auto_reset_opacity_on_pick == 1:
        g.g_auto_reset_opacity_on_pick = 0
        quickMessage("Auto reset opacity on color pick: disabled")
    else:
        g.g_auto_reset_opacity_on_pick = 1
        quickMessage(
            f"Auto reset opacity on color pick: enabled. Will be reset to {round(g.g_auto_reset_opacity_on_pick_level)}.")

    Krita.instance().writeSetting("colorPlus", "g.g_auto_reset_opacity_on_pick",
                                  str(g.g_auto_reset_opacity_on_pick))


# def toggleMixClearsCurrentLayer(self):
    # global g.g_mix_auto_clears_cur_layer
    # if g.g_mix_auto_clears_cur_layer == "1":
    # g.g_mix_auto_clears_cur_layer = "0"
    # quickMessage("Color mix will not clear current layer automatically")
    # else:
    # g.g_mix_auto_clears_cur_layer = "1"
    # quickMessage("Color mix will clear current layer automatically")

    # Krita.instance().writeSetting("colorPlus", "g.g_mix_auto_clears_cur_layer", g.g_mix_auto_clears_cur_layer)

def toggleMultiLayerMode():

    g.g_multi_layer_mode = not g.g_multi_layer_mode

    multi_layer_mode_str = "1" if g.g_multi_layer_mode else "0"

    Krita.instance().writeSetting(
        "colorPlus", "g.g_multi_layer_mode", multi_layer_mode_str)


# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance()))
