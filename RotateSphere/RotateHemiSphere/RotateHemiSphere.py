import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
import qt
import ctk


#
# RotateHemiSphere
#

class RotateHemiSphere(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "RotateHemiSphere"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#RotateHemiSphere">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # RotateHemiSphere1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='RotateHemiSphere',
        sampleName='RotateHemiSphere1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'RotateHemiSphere1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='RotateHemiSphere1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='RotateHemiSphere1'
    )

    # RotateHemiSphere2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='RotateHemiSphere',
        sampleName='RotateHemiSphere2',
        thumbnailFileName=os.path.join(iconsPath, 'RotateHemiSphere2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='RotateHemiSphere2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='RotateHemiSphere2'
    )


#
# RotateHemiSphereWidget
#

class RotateHemiSphereWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = RotateHemiSphereLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).

        # Buttons
        inputsCollapsibleButton = ctk.ctkCollapsibleButton()
        inputsCollapsibleButton.text = "Pan Planning"
        self.layout.addWidget(inputsCollapsibleButton)
        inputsFormLayout = qt.QFormLayout(inputsCollapsibleButton)

        self.center = slicer.qSlicerSimpleMarkupsWidget()
        self.center.objectName = "C"
        self.center.toolTip = "Select a fiducial to use as the ASIS left point."
        self.center.setNodeBaseName("C")
        self.center.defaultNodeColor = qt.QColor("#ff1472")
        self.center.tableWidget().hide()
        self.center.markupsSelectorComboBox().noneEnabled = True
        self.center.markupsPlaceWidget().placeMultipleMarkups = (
            slicer.qSlicerMarkupsPlaceWidget.ForcePlaceSingleMarkup
        )
        self.center.markupsPlaceWidget().buttonsVisible = False
        self.center.markupsPlaceWidget().placeButton().show()
        self.center.setMRMLScene(slicer.mrmlScene)
        inputsFormLayout.addRow("Center:", self.center)
        self.parent.connect(
            "mrmlSceneChanged(vtkMRMLScene*)",
            self.center,
            "setMRMLScene(vtkMRMLScene*)",
        )


        self.displayThresholdSlider = slicer.qMRMLSliderWidget()
        self.displayThresholdSlider.decimals = 2
        self.displayThresholdSlider.minimum = 0
        self.displayThresholdSlider.maximum = 100.0
        self.displayThresholdSlider.singleStep = 1
        self.displayThresholdSlider.toolTip = "Voxels below this vesselness value will be hidden. It does not change the voxel values, only how the vesselness volume is displayed."
        inputsFormLayout.addRow("Radius:", self.displayThresholdSlider)
        self.displayThresholdSlider.connect('valueChanged(double)', self.displayRadius)

        self.StartButton = qt.QPushButton('start')
        self.StartButton.connect("clicked(bool)",self.onInteractiveCupButton)

        self.RemoveButton = qt.QPushButton('remove')
        self.RemoveButton.connect("clicked(bool)",self.onRemoveCupButton)

        self.StartBox = qt.QHBoxLayout()
        self.StartBox.addWidget(self.StartButton)
        self.StartBox.addWidget(self.RemoveButton)
        inputsFormLayout.addRow(self.StartBox)

      #  Create widget

        self.widget = qt.QFrame()
        layout = qt.QFormLayout()
        self.widget.setLayout(layout)
        self.axisSliderWidgets = []
        for i in range(3):
            self.axisSliderWidget = ctk.ctkSliderWidget()
            self.axisSliderWidget.singleStep = 1.0
            self.axisSliderWidget.minimum = -180
            self.axisSliderWidget.maximum = 180
            self.axisSliderWidget.value = 0
            self.axisSliderWidget.tracking = True
            layout.addRow(f"Axis {i+1}: ", self.axisSliderWidget)
            self.axisSliderWidgets.append(self.axisSliderWidget)
            self.axisSliderWidget.connect("valueChanged(double)", self.updateTransformFromWidget)

        self.resetButton = qt.QPushButton("Reset")
        layout.addWidget(self.resetButton)
        self.resetButton.connect("clicked()", self.resetTransform)

        inputsFormLayout.addRow(self.widget)

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
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

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
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

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
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

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

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch
        self._parameterNode.EndModify(wasModified)


    def displayRadius(self):
        radius = self.displayThresholdSlider.value 
        self.logic.CreateSphere(radius)
        
    def interactivePlaneRotation(self):
        model = slicer.util.getNode('model')
        rotatingplane = slicer.util.getNode('MarkupsPlane')
        center = slicer.util.getNode('C')
        rotationTransformNode = slicer.util.getNode('worldToInitialModel')

        model.SetAndObserveTransformNodeID(rotationTransformNode.GetID())
        rotatingplane.SetAndObserveTransformNodeID(rotationTransformNode.GetID())
        center.SetAndObserveTransformNodeID(rotationTransformNode.GetID())

    def onInteractiveCupButton(self):
        leg_side = "right"# if self.ui.radioButton.checked is True else "left"
        self.logic.interactiveCup(leg_side)
        rotationTransformNode = slicer.util.getNode('planeToWorld')
        self.interactivePlaneRotation()

    def onRemoveCupButton(self):
        self.logic.removeCup()

    def newPlane(self):
        model = slicer.util.getNode('model')
        rotatingplane = slicer.util.getNode('MarkupsPlane')
        center = slicer.util.getNode('C')

        transformNode = slicer.util.getNode('planeToWorld')
   #     self.ui.MRMLTransformSliders_3.setMRMLTransformNode(transformNode)
        model.SetAndObserveTransformNodeID(transformNode.GetID())
        rotatingplane.SetAndObserveTransformNodeID(transformNode.GetID())
        center.SetAndObserveTransformNodeID(transformNode.GetID())

        #transformNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLTransformNode')

    def updateTransformFromWidget(self, value):
        transform = vtk.vtkTransform()
        transform.RotateZ(self.axisSliderWidgets[2].value)
        transform.RotateX(self.axisSliderWidgets[0].value)
        transform.RotateY(self.axisSliderWidgets[1].value)

        transformNode = slicer.util.getNode('planeToWorld')
        transformNode.SetMatrixTransformToParent(transform.GetMatrix())

    # def updateWidgetFromTransform(self, caller, event):
    #     transformNode = slicer.util.getNode('planeToWorld')
    #     transformMatrix = transformNode.GetMatrixTransformToParent()
    #     transform = vtk.vtkTransform()
    #     transform.SetMatrix(transformMatrix)
    #     orientation = transform.GetOrientation()
    #     for i in range(1,3):
    #         axisSliderWidget = self.axisSliderWidgets[i]
    #         wasBlocked = axisSliderWidget.blockSignals(True)
    #         axisSliderWidget.value = orientation[i]
    #         axisSliderWidget.blockSignals(wasBlocked)

    def resetTransform(self):
        transformNode = slicer.util.getNode('planeToWorld')
        transformNode.SetMatrixTransformToParent(vtk.vtkMatrix4x4())


#
# RotateHemiSphereLogic
#

class RotateHemiSphereLogic(ScriptedLoadableModuleLogic):
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
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")


    def CreateSphere(self, radius):
        pointListNode = slicer.util.getNode("C")
        pointListNode.GetDisplayNode().SetTextScale(0)

        if slicer.mrmlScene.GetFirstNodeByName("model"):
            slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("model"))
        sphere = vtk.vtkSphereSource()
    

        def UpdateSphere(param1, param2):
            """Update the sphere from the control points
            """
            import math
           # pointListNode = slicer.util.getNode("F")
            centerPointCoord = [0.0, 0.0, 0.0]
            pointListNode.GetNthControlPointPosition(0,centerPointCoord)

            sphere.SetCenter(centerPointCoord)
            sphere.SetRadius(radius)
            sphere.SetPhiResolution(30)
            sphere.SetThetaResolution(30)
            sphere.Update()
            # Get point list node from scene
        UpdateSphere(0,0)

        # Create model node and add to scene
        modelsLogic = slicer.modules.models.logic()
        model = modelsLogic.AddModel(sphere.GetOutput())
        model.SetName("model")
        model.GetDisplayNode().SetSliceIntersectionVisibility(True)
        model.GetDisplayNode().SetSliceIntersectionThickness(3)
        model.GetDisplayNode().SetColor(1,0.75,0)

        # Call UpdateSphere whenever the control points are changed
        pointListNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, UpdateSphere, 2)
        

    def interactiveCup(self, leg_side):
        model = slicer.util.getNode('model')
        line = slicer.mrmlScene.AddNewNodeByClass( 'vtkMRMLMarkupsLineNode', 'L')

        # First point
        pointListNode = slicer.util.getNode("C")
        centerPointCoord = [0.0, 0.0, 0.0]
        pointListNode.GetNthControlPointPosition(0,centerPointCoord)
        pBegin = vtk.vtkVector3d(centerPointCoord)

        # Second point
        pEnd = vtk.vtkVector3d( 100, 0, 0)
        # Add points
        line.AddControlPointWorld(centerPointCoord)

        end = [sum(i) for i in zip(centerPointCoord, [100, 0, 0])] 

        line.AddControlPointWorld(end)

        center = centerPointCoord
        normal = [100, 0, 0]

        # Display best fit plane as a markups plane
        planeNode = slicer.mrmlScene.AddNewNodeByClass('vtkMRMLMarkupsPlaneNode')
        planeNode.SetCenter(center)
        planeNode.SetNormal(normal)
        planeNode.SetName("MarkupsPlane")
        planeNode.GetDisplayNode().SetSelectedColor(0.38, 0.55, 1)
        planeNode.GetDisplayNode().SetTextScale(0)
        planeNode.GetDisplayNode().SetScaleHandleVisibility(0)
           
        hollowModeler = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        hollowModeler.SetToolName("Hollow")
        hollowModeler.SetNodeReferenceID("Hollow.InputModel", model.GetID())
        #hollowedModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")  # this node will store the hollow model
        hollowModeler.SetNodeReferenceID("Hollow.OutputModel", model.GetID())
        hollowModeler.SetAttribute("ShellThickness", "2.5")  # grow outside
        hollowModeler.SetContinuousUpdate(True)  # auto-update output model if input parameters are changed

        #hollowModeler.SetNodeReferenceID("PlaneCut.OutputPositiveModel", PlaneCuttedModelNode.GetID())
        slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(hollowModeler)

        # Set up Plane Cut tool
        PlaneModeler = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLDynamicModelerNode")
        PlaneModeler.SetToolName("Plane cut")
        PlaneModeler.SetNodeReferenceID("PlaneCut.InputModel", model.GetID())
        PlaneModeler.SetNodeReferenceID("PlaneCut.InputPlane", planeNode.GetID())
        PlaneCuttedModelNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode")  # this node will store the hollow model
        PlaneModeler.SetNodeReferenceID("PlaneCut.OutputModel", model.GetID())
        PlaneModeler.SetAttribute("OperationType", "Difference")  # grow outside
        PlaneModeler.SetContinuousUpdate(True)  # auto-update output model if input parameters are changed

        PlaneModeler.SetNodeReferenceID("PlaneCut.OutputPositiveModel", model.GetID())
        slicer.modules.dynamicmodeler.logic().RunDynamicModelerTool(PlaneModeler)

        #pointListNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, UpdateSphere, 2)
        
        PlaneNode = slicer.util.getNode('MarkupsPlane')
    
        planeToWorldTransformNode = slicer.vtkMRMLLinearTransformNode()
        planeToWorldTransformNode.SetName("planeToWorld")
        #planeToWorldTransformNode.SetName(slicer.mrmlScene.GetUniqueNameByString("planeToWorld"))
        slicer.mrmlScene.AddNode(planeToWorldTransformNode)

        # Save the inverse of the initial transform of the plane
        worldToInitialModelTransformNode = slicer.vtkMRMLLinearTransformNode()
        worldToInitialModelTransformNode.SetName("worldToInitialModel")
        #worldToInitialModelTransformNode.SetName(slicer.mrmlScene.GetUniqueNameByString("worldToInitialModel"))
        slicer.mrmlScene.AddNode(worldToInitialModelTransformNode)


        # This markups point list node specifies the center of rotation
 #       rotationAxisMarkupsNode = slicer.util.getNode("L")
        # This transform can be edited in Transforms module (Edit / Rotation / IS slider)
        rotationTransformNode = slicer.util.getNode("planeToWorld")
        # This transform has to be applied to the image, model, etc.
        finalTransformNode = slicer.util.getNode("worldToInitialModel")


        # This markups point list node specifies the center of rotation
        centerOfRotationMarkupsNode = slicer.util.getNode("C")
        # This transform can be  edited in Transforms module
 #       rotationTransformNode = slicer.util.getNode("LinearTransform_3")
        # This transform has to be applied to the image, model, etc.
  #      finalTransformNode = slicer.util.getNode("LinearTransform_4")

        def updateFinalTransform(unusedArg1=None, unusedArg2=None, unusedArg3=None):
            rotationMatrix = vtk.vtkMatrix4x4()
            rotationTransformNode.GetMatrixTransformToParent(rotationMatrix)
            rotationCenterPointCoord = [0.0, 0.0, 0.0]
            centerOfRotationMarkupsNode.GetNthControlPointPositionWorld(0, rotationCenterPointCoord)
            finalTransform = vtk.vtkTransform()
            finalTransform.Translate(rotationCenterPointCoord)
            finalTransform.Concatenate(rotationMatrix)
            finalTransform.Translate(-rotationCenterPointCoord[0], -rotationCenterPointCoord[1], -rotationCenterPointCoord[2])
            finalTransformNode.SetAndObserveMatrixTransformToParent(finalTransform.GetMatrix())

        # Manual initial update
        updateFinalTransform()

        # Automatic update when point is moved or transform is modified
        rotationTransformNodeObserver = rotationTransformNode.AddObserver(slicer.vtkMRMLTransformNode.TransformModifiedEvent, updateFinalTransform)
        centerOfRotationMarkupsNodeObserver = centerOfRotationMarkupsNode.AddObserver(slicer.vtkMRMLMarkupsNode.PointModifiedEvent, updateFinalTransform)


    def removeCup(self):
        slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("F"))
        slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("MarkupsPlane"))
        slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("model"))
       # slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("worldToInitialModelTransformNode"))
        slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("worldToInitialModel"))
        slicer.mrmlScene.RemoveNode(slicer.mrmlScene.GetFirstNodeByName("planeToWorld"))

#
# RotateHemiSphereTest
#

class RotateHemiSphereTest(ScriptedLoadableModuleTest):
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
        self.test_RotateHemiSphere1()
