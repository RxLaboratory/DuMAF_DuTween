# -*- coding: utf-8 -*-
"""Duduf Tween Machine"""

import sys
from PySide2.QtWidgets import ( # pylint: disable=no-name-in-module
    QDialog,
    QApplication,
    QSlider,
    QHBoxLayout,
    QDoubleSpinBox,
)
from PySide2.QtCore import ( # pylint: disable=no-name-in-module
    Qt,
    Slot,
    QSignalBlocker,
)
import maya.api.OpenMaya as om # pylint: disable=import-error
import maya.cmds as cmds

vendor = "RxLaboratory"
version = "1.0.0"
debug_mode = True

# <=== GENERAL FUNCTIONS ===>

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

def getMayaWindow():
    app = QApplication.instance() #get the qApp instance if it exists.
    if not app:
        app = QApplication(sys.argv)

    try:
        mayaWin = next(w for w in app.topLevelWidgets() if w.objectName()=='MayaWindow')
        return mayaWin
    except:
        return None

def log( message ):
    """Logs a message to the console"""
    print( "DuTween: " + message )

# <=== TWEEN FUNCTION ===>

def tween( value=0.5, nodes=None, time=None ):
    """Tweens all/selected attributes on the (selected) nodes,
    using the current time by default."""
    # Fix args
    if isinstance(nodes, list) and not nodes:
        nodes = None
    if time is None:
        time = cmds.timeControl("timeControl1", q=True, ra=True)[0]
    # Get nodes
    if nodes is None:
        nodes = cmds.ls(sl=True)
        if not nodes:
            return
    # Get curves from selection
    attributes = cmds.channelBox("mainChannelBox", q=True, sma=True)
    if attributes is not None:
        curves = []
        for attribute in attributes:
            for node in nodes:
                nodeAttr = node + "." + attribute
                if not cmds.objExists(nodeAttr):
                    continue
                curve = cmds.keyframe( nodeAttr, q=True, name=True)
                if curve is None:
                    continue
                curves += curve    
    # get all curves
    else:
        curves = cmds.keyframe(nodes, q=True, name=True)
    # Nothing to do
    if curves is None:
        return
    if len(curves) == 0:
        return
    # Process
    cmds.waitCursor(state=True)

    try:
        for curve in curves:
            tweenCurve( value, curve, time )
    except:
        raise
    finally:
        cmds.waitCursor(state=False)
        # Set focus to Maya
        cmds.currentTime(time)
        mayaWin = getMayaWindow()
        mayaWin.setFocus()

def tweenCurve( value, curve, time ):
    """Tweens the curve"""
    # Get time for next and previous keys...
    previousTime = cmds.findKeyframe(curve, which="previous")
    nextTime = cmds.findKeyframe(curve, which="next")
    # Get previous and next key values
    previousValue = cmds.keyframe(curve, time=(previousTime,), q=True, valueChange=True)[0]
    nextValue = cmds.keyframe(curve, time=(nextTime,), q=True, valueChange=True)[0]
    newValue = previousValue*(1-value) + nextValue*value
    # Create new Keyframe or set attribute value
    cmds.setKeyframe( curve, time=(time,), v=newValue, breakdown=True)
    # snap it
    cmds.snapKey(curve, time=(time,))

# <=== UI ===>

class DuTweenUI( QDialog ):
    def __init__(self, parent=None):
        super(DuTweenUI, self).__init__(parent)
        self.__setupUi()
        self.__connectEvents()
        self.__undoOpened = False

    def __setupUi(self):
        self.setWindowTitle( "DuTween" )
        self.setMinimumWidth(200)

        mainLayout = QHBoxLayout(self)
        mainLayout.setContentsMargins(6,6,6,6)
        mainLayout.setSpacing(3)

        self.slider = QSlider(self)
        self.slider.setOrientation( Qt.Horizontal )
        self.slider.setMaximum(1000)
        self.slider.setMinimum(0)
        self.slider.setSingleStep(10)
        self.slider.setPageStep(100)
        #self.slider.setTickPosition( QSlider.TicksBelow )
        #self.slider.setTickInterval(100)
        self.slider.setValue(500)

        mainLayout.addWidget( self.slider )

        self.spinBox = QDoubleSpinBox(self)
        self.spinBox.setMinimum(0)
        self.spinBox.setMaximum(100.0)
        self.spinBox.setValue(50.0)
        self.spinBox.setSuffix(" %")

        mainLayout.addWidget( self.spinBox )

        mainLayout.setStretch(0, 100)
        mainLayout.setStretch(1, 0)

    def __connectEvents(self):
        self.slider.sliderPressed.connect(self.__beginSlide)
        self.slider.sliderReleased.connect(self.__endSlide)

        self.slider.valueChanged.connect(self.__sliderValueChanged)
        self.spinBox.valueChanged.connect(self.__spinBoxValueChanged)

    @Slot()
    def __sliderValueChanged(self, value):
        b = QSignalBlocker( self.spinBox )
        self.spinBox.setValue( value / 10 )
        self.__beginSlide()
        self.tween()

    @Slot()
    def __spinBoxValueChanged(self, value):
        b = QSignalBlocker( self.slider )
        self.slider.setValue( value * 10 )
        self.__beginSlide()
        self.tween()
        self.__endSlide()

    @Slot()
    def __beginSlide(self):
        if not self.__undoOpened:
            cmds.undoInfo(chunkName="DuTween", openChunk=True)
            self.__undoOpened = True

    @Slot()
    def __endSlide(self):
        if self.__undoOpened:
            cmds.undoInfo(chunkName="DuTween", closeChunk=True)
            self.__undoOpened = False

    @Slot()
    def tween(self):
        value = self.spinBox.value() / 100
        tween(value)

# <=== CMDS CLASSES ===>

class DuTweenCmd( om.MPxCommand ):
    """The dutween Maya command"""
    name = "dutween"

    def __init__(self):
        om.MPxCommand.__init__(self)
        self.ratio = 0.5

    @staticmethod
    def createCommand():
        return DuTweenCmd()

    @staticmethod
    def createSyntax():
        syntax = om.MSyntax()
        syntax.addFlag('-r', "-ratio", om.MSyntax.kDouble )
        return syntax

    def parseArgs(self, args):
        parser = om.MArgParser( self.syntax(), args)
        if parser.isFlagSet( '-r' ):
            self.ratio = parser.flagArgumentDouble('-r', 0)
        else:
            # Show window
            ui = DuTweenUI( getMayaWindow() )
            ui.show()
            return True

    def doIt(self, args):
        try:
            self.run(args)
        except Exception as e:
            if debug_mode:
                raise e
            else:
                print(e)
                log( "Failed!" )

    def run(self, args):
        # Parse arguments
        if self.parseArgs(args):
            return

        # Use args to tween
        #TODO Use list of nodes from args
        cmds.undoInfo(chunkName="DuTween", openChunk=True)
        tween( self.ratio )
        cmds.undoInfo(chunkName="DuTween", closeChunk=True)

cmds_classes = (
    DuTweenCmd,
    )

def initializePlugin( obj ):
    plugin = om.MFnPlugin(obj, vendor, version)

    for c in cmds_classes:
        try:
            plugin.registerCommand( c.name, c.createCommand, c.createSyntax )
        except Exception as e:
            if debug_mode:
                raise e
            else:
                print(e)
                log( "Failed to register command: %s\n" % c.name )

def uninitializePlugin( obj ):
    plugin = om.MFnPlugin(obj, vendor, version)

    for c in reversed( cmds_classes ):
        try:
            plugin.deregisterCommand( c.name )
        except Exception as e:
            if debug_mode:
                raise e
            else:
                print(e)
                log( "Failed to unregister command: %s\n" % c.name )

if __name__ == '__main__':
    # UI
    ui = DuTweenUI( getMayaWindow() )
    ui.show()