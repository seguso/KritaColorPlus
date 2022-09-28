from krita import *

from krita import (
        Krita,)

from PyQt5.QtCore import (
        Qt,
        QEvent,
        QPointF,
        QRect,
        QTimer)

from PyQt5.QtGui import (
        QTransform,
        QPainter,
        QBrush,
        QColor,
        QPolygonF,
        QInputEvent,
        QCursor)

from PyQt5.QtWidgets import (
        QWidget,
        QMdiArea,
        QTextEdit,
        QAbstractScrollArea)


# from PyQt5 import QtWidgets, QtCore, QtGui, uic
import os.path
import time
import datetime
import xml


class rgb:
    def __init__(self, r, g, b, a):
        self.a = a
        self.r = r
        self.g = g
        self.b = b
        
    def print(self, msg):
        print(f"{msg}:   r:{self.r}, g:{self.g}, b:{self.b} ,a:{self.a}")


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
            col.print("cur color")
            if mergedColor is None:
                mergedColor = col
                mergedColor.print("setto merged color")
            else:
                a = float(col.a) / 255.0
                print (f"a = {a}")
                invA = (1.0 - a) 
                print (f"invA = {invA}")
                mergedColor = rgb( mergedColor.r * invA + col.r * a,
                                        mergedColor.g * invA + col.g * a,
                                        mergedColor.b* invA + col.b * a,
                                        255)
                mergedColor.print("merged color")
    return mergedColor
    
def get_q_canvas(q_view):
    scroll_area = q_view.findChild(QAbstractScrollArea)
    viewport = scroll_area.viewport()
    for child in viewport.children():
        cls_name = child.metaObject().className()
        if cls_name.startswith('Kis') and ('Canvas' in cls_name):
            return child


def get_transform(view):
    def _offset(scroller):
        mid = (scroller.minimum() + scroller.maximum()) / 2.0
        return -(scroller.value() - mid)
    canvas = view.canvas()
    document = view.document()
    q_view = get_q_view(view)
    area = q_view.findChild(QAbstractScrollArea)
    zoom = (canvas.zoomLevel() * 72.0) / document.resolution()
    transform = QTransform()
    transform.translate(
            _offset(area.horizontalScrollBar()),
            _offset(area.verticalScrollBar()))
    transform.rotate(canvas.rotation())
    transform.scale(zoom, zoom)
    return transform
    

def get_cursor_in_document_coords():
    app = Krita.instance()
    view = app.activeWindow().activeView()
    if view.document():
        q_view = get_q_view(view)
        q_canvas = get_q_canvas(q_view)    
        transform = get_transform(view)
        transform_inv, _ = transform.inverted()
        global_pos = QCursor.pos()
        local_pos = q_canvas.mapFromGlobal(global_pos)
        center = q_canvas.rect().center()
        return transform_inv.map(local_pos - QPointF(center))


# from PyQt5.QtCore import (
        # Qt,)

# from PyQt5.QtWidgets import (
        # QTextEdit,
        # QTableView)





def listEqual(l1,l2):
   if(len(l1)==len(l2) and len(l1)==sum([1 for i,j in zip(l1,l2) if i==j])):
      return True
   else:
      return False
      
      
class MyExtension(Extension):

    def __init__(self, parent):
        # This is initialising the parent, always important when subclassing.
        super().__init__(parent)
        
        
        print("LastColor init ok")


        
    def setup(self):
        
        
        
        
        self.currentColor = [0,0,0,0]
        self.previousColor = [0,0,0,0]
        self.inited = False
        
        print("LastColor setup ok")
        
        
        
    
    def swap(self):
        try:
            # doc  = Krita.instance().activeWindow().activeView().document()
            # print(doc)
            
            # sel  = doc.selection()
            # print(sel )
            
            # x = sel.x()
            # print(x)
    
            pos = QtGui.QCursor.pos()
            print("cursor absolute = ", pos)

            win = Krita.instance().activeWindow().qwindow().mapFromGlobal(pos);

            print("cursor mapped = ", win)
    
            if not self.inited:
                print ("swap: initializing...")
                
                
                
                
                
                
                
                
                
                app = Krita.instance()
                history_docker = next((d for d in app.dockers() if d.objectName() == 'History'), None)
                kis_undo_view = next((v for v in history_docker.findChildren(QListView) if v.metaObject().className() == 'KisUndoView'), None)
                s_model = kis_undo_view.selectionModel()
                s_model.currentChanged.connect(self._on_history_was_made)
                
                self.inited = True;
                print ("swap: initialized")
            else:
                
                acView = Krita.instance().activeWindow().activeView()

                col = acView.foregroundColor()
                comp = col.components()
                
                
                col.setComponents(self.previousColor)
                acView.setForeGroundColor(col)
                
                self.previousColor = self.currentColor
                    
        except Exception as e:
                print("errore trovato in swap:")
                print(e)
                
                


    
    def _on_history_was_made(self):
        # print ("user painted")
        try:
            
            acView = Krita.instance().activeWindow().activeView()
            if acView is not None: 
                col = acView.foregroundColor()
                if col is not None:   
                    comp = col.components()
                    if listEqual( comp, self.currentColor ):   # user did not change color
                         pass
                    else:  # user changed color
                        print("color changed")
                        self.previousColor = list.copy(self.currentColor) 
                        self.currentColor = list.copy(comp)
                

                
        except:
                print("found error")
                #self.timer_hm.stop()
                raise

    def mixOld(self):
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            view = win.activeView()
            if view is not None:
                document = view.document()
                if document:
                    center = QPointF(0.5 * document.width(), 0.5 * document.height())
                    p = get_cursor_in_document_coords()
                    doc_pos = p + center
                    print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                    
                    self.pixelBytes = document.activeNode().pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                    
                    self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                    self.pixelC = self.imageData.pixelColor(0,0)
                    print(f"color under cursor = {self.pixelC.red()}, {self.pixelC.green()}, {self.pixelC.blue()}")
                    
                    fg = view.foregroundColor()
                    comp = fg.components() 
                    print(f"fg color = {comp}")
     
     
                    canv = 0.45
                    fgMul = 1.0 - canv
                    comp[0] = comp[0] * fgMul + (self.pixelC.red() / 255.0)  * canv
                    comp[1] = comp[1] * fgMul + (self.pixelC.green() / 255.0)  * canv
                    comp[2] = comp[2] * fgMul + (self.pixelC.blue()  / 255.0)  * canv
                  
                    fg.setComponents(comp)
                    
                    view.setForeGroundColor(fg)

        

    def mix(self):
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            view = win.activeView()
            if view is not None:
                document = view.document()
                if document:
                    center = QPointF(0.5 * document.width(), 0.5 * document.height())
                    p = get_cursor_in_document_coords()
                    doc_pos = p + center
                    print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                    
                    
                    parentNode = document.activeNode().parentNode()
                    
                    
                    if parentNode is not None:
                    
                        brothers = parentNode.childNodes()
                        colors = []
                        
                        #costruisco colors
                        for curLayer in brothers:
                        
                            self.pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                            
                            self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                            self.pixelC = self.imageData.pixelColor(0,0)
                            print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha()}")
                            
                            colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() ))
                        
                        #creo il colore composito
                        
                        mergedColor = calcolaCompositeColor(colors);
                                                        
                                

                                
                        # setto il fg color uguale a merged color mischiato con il fg
                        fg = view.foregroundColor()
                        comp = fg.components() 
                        print(f"fg color = {comp}")
         
         
                        
                        canv = 0.45
                        fgMul = 1.0 - canv
                        comp[0] = comp[0] * fgMul + (mergedColor.r / 255.0)  * canv
                        comp[1] = comp[1] * fgMul + (mergedColor.g / 255.0)  * canv
                        comp[2] = comp[2] * fgMul + (mergedColor.b  / 255.0)  * canv
                        
                        # comp[0] =  (mergedColor.r / 255.0)  
                        # comp[1] =  (mergedColor.g / 255.0)
                        # comp[2] = (mergedColor.b  / 255.0)
                      
                        fg.setComponents(comp)
                        
                        view.setForeGroundColor(fg)
                        
                        
                    # self.pixelBytes = document.activeNode().pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                    
                    # self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                    # self.pixelC = self.imageData.pixelColor(0,0)
                    # print(f"color under cursor = {self.pixelC.red()}, {self.pixelC.green()}, {self.pixelC.blue()}")
                    
                    # fg = view.foregroundColor()
                    # comp = fg.components() 
                    # print(f"fg color = {comp}")
     
     
                    # canv = 0.45
                    # fgMul = 1.0 - canv
                    # comp[0] = comp[0] * fgMul + (self.pixelC.red() / 255.0)  * canv
                    # comp[1] = comp[1] * fgMul + (self.pixelC.green() / 255.0)  * canv
                    # comp[2] = comp[2] * fgMul + (self.pixelC.blue()  / 255.0)  * canv
                  
                    # fg.setComponents(comp)
                    
                    # view.setForeGroundColor(fg)

        
    def pickOld(self):
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            view = win.activeView()
            if view is not None:
                document = view.document()
                if document:
                    center = QPointF(0.5 * document.width(), 0.5 * document.height())
                    p = get_cursor_in_document_coords()
                    doc_pos = p + center
                    print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                    
                    self.pixelBytes = document.activeNode().pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                    
                    self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                    self.pixelC = self.imageData.pixelColor(0,0)
                    print(f"color under cursor = {self.pixelC.red()}, {self.pixelC.green()}, {self.pixelC.blue()}")
                    
                    fg = view.foregroundColor()
                    comp = fg.components() 
                    print(f"fg color = {comp}")
     
                    comp[0] =  (self.pixelC.red() / 255.0)  
                    comp[1] =  (self.pixelC.green() / 255.0)
                    comp[2] = (self.pixelC.blue()  / 255.0)
                  
                    fg.setComponents(comp)
                    
                    view.setForeGroundColor(fg)



                                
    def pick(self):
        app = Krita.instance()
        win = app.activeWindow()
        if win is not None:
            view = win.activeView()
            if view is not None:
                document = view.document()
                if document:
                    center = QPointF(0.5 * document.width(), 0.5 * document.height())
                    p = get_cursor_in_document_coords()
                    doc_pos = p + center
                    print(f'cursor at: x={doc_pos.x()}, y={doc_pos.y()}')
                    
                    parentNode = document.activeNode().parentNode()
                    
                    
                    if parentNode is not None:
                    
                        brothers = parentNode.childNodes()
                        colors = []
                        
                        #costruisco colors
                        for curLayer in brothers:
                        
                            self.pixelBytes = curLayer.pixelData(doc_pos.x(), doc_pos.y(), 1, 1)
                            
                            self.imageData = QImage(self.pixelBytes, 1, 1, QImage.Format_RGBA8888)
                            self.pixelC = self.imageData.pixelColor(0,0)
                            print(f"color under cursor =  r:{self.pixelC.red()}, g:{self.pixelC.green()}, b:{self.pixelC.blue()} ,a:{self.pixelC.alpha()}")
                            
                            colors.append(  rgb(self.pixelC.red(),  self.pixelC.green(),  self.pixelC.blue(),  self.pixelC.alpha() ))
                        
                        #creo il colore composito
                        
                        mergedColor = calcolaCompositeColor(colors);
                                                        
                                

                                
                        # setto il fg color uguale a merged color
                        fg = view.foregroundColor()
                        comp = fg.components() 
                        print(f"fg color = {comp}")
         
                        comp[0] =  (mergedColor.r / 255.0)  
                        comp[1] =  (mergedColor.g / 255.0)
                        comp[2] = (mergedColor.b  / 255.0)
                      
                        fg.setComponents(comp)
                        
                        view.setForeGroundColor(fg)

    
    
    def layerMergeAndCreate(self):
        application = Krita.instance()
        currentDoc = application.activeDocument()
        activeLayer = currentDoc.activeNode()
        parentNode = activeLayer.parentNode()
        if parentNode is not None:
            oldOpacity = activeLayer.opacity()
            activeLayer.mergeDown()
            root = currentDoc.rootNode()
            newLa = currentDoc.createNode("temp_layer", "paintLayer")
            newLa.setOpacity(oldOpacity)
            parentNode.addChildNode(newLa, None)
        else:
            newLa = currentDoc.createNode("temp_layer", "paintLayer")
            newLa.setOpacity(160)
            root.addChildNode(newLa, None)
            
        
    
    def createActions(self, window):
    


        action = window.createAction("LastColor", "LastColor")
        action.triggered.connect(self.swap)
        
        action2 = window.createAction("MixColor", "MixColor")
        action2.triggered.connect(self.mix)
        
        action2 = window.createAction("PickColor", "PickColor")
        action2.triggered.connect(self.pick)

        action2 = window.createAction("LayerMergeDownAndNew", "LayerMergeDownAndNew")
        action2.triggered.connect(self.layerMergeAndCreate)

        
# And add the extension to Krita's list of extensions:
Krita.instance().addExtension(MyExtension(Krita.instance()))

