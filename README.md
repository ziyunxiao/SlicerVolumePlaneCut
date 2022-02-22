

# Development tips
## reference objects and method

Test your code in Python console
```py

import slicer

volumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
volumeNode.GetID()

print("Volume size: {0}".format(volumeNode.GetImageData().GetDimensions()))

displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
print(f"Display Node: { displayNode.GetID() }")
roiNode = displayNode.GetMarkupsROINode()
print(f"Display Markup Node: { roiNode.GetID() }")

# croping
displayNode.SetCroppingEnabled(True)
roiNode.GetDisplayNode().SetVisibility(True)



planes = vtk.vtkPlanes()
roiNode.GetPlanes(planes)
roiNode.SetVisibility(False)
n1 = planes.GetNumberOfPlanes()
print(f"Number of Planes {n1}")


```
## Volume rendering

```py

def showVolumeRendering(volumeNode,adjust_preset=False):
  print("Show volume rendering of node " + volumeNode.GetName())
  volRenLogic = slicer.modules.volumerendering.logic()
  displayNode = volRenLogic.CreateDefaultVolumeRenderingNodes(volumeNode)
  displayNode.SetVisibility(True)
  scalarRange = volumeNode.GetImageData().GetScalarRange()
  if adjust_preset:
    if scalarRange[1]-scalarRange[0] < 1500:
        # Small dynamic range, probably MRI
        displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName("MR-Default"))
    else:
        # Larger dynamic range, probably CT
        displayNode.GetVolumePropertyNode().Copy(volRenLogic.GetPresetByName("CT-Chest-Contrast-Enhanced"))


showVolumeRendering(volumeNode)

```



```
slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLSegmentationNode")
```
