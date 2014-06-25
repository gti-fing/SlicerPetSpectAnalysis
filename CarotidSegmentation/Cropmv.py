from __main__ import vtk, qt, ctk, slicer
import sys, string

#
# HelloPython
#

class Cropmv:
  def __init__(self, parent):
    parent.title = "Cropmv"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Idk"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Test: A partir de un multivolume extrae las frames y las recorta, ademas despliega
    """
    parent.acknowledgementText = """
    idk""" # replace with organization, grant and thanks.
    self.parent = parent


#
# qHelloPythonWidget

class CropmvWidget:
  def __init__(self, parent = None):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout(qt.QVBoxLayout())
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
      self.setup()
      self.parent.show()

  def setup(self):
    # Instantiate and connect widgets ...

    #PARCHEE"
    w = qt.QWidget()
    layout = qt.QGridLayout()
    w.setLayout(layout)
    self.layout.addWidget(w)
    w.show()
    self.layout = layout

    # INPUT MENU
    self.inputFrame = ctk.ctkCollapsibleButton()
    self.inputFrame.text = "Input"
    self.inputFrame.collapsed = 0
    inputFrameLayout = qt.QFormLayout(self.inputFrame)
    self.layout.addWidget(self.inputFrame)
    
    #Nodo del multivolume
    self.__mvNode = None
    
    #Entrada multivolume
    label = qt.QLabel('Input multivolume')
    self.mvSelector = slicer.qMRMLNodeComboBox()
    self.mvSelector.nodeTypes = ['vtkMRMLMultiVolumeNode']
    self.mvSelector.setMRMLScene(slicer.mrmlScene)
    self.mvSelector.addEnabled = 0
    self.mvSelector.noneEnabled = 1
    inputFrameLayout.addRow(label, self.mvSelector)

    #Entrada ROI
    label = qt.QLabel('Input ROI')
    self.RoiSelector = slicer.qMRMLNodeComboBox()
    self.RoiSelector.nodeTypes = ["vtkMRMLAnnotationROINode"]
    self.RoiSelector.setMRMLScene(slicer.mrmlScene)
    self.RoiSelector.addEnabled = 0
    self.RoiSelector.noneEnabled = 1
    inputFrameLayout.addRow(label, self.RoiSelector)
    
    #Entrada frame a mostrar
    label = qt.QLabel('Frame a mostrar')
    self.__veInitial = qt.QDoubleSpinBox()
    self.__veInitial.value = 0
    inputFrameLayout.addRow(label, self.__veInitial)
    
    
    ###PARTE HELLO WORLD## BUTTON DE ACTIVACION
         
    # Collapsible button
    sampleCollapsibleButton = ctk.ctkCollapsibleButton()
    sampleCollapsibleButton.text = "A collapsible button"
    self.layout.addWidget(sampleCollapsibleButton)
    
    # Collapsible button 2
    sampleCollapsibleButton2 = ctk.ctkCollapsibleButton()
    sampleCollapsibleButton2.text = "A collapsible button2"
    self.layout.addWidget(sampleCollapsibleButton2)

    # Layout within the sample collapsible button
    sampleFormLayout = qt.QFormLayout(sampleCollapsibleButton)
    helloWorldButton2 = qt.QPushButton("Ver 1 Frame para ROI")
    helloWorldButton2.toolTip="Ver un frame para ROI."
    sampleFormLayout.addWidget(helloWorldButton2)
    helloWorldButton2.connect('clicked(bool)',self.onHelloWorldButtonClicked2)

    # Set local var as instance attribute
    self.helloWorldButton2 = helloWorldButton2


    # Layout within the sample collapsible button
    sampleFormLayout = qt.QFormLayout(sampleCollapsibleButton2)
    helloWorldButton = qt.QPushButton("Hello World")
    helloWorldButton.toolTip="Print 'Hello World' in standard output."
    sampleFormLayout.addWidget(helloWorldButton)
    helloWorldButton.connect('clicked(bool)',self.onHelloWorldButtonClicked)

    # Set local var as instance attribute
    self.helloWorldButton = helloWorldButton

  def onHelloWorldButtonClicked(self):
    print "Hello World !"
    
    #multivolume y roi volume de referencia#
    self.__mvNode = self.mvSelector.currentNode()
    roi=self.RoiSelector.currentNode()
    
    #SCALAR VOLUME DE REFERENCIA
    frameVolume = slicer.vtkMRMLScalarVolumeNode()
    frameVolume.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(frameVolume)
        
    nComponents = self.__mvNode.GetNumberOfFrames()
    f=int(self.__veInitial.value)
    frameId = min(f,nComponents-1)
    
    ras2ijk = vtk.vtkMatrix4x4()
    ijk2ras = vtk.vtkMatrix4x4()
    self.__mvNode.GetRASToIJKMatrix(ras2ijk)
    self.__mvNode.GetIJKToRASMatrix(ijk2ras)
    frameImage = frameVolume.GetImageData()
    if frameImage == None:
        frameVolume.SetRASToIJKMatrix(ras2ijk)
        frameVolume.SetIJKToRASMatrix(ijk2ras)
    
    mvImage = self.__mvNode.GetImageData()
    dictCrop = {}
    #Medias de la ROI para cada frame#
    CropMean = {}
    for i in range(nComponents-1):
      extract = vtk.vtkImageExtractComponents()
      extract.SetInput(mvImage)
      extract.SetComponents(i)
      extract.Update()
      frameVolume.SetAndObserveImageData(extract.GetOutput())
      #DEBO TENER EL NODO DE INPUT EN LA ESCENA PARA PODER USAR EL CROP#
      frameName = 'Frame'
      frameVolume.SetName(frameName)
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      selectionNode.SetReferenceActiveVolumeID(frameVolume.GetID())
      slicer.app.applicationLogic().PropagateVolumeSelection(0)
      #CROP#    
      mainWindow = slicer.util.mainWindow()
      mainWindow.moduleSelector().selectModule('CropVolume')
      #Parametros del crop#
      cropVolumeNode = slicer.vtkMRMLCropVolumeParametersNode()
      cropVolumeNode.SetScene(slicer.mrmlScene)
      cropVolumeNode.SetName('CropVolumeNode')
      cropVolumeNode.SetVoxelBased(True)
      slicer.mrmlScene.AddNode(cropVolumeNode)
      cropVolumeNode.SetInputVolumeNodeID(frameVolume.GetID())
      cropVolumeNode.SetROINodeID(roi.GetID())
      cropVolumeLogic = slicer.modules.cropvolume.logic()
      cropVolumeLogic.Apply(cropVolumeNode)
      output = slicer.mrmlScene.GetNodeByID(cropVolumeNode.GetOutputVolumeNodeID())
      NameOut="crop_f"+str(i)
      output.SetName(NameOut)
      #Agrego la frame al diccionario#
      dictCrop.update({i:output})
      Data=slicer.util.array(output.GetID())
      CropMean.update({i:Data.mean()})

  def onHelloWorldButtonClicked2(self):
    print "Ver un frame para marcar ROI"
    
    self.__mvNode = self.mvSelector.currentNode()
    
    #SCALAR VOLUME DE REFERENCIA
    frameVolume = slicer.vtkMRMLScalarVolumeNode()
    frameVolume.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(frameVolume)
        
    nComponents = self.__mvNode.GetNumberOfFrames()
    f=int(self.__veInitial.value)
    frameId = min(f,nComponents-1)
    
    ras2ijk = vtk.vtkMatrix4x4()
    ijk2ras = vtk.vtkMatrix4x4()
    self.__mvNode.GetRASToIJKMatrix(ras2ijk)
    self.__mvNode.GetIJKToRASMatrix(ijk2ras)
    frameVolume.SetRASToIJKMatrix(ras2ijk)
    frameVolume.SetIJKToRASMatrix(ijk2ras)
    
    mvImage = self.__mvNode.GetImageData()
    extract = vtk.vtkImageExtractComponents()
    extract.SetInput(mvImage)
    extract.SetComponents(frameId)
    extract.Update()
    frameVolume.SetAndObserveImageData(extract.GetOutput())
    #DEBO TENER EL NODO DE INPUT EN LA ESCENA PARA PODER USAR EL CROP#
    frameName = 'Frame_ref'+str(frameId)
    frameVolume.SetName(frameName)
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(frameVolume.GetID())
    slicer.app.applicationLogic().PropagateVolumeSelection(0)
