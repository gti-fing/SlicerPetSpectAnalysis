from __main__ import vtk, qt, ctk, slicer
import sys, string

#
# HelloPython
#

class TestPy1:
  def __init__(self, parent):
    parent.title = "Test1"
    parent.categories = ["Examples"]
    parent.dependencies = []
    parent.contributors = ["Idk"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Test: A partir de un multivolume extrae la frame seleccionada, no necesita scalar volume de referencia/
    hello button activa la extraccion.
    """
    parent.acknowledgementText = """
    idk""" # replace with organization, grant and thanks.
    self.parent = parent

#
# qHelloPythonWidget
#

class TestPy1Widget:
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
    
    #Descubriendo que seria esto#
    self.__mvNode = None
    
    #Entrada multivolume
    label = qt.QLabel('Input multivolume')
    self.mvSelector = slicer.qMRMLNodeComboBox()
    self.mvSelector.nodeTypes = ['vtkMRMLMultiVolumeNode']
    self.mvSelector.setMRMLScene(slicer.mrmlScene)
    self.mvSelector.addEnabled = 0
    self.mvSelector.noneEnabled = 1
    inputFrameLayout.addRow(label, self.mvSelector)
    
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

    # Layout within the sample collapsible button
    sampleFormLayout = qt.QFormLayout(sampleCollapsibleButton)
    helloWorldButton = qt.QPushButton("Hello World")
    helloWorldButton.toolTip="Print 'Hello World' in standard output."
    sampleFormLayout.addWidget(helloWorldButton)
    helloWorldButton.connect('clicked(bool)',self.onHelloWorldButtonClicked)

    # Set local var as instance attribute
    self.helloWorldButton = helloWorldButton

  def onHelloWorldButtonClicked(self):
    print "Hello World !"
    
    #frame volume sera el scalar volume de referencia#
    self.__mvNode = self.mvSelector.currentNode()
    
    #NODO REFERENCIA
    frameVolume = slicer.vtkMRMLScalarVolumeNode()
    frameVolume.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(frameVolume)
    
    
    nComponents = self.__mvNode.GetNumberOfFrames()
    #frameId = 6
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
    extract = vtk.vtkImageExtractComponents()
    extract.SetInput(mvImage)
    extract.SetComponents(frameId)
    extract.Update()
    
    frameName = 'Holaaa'
    frameVolume.SetName(frameName)
    
    frameVolume.SetAndObserveImageData(extract.GetOutput())
    displayNode = frameVolume.GetDisplayNode()
    
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(frameVolume.GetID())
    slicer.app.applicationLogic().PropagateVolumeSelection(0)
