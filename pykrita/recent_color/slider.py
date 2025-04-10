from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QLinearGradient

class KritaStyleSlider(QWidget):
    """
    Widget che replica lo slider di Krita.
    - Mostra un riquadro grigio chiaro con una barra blu che indica il valore
    - Permette di cliccare in qualsiasi punto per impostare il valore
    - Mostra un testo personalizzabile e la percentuale con ombra
    - Supporta la regolazione fine con la rotella del mouse
    """
    valueChanged = pyqtSignal(float)
    
    def __init__(self, parent=None, label="Value"):
        super().__init__(parent)
        self._value = 0.5  # Valore iniziale tra 0.0 e 1.0
        self._label = label
        self._dragging = False
        
        # Colori
        self._background_color = QColor(220, 220, 220)  # Grigio chiaro
        self._bar_color = QColor(30, 130, 255)          # Blu
        self._text_color = QColor(255, 255, 255)        # Bianco
        self._shadow_color = QColor(0, 0, 0, 120)       # Nero semi-trasparente
        
        # Impostazioni del widget
        self.setMinimumSize(200, 30)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setCursor(Qt.PointingHandCursor)
        
    def setValue(self, value):
        """Imposta il valore dello slider (tra 0.0 e 1.0)"""
        # Limita il valore tra 0.0 e 1.0
        value = max(0.0, min(1.0, value))
        
        if value != self._value:
            self._value = value
            self.valueChanged.emit(self._value)
            self.update()
            
    def value(self):
        """Ritorna il valore corrente dello slider"""
        return self._value
    
    def setLabel(self, label):
        """Imposta il testo personalizzato"""
        self._label = label
        self.update()
        
    def paintEvent(self, event):
        """Disegna lo slider"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)  # Margine
        
        # Disegna il background grigio
        painter.fillRect(rect, self._background_color)
        
        # Calcola la larghezza della barra blu in base al valore
        bar_width = int(rect.width() * self._value)
        bar_rect = QRect(rect.x(), rect.y(), bar_width, rect.height())
        
        # Disegna la barra blu
        painter.fillRect(bar_rect, self._bar_color)
        
        # Prepara il testo
        text = f"{self._label}: {int(self._value * 100)}%"
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        
        # Disegna l'ombra del testo
        shadow_offset = 1
        painter.setPen(self._shadow_color)
        painter.drawText(rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset), 
                         Qt.AlignCenter, text)
        
        # Disegna il testo
        painter.setPen(self._text_color)
        painter.drawText(rect, Qt.AlignCenter, text)
        
    def mousePressEvent(self, event):
        """Gestisce il click del mouse"""
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._updateValueFromPosition(event.pos())
            
    def mouseMoveEvent(self, event):
        """Gestisce il trascinamento del mouse"""
        if self._dragging:
            self._updateValueFromPosition(event.pos())
            
    def mouseReleaseEvent(self, event):
        """Gestisce il rilascio del mouse"""
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self._updateValueFromPosition(event.pos())
            
    def wheelEvent(self, event):
        """Gestisce la rotella del mouse per regolazione fine"""
        delta = event.angleDelta().y()
        # Regolazione fine: cambia di 0.01 per ogni step della rotella
        step = 0.01 if delta > 0 else -0.01
        self.setValue(self._value + step)
            
    def _updateValueFromPosition(self, pos):
        """Aggiorna il valore in base alla posizione del mouse"""
        rect = self.rect().adjusted(2, 2, -2, -2)
        if rect.width() > 0:
            value = (pos.x() - rect.x()) / rect.width()
            value = max(0.0, min(1.0, value))
            self.setValue(value)

# # Esempio di utilizzo
# if __name__ == "__main__":
#     import sys
    
#     app = QApplication(sys.argv)
    
#     window = QWidget()
#     window.setWindowTitle("Krita Style Slider Demo")
#     window.setGeometry(100, 100, 400, 200)
    
#     slider = KritaStyleSlider(window, "Opacity")
#     slider.setGeometry(50, 50, 300, 30)
#     slider.setValue(0.7)  # Imposta un valore iniziale
    
#     slider2 = KritaStyleSlider(window, "Flow")
#     slider2.setGeometry(50, 100, 300, 30)
#     slider2.setValue(0.3)  # Imposta un valore iniziale
    
#     window.show()
#     sys.exit(app.exec_())