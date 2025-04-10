# krita_style_slider.py
# Widget che implementa uno slider in stile Krita

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QFontMetrics
from PyQt5.QtWidgets import QWidget

class KritaStyleSlider(QWidget):
    """Widget slider in stile Krita senza thumb, con barra blu e testo sovrapposto"""
    
    # Segnale emesso quando il valore cambia
    valueChanged = pyqtSignal(float)
    
    def __init__(self, parent=None, label=""):
        super().__init__(parent)
        
        # Proprietà dello slider
        self._value = 0.0  # Valore corrente (0.0 - 1.0)
        self._label = label  # Testo da visualizzare
        
        # Colori
        self._background_color = QColor(230, 230, 230)  # Grigio chiaro
        self._bar_color = QColor(0, 120, 215)  # Blu
        self._text_color = QColor(255, 255, 255)  # Bianco
        self._text_shadow_color = QColor(0, 0, 0, 128)  # Nero semi-trasparente
        
        # Impostazioni di dimensione
        self.setMinimumHeight(24)
        self.setMinimumWidth(100)
        
        # Abilita il tracciamento del mouse
        self.setMouseTracking(True)
        
        # Abilita il focus per ricevere eventi da tastiera
        self.setFocusPolicy(Qt.StrongFocus)
    
    def value(self):
        """Restituisce il valore corrente dello slider"""
        return self._value
    
    def setValue(self, value):
        """Imposta il valore dello slider e aggiorna il widget"""
        # Limita il valore tra 0.0 e 1.0
        new_value = max(0.0, min(1.0, value))
        
        # Aggiorna solo se il valore è cambiato
        if new_value != self._value:
            self._value = new_value
            self.update()  # Ridisegna il widget
            self.valueChanged.emit(self._value)  # Emette il segnale
    
    def setLabel(self, label):
        """Imposta il testo da visualizzare sullo slider"""
        self._label = label
        self.update()  # Ridisegna il widget
    
    def paintEvent(self, event):
        """Gestisce il disegno del widget"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)  # Attiva l'antialiasing
        
        # Dimensioni del widget
        width = self.width()
        height = self.height()
        
        # Disegna lo sfondo
        painter.fillRect(0, 0, width, height, self._background_color)
        
        # Disegna la barra di progresso
        bar_width = int(width * self._value)
        if bar_width > 0:
            painter.fillRect(0, 0, bar_width, height, self._bar_color)
        
        # Prepara il testo da visualizzare
        display_text = f"{self._label} {int(self._value * 100)}%"
        
        # Imposta il font
        font = QFont()
        font.setPixelSize(height // 2)  # Dimensione proporzionale all'altezza
        painter.setFont(font)
        
        # Calcola la posizione del testo (centrato)
        fm = QFontMetrics(font)
        text_width = fm.width(display_text)
        text_height = fm.height()
        text_x = (width - text_width) // 2
        text_y = (height + text_height // 2) // 2
        
        # Disegna l'ombra del testo
        painter.setPen(QPen(self._text_shadow_color))
        painter.drawText(text_x + 1, text_y + 1, display_text)
        
        # Disegna il testo
        painter.setPen(QPen(self._text_color))
        painter.drawText(text_x, text_y, display_text)
    
    def mousePressEvent(self, event):
        """Gestisce il clic del mouse"""
        if event.button() == Qt.LeftButton:
            # Calcola il nuovo valore in base alla posizione X del clic
            new_value = event.x() / self.width()
            self.setValue(new_value)
    
    def mouseMoveEvent(self, event):
        """Gestisce il trascinamento del mouse"""
        if event.buttons() & Qt.LeftButton:
            # Aggiorna il valore durante il trascinamento
            new_value = event.x() / self.width()
            self.setValue(new_value)
    
    def wheelEvent(self, event):
        """Gestisce la rotella del mouse per regolazione fine"""
        # Determina la direzione dello scroll
        delta = event.angleDelta().y()
        
        # Calcola l'incremento (più piccolo per una regolazione fine)
        step = 0.01 if delta > 0 else -0.01
        
        # Aggiorna il valore
        self.setValue(self._value + step)
        
        # Previene la propagazione dell'evento
        event.accept()
    
    def keyPressEvent(self, event):
        """Gestisce gli eventi da tastiera"""
        key = event.key()
        
        if key == Qt.Key_Left or key == Qt.Key_Down:
            # Freccia sinistra/giù: diminuisce il valore
            self.setValue(self._value - 0.01)
            event.accept()
        elif key == Qt.Key_Right or key == Qt.Key_Up:
            # Freccia destra/su: aumenta il valore
            self.setValue(self._value + 0.01)
            event.accept()
        elif key == Qt.Key_Home:
            # Home: imposta al minimo
            self.setValue(0.0)
            event.accept()
        elif key == Qt.Key_End:
            # End: imposta al massimo
            self.setValue(1.0)
            event.accept()
        else:
            # Passa l'evento alla classe base
            super().keyPressEvent(event)