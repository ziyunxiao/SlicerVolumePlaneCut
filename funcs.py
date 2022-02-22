import vtk
import slicer

def show_3Dviews():
    layoutManager = slicer.app.layoutManager()
    for threeDViewIndex in range(layoutManager.threeDViewCount) :
        view = layoutManager.threeDWidget(threeDViewIndex).threeDView()
        threeDViewNode = view.mrmlViewNode()
        cameraNode = slicer.modules.cameras.logic().GetViewActiveCameraNode(threeDViewNode)
        print("View node for 3D widget " + str(threeDViewIndex))
        print("  Name: " + threeDViewNode .GetName())
        print("  ID: " + threeDViewNode .GetID())
        print("  Camera ID: " + cameraNode.GetID())

def showVolumeRendering(volumeNode, adjust_preset=False):
    print("Show volume rendering of node " + volumeNode.GetName())
    volRenLogic = slicer.modules.volumerendering.logic()
    displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
    # disply volume rendering
    displayNode.SetVisibility(True)

    # croping
    # roiNode = displayNode.GetMarkupsROINode()
    # displayNode.SetCroppingEnabled(True)
    # roiNode.GetDisplayNode().SetVisibility(True)

    scalarRange = volumeNode.GetImageData().GetScalarRange()
    if adjust_preset:
        if scalarRange[1]-scalarRange[0] < 1500:
            # Small dynamic range, probably MRI
            displayNode.GetVolumePropertyNode().Copy(
                volRenLogic.GetPresetByName("MR-Default"))
        else:
            # Larger dynamic range, probably CT
            displayNode.GetVolumePropertyNode().Copy(
                volRenLogic.GetPresetByName("CT-Chest-Contrast-Enhanced"))


def ShowVolumePlaneCut(volumeData, renWin):
    # Define volume mapper
    volumeMapper = vtk.vtkSmartVolumeMapper()
    # volumeMapper = vtk.vtkVolumeMapper()
    volumeMapper.SetInputData(volumeData)
    # add plane cutter
    planeWidget = vtk.vtkImplicitPlaneWidget()
    # vtk.vtkImplicitPlaneWidget2()
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    planeWidget.SetInteractor(iren)
    planeWidget.SetPlaceFactor(1.0)
    # renderer.AddVolume(volume)
    # interactor.Render()
    plane = vtk.vtkPlane()
    # center = volumeData.GetCenter()
    # plane.SetOrigin(center)

    def clipVolumeRender(obj, event):
        obj.GetPlane(plane)
        volumeMapper.AddClippingPlane(plane)

    # planeWidget.SetInputData(volumeData)
    planeWidget.GetSelectedOutlineProperty().SetColor(1, 0, 1)
    planeWidget.GetOutlineProperty().SetColor(0.2, 0.2, 0.2)
    planeWidget.GetOutlineProperty().SetOpacity(0.7)
    planeWidget.SetPlaceFactor(1.0)
    planeprop = planeWidget.GetPlaneProperty()
    planeprop.SetColor(1, 0, 1)
    planeprop.SetOpacity(0.1)
    planeWidget.PlaceWidget()
    planeWidget.On()
    planeWidget.AddObserver("InteractionEvent", clipVolumeRender)

