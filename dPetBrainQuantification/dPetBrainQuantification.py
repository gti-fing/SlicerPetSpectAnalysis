import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import sys, string, numpy
import SimpleITK

class dPetBrainQuantification:
  def __init__(self, parent):
    parent.title = "dPetBrainQuantification"
    parent.categories = ["Quantification"]
    parent.dependencies = []
    parent.contributors = ["Idk"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    Test: A partir de un multivolume extrae las frames y las recorta, ademas despliega
    """
    parent.acknowledgementText = """
    idk""" # replace with organization, grant and thanks.
    self.parent = parent
    
class dPetBrainQuantificationWidget:
  def __init__( self, parent=None ):
    if not parent:
      self.parent = slicer.qMRMLWidget()
      self.parent.setLayout( qt.QVBoxLayout() )
      self.parent.setMRMLScene(slicer.mrmlScene)
    else:
      self.parent = parent
    self.layout = self.parent.layout()
    if not parent:
        self.setup()
        self.parent.show()
      
    #
    # Multivolume Node
    #
    self.mvNode = None
    #venous samples
    self.VenousSamplepTAC=[]
    self.VenousSampleTime=[]
    #Segmentation parameters
    self.CarSegmParameters  = None
    self.pTACestParameters = None
    self.CarSegmType = 0
    self.pTACEstType = 0
    #Last Logic
    self.lastLogic = None
    #Plot Mean curves
    self.lns = None
    self.cvns = None
    self.cn = None

  def setup (self) :    
    self.lastLogic=dPetBrainQuantificationLogic()
    #self.parent.connect('mrmlSceneChanged(vtkMRMLScene*)', self.onVCMRMLSceneChanged)
    
    #
    # Input Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "PET dynamic Study and Information"
    parametersCollapsibleButton.collapsed = 0
    self.layout.addWidget(parametersCollapsibleButton)
  
    # Layout input parameters within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # Visualization Area
    #
    VisualizationCollapsibleButton = ctk.ctkCollapsibleButton()
    VisualizationCollapsibleButton.text = "Visualization Options"
    VisualizationCollapsibleButton.collapsed = 0
    self.layout.addWidget(VisualizationCollapsibleButton)

    # Layout visualization within the dummy collapsible button
    VisualizationFormLayout = qt.QFormLayout(VisualizationCollapsibleButton)
    
    #
    # K-Map Estimation Widget area
    #
    self.KMapCollapsibleButton = ctk.ctkCollapsibleButton()
    self.KMapCollapsibleButton.text = "K-Map Estimation options"
    self.KMapCollapsibleButton.collapsed = 1
    self.layout.addWidget(self.KMapCollapsibleButton)
     # Layout visualization within the K-Map collapsible button
    self.KMapFormLayout = qt.QFormLayout(self.KMapCollapsibleButton)

    #
    # pTAC estimation Area
    #
    pTACestimationCollapsibleButton = ctk.ctkCollapsibleButton()
    pTACestimationCollapsibleButton.text = "pTAC estimation Options"
    pTACestimationCollapsibleButton.collapsed = 1
    self.layout.addWidget(pTACestimationCollapsibleButton)

    # Layout visualization within the dummy collapsible button
    pTACestimationFormLayout = qt.QFormLayout(pTACestimationCollapsibleButton)
    
    #
    # Carotid Segmentation Area
    #
    CarSegmentationCollapsibleButton = ctk.ctkCollapsibleButton()
    CarSegmentationCollapsibleButton.text = "Carotid Segmentation Options"
    CarSegmentationCollapsibleButton.collapsed = 1
    self.layout.addWidget(CarSegmentationCollapsibleButton)

    # Layout visualization within the dummy collapsible button
    CarSegmentationFormLayout = qt.QFormLayout(CarSegmentationCollapsibleButton)

    #
    # Input items
    #
    
    # DICOM study import Option
    label = qt.QLabel('Import DICOM Study : ')
    DICOMbrowser = qt.QPushButton("DICOM Browser")
    DICOMbrowser.toolTip="Opens the DICOM browser to import the study"
    DICOMbrowser.connect('clicked(bool)',self.onDICOMbrowser)
    parametersFormLayout.addRow(label,DICOMbrowser)
    
    # Nifti + Sif import directory
    label = qt.QLabel('Nifti + SIF input directory')
    self.DirSelector = ctk.ctkDirectoryButton()
    self.DirSelector.caption = 'Nifti + Sif input directory'
    self.DirSelector.directoryChanged.connect(self.onNiftiParser)
    parametersFormLayout.addRow(label,self.DirSelector)
    
    ##Nifti + sif study import Option
    #self.NiftiParser = qt.QPushButton("Import Nifti + SIF dinamic PET")
    #self.NiftiParser.toolTip="Parses the .Nifti files in the directory and loads frame data from .SIF"
    #self.NiftiParser.connect('clicked(bool)',self.onNiftiParser)
    #parametersFormLayout.addWidget(self.NiftiParser)
    
   # Multivolume input volume selector
    label = qt.QLabel('Input multivolume')
    self.mvSelector = slicer.qMRMLNodeComboBox()
    self.mvSelector.nodeTypes = ['vtkMRMLMultiVolumeNode']
    self.mvSelector.setMRMLScene(slicer.mrmlScene)
    self.mvSelector.connect('currentNodeChanged(vtkMRMLNode*)', self.onInputChanged)
    self.mvSelector.addEnabled = 0
    parametersFormLayout.addRow(label, self.mvSelector)
    
    #
    # Visualization items
    #
    
    # Frame selector
    label = qt.QLabel('Display frame selector')
    self.frameSlider = ctk.ctkSliderWidget()
    self.frameSlider.connect('valueChanged(double)', self.onSliderChanged)
    VisualizationFormLayout.addRow(label, self.frameSlider)
    
    # Brain Mask display Button
    DisplayBrainMaskButton = qt.QPushButton("Display Brain Mask")
    DisplayBrainMaskButton.toolTip="Displays the Brain Mask Calculated"
    DisplayBrainMaskButton.connect('clicked(bool)',self.onDisplayBrainMask)
    VisualizationFormLayout.addWidget(DisplayBrainMaskButton)
    
    #
    # Carotid Segmentation items
    #
    
    # type of segmentation selector
    self.CarotidSegmTypeSelector = qt.QComboBox()
    CarSegmentationFormLayout.addRow("Type:", self.CarotidSegmTypeSelector)
    #CarSegmentationFormLayout.addWidget(self.CarotidSegmTypeSelector,0,0)
    self.CarotidSegmTypeSelector.addItem('Automatic Carotid segmentation', 0)
    self.CarotidSegmTypeSelector.addItem('Segmentation with manual ROI over Carotids', 1)
    
    #Parameters 
    CarSegmParameters = ctk.ctkCollapsibleButton()
    CarSegmParameters.text = "Parameters of the selected segmentation"
    CarSegmParameters.collapsed = 1
    CarSegmentationFormLayout.addWidget(CarSegmParameters)
    CarSegmParametersLayout = qt.QFormLayout(CarSegmParameters)
    
    self.CarSegmParameters = ParametersWidget(CarSegmParameters)
    
    # Initlial Selection
    self.CarotidSegmTypeSelector.connect('currentIndexChanged(int)', self.onCarotidSegmSelector)

    #Output scalar volume Node
    label = qt.QLabel('Output volume')
    self.csvSelector = slicer.qMRMLNodeComboBox()
    self.csvSelector.nodeTypes = ['vtkMRMLScalarVolumeNode']
    self.csvSelector.setMRMLScene(slicer.mrmlScene)
    self.csvSelector.addEnabled = True
    CarSegmentationFormLayout.addRow(label, self.csvSelector)
    
    #display Segmentation button
    DisplaySegmentation = qt.QPushButton("Display Carotid Segmentation")
    DisplaySegmentation.toolTip="Displays the carotid segmentation selected"
    DisplaySegmentation.connect('clicked(bool)',self.onDisplaySegmentation)
    CarSegmentationFormLayout.addWidget(DisplaySegmentation)

    #
    # pTAC estimation items
    #
    
    # pTAC  selector
    self.pTACSelector = qt.QComboBox()
    pTACestimationFormLayout.addRow("Type:", self.pTACSelector)
    #CarSegmentationFormLayout.addWidget(self.CarotidSegmTypeSelector,0,0)
    self.pTACSelector.addItem('IDIF pTAC estimation', 0)
    self.pTACSelector.addItem('PBIF Hunter pTAC estimation with venous samples', 1)

    #Parameters 
    pTACestParameters = ctk.ctkCollapsibleButton()
    pTACestParameters.text = "Parameters of the selected pTAC estimation"
    pTACestParameters.collapsed = 1
    pTACestimationFormLayout.addWidget(pTACestParameters)
    pTACestParametersLayout = qt.QFormLayout(pTACestParameters)
    
    self.pTACestParameters = ParametersWidget(pTACestParameters)
    
    # Initlial Selection
    self.pTACSelector.connect('currentIndexChanged(int)', self.onpTACestSelector)
    
    #display Segmentation button
    getpTAC = qt.QPushButton("get pTAC estimation")
    getpTAC.toolTip="get pTAC estimation selected"
    getpTAC.connect('clicked(bool)',self.onGetpTAC)
    pTACestimationFormLayout.addWidget(getpTAC)
            
    #
    #Input samples button for pTAC estimation
    #
    self.ImportVenousSampleButton=qt.QPushButton("Import acquired blood samples")
    self.ImportVenousSampleButton.toolTip="Loads the selected samples from a .CSV file"
    self.ImportVenousSampleButton.connect('clicked(bool)',self.onImportVenousSampleButtonClicked)
    parametersFormLayout.addWidget(self.ImportVenousSampleButton)
    
    self.ImportVenousSampleFile = qt.QFileDialog()
    self.ImportVenousSampleFile.setNameFilter("CSV (*.csv)")
    self.ImportVenousSampleFile.fileSelected.connect(self.onImportVenousSampleFileChanged)
#
    #K-Map Options area
    #K-Map Ptac input options
    label = qt.QLabel('pTAC input options')
    self.KMapPtacOptionsBox = qt.QComboBox()
    self.KMapPtacOptionsBox.addItem('Automatic pTAC extraction', 0)
    self.KMapPtacOptionsBox.addItem('Load pTAC estimation from .csv', 1)
    self.KMapFormLayout.addRow(label,self.KMapPtacOptionsBox)

    #K-Map input pTAC collapsible button parameters
    KMapPtacParameters = ctk.ctkCollapsibleButton()
    KMapPtacParameters.text = "Parameters of the selected pTAC input"
    KMapPtacParameters.collapsed = 1
    self.KMapFormLayout.addWidget(KMapPtacParameters)
    KMapPtacParametersLayout = qt.QFormLayout(KMapPtacParameters)
    
    self.KMapPtacParametersWidget=ParametersWidget(KMapPtacParameters)
    self.KMapPtacParametersWidget.CreateKMpTACParameters(0)
    self.KMapPtacOptionsBox.currentIndexChanged.connect(self.onKMapPtacOptionsChanged)
    
    #K-Map Region selection input options
    label = qt.QLabel('Region of interest input options')
    self.KMapMaskOptionsBox = qt.QComboBox()
    self.KMapMaskOptionsBox.addItem('Automatic Mask generation', 0)
    self.KMapMaskOptionsBox.addItem('Input Labelmap', 1)
    self.KMapMaskOptionsBox.addItem('Input ROI', 2)
    self.KMapFormLayout.addRow(label,self.KMapMaskOptionsBox)
    #K-Map input Mask collapsible button parameters
    KMapMaskParameters = ctk.ctkCollapsibleButton()
    KMapMaskParameters.text = "Parameters of the selected Mask input"
    KMapMaskParameters.collapsed = 1
    self.KMapFormLayout.addWidget(KMapMaskParameters)
    KMapMaskParametersLayout = qt.QFormLayout(KMapMaskParameters)
    
    self.KMapMaskParametersWidget=ParametersWidget(KMapMaskParameters)
    self.KMapMaskParametersWidget.CreateKMapParameters(0)
    self.KMapMaskOptionsBox.currentIndexChanged.connect(self.onKMapMaskOptionsChanged)
    
    #
    # Apply KMap Estimation button
    #
    self.ApplyKMap = qt.QPushButton("Apply selected K-Map estimation")
    self.ApplyKMap.toolTip="Applies the selected K-Map estimation"
    self.ApplyKMap.connect('clicked(bool)',self.onApplyKmap)
    self.KMapFormLayout.addWidget(self.ApplyKMap)
    
    #
    # pTAC estimation csv file output
    #
    self.pTACcsvOutputFileDialog = qt.QFileDialog()
    self.pTACcsvOutputFileDialog.setNameFilter("CSV (*.csv)")
    self.pTACcsvOutputFileDialog.setDefaultSuffix('csv')
    self.pTACcsvOutputFileDialog.fileSelected.connect(self.onpTACcsvOutputFileChanged)
    
    #
    # pTAC estimation csv file Button
    #
    label=qt.QLabel('Output CSV file')
    self.pTACcsvOutputFileButton=qt.QPushButton("Write estimated pTAC to .csv file")
    self.pTACcsvOutputFileButton.toolTip="Opens a file dialog window to output CSV pTAC file"
    self.pTACcsvOutputFileButton.connect('clicked(bool)',self.onpTACcsvOutputFileButtonClicked)
    pTACestimationFormLayout.addRow(label,self.pTACcsvOutputFileButton)
    
    #Apply All
    self.ApplyKMap_all = qt.QPushButton("Apply selected K-Map estimation")
    self.ApplyKMap_all.toolTip="Applies the selected K-Map estimation"
    self.ApplyKMap_all.enabled = True
    self.layout.addWidget(self.ApplyKMap_all)
    # connections
    self.ApplyKMap_all.connect('clicked(bool)', self.onApplyKmap)
    # Add vertical spacer
    self.layout.addStretch(1)

  def onImportVenousSampleButtonClicked(self):
    self.ImportVenousSampleFile.show()
      
  def onImportVenousSampleFileChanged(self,filename):
    print filename
    t,pTAC =self.lastLogic.readCSVsamples(filename)
    self.VenousSamplepTAC=pTAC
    self.VenousSampleTime=t
    print pTAC
    print t
        
  def onInputChanged(self):
    self.mvNode = self.mvSelector.currentNode()
    print('Entro a funcion')
    if self.mvNode != None:
      Helper.SetBgFgVolumes(self.mvNode.GetID(), None)
      nFrames = self.mvNode.GetNumberOfFrames()
      self.frameSlider.minimum = 0
      self.frameSlider.maximum = nFrames-1
      print ('Se reconocio cambio y se selecciono ',self.frameSlider.maximum)
      self.lastLogic.loadData(self.mvNode)
      self.onSliderChanged()
      self.onCarotidSegmSelector()
      self.onpTACestSelector()
  
  def onSliderChanged(self):
    nframe = int(self.frameSlider.value)
    if self.mvNode != None :
        mvDisplay = self.mvNode.GetDisplayNode()
        mvDisplay.SetFrameComponent(nframe)
    else:
        return
          

  def onVCMRMLSceneChanged(self, mrmlScene):
    self.mvSelector.setMRMLScene(slicer.mrmlScene)
    self.onInputChanged()
    self.onSliderChanged()
    self.onCarotidSegmSelector()
    self.onpTACestSelector()
         
  def onDICOMbrowser(self):
    DICOMWidget().enter()
          
  def onDisplayBrainMask(self):
    if self.lastLogic.BrainMask == None :
        return
    BrainMaskVolume = self.lastLogic.getBrainMaskVolume()
    BrainMaskVolume.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(BrainMaskVolume)
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(BrainMaskVolume.GetID())
    slicer.app.applicationLogic().PropagateVolumeSelection(0)
          
  def onCarotidSegmSelector(self):
    self.CarSegmParameters.CSdestroy()
    index = self.CarotidSegmTypeSelector.currentIndex
    if index < 0:
            return
    self.CarSegmParameters.CreateCSParameters(index)
    #self.CarSegmParameters.pTACwidgets[1].connect('stateChanged(int)', self.onBoxStateChangeRequested(self.CarSegmParameters.pTACwidgets[1]))
    if self.mvNode != None :
        Helper.SetBgFgVolumes(self.mvNode.GetID(), None)
        nFrames = self.mvNode.GetNumberOfFrames()
        self.CarSegmParameters.CSwidgets[-1].setChecked(1)
        self.CarSegmParameters.CSwidgets[-5].maximum = nFrames-1
    self.CarSegmType = index
          
  def onDisplaySegmentation(self):
    index = self.CarotidSegmTypeSelector.currentIndex
    if index == 0:
            roi = None
            print(index,' ',roi)
    if index == 1:
            roi = self.CarSegmParameters.CSwidgets[1].currentNode()
            print(index,' ',roi)
    #self.lastLogic = dPetBrainQuantificationLogic()
    
    connectivityfilter = self.CarSegmParameters.CSwidgets[-3].isChecked()
    FrameForSegm = None
    if self.CarSegmParameters.CSwidgets[-6].isChecked() :
        FrameForSegm = self.CarSegmParameters.CSwidgets[-5].value
        FrameForSegm = int(FrameForSegm)
        
    CarotidMask = self.lastLogic.applyCarotidSegmentation(self.mvNode,roi,connectivityfilter,FrameForSegm)
    CarotidMask .SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(CarotidMask)
    self.csvSelector.setCurrentNode(CarotidMask)
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID(CarotidMask.GetID())
    slicer.app.applicationLogic().PropagateVolumeSelection(0)
    
    if self.CarSegmParameters.CSwidgets[-1].isChecked() :
            mCar = self.lastLogic.mCar
            mTis = self.lastLogic.mTis
            frameTime = self.lastLogic.frameTime
            self.lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
            self.cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
            self.cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
            self.lastLogic.iniChart('mean of Tissue and carotid regions','time','value',self.lns,self.cvns,self.cn)
            self.lastLogic.addChart(frameTime,mTis,'Mean Tissue region Carotid segm',self.cn,self.cvns)
            self.lastLogic.addChart(frameTime,mCar,'Mean Carotid region Carotid segm',self.cn,self.cvns)

  def onpTACestSelector(self) :
    index = self.pTACSelector.currentIndex
    self.pTACestParameters.pTACdestroy()
    if index < 0:
            return
        
    self.pTACestParameters.CreatepTACParameters(index)
    #Caso IDIF
    if (self.lastLogic != None) & (index == 0) :
            self.pTACestParameters.pTACwidgets[1].setChecked(1)
            if (self.VenousSamplepTAC != []) & (self.VenousSampleTime != []) :
                self.pTACestParameters.pTACwidgets[3].setChecked(1)
                
    self.pTACEstType = index

  def onGetpTAC(self) :
    index = self.pTACSelector.currentIndex
    if index < 0:
        return          
    #caso IDIF
    if (index == 0) :
        if (self.lastLogic == None) | (not(self.pTACestParameters.pTACwidgets[1].isChecked())) :
            self.onDisplaySegmentation()
                  
        HunterTailfit = self.pTACestParameters.pTACwidgets[5].isChecked()
        #without venous samples
        if not(self.pTACestParameters.pTACwidgets[3].isChecked()) :
            frameTime, pTAC, hotvox= self.lastLogic.pTACestimationIDIF(None,None,HunterTailfit)
            #with venous samples
        if (self.pTACestParameters.pTACwidgets[3].isChecked()) :
            if (self.VenousSamplepTAC == []) | (self.VenousSampleTime == []) :
                print('A venous sample file was not load')
                return
            frameTime, pTAC,hotvox = self.lastLogic.pTACestimationIDIF(self.VenousSampleTime,self.VenousSamplepTAC,HunterTailfit)
                  
    if (index == 1) :
        if (self.VenousSamplepTAC == []) | (self.VenousSampleTime == []) :
            print('A venous sample file was not load')
            return
        Dosage = self.pTACestParameters.pTACwidgets[1].value
        print('dosage' , Dosage)
        LeanWeight = self.pTACestParameters.pTACwidgets[3].value
        print('LeanWeight' , LeanWeight)
        frameTime, pTAC = self.lastLogic.PBIFhunter(Dosage, LeanWeight, self.VenousSamplepTAC,self.VenousSampleTime)
                  
                           
    if self.pTACestParameters.pTACwidgets[-1].isChecked() :
        self.lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
        self.cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
        self.cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
        self.lastLogic.iniChart('estimated pTAC','time','value',self.lns,self.cvns,self.cn)
        self.lastLogic.addChart(frameTime,pTAC,'estimated pTAC',self.cn,self.cvns)
        if index == 0 :
            self.lastLogic.addChart(frameTime,hotvox,'hot voxels',self.cn,self.cvns)
          
    if self.pTACestParameters.pTACwidgets[-3].isChecked():
        print('saving pTAC estimated in .csv')
        self.lastLogic.writeCSVsamples(self.outputcsvDir, self.lastLogic.frameTime, self.lastLogic.pTAC_est)
          
  def onNiftiParser(self):
    #create new multivolume node
    mvNode=slicer.vtkMRMLMultiVolumeNode()
    mvNode.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(mvNode)
    self.lastLogic.NiftiParser(self.DirSelector.directory,mvNode)
    #auto set the new node as the input volume and add it into the scene
    self.mvSelector.setCurrentNode(mvNode)
      
  def oncsvInputKMapFileButtonClicked(self):
    self.KMapPtacParametersWidget.KMwidgets[2].show()
      
  def oncsvInputKMapFileChanged(self,filename):
    print filename
    t,pTAC =self.lastLogic.readCSVsamples(filename)
    self.KMappTACSamplespTAC=pTAC
    self.KMappTACSamplesTime=t
      
  def onKMapPtacOptionsChanged(self,index):
    print 'option changed', index
    self.KMapPtacParametersWidget.KMpTACDestroy()
    if index < 0:
      return
    self.KMapPtacParametersWidget.CreateKMpTACParameters(index)
    if index == 1: #Make the connections
        self.KMapPtacParametersWidget.KMwidgets[1].connect('clicked(bool)',self.oncsvInputKMapFileButtonClicked) #connect the button 
        self.KMapPtacParametersWidget.KMwidgets[2].fileSelected.connect(self.oncsvInputKMapFileChanged)
        
  def onKMapMaskOptionsChanged(self,index):
    print 'Mask option changed', index
    self.KMapMaskParametersWidget.KMapdestroy()
    if index < 0:
      return
    self.KMapMaskParametersWidget.CreateKMapParameters(index)  
    
  def onApplyKmap(self):
    print 'About to apply K-Map'
    #Decide later what to do about special cases of undefined values from previous stages
    #Sort by options
    #pTAC input options
    pTAC=None
    tpTAC=None
    Mask=None
    if self.KMapPtacOptionsBox.currentIndex == 0: #automatic pTAC estimation
        pTACOption='Auto'
    elif self.KMapPtacOptionsBox.currentIndex == 1: #read pTAC from file
        pTACOption='FromFile'
        pTAC=self.KMappTACSamplespTAC
        tpTAC=self.KMappTACSamplesTime
    #Mask input options
    if self.KMapMaskOptionsBox.currentIndex ==0: #automatic mask generation
        MaskOption='Auto'
    elif self.KMapMaskOptionsBox.currentIndex ==1: #Mask from labelmap
        MaskOption='Labelmap'
        Mask=self.KMapMaskParametersWidget.KMapwidgets[1].currentNode()
    elif self.KMapMaskOptionsBox.currentIndex ==2: #Mask from ROI
        MaskOption='ROI'
        Mask=self.KMapMaskParametersWidget.KMapwidgets[1].currentNode()
    print 'FALTA MANDAR Y HACER EL RUN, TESTEAR SOLO QUE ESTE DEFINIENDO BIEN LAS COSAS'
    KMap=self.lastLogic.applyKMapEstimation(pTACOption, pTAC,tpTAC, MaskOption, Mask)
    KMap.SetScene(slicer.mrmlScene)
    KMap.SetName("HELLO PATLAK OUTPUT")
    slicer.mrmlScene.AddNode(KMap)
      
  def onpTACcsvOutputFileChanged(self,t):
    self.outputcsvDir=t
      
  def onpTACcsvOutputFileButtonClicked(self):
    self.pTACcsvOutputFileDialog.show()
      
class dPetBrainQuantificationLogic:

  def __init__(self, parent=None):
    self.parent = parent
    self.DataMatrix = []
    self.frameTime= []
    self.Dim = None 
    self.BrainMask = None
    self.Carotids_array_Mask = []
    self.mTis = []
    self.mCar = []
    self.pTAC_est = []
    self.scalarVolumeTemplate = None
    self.numInitshort=None
    self.numEndshort=None
    
  def extractFrame(self,mvNode,frameId):
    #Reference Scalar Volume
    frameVolume = slicer.vtkMRMLScalarVolumeNode()
    
    #
    # Coordenadas compatibles 
    #   
    ras2ijk = vtk.vtkMatrix4x4()
    ijk2ras = vtk.vtkMatrix4x4()
    mvNode.GetRASToIJKMatrix(ras2ijk)
    mvNode.GetIJKToRASMatrix(ijk2ras)
    frameVolume.SetRASToIJKMatrix(ras2ijk)
    frameVolume.SetIJKToRASMatrix(ijk2ras)
  
    #
    # Get extract frame from de multivolume node
    #
    mvImage = mvNode.GetImageData()
    extract = vtk.vtkImageExtractComponents()
    extract.SetInput(mvImage)
    extract.SetComponents(frameId)
    extract.Update()
    frameVolume.SetAndObserveImageData(extract.GetOutput())
    
    #Set Name
    frameName = 'Frame_ref'+str(frameId)
    frameVolume.SetName(frameName)

    return frameVolume
  
  def applyCarotidSegmentation(self,mvNode,roi,connectivityfilter,FrameForSegm) :
    if mvNode == None :
            print('No multivolume selected')
            return
    #self.loadData(mvNode)
    segmType = 0
    #First frames
    firstFr = self.frameTime[self.frameTime < self.frameTime [0] + 90].argmax()
    print('first frames :',firstFr)
    
    #
    # Automatic Segmentation
    #
    
    if roi == None :
      CVar = numpy.var(self.DataMatrix[:,self.BrainMask>0],axis = 1)
      CMean = numpy.mean(self.DataMatrix[:,self.BrainMask>0],axis = 1)
        #peak index
      peak_index = CVar[0:firstFr+1].argmax()
      print('peak_index :',peak_index)
      #generic pTAC
      pTAC_gen = self.genpTAC(self.frameTime,peak_index)
      #acumulate until peak & get correlation of each voxel with pTAC_gen
      if FrameForSegm == None :
          acData = self.accumulate_array(self.DataMatrix,0,peak_index,None)
      else :
          acData = self.DataMatrix[FrameForSegm,:]
      
      aCorrelation = self.corrDatapTAC(self.DataMatrix,pTAC_gen)
      #Correlation threshold is 50% 
      CorrUm = 0.5
      sigUm = self.OtsuThreshold(acData[(aCorrelation > CorrUm) ] ,100,None,None)
      print('Data Mean',acData.mean())
      Carotids_array_Mask = numpy.zeros(aCorrelation.size)
      Carotids_array_Mask[(aCorrelation>CorrUm) & (acData>sigUm) ] = 1
            
            
    #
    # ROI Based segmentation
    #
    
    if roi != None :
      segmType = 1
      frameVolume = self.extractFrame(mvNode,0)
      array_ROIMask = self.Roi2MapArray(frameVolume,roi)
      array_ROIMask = array_ROIMask.reshape(-1)
      array_ROIData = numpy.zeros(self.DataMatrix.shape)
      array_ROIData[:] = self.DataMatrix
      array_ROIData[:,array_ROIMask == 0] = 0
      #find peak
      CVar = numpy.var(array_ROIData[:,array_ROIMask>0],axis = 1)
      CMean = numpy.mean(array_ROIData[:,array_ROIMask>0],axis = 1)
      print('Cmean :', CMean)
      print('Cvar :', CVar)
      #peak index
      peak_index_v = CVar[0:firstFr+1].argmax()
      peak_index_m = CMean[0:firstFr+1].argmax()
      peak_index = min(peak_index_v,peak_index_m)
      print('peak_index :',peak_index)
      #Otsu threshold
      if FrameForSegm == None :
          acData = self.accumulate_array(self.DataMatrix,0,peak_index,None)
      else :
          acData = self.DataMatrix[FrameForSegm,:]
      sigUm = self.OtsuThreshold(acData[(array_ROIMask>0) & (acData>0)] ,100,None,None)
      #sigUm = self.OtsuThreshold(acData[(array_ROIMask>0)] ,100,0,None)
      Carotids_array_Mask = numpy.zeros(array_ROIMask.shape)
      Carotids_array_Mask[(acData > sigUm) & (array_ROIMask>0)] = 1
            
    #Filter        
    Carotids_array_Mask= Carotids_array_Mask.reshape([self.Dim[2],self.Dim[1],self.Dim[0]])
            
    #Cast Image
    castFilter = SimpleITK.CastImageFilter()
    castFilter.SetOutputPixelType(2)
    carotid_castITKim = castFilter.Execute(SimpleITK.GetImageFromArray(Carotids_array_Mask))
            
    #BinaryOpening By Reconstruction
    BinOpRec = SimpleITK.BinaryOpeningByReconstructionImageFilter()
    BinOpRec.SetKernelType(BinOpRec.Ball)
    BinOpRec.SetKernelRadius([1,1,1])
    BinOpRec.SetForegroundValue(1)
    BinOpRec.SetBackgroundValue(0)
            
    CarotidBinOpRec_Img = BinOpRec.Execute(carotid_castITKim)
    Carotids_array_Mask = SimpleITK.GetArrayFromImage(CarotidBinOpRec_Img)
            
    #Connectivity filter
    if connectivityfilter :
      Carotids_array_Mask = self.connectivityFilterSegmentation(Carotids_array_Mask,segmType)

    Dilate = SimpleITK.BinaryDilateImageFilter()
    Dilate.Ball
    Dilate.SetKernelRadius([2,2,2])
    DilateImg = Dilate.Execute(SimpleITK.GetImageFromArray(Carotids_array_Mask))
    Dilate_array = SimpleITK.GetArrayFromImage(DilateImg)
    Dilate_array = Dilate_array * 2
    print('Dilate',Dilate_array.max())
    Carotids_array_Mask = Dilate_array - Carotids_array_Mask
    Carotids_array_Mask = Carotids_array_Mask.reshape(-1)

            
    self.mTis = numpy.mean(self.DataMatrix[:,Carotids_array_Mask==2],axis = 1)
    self.mCar = numpy.mean(self.DataMatrix[:,Carotids_array_Mask==1],axis = 1)
    
    print('Peak de mCar',self.mCar.argmax())
           
    #
    #Mask Volume
    #
    self.Carotids_array_Mask = Carotids_array_Mask
    Mask = self.extractFrame(mvNode,0)
    name = 'Carotid Mask'
    Mask.SetName(name)
    Mask_Image = Mask.GetImageData()
    Mask_array = vtk.util.numpy_support.vtk_to_numpy(Mask_Image.GetPointData().GetScalars())
    print('Max self BrainMask' , self.BrainMask.max())
    Mask_array[:] = self.Carotids_array_Mask
    Mask_Image.Modified()
    
    #hot voxels index
    peak_index = self.mCar[0:firstFr+1].argmax()
    sortPeakCarotid = self.DataMatrix[peak_index,Carotids_array_Mask == 1].argsort()
    minIndex = -1 * int(sortPeakCarotid.size*0.03)
    self.hotvoxelsindex = sortPeakCarotid[minIndex:] 
    print ( ' Hot Voxels index :',self.hotvoxelsindex)
    
    return Mask
   
  def connectivityFilterSegmentation(self,array_Img,typeofSegm):
    castFilter = SimpleITK.CastImageFilter()
    castFilter.SetOutputPixelType(2)
    castITKim = castFilter.Execute(SimpleITK.GetImageFromArray(array_Img))
    ConnectFilter = SimpleITK.ConnectedComponentImageFilter()
    Connect_array = SimpleITK.GetArrayFromImage(ConnectFilter.Execute(castITKim))
            
    #Automatic segmentation CASE
    if typeofSegm == 0 :
        shape = Connect_array.shape
        #set top half slices to background (we asume carotids are on the botton half)
        h_slices = int(shape[0]/2)
        Connect_array[h_slices: , : , :] = 0
    
    Connect_array = Connect_array.reshape(-1)
    Hist = numpy.histogram(Connect_array,Connect_array.max())
    H_v = Hist[1]
    H_i = Hist[0]
    sort_Hi = H_i.argsort()
    print('H_v:',H_v)
    print('H_i:', H_i)
    #get the largest cluster ignoring background (0)
    if H_v.size>3:
        LargestClusterIndex = H_v[sort_Hi[-3:-1]]
    if H_v.size == 3 :
        LargestClusterIndex = H_v[sort_Hi[0]:sort_Hi[0]+2]
    if H_v.size <= 2:
        LargestClusterIndex = H_v[1]
            
    if H_v.size>2: 
        Connect_array[(Connect_array != LargestClusterIndex[0]) & (Connect_array != LargestClusterIndex[1]) ] = 0
    if H_v.size <= 2:
        Connect_array[(Connect_array != LargestClusterIndex) ] = 0
    
    Connect_array[Connect_array>0] = 1
    Connect_array = Connect_array.reshape(array_Img.shape)
    
    return Connect_array
      
  def loadData(self,mvNode) :
    #frame time units 
    frameUnits = mvNode.GetAttribute("MultiVolume.FrameIdentifyingDICOMTagUnits")
    #frame string
    frTimeStr = string.split(mvNode.GetAttribute("MultiVolume.FrameLabels"), ",")
    frTimeStr = numpy.array(frTimeStr)
    nFrames = frTimeStr.size
    #get dimensions and set global variables
    mvImageData = mvNode.GetImageData()
    self.Dim = mvImageData.GetDimensions()
    nVoxels = self.Dim[0]*self.Dim[1]*self.Dim[2]
    
    self.frameTime = numpy.zeros([frTimeStr.size])
    self.DataMatrix = numpy.zeros([nFrames , nVoxels])
    
    # save frame Data and frameTime vector
    for i in range(nFrames) : 
      frameVolume = self.extractFrame(mvNode,i)
      vImageData = frameVolume.GetImageData()
      DataArray = vtk.util.numpy_support.vtk_to_numpy(vImageData.GetPointData().GetScalars())
      #DataArray[:,:,0] = 0
      self.DataMatrix[i,:] = DataArray.reshape(-1)
      self.frameTime[i] = float(frTimeStr[i])
      #DICOM multivolume doesnt specify scan start time, assume first frame = length than second
      if frameUnits == 'ms':
        self.frameTime[i] = self.frameTime[i] / 1000
        #self.frameTime = self.frameTime - self.frameTime[0]
    #CASO DICOM Y LA FALTA DE SCAN START TIME EN EL NODO MV
    if frameUnits == 'ms':
      deltaF1 = self.frameTime[1] - self.frameTime[0]
      self.frameTime = self.frameTime + deltaF1 - self.frameTime[0]
    self.frameTime = numpy.array(self.frameTime)
    print('Frame times ', self.frameTime) 
    
    #
    #Get Brain Mask
    #
    
    frameDelta = numpy.zeros(self.frameTime.size)
    frameDelta[:] = self.frameTime
    frameDelta[1:] = frameDelta[1:] - self.frameTime[0:-1]
    frameDelta[0] = frameDelta[1]
    print ( ' Frame delta :', frameDelta)
    print('Size Data Matrix : ' , self.DataMatrix.size)
    AcumulateBrain_array = self.accumulate_array(self.DataMatrix,self.frameTime.size-10,self.frameTime.size - 1,frameDelta)
    print('AcumulateBrain_array mean ',AcumulateBrain_array.mean())
    #Filter AcimilateBrain_array        
    AcumulateBrain_array= AcumulateBrain_array.reshape([self.Dim[2],self.Dim[1],self.Dim[0]])
            
    #Cast Image
    castFilter = SimpleITK.CastImageFilter()
    castFilter.SetOutputPixelType(2)
    AcumulateBrain_castITKim = castFilter.Execute(SimpleITK.GetImageFromArray(AcumulateBrain_array))
    
    #Double Otsu threshold
    MOTFilter = SimpleITK.OtsuMultipleThresholdsImageFilter()
    MOTFilter.SetNumberOfHistogramBins(100)
    MOTFilter.SetNumberOfThresholds(2)
    MOTFilter.SetLabelOffset(0)
    BrainMask_ITKim = MOTFilter.Execute(AcumulateBrain_castITKim)
    
    #Set both classes to 1
    BrainMask_array = SimpleITK.GetArrayFromImage(BrainMask_ITKim)
    BrainMask_array[BrainMask_array>0] = 1
    BrainMask_ITKim = SimpleITK.GetImageFromArray(BrainMask_array)
    
    #BinaryOpening By Reconstruction (eliminate small elements)
    BinOpRec = SimpleITK.BinaryOpeningByReconstructionImageFilter()
    BinOpRec.SetKernelType(BinOpRec.Ball)
    BinOpRec.SetKernelRadius([3,3,3])
    BinOpRec.SetForegroundValue(1)
    BinOpRec.SetBackgroundValue(0)
            
    BrainMask_ITKim = BinOpRec.Execute(BrainMask_ITKim)
    self.BrainMask = SimpleITK.GetArrayFromImage(BrainMask_ITKim)
    self.BrainMask = self.BrainMask.reshape(-1)
    
    #Scalar Volume Template
    self.scalarVolumeTemplate = self.extractFrame(mvNode, 0)

  def getBrainMaskVolume(self):
    #Get Scalar Volume
    BrainMaskScalarVolume=slicer.vtkMRMLScalarVolumeNode()
    BrainMaskScalarVolume.Copy(self.scalarVolumeTemplate)
    
    BrainMaskImageData = BrainMaskScalarVolume.GetImageData()
    array = vtk.util.numpy_support.vtk_to_numpy(BrainMaskImageData.GetPointData().GetScalars())
    #Set Brain Mask Data
    array[:] = self.BrainMask
    BrainMaskScalarVolume.GetImageData().Modified()
    #Set Name
    Name = 'Brain Mask'
    BrainMaskScalarVolume.SetName(Name)
    
    return BrainMaskScalarVolume
      
      
          
  def OtsuThreshold(self,array,bin,min,max):
    a_min = min
    a_max = max      
    if (min == None) | (min>array.max()):
            a_min = array.min()              
    if (max == None) | (max<array.min()):
            a_max = array.max()               
            
    Hist=numpy.histogram(array,bin,(a_min,a_max))      
    h_v = Hist[1]
    h_i = Hist[0]
    
    step = (h_v[1]-h_v[0])/2
    h_v = h_v[0:h_v.shape[0]-1]+step
    
    sig = numpy.zeros(h_v.shape)
    vox = h_i.sum()
    
    #OTSU#
    for i in range(sig.shape[0]):
      if i==0 :
        w1 = h_i[0]
        w2 = vox - w1
        mu1 = (h_v[0]*h_i[0])/w1
        mu2 = numpy.multiply(h_v[i+1:sig.shape[0]-1],h_i[i+1:sig.shape[0]-1])
        mu2 = mu2.sum()/w2
      else :    
        w1 = h_i[0:i].sum()
        w2 = vox - w1
        mu1 = numpy.multiply(h_v[0:i],h_i[0:i])
        mu1 = mu1.sum()/w1
        mu2 = numpy.multiply(h_v[i+1:sig.shape[0]-1],h_i[i+1:sig.shape[0]-1])
        mu2 = mu2.sum()/w2
      sig[i] = (w1*w2*((mu1-mu2) ** 2))
           
    Um = sig.argmax()
    Um = h_v[Um]
    print('Umbral Otsu',Um)
    return Um
  
  def accumulate_array(self,array,r_min,r_max,w) :
    if r_min == None :
            r_min = 0
    if r_max == None :
            r_max = array[:,1].size - 1
    if w == None :
            k = (r_max + 1 - r_min)
            w = numpy.ones(array[0,:].size)*k
            print('weight vector :',w)
            
    acArray = numpy.zeros(array[0,:].size)
    for i in range(r_min,r_max + 1) :
            acArray = acArray + (array[i,:]/w[i])
    return acArray
    
  def corrDatapTAC(self,array_Data,pTAC_gen) :
    Corr = numpy.zeros(array_Data[0,:].size)
    Ip = pTAC_gen.argmax()
    M = array_Data[Ip,:].mean()
    pTAC_gen = M*pTAC_gen/pTAC_gen[Ip]
    for i in range(array_Data[0,:].size) :
            if (array_Data[Ip,i]>0):
              CorrCoef = numpy.corrcoef(array_Data[:,i],pTAC_gen)
              Corr[i] = CorrCoef[0,1]
            else:
              Corr[i] = -1
    print('Termino de calcular correlacion correlacion va desde ',Corr.min(),'Hasta ',Corr.max())
    return Corr
      
  def genpTAC(self,Time,Ip):
      pTAC = numpy.zeros(Time.shape)
      Time = Time - Time[0]
      for i  in range(Time.size) :
          
          #line to peak
          if (Time[i]<=Time[Ip]) &  (Time[i] >= (Time[Ip]-20)):
              pTAC[i] = (Time[i] - Time[Ip] + 20)/2
              #print('pTAC1 es:',pTAC[i], 'Time es: ',Time[i])
                        
          #line down from peak
          if (Time[i]> Time[Ip] ) & (Time[i]<= Time[Ip]  + 60) :
              pTAC[i] = -((10-1.67)/60)*(Time[i]-Time[Ip] )+10
              #print('pTAC2 es:',pTAC[i], 'Time es: ',Time[i])        
          
          #exponential tail
          if (Time[i]> (Time[Ip]  + 60)) :
              c=1.13
              d=-0.0035
              e=1.056
              f=-0.00034
              pTAC[i]  = e* numpy.exp(f*(Time[i]-Time[Ip])) + c * numpy.exp(d*(Time[i]-Time[Ip])) 
                        #print('pTAC3 es:',pTAC[i], 'Time es: ',Time[i])
      return pTAC
    
  def iniChart(self,title,xlabel,ylabel,lns,cvns,cn):
    # Switch to a layout (24) that contains a Chart View to initiate the construction of the widget and Chart View Node
    lns.InitTraversal()
    ln = lns.GetNextItemAsObject()
    ln.SetViewArrangement(24)
    # Get the Chart View Node
    cvns.InitTraversal()
    #cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
    cn.SetProperty('default', 'title', title)
    cn.SetProperty('default', 'xAxisLabel', xlabel)
    cn.SetProperty('default', 'yAxisLabel', ylabel)
    cvn = cvns.GetNextItemAsObject()
    cvn.SetChartNodeID(cn.GetID())
    
  def addChart(self,x,y,Name,cn,cvns):
    dn = self.setDoubleArrayNode(x, y,Name)    
    cn.AddArray(Name, dn.GetID())
    #cvn = cvns.GetNextItemAsObject()
    #cvn.SetChartNodeID(cn.GetID())
    
  def setDoubleArrayNode(self,x,y,Name):
    dn = slicer.mrmlScene.AddNode(slicer.vtkMRMLDoubleArrayNode())
    dn.SetName(Name)
    a = dn.GetArray()
    a.SetNumberOfTuples(min(x.size,y.size))
    for i in range(min(x.size,y.size)):
        a.SetComponent(i,0,x[i])
        a.SetComponent(i,1,y[i])
        a.SetComponent(i,2,0)
    return dn

  def Roi2MapArray(self,template,ROI):
    #obtengo matriz RAStoIJK de template
    RASToIJK=vtk.vtkMatrix4x4()
    template.GetRASToIJKMatrix(RASToIJK)   
    #obtengo limites
    radio=numpy.zeros(3)
    ROI.GetRadiusXYZ(radio)
    centro=numpy.zeros(3)
    ROI.GetXYZ(centro)
    corner1=centro-radio
    corner2=centro+radio
   
    #transformo de coordenadas RAS a coordenadas IJK de el template
    corner1IJK=numpy.hstack([corner1,1])
    corner1IJK=RASToIJK.MultiplyPoint(corner1IJK)
    corner1IJK=corner1IJK[2::-1] #invierto orden e ignoro el 1 anadido
    corner1IJK=numpy.floor(corner1IJK)
   
    corner2IJK=numpy.hstack([corner2,1])
    corner2IJK=RASToIJK.MultiplyPoint(corner2IJK)
    corner2IJK=corner2IJK[2::-1] #invierto orden e ignoro el 1 anadido
    corner2IJK=numpy.floor(corner2IJK)
       
    #obtengo intervalos maximos y minimos de indices validos
    ijk=numpy.vstack([corner1IJK,corner2IJK])
    #print ijk
    i_min=numpy.min(ijk[:,0])
    i_max=numpy.max(ijk[:,0])
    j_min=numpy.min(ijk[:,1])
    j_max=numpy.max(ijk[:,1])
    k_min=numpy.min(ijk[:,2])
    k_max=numpy.max(ijk[:,2])
   
    template.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(template)
    array=slicer.util.array(template.GetID())
    array[:]=0
    array[i_min:i_max,j_min:j_max,k_min:k_max]=1
    slicer.mrmlScene.RemoveNode(template)
    return array

  def pTACestimationIDIF(self,sampleTime,samples,HunterTailfit) :
    #Get hot voxels
    #hotVoxelvalues = self.DataMatrix[:,self.hotvoxelsindex] 
    CarotidData = self.DataMatrix[:,self.Carotids_array_Mask == 1]
    print('Max hot voxel: ',CarotidData[:,self.hotvoxelsindex[-1]])
    hotVoxelvalues = numpy.mean(CarotidData[:,self.hotvoxelsindex] ,axis=1)
    print('hot voxels values :',hotVoxelvalues)
         
    nsamples = 0
    if (samples != None) & (sampleTime != None):
        nsamples = min(samples.size,sampleTime.size)
        #ONE OR NO SAMPLES    
    if (samples == None) | (sampleTime == None) | (nsamples < 2):
        b_expTail = None
        if HunterTailfit :
            print('FIT CON EXP HUNTER TAIL')
            b_expTail = -float(0.0125/60)
        #Estimation
        self.pTAC_est = self.estimatepTACgen(self.mTis,self.mCar,self.frameTime,hotVoxelvalues,b_expTail)
        print('pTAC Estimated :' , self.pTAC_est)
            #CASO UNA MUESTRA (SOLO PUEDO EVALUAR GANANCIA)
        if (nsamples == 1) :
            #ajusto ganancia
            Ip = hotVoxelvalues[self.frameTime<self.frameTime[0] + 90].argmax()
            TailIndex = self.frameTime>self.frameTime[Ip]+1200
            TailTimes = self.frameTime[TailIndex == 1]
            TailpTAC = self.pTAC_est[TailIndex == 1]
            a,b = self.fitOneExp(TailTimes,TailpTAC)
            print('b of IDIF hotVoxels :', b)
            G = float(samples[0]) / float(a*numpy.exp(b*sampleTime[0]))
            print('valor de la exponencial :', a*numpy.exp(b*sampleTime[0]))
            print('valor de la muestra : ' , samples[0])
            self.pTAC_est = self.pTAC_est * G
            print('G :',G)
        return self.frameTime,self.pTAC_est,hotVoxelvalues
        
          #TWO OR MORE SAMPLES
    if (nsamples > 1) :
        a,b = self.fitOneExp(sampleTime, samples)
        vTAC_tail = a*numpy.exp(b*self.frameTime)
        print('VTAC_TAIL' ,vTAC_tail)
        print('Samples',samples)
        print('Samples :',samples, ' time :' , sampleTime)
        self.pTAC_est = self.estimatepTACvSamples(self.mTis,self.mCar,self.frameTime,vTAC_tail,b,hotVoxelvalues)  
        return self.frameTime,self.pTAC_est,vTAC_tail
              
  def estimatepTACgen(self,mTis,mCar,Time,hotVoxelvalues,b):
    #get peak index
    Ip = hotVoxelvalues[Time<Time[0] + 90].argmax()
    TailIndex = Time>Time[Ip]+1200
    #possible spill in values
    K = numpy.linspace(0,1,100)
    DS = numpy.ones(K.shape)
    if b == None :
        a,b = self.fitOneExp(Time[TailIndex == 1] - Time[Ip],hotVoxelvalues[TailIndex == 1])
    print('b :',b)
    print('b del fit ref :', b)
    for i in range(K.size):
        ki = K[i]
        pTAC_est = (mCar - ki*mTis)
        if (pTAC_est[Ip:].min() > 0) :
            A,L = self.fitOneExp(Time[TailIndex == 1]- Time[Ip],pTAC_est[TailIndex == 1])
            print('L :', L)
            DS[i] = abs(float(L) - float(b))        
    Ind = DS.argmin()
    Kf2 = K[Ind]
    print 'Kind2',Kf2   
    print('DS :' , DS) 
    pTAC_est = (mCar - Kf2 * mTis)/(1-Kf2)
    #Adjust peak with hotvoxels.
    pTAC_est = self.pTACpeakCorrection(pTAC_est, hotVoxelvalues)
    return pTAC_est
      
  def estimatepTACvSamples(self,mTis,mCar,Time,vTAC_tail,b,hotVoxelvalues) :
    #get peak index
    Ip = mCar[Time<Time[0] + 90].argmax()
    TailIndex = Time>Time[Ip]+1200
    K = numpy.linspace(0,1,100)
    DS = numpy.ones(K.shape)
    for i in range(K.size):
        ki = K[i]
        pTAC_est = (mCar - ki*mTis)
        if (pTAC_est[Ip:].min() > 0) :
            A,L = self.fitOneExp(Time[Time>Time[Ip]+1200],pTAC_est[TailIndex])
            DS[i] = abs(L - b)
    print('Difference shape :',DS)
    Ind = DS.argmin()
    Kf2 = K[Ind]
    print 'Kind2',Kf2
    print('vTAC : ',vTAC_tail[TailIndex])
    pTAC_est = ((mCar - Kf2 * mTis)/(1-Kf2))
    print('Maximo pTAC :', pTAC_est[Ip], 'Maximo de toda la parte carotidas en el pico : ',self.DataMatrix[Ip,self.Carotids_array_Mask == 1].max())
    #Adjust peak with hotvoxels.
    pTAC_est = self.pTACpeakCorrection(pTAC_est, hotVoxelvalues) 
    # mx + c = y     
    D = numpy.vstack([pTAC_est[TailIndex]]).T
    print('D : ',D)
    Gain = numpy.linalg.lstsq(D, vTAC_tail[TailIndex])[0]
    print('Gain_ cross calibration scan-counter: ',Gain)
    return Gain*pTAC_est
  
  def pTACpeakCorrection(self,pTAC_est,hotVoxelvalues):
    #Adjust peak with hotvoxels.
    Ip = hotVoxelvalues.argmax()
    if (pTAC_est[Ip]<hotVoxelvalues[Ip]) | (pTAC_est[Ip] > 1.5*hotVoxelvalues[Ip]) :
        pTAC_est[Ip] = hotVoxelvalues[Ip]
        pTAC_est[Ip + 1] = hotVoxelvalues[Ip + 1]
        if Ip>0 :
            pTAC_est[Ip - 1] = hotVoxelvalues[Ip - 1]
    return pTAC_est
      
  def fitOneExp(self,time,value):
    # v = a*exp(b*t) --> ln(v) = ln(a) + b*t
    y = numpy.log(numpy.float32(value))
    x = numpy.float32(time)
    D = numpy.vstack([x, numpy.ones(len(x))]).T
    # mx + c = y 
    m,c = numpy.linalg.lstsq(D, y)[0]
    a = numpy.exp(c)
    b = m
    return a,b
  
  def PBIFhunter(self,dosage, leanWeight, samples,sampleTimes):
    
    if self.frameTime == []:
        return
    PeakTime = 0
    if self.DataMatrix != []:
      firstFr = self.frameTime[self.frameTime < self.frameTime [0] + 90].argmax()
      CVar = numpy.var(self.DataMatrix[:,self.BrainMask>0],axis = 1)
      #peak index
      peak_index = CVar[0:firstFr+1].argmax()
      print('peak_index :',peak_index)
      PeakTime = self.frameTime[peak_index]
      print('pico pico time: ',PeakTime)
      
    #times in seconds
    #dosage in MBq
    #leanWeigth in Kg
    #samples in Bq/g
   
    b1=-9.33/60
    b2=-0.289/60
    b3=-0.0125/60
    dosageInBq=dosage*10**6
    bloodInGrams=leanWeight*70
    Concentration=dosageInBq/bloodInGrams
    C=6.4687
    A2=Concentration/(C+1)
    A1=A2*C
   
    A_matrix=numpy.vstack(numpy.exp(b3*(sampleTimes-PeakTime)))
    Y=numpy.vstack(samples)
    A3=numpy.linalg.lstsq(A_matrix, Y)[0]
    A3 = A3[0]
    #print('A3',A3)
    #print('Primer coso:', A1*numpy.exp(b1*(self.frameTime-PeakTime)))
    pTAC=A1*numpy.exp(b1*(self.frameTime-PeakTime))+A2*numpy.exp(b2*(self.frameTime-PeakTime))+A3*numpy.exp(b3*(self.frameTime-PeakTime))
    #pTAC = numpy.add(A1*numpy.exp(b1*(self.frameTime-PeakTime)),A2*numpy.exp(b2*(self.frameTime-PeakTime)),A3*numpy.exp(b3*(self.frameTime-PeakTime)))
    aux=self.frameTime<PeakTime
    pTAC[aux]=0
    #print('pTAC',pTAC)
    self.pTAC_est = numpy.array(pTAC)
    self.pTAC_est.reshape(-1)
    #print('pTAC',self.pTAC_est)
    #print('pTAC size',self.pTAC_est.size)
    #print('pTAC shape',self.pTAC_est.shape)
    
    return self.frameTime,self.pTAC_est

#Patlak Functions
# FUNCIONES  A PASAR 

  def cumtrapz(self,t,y):#Defino integral trapezoidal cumulativa
    endt=t.size-1
    auxt1=numpy.concatenate(([0],t[0:endt]),axis=1)
    deltat=t-auxt1
    endy=y.size-1
    auxy1=numpy.concatenate(([0],y[0:endy]),axis=1)
    trapecio=(y+auxy1)/2
    trapecio=trapecio*deltat
    return trapecio.cumsum()

  def patlak_voxel(self,integral,pTAC,voxel):#
    ind=(integral>0)&(voxel>0)&(pTAC>0) #Rev
    X=numpy.array(integral[ind]/pTAC[ind]) #Rev
    Y=numpy.array(voxel[ind]/pTAC[ind]) #Rev
    tolerancia=0.2
    #Primer estimador
    #voxel casi totalmente sin datos, no opero
    if len(X)<4:
        return 0
        self.numInitshort=self.numInitshort+1
    A = numpy.vstack([X, numpy.ones(len(X))]).T      
    K, Vo = numpy.linalg.lstsq(A, Y)[0]
    desviacion=numpy.abs((Y-K*X-Vo)/Vo)
    ind=desviacion<tolerancia
    #Segundo estimador
    #establezco nuevos conjuntos de datos para operar
    Y_2=numpy.array(Y[ind])
    X_2=numpy.array(X[ind])
    #voxel casi totalmente sin datos, no opero
    if len(X_2)<4:
       return 0
       self.numEndshort=self.numEndshort+1
    A = numpy.vstack([X_2, numpy.ones(len(X_2))]).T      
    K, Vo = numpy.linalg.lstsq(A, Y_2)[0]
    K=numpy.max([K,0])
    return K*10**8
    
  def patlak(self,array,DataMatrix,time,pTAC,Mask): #REVISAR MANEJO DE NEGATIVOS Y PUNTOS SIN INFORMACION (Estan entrando conteos o CPET?)
    self.numInitshort=0
    self.numEndshort=0
    #Obtain pTAC integral
    integral=self.cumtrapz(time,pTAC)
    lateFrame=time>(20*60) # frames later than 20 minutes post injection
    indFrame=lateFrame.argmax()
    integral=integral[indFrame:]
    pTAC=pTAC[indFrame:]
    #Operate
    voxel=numpy.zeros_like(DataMatrix[indFrame:,0])
    for i in range(Mask.size-1):
        if Mask[i]:
            voxel=DataMatrix[indFrame:,i]
            array[i]=self.patlak_voxel(integral,pTAC,voxel)
        else:
            array[i]=0
    return array
    
  def readCSVsamples(self,filename):
    if filename.endswith('.csv'):
      file = open(filename,'r')
      ValueStr = numpy.array(string.split(file.read(),","))
      file.close()
      Value=map(float,ValueStr)
      time=numpy.array(Value[0::2])
      sample=numpy.array(Value[1::2])
      return time, sample
    else:
      return
    
  def writeCSVsamples(self,filename,time,sample):
    Value= [item for i in zip(time,sample) for item in i] #parse the time and sample lists
    ValueStr=[str(item) for item in Value]
    ValueStr = string.join(ValueStr,',')
    print ValueStr
    file=open(filename,'w')
    file.write(ValueStr)
    file.close()
      
  def NiftiParser(self,inputDir,mvNode):
    #configure the multivolumeimporter options and load the chosen directory and ouptut image
    s = slicer.modules.multivolumeimporter.widgetRepresentation().self()
    DirSelectorDummy = ctk.ctkDirectoryButton()
    DirSelectorDummy.directory=inputDir
    s._MultiVolumeImporterWidget__fDialog=DirSelectorDummy
    mvSelectorDummy = slicer.qMRMLNodeComboBox()
    mvSelectorDummy.nodeTypes = ['vtkMRMLMultiVolumeNode']
    mvSelectorDummy.setMRMLScene(slicer.mrmlScene)
    mvSelectorDummy.addEnabled = True
    mvSelectorDummy.setCurrentNode(mvNode)
    s._MultiVolumeImporterWidget__mvSelector=mvSelectorDummy
    #Run multivolume importer
    s.onImportButtonClicked()
    #extract frame endtime information from .SIF File
    fileNames = []
   
    SIFDir=[]
    for f in os.listdir(inputDir):
      if not f.startswith('.'):
        if f.endswith ('.sif'):
          fileName = inputDir+'/'+f
          SIFDir=fileName
    #Open the .SIF file and obtain the frame end times
    file = open(SIFDir)
    file.readline() #ignore title line
    frames=[]
    for line in file:
        frTimeStr = numpy.array(string.split(line," "))
        frames.append(frTimeStr[1]) #append the end frame value
    frames=numpy.array(frames)
    frames=frames.astype(int)  
    file.close()
    #generate the string in the format required by the MultiVolume.FrameLabels attribute
    strFrame=""
    for i in frames:
      if i==frames[-1]:
        strFrame=strFrame+repr(i)
      else:
        strFrame=strFrame+repr(i)+","
    #set the attribute
    mvNode.SetAttribute("MultiVolume.FrameLabels",strFrame)
    return mvNode
  
  def applyKMapEstimation(self,pTACOption,pTAC,tpTAC,MaskOption,Mask):
    #currently, only patlak is implemented
    print 'hello kMap logic apply'
    #GetpTAC CON WARNING E INTERPOLACION PARA LAS MUESTRAS!
    pTAC=self.getpTAC(pTACOption,pTAC,tpTAC)
    #GetMask que devuelva el array #OJO SI ES AUTO Y NO ESTA DEFINIDA LA MASCARA
    Mask=self.getMask(MaskOption,Mask)
    #generate new ScalarVolume to store the output
    KMapScalarVolume=slicer.vtkMRMLScalarVolumeNode()
    KMapScalarVolume.Copy(self.scalarVolumeTemplate)
    
    vImageData = KMapScalarVolume.GetImageData()
    array = vtk.util.numpy_support.vtk_to_numpy(vImageData.GetPointData().GetScalars())
    
    #apply Estimation
    array=self.patlak(array, self.DataMatrix, self.frameTime, pTAC, Mask)
    KMapScalarVolume.GetImageData().Modified()
    
    self.KMap_array = numpy.zeros(array.shape)
    self.KMap_array[:] = array/(10 ** 4)
    
    Hist=numpy.histogram(self.KMap_array,50,(self.KMap_array[self.KMap_array>0].min(),self.KMap_array.max()))      
    h_v = Hist[1]
    h_i = Hist[0]
    step = (h_v[1]-h_v[0])/2
    h_v = h_v[0:h_v.shape[0]-1]+step
    dn = self.setDoubleArrayNode(h_v, h_i, 'Kmap_Histogram')
    
    
    return KMapScalarVolume
      
  def getpTAC(self,pTACOption,pTAC,tpTAC):
    print 'hello getpTAC'
    if pTACOption == 'Auto':
      print 'Auto'
      return self.pTAC_est
    elif pTACOption == 'FromFile':
      print 'FromFile'
      if not(numpy.allclose(tpTAC,self.frameTime,rtol=0.01)): #compare the time vectors to see if they match
        print 'WARNING, sample times do not match up with frame end times, attempting interpolation, this may compromise the estimation'
        print pTAC
        print numpy.interp(self.frameTime, tpTAC, pTAC, left=0)
        return numpy.interp(self.frameTime, tpTAC, pTAC, left=0)
      else:
        print pTAC
        return pTAC
          
  def getMask(self,MaskOption,Mask):
    print 'hello getMASK'
    if MaskOption == 'Auto':
      print "OJO CON ESTO, NO ESTOY CHEQUEANDO QUE ESTE LA AUTO MASK VACIA, MUCHO MENOS CORRIENDO LOS COMANDOS PARA GENERARLA SI NO ESTUVIESE"
      return self.BrainMask.astype('bool') #brute cast to boolean
    elif MaskOption == 'Labelmap':
      print "from labelmap"
      MaskArray = vtk.util.numpy_support.vtk_to_numpy(Mask.GetImageData().GetPointData().GetScalars())
      return MaskArray.astype('bool')
    elif MaskOption == 'ROI':
      print 'from ROI'
      MaskArray = Roi2MapArray(self,self.scalarVolumeTemplate,ROI)
      return MaskArray.astype('bool')


          
          
      
class ParametersWidget(object):
  def __init__(self, parent=None):
    self.parent = parent
    self.CSwidgets = []
    self.pTACwidgets = []
    self.inputs = []
    self.KMwidgets=[]
    self.KMapwidgets=[]
  def __del__(self):
    self.CSdestroy()
    self.KMpTACDestroy()
    self.Kmapdestroy()
    self.pTACdestroy()    
    
  def CreateCSParameters(self,index):
    if not self.parent:
      raise "no parent"
    
    parametersFormLayout = self.parent.layout()
    self.inputs = []
    
    #
    # Carotid Segmentation Parameters
    # Index : 0 - Automatic segmentation , 1 - ROI based Segmentation
    #

    #Case ROI based carotid segmentation
    if index == 1 :
      #Input ROI
      label = qt.QLabel('Input ROI')
      RoiSelector = slicer.qMRMLNodeComboBox()
      RoiSelector.nodeTypes = ["vtkMRMLAnnotationROINode"]
      RoiSelector.setMRMLScene(slicer.mrmlScene)
      RoiSelector.addEnabled = 0
      RoiSelector.noneEnabled = 1
      parametersFormLayout.addRow(label,RoiSelector) 
      #add to CS widgets
      self.CSwidgets.append(label)
      self.CSwidgets.append(RoiSelector)                  
    
    #Frame for segmentation 
    UseFrameCheckBox = qt.QCheckBox()
    UseFrameCheckBox.setChecked(0)
    label = qt.QLabel('Choose a Frame for better segmentation : ')
    DoubleFrameBox = qt.QDoubleSpinBox()
    DoubleFrameBox.value = 0               
    self.parent.collapsed = 0
    #add to CS widgets
    self.CSwidgets.append(label)
    self.CSwidgets.append(UseFrameCheckBox)
    self.CSwidgets.append(DoubleFrameBox)
    parametersFormLayout.addRow(UseFrameCheckBox,label)
    parametersFormLayout.addWidget(DoubleFrameBox)   
         
    
    #Connectivity filter
    connectivityFilterCheckBox = qt.QCheckBox()
    connectivityFilterCheckBox.setChecked(0)
    label = qt.QLabel('Apply connectivity filter to the segmentation')
    self.parent.collapsed = 0
    #add to CS widgets
    self.CSwidgets.append(label)
    self.CSwidgets.append(connectivityFilterCheckBox)
    parametersFormLayout.addRow(connectivityFilterCheckBox,label)
    
     #Chart Option
    chartCheckBox = qt.QCheckBox()
    chartCheckBox.setChecked(0)
    label = qt.QLabel('Get chart with tissue and carotid mean activity')
    self.parent.collapsed = 0
    #add to CS widgets
    self.CSwidgets.append(label)
    self.CSwidgets.append(chartCheckBox)
    parametersFormLayout.addRow(chartCheckBox,label)     

  def CSdestroy(self):
    print ('HOLA destroy')
    if self.CSwidgets != [] :
      for w in self.CSwidgets:
        print(w)
        self.parent.layout().removeWidget(w)
        w.deleteLater()
        w.setParent(None)
    self.CSwidgets = []
    self.parent.collapsed = 1
          
  def  CreatepTACParameters(self,index):
    if not self.parent:
            raise "no parent"
    
    parametersFormLayout = self.parent.layout()
    self.inputs = []
    
    #
    # pTAC estimation Options
    # Index : 0 - IDIF estimation , 1 - PBIF Hunter estimation 
    #
    
    if index == 0 :
      #Use previous carotid segmentation
      carSegCheckBox = qt.QCheckBox()
      carSegCheckBox.setChecked(0)
      label = qt.QLabel('Use previous carotid segmentation')
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(carSegCheckBox)           
      parametersFormLayout.addRow(carSegCheckBox,label)

      UseVenousSamplesCheckBox = qt.QCheckBox()
      UseVenousSamplesCheckBox.setChecked(0)
      label = qt.QLabel('Use venous blood samples')
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(UseVenousSamplesCheckBox)           
      parametersFormLayout.addRow(UseVenousSamplesCheckBox,label)
      
      UseHunterTailfitCheckBox = qt.QCheckBox()
      UseHunterTailfitCheckBox.setChecked(0)
      label = qt.QLabel('Fit with Hunters tail (FDG) when one or no sample is provided')
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(UseHunterTailfitCheckBox)           
      parametersFormLayout.addRow(UseHunterTailfitCheckBox,label)
  
    if index == 1 :
      #Dosage
      label = qt.QLabel('Dosage inyected in MBq')
      DosageInyectedValue = qt.QDoubleSpinBox()
      DosageInyectedValue.value = 0
      DosageInyectedValue.setMaximum(9999999)
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(DosageInyectedValue)
      parametersFormLayout.addRow(label, DosageInyectedValue)
      #weigth
      label = qt.QLabel('Lean weight Kg')
      LeanWeightValue = qt.QDoubleSpinBox()
      LeanWeightValue.value = 0
      LeanWeightValue.setMaximum(9999999)
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(LeanWeightValue)
      parametersFormLayout.addRow(label, LeanWeightValue)
            
    
    #save pTAC estimated ina .csv
    savepTACSegCheckBox = qt.QCheckBox()
    savepTACSegCheckBox.setChecked(0)
    label = qt.QLabel('Save pTAC estimated in a .csv file')
    self.pTACwidgets.append(label)
    self.pTACwidgets.append(savepTACSegCheckBox)           
    parametersFormLayout.addRow(savepTACSegCheckBox,label)
     
    #get Chart
    chartCheckBox = qt.QCheckBox()
    chartCheckBox.setChecked(1)
    label = qt.QLabel('Get chart with the estimated pTAC')
    self.pTACwidgets.append(label)
    self.pTACwidgets.append(chartCheckBox)           
    parametersFormLayout.addRow(chartCheckBox,label)
    self.parent.collapsed = 0
    print (self.pTACwidgets)

  def pTACdestroy(self):
    print ('HOLA pTAC destroy')
    if self.pTACwidgets != [] :
      for w in self.pTACwidgets:
        print(w)
        self.parent.layout().removeWidget(w)
        w.deleteLater()
        w.setParent(None)
    self.pTACwidgets = []
    self.parent.collapsed = 1
          
  def  CreateKMpTACParameters(self,index):
    if not self.parent:
        raise "no parent"
        
    parametersFormLayout = self.parent.layout()
    self.inputs = []
    
    #Case pTAC from csv file
    if index == 1 :
        
      #Input Samples file button
      label_button = qt.QLabel('Input csv blood samples file')
      csvInputKMapFileButton = qt.QPushButton("Input csv blood samples file (evaluated at frame endtimes)")
      csvInputKMapFileButton.toolTip="Opens a file dialog window to input CSV sample file"
      #self.csvInputKMapFileButton.connect('clicked(bool)',self.oncsvInputKMapFileButtonClicked)
      #input Sample files
      
      csvInputKMapFile = qt.QFileDialog()
      csvInputKMapFile.setNameFilter("CSV (*.csv)")
      #self.csvInputKMapFile.fileSelected.connect(self.oncsvInputKMapFileChanged)
      self.KMwidgets.append(label_button)
      self.KMwidgets.append(csvInputKMapFileButton)
      self.KMwidgets.append(csvInputKMapFile)
      parametersFormLayout.addRow(label_button,csvInputKMapFileButton)
      self.parent.collapsed = 0
      print (self.KMwidgets)
        
  def  KMpTACDestroy(self):
    print ('HOLA destroy KM')
    if self.KMwidgets != [] :
      for w in self.KMwidgets:
        print(w)
        self.parent.layout().removeWidget(w)
        w.deleteLater()
        w.setParent(None)
      self.KMwidgets = []
    self.parent.collapsed = 1
      
  def  CreateKMapParameters(self,index):
    if not self.parent:
        raise "no parent"
        
    parametersFormLayout = self.parent.layout()
    self.inputs = []
    
    #Case Map from labelmap
    if index == 1 :
      label = qt.QLabel('Input Mask')
      MaskSelector = slicer.qMRMLNodeComboBox()
      MaskSelector.nodeTypes = ["vtkMRMLScalarVolumeNode"]
      MaskSelector.setMRMLScene(slicer.mrmlScene)
      MaskSelector.addEnabled = 0
      MaskSelector.noneEnabled = 1
      self.KMapwidgets.append(label)
      self.KMapwidgets.append(MaskSelector)
      parametersFormLayout.addRow(label,MaskSelector)
      self.parent.collapsed = 0
    if index == 2:
          #Entrada ROI
      label = qt.QLabel('Input ROI')
      RoiSelector = slicer.qMRMLNodeComboBox()
      RoiSelector.nodeTypes = ["vtkMRMLAnnotationROINode"]
      RoiSelector.setMRMLScene(slicer.mrmlScene)
      RoiSelector.addEnabled = 0
      RoiSelector.noneEnabled = 1
      self.KMapwidgets.append(label)
      self.KMapwidgets.append(RoiSelector)
      parametersFormLayout.addRow(label, RoiSelector)
      self.parent.collapsed = 0
          
  def  KMapdestroy(self):
    print ('HOLA destroy KMap')
    if self.KMapwidgets != [] :
      for w in self.KMapwidgets:
        print(w)
        self.parent.layout().removeWidget(w)
        w.deleteLater()
        w.setParent(None)
      self.KMapwidgets = []
    self.parent.collapsed = 1


          

          