from PyQt5.QtCore import (
    Qt,
    QObject,
    QEvent,
    QPointF,
    QRect,
    QTimer,
    pyqtSignal)  # Added pyqtSignal
from . import globals as g
from PyQt5.QtGui import (
    QTransform,
    QPainter,
    QImage,
    QBrush,
    QIcon,
    QColor,
    QPolygonF,
    QInputEvent,
    QKeyEvent,
    QCursor)

from .slider import KritaStyleSlider # Import the new slider

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


from krita import (
    Krita, ManagedColor, Extension, DockWidget)


from .recent_color import dryPaper, toggleAutoFocus, toggleDirtyBrush, toggleAutoMixing, toggleAutoResetOpacityOnPick,updateAutoResetOpacityLevel, toggleMultiLayerMode, mergeCleanup, quickMessage, brush_cycler, BrushListDialog

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


        g.lblActiveColor = QLabel()
        g.lblActiveColor.setToolTip("Current foreground color")
        layoutHorizColorAndDry.addWidget(g.lblActiveColor)
        # lblActiveColor.setStyleSheet("background-color: red")
        g.lblActiveColor.setMinimumHeight(45)
        g.lblActiveColor.setMinimumWidth(65)




        btnDry = QPushButton("Dry paper", mainWidget)
        layoutHorizColorAndDry.addWidget(btnDry)
        font = btnDry.font()
        font.setPixelSize(15)
        btnDry.setFont(font)
        btnDry.setMinimumHeight(50)

        btnDry.clicked.connect(lambda: dryPaper())

        
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
        g.g_slider_auto_mix_level.setEnabled(g.g_auto_mix_enabled)

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
        g.g_slider_dirty_brush_level.setEnabled(g.g_dirty_brush_overall_enabled)

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
        
        # Autofocus windows layout
        layoutHorizAutoFocus = QHBoxLayout()
        mainLayout.addLayout(layoutHorizAutoFocus)
        
        # Autofocus windows button
        g.g_btn_auto_focus = QPushButton("Autofocus windows", mainWidget)
        g.g_btn_auto_focus.setCheckable(True)
        g.g_btn_auto_focus.setChecked(g.g_auto_focus == "true")
        layoutHorizAutoFocus.addWidget(g.g_btn_auto_focus)
        font = g.g_btn_auto_focus.font()
        font.setPixelSize(15)
        g.g_btn_auto_focus.setFont(font)
        g.g_btn_auto_focus.setToolTip("Autofocus windows on mouse over")
        g.g_btn_auto_focus.clicked.connect(toggleAutoFocus)
        
        # Auto-reset layer opacity layout
        layoutHorizAutoResetOpacity = QHBoxLayout()
        mainLayout.addLayout(layoutHorizAutoResetOpacity)
        
        # Auto-reset layer opacity button
        g.g_btn_auto_reset_opacity = QPushButton("Auto-reset opacity", mainWidget)
        g.g_btn_auto_reset_opacity.setCheckable(True)
        g.g_btn_auto_reset_opacity.setChecked(g.g_auto_reset_opacity_on_pick == 1)
        layoutHorizAutoResetOpacity.addWidget(g.g_btn_auto_reset_opacity)
        font = g.g_btn_auto_reset_opacity.font()
        font.setPixelSize(15)
        g.g_btn_auto_reset_opacity.setFont(font) 
        g.g_btn_auto_reset_opacity.setToolTip("Auto-reset layer opacity to default on color pick")
        g.g_btn_auto_reset_opacity.clicked.connect(toggleAutoResetOpacityOnPick)

        # Auto-reset layer opacity slider
        g.g_slider_auto_reset_opacity = KritaStyleSlider( mainWidget, "Auto-reset opacity")
        # g.g_slider_auto_reset_opacity.setRange(0, 100)
        g.g_slider_auto_reset_opacity.setValue(g.g_auto_reset_opacity_on_pick_level / 100.0)
        # g.g_slider_auto_reset_opacity.setToolTip(f"Set default opacity level ({int(g.g_auto_reset_opacity_on_pick_level * 100.0)}%)")
        g.g_slider_auto_reset_opacity.valueChanged.connect(updateAutoResetOpacityLevel)
        # g.g_slider_auto_reset_opacity.setMinimumWidth(80) # Give it some minimum width
        layoutHorizAutoResetOpacity.addWidget(g.g_slider_auto_reset_opacity)

        g.g_slider_auto_reset_opacity.setEnabled(g.g_auto_reset_opacity_on_pick)
        # Add stretch to push button and slider to the left
        # layoutHorizAutoResetOpacity.addStretch(1)

        # Single-layer mode layout
        layoutHorizSingleLayer = QHBoxLayout()
        mainLayout.addLayout(layoutHorizSingleLayer)
        
        # Single-layer mode button
        g.g_btn_single_layer = QPushButton("Single-layer mode", mainWidget)
        g.g_btn_single_layer.setCheckable(True)
        g.g_btn_single_layer.setChecked(not g.g_multi_layer_mode)
        layoutHorizSingleLayer.addWidget(g.g_btn_single_layer)
        font = g.g_btn_single_layer.font()
        font.setPixelSize(15)
        g.g_btn_single_layer.setFont(font)
        g.g_btn_single_layer.setToolTip("Single-layer mode (don't auto create layers for watercolor effect)")
        g.g_btn_single_layer.clicked.connect(toggleMultiLayerMode)
        
        # Cleanup layers layout
        layoutHorizCleanup = QHBoxLayout()
        mainLayout.addLayout(layoutHorizCleanup)
        
        # Cleanup layers button
        btnCleanup = QPushButton("Cleanup layers", mainWidget)
        layoutHorizCleanup.addWidget(btnCleanup)
        font = btnCleanup.font()
        font.setPixelSize(15)
        btnCleanup.setFont(font)
        btnCleanup.setToolTip("Merge all temporary layers")
        # btnCleanup.setMinimumHeight(50)
        btnCleanup.clicked.connect(mergeCleanup)
        
        # mix radius dial
        g.g_slider_mix_radius = KritaStyleSlider(mainWidget, "Mix radius")
        g.g_slider_mix_radius.setToolTip("Mix radius in pixels (0-20)")
        layoutHorizMixRadius.addWidget(g.g_slider_mix_radius)
        # Set initial value (map 0-20 range to 0.0-1.0)
        initial_radius_value = g.g_mix_radius / 20.0 if g.g_mix_radius is not None else 0.0
        g.g_slider_mix_radius.setValue(max(0.0, min(1.0, initial_radius_value))) # Clamp value
        g.g_slider_mix_radius.valueChanged.connect(self.mixRadiusValueChanged)

        g.g_slider_mix_radius.setEnabled(g.g_mix_radius_enabled) 








        # per ora commento il brush cycler, non e' chiaro lo scopo
        # Brush cycler layout
        layoutHorizBrushCycler = QHBoxLayout()
        mainLayout.addLayout(layoutHorizBrushCycler)
        
        # Brush cycler button
        g.g_btn_brush_cycler = QPushButton("Auto-cycle brushes", mainWidget)
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

        g.g_slider_mix_radius.setEnabled(g.g_mix_radius_enabled) 
        
        # Aggiorna lo stato del pulsante
        g.g_btn_mix_radius.setChecked(g.g_mix_radius_enabled)

        # g.g_slid.setEnabled(True)
        
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
