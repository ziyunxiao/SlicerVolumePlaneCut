import os
import unittest
import logging
import vtk
import qt
import ctk
import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
# from PlaneCut.funcs import showVolumeRendering, ShowVolumePlaneCut

#
# planecut
#

# def show_3Dviews():
#     layoutManager = slicer.app.layoutManager()
#     for threeDViewIndex in range(layoutManager.threeDViewCount):
#         view = layoutManager.threeDWidget(threeDViewIndex).threeDView()
#         threeDViewNode = view.mrmlViewNode()
#         cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDViewNode)
#         print("View node for 3D widget " + str(threeDViewIndex))
#         print("  Name: " + threeDViewNode .GetName())
#         print("  ID: " + threeDViewNode .GetID())
#         print("  Camera ID: " + cameraNode.GetID())


# def showVolumeRendering(volumeNode, adjust_preset=False):
#     print("Show volume rendering of node " + volumeNode.GetName())
#     volRenLogic = slicer.modules.volumerendering.logic()
#     displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
#     # disply volume rendering
#     displayNode.SetVisibility(True)

#     # croping
#     # roiNode = displayNode.GetMarkupsROINode()
#     # displayNode.SetCroppingEnabled(True)
#     # roiNode.GetDisplayNode().SetVisibility(True)

#     scalarRange = volumeNode.GetImageData().GetScalarRange()
#     if adjust_preset:
#         if scalarRange[1]-scalarRange[0] < 1500:
#             # Small dynamic range, probably MRI
#             displayNode.GetVolumePropertyNode().Copy(
#                 volRenLogic.GetPresetByName("MR-Default"))
#         else:
#             # Larger dynamic range, probably CT
#             displayNode.GetVolumePropertyNode().Copy(
#                 volRenLogic.GetPresetByName("CT-Chest-Contrast-Enhanced"))


class VolumePlaneWidget(object):

    def __init__(self, volumeNode) -> None:

        self.volumeNode = volumeNode

        self.volume = vtk.vtkVolume()
        self.ren = vtk.vtkRenderer()
        self.ren.AddVolume(self.volume)

        # displayNode = volumeNode.GetDisplayNode()
        volRenLogic = slicer.modules.volumerendering.logic()
        displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
        volumeProperty = displayNode.GetVolumePropertyNode().GetVolumeProperty()
        self.volume.SetProperty(volumeProperty)

        # Define volume mapper
        self.volumeMapper = vtk.vtkSmartVolumeMapper()
        # self.volumeMapper.SetInputData(self.volumeNode.GetImageData())
        self.volumeMapper.SetInputConnection(
            self.volumeNode.GetImageDataConnection())
        self.volume.SetMapper(self.volumeMapper)

    def clipVolumeRender(self, widget, event):
        widget.GetPlane(self.plane)
        self.volumeMapper.AddClippingPlane(self.plane)
        print(f"clipVolumeRender: {event}")

    def ShowVolumePlaneCut(self, renWin):
        # setup pipline
        renWin.AddRenderer(self.ren)

        iren = renWin.GetInteractor()
        # iren = vtk.vtkRenderWindowInteractor()
        # iren.SetRenderWindow(renWin)
        renWin.DebugOn()
        iren.DebugOn()

        # create plane widget
        planeWidget = vtk.vtkImplicitPlaneWidget()
        planeWidget.SetInteractor(iren)
        planeWidget.SetPlaceFactor(1.0)

        self.plane = vtk.vtkPlane()
        center = self.volumeNode.GetImageData().GetCenter()
        self.plane.SetOrigin(center)

        planeWidget.SetInputData(self.volume.GetMapper().GetInput())
        planeWidget.GetSelectedOutlineProperty().SetColor(1, 0, 1)
        planeWidget.GetOutlineProperty().SetColor(0.2, 0.2, 0.2)
        planeWidget.GetOutlineProperty().SetOpacity(0.7)
        planeWidget.SetPlaceFactor(1.0)

        planeprop = planeWidget.GetPlaneProperty()
        planeprop.SetColor(1, 0, 1)
        planeprop.SetOpacity(0.1)
        planeWidget.PlaceWidget()
        planeWidget.On()
        planeWidget.AddObserver("InteractionEvent", self.clipVolumeRender)

        # iren.Initialize()
        renWin.Render()
        # iren.Start()

        return


class PlaneCut(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        # TODO: make this more human readable by adding spaces
        self.parent.title = "PlaneCut"
        # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.categories = ["Utilities"]
        # TODO: add here list of module names that this module requires
        self.parent.dependencies = []
        # TODO: replace with "Firstname Lastname (Organization)"
        self.parent.contributors = ["Li Bin Song(UofA)"]
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an extension to enhance the function of volume rendering. The out of box volume redering function includes function of crop. While this function is fixed on six faces of ROI widget cube.
this extension enable the function to rotate the widget cube in 360 degrees. And this will give the user capability to cut the volume in any direction and any position.
For more details please visit GitHub <a href="https://github.com/ziyunxiao/SlicerVolumePlaneCut">source code</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This project is created with MM802 course at UofA 2022 by Li Bin Song and Antarpuneet Singh with the guidance from Professor Kumaradevan Punithakumar.  
"""

        # Additional initialization step after application startup is complete
        # slicer.app.connect("startupCompleted()", registerSampleData)

#
# PlaneCutWidget
#

class PlaneCutWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        # needed for parameter node observation
        VTKObservationMixin.__init__(self)
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/PlaneCut.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = PlaneCutLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(
            slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene,
                         slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.inputSelector.connect(
            "currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(
            self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass(
                "vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID(
                    "InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(
                self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(
                self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update buttons states and tooltips
        if self._parameterNode.GetNodeReference("InputVolume"):
            self.ui.applyButton.toolTip = "Apply Rotation of Display ROI"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input nodes"
            self.ui.applyButton.enabled = False

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Modify all properties in a single batch
        wasModified = self._parameterNode.StartModify()

        self._parameterNode.SetNodeReferenceID(
            "InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetParameter("LR", str(
            self.ui.SliderWidget_LR.value))
        self._parameterNode.SetParameter("LA", str(
            self.ui.SliderWidget_LA.value))
        self._parameterNode.SetParameter("LS", str(
            self.ui.SliderWidget_LS.value))

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """

        print("onApplyButton is clicked.")
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):
            # custome code RS
            LR = self.ui.SliderWidget_LR.value
            LA = self.ui.SliderWidget_LA.value
            LS = self.ui.SliderWidget_LS.value
            self.logic.process(self.ui.inputSelector.currentNode(),LR, LA, LS)

#
# PlaneCutLogic
#

class PlaneCutLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("LR"):
            parameterNode.SetParameter("LR", "0")
        if not parameterNode.GetParameter("LA"):
            parameterNode.SetParameter("LA", "0")
        if not parameterNode.GetParameter("LS"):
            parameterNode.SetParameter("LS", "0")            

    def process(self, inputVolume, LR, LA, LS):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume for rendering
        """

        if not inputVolume:
            raise ValueError("Input volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        inputID = inputVolume.GetID()
        logging.info(f"Input Volume ID: {inputID}")

        # Retrieve Display ROI Node
        volumeRoi = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLMarkupsROINode")
        if volumeRoi is None:
            raise UnboundLocalError("Display ROI not found. Please run volume rendering fisrt and check Display ROI and enable crop.")

        logging.info(f"Display ROI node: {volumeRoi.GetID()}")
        # volumeRoi.GetCenter()

        # rotate 
        trans = vtk.vtkTransform()
        logging.info(f"RAS value: {(LR, LA, LS)} xyz value: {(-LR,-LA,LS)}")
        trans.RotateX(-LR)
        trans.RotateY(-LA)
        trans.RotateZ(LS)
        # trans.GetMatrix()
        volumeRoi.ApplyTransform(trans)

        stopTime = time.time()
        logging.info(
            f'Processing completed in {stopTime-startTime:.2f} seconds')

#
# PlaneCutTest
#

class PlaneCutTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_PlaneCut1()

    def test_PlaneCut1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        inputVolume = SampleData.downloadSample('CTChest')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        # threshold = 100

        # Test the module logic

        logic = PlaneCutLogic()

        # Test algorithm with non-inverted threshold
        # logic.process(inputVolume, outputVolume, threshold, True)
        # outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        # self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        # self.assertEqual(outputScalarRange[1], threshold)


        self.delayDisplay('Test passed')
