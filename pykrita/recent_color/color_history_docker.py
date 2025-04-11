from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QResizeEvent # Import QResizeEvent
from PyQt5.QtWidgets import QDockWidget, QWidget, QGridLayout, QLabel
from krita import DockWidget
from . import globals as g

# --- Custom Widget for Clickable Color Squares ---
class ClickableColorLabel(QLabel):
    """ A QLabel that displays a color and emits a signal when clicked. """
    clicked = pyqtSignal(QColor)

    def __init__(self, color, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(32, 32)
        self.setStyleSheet(f"background-color: {self._color.name()}; border: 1px solid black;")
        self.setToolTip(f"Color: {self._color.name()}")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            g.log(f"ClickableColorLabel clicked: emitting color {self._color.name()}")
            self.clicked.emit(self._color)
        super().mousePressEvent(event)

# --- Color History Docker Definition ---
class ColorHistoryDocker(DockWidget):
    def __init__(self):
        super().__init__()
        g.g_color_history_docker_instance = self  # Store instance globally
        self.setWindowTitle("ColorPlus Color History")
        mainWidget = QWidget(self)
        self.setWidget(mainWidget)
        
        # Use a grid layout for multi-row display
        self.color_history_layout = QGridLayout()
        self.color_history_layout.setContentsMargins(5, 5, 5, 5)
        self.color_history_layout.setSpacing(2)  # Spacing between squares
        mainWidget.setLayout(self.color_history_layout)
        
        # Initial UI population
        self.update_color_history_ui()
    
    def update_color_history_ui(self):
        """ Clears and rebuilds the color history UI display in a grid layout. """
        # Clear existing widgets from the layout
        while self.color_history_layout.count() > 0:
            item = self.color_history_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # Add new color squares in a grid layout
        # g.log(f"Updating color history UI with {len(g.g_last_virtual_colors_used)} colors.")
        
        # Calculate how many color squares can fit in the current width
        docker_width = self.width()
        square_size = 32  # Size of each color square
        spacing = 2       # Spacing between squares
        margins = 10      # Total horizontal margins (5px on each side)
        
        # Calculate available width and how many squares can fit
        available_width = docker_width - margins
        colors_per_row = max(1, available_width // (square_size + spacing))
        # g.log(f"Docker width: {docker_width}px, can fit {colors_per_row} color squares per row")
        
        for i, item in enumerate(g.g_last_virtual_colors_used):
            qcolor_to_display = None
            if hasattr(item, 'r') and hasattr(item, 'g') and hasattr(item, 'b'):  # Check if it's our custom rgb class
                # Convert rgb object to QColor, ensuring values are integers
                try:
                    r_val = int(round(item.b))  # inverto! perche' in realta' la mia immagine e' bgr
                    g_val = int(round(item.g))
                    b_val = int(round(item.r))
                    # Clamp values to 0-255 just in case
                    r_val = max(0, min(255, r_val))
                    g_val = max(0, min(255, g_val))
                    b_val = max(0, min(255, b_val))
                    qcolor_to_display = QColor(r_val, g_val, b_val)
                except Exception as e:
                    g.log(f"Error converting rgb to QColor: {e}, rgb values: r={item.r}, g={item.g}, b={item.b}")
            elif isinstance(item, QColor):  # Handle if it's already a QColor
                qcolor_to_display = item
            else:
                g.log(f"Warning: Item in g_last_virtual_colors_used is not an rgb or QColor object: {type(item)}")

            if qcolor_to_display:
                color_square = ClickableColorLabel(qcolor_to_display)  # Pass the QColor
                color_square.clicked.connect(self._on_color_square_clicked)
                
                # Calculate row and column for grid layout
                row = i // colors_per_row
                col = i % colors_per_row
                self.color_history_layout.addWidget(color_square, row, col)
    
    # --- Slot for Color Square Clicks ---
    def _on_color_square_clicked(self, color):
        """ Handles clicks on the color history squares. """
        g.log(f"Color square clicked: {color.name()}")
        # Set as foreground color in Krita
        from krita import Krita
        view = Krita.instance().activeWindow().activeView()
        fg = view.foregroundColor()
        # Converti il QColor in ManagedColor
        comp = fg.components()
        comp[0] = color.blueF()
        comp[1] = color.greenF()
        comp[2] = color.redF()
        fg.setComponents(comp)
        view.setForeGroundColor(fg)
        
    def canvasChanged(self, canvas):
        """ Override of the abstract method from DockWidget class.
        Called when the canvas changes in Krita. """
        # g.log(f"Canvas changed in ColorHistoryDocker")
        # Update the UI when canvas changes
        # self.update_color_history_ui()  # commentato perche lo fa ad ogni stroke

    def resizeEvent(self, event: QResizeEvent):
        """ Called when the docker widget is resized. """
        g.log(f"ColorHistoryDocker resized to: {event.size().width()}x{event.size().height()}")
        self.update_color_history_ui() # Recalculate layout
        super().resizeEvent(event) # Call base class implementation