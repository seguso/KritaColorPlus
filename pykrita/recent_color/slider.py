from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QPainterPath, QLinearGradient

class KritaStyleSlider(QWidget):
    """
    Widget che replica lo slider di Krita.
    - Mostra un riquadro grigio chiaro con una barra blu che indica il valore
    - Permette di cliccare in qualsiasi punto per impostare il valore
    - Mostra un testo personalizzabile e la percentuale con ombra rinforzata
    - Supporta la regolazione fine con la rotella del mouse
    - Implementa stato disabled con barra grigia e nessuna interazione
    - Testo semi-trasparente quando disabilitato
    """
    valueChanged = pyqtSignal(float)
    
    def __init__(self, parent=None, label="Value"):
        super().__init__(parent)
        self._value = 0.5  # Valore iniziale tra 0.0 e 1.0
        self._label = label
        self._dragging = False
        
        # Colori
        self._background_color = QColor(220, 220, 220)    # Grigio chiaro
        self._bar_color = QColor(30, 130, 255)            # Blu
        self._bar_disabled_color = QColor(150, 150, 150)  # Grigio per stato disabled
        self._text_color = QColor(255, 255, 255)          # Bianco
        self._shadow_color = QColor(0, 0, 0, 180)         # Nero più opaco
        
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

    def setEnabled(self, enabled):
        """Override del metodo setEnabled per aggiornare il cursore"""
        super().setEnabled(enabled)
        if enabled:
            self.setCursor(Qt.PointingHandCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        self.update()
        
    def paintEvent(self, event):
        """Disegna lo slider"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        rect = self.rect().adjusted(2, 2, -2, -2)  # Margine
        
        # Disegna il background grigio
        painter.fillRect(rect, self._background_color)
        
        # Calcola la larghezza della barra in base al valore
        bar_width = int(rect.width() * self._value)
        bar_rect = QRect(rect.x(), rect.y(), bar_width, rect.height())
        
        # Disegna la barra con colore appropriato per lo stato
        if self.isEnabled():
            bar_color = self._bar_color  # Blu se abilitato
        else:
            bar_color = self._bar_disabled_color  # Grigio se disabilitato
            
        painter.fillRect(bar_rect, bar_color)
        
        # Prepara il testo
        text = f"{self._label}: {int(self._value * 100)}%"
        font = painter.font()
        font.setBold(True)
        painter.setFont(font)
        
        # Imposta l'opacità del testo in base allo stato
        if self.isEnabled():
            text_color = self._text_color
            shadow_color = self._shadow_color
        else:
            # Riduce l'opacità al 50% se disabilitato
            text_color = QColor(self._text_color)
            text_color.setAlpha(int(self._text_color.alpha() * 0.5))
            
            shadow_color = QColor(self._shadow_color)
            shadow_color.setAlpha(int(self._shadow_color.alpha() * 0.5))
        
        # Tecnica di ombra potenziata: disegna l'ombra più volte con offset leggermente diversi
        shadow_offsets = [
            (1, 1), (1, 0), (0, 1), (-1, 1), (1, -1),
            (2, 2), (2, 1), (1, 2), (2, 0), (0, 2)
        ]
        
        painter.setPen(shadow_color)
        for offset_x, offset_y in shadow_offsets:
            # Usa la correzione fornita dall'utente
            shadow_rect = rect.adjusted(offset_x - 1, offset_y - 1, offset_x - 1, offset_y - 1)
            painter.drawText(shadow_rect, Qt.AlignCenter, text)
        
        # Disegna il testo principale
        painter.setPen(text_color)
        painter.drawText(rect, Qt.AlignCenter, text)
        
    def mousePressEvent(self, event):
        """Gestisce il click del mouse solo se il widget è abilitato"""
        if not self.isEnabled():
            return
            
        if event.button() == Qt.LeftButton:
            self._dragging = True
            self._updateValueFromPosition(event.pos())
            
    def mouseMoveEvent(self, event):
        """Gestisce il trascinamento del mouse solo se il widget è abilitato"""
        if not self.isEnabled():
            return
            
        if self._dragging:
            self._updateValueFromPosition(event.pos())
            
    def mouseReleaseEvent(self, event):
        """Gestisce il rilascio del mouse solo se il widget è abilitato"""
        if not self.isEnabled():
            return
            
        if event.button() == Qt.LeftButton and self._dragging:
            self._dragging = False
            self._updateValueFromPosition(event.pos())
            
    def wheelEvent(self, event):
        """Gestisce la rotella del mouse solo se il widget è abilitato"""
        if not self.isEnabled():
            return
            
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
#     from PyQt5.QtWidgets import QVBoxLayout, QCheckBox
    
#     app = QApplication(sys.argv)
    
#     window = QWidget()
#     window.setWindowTitle("Krita Style Slider Demo")
#     window.setGeometry(100, 100, 400, 250)
    
#     layout = QVBoxLayout()
    
#     slider1 = KritaStyleSlider(None, "Opacity")
#     slider1.setValue(0.7)  # Imposta un valor