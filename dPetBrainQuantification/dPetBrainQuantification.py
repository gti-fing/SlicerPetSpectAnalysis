
import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import sys, string, numpy
import SimpleITK

from MultiVolumeImporterLib.Helper import Helper
from DICOM import *

class dPetBrainQuantification:
  def __init__(self, parent):
    parent.title = "dPetBrainQuantification"
    parent.categories = ["Quantification"]
    parent.dependencies = []
    parent.contributors = ["Martin Bertran, Natalia Martinez, Guillermo Carbajal, Alvaro Gomez"] # replace with "Firstname Lastname (Org)"
    parent.helpText = """
    This module allows the quantization of dynamic PET (dPET) brain scans. It is optimized to work with FDG tracer.
    It is possible to segment relevant blood pools, derive pTAC curves, and perform voxel or region based Patlak analysis.
    """
    parent.acknowledgementText = """
    This work was supported by Comision Sectorial de Investigacion Cientifica (CSIC, Universidad de la Republica, Uruguay) under program "Proyecto de Inclusion Social".""" # replace with organization, grant and thanks.
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
    self.VenousSamplepTAC=numpy.array([])
    self.VenousSampleTime=numpy.array([])
    #Segmentation parameters
    self.CarSegmParameters  = None
    self.pTACestParameters = None
    self.CarSegmType = 0
    self.pTACEstType = 0
    #Last Logic
    self.lastLogic = None
    #Display parameters
    self.lns = None
    self.cvns = None
    self.cn = None
    self.Chart = False
    self.foregroundVolumeNode = None

  def setup (self) :    
    self.lastLogic=dPetBrainQuantificationLogic()
    
    #
    # Input Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "dynamic PET Study and Information"
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
    # Carotid Segmentation Area
    #
    CarSegmentationCollapsibleButton = ctk.ctkCollapsibleButton()
    CarSegmentationCollapsibleButton.text = "Carotid Segmentation Options"
    CarSegmentationCollapsibleButton.collapsed = 1
    self.layout.addWidget(CarSegmentationCollapsibleButton)

    # Layout visualization within the dummy collapsible button
    CarSegmentationFormLayout = qt.QFormLayout(CarSegmentationCollapsibleButton)    

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
    # K-Map Estimation Widget area
    #
    self.KMapCollapsibleButton = ctk.ctkCollapsibleButton()
    self.KMapCollapsibleButton.text = "K-Map Estimation options"
    self.KMapCollapsibleButton.collapsed = 1
    self.layout.addWidget(self.KMapCollapsibleButton)
     # Layout visualization within the K-Map collapsible button
    self.KMapFormLayout = qt.QFormLayout(self.KMapCollapsibleButton)

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
    DisplayBrainMaskButton.toolTip="Display the obtained Brain Mask"
    DisplayBrainMaskButton.connect('clicked(bool)',self.onDisplayBrainMask)
    VisualizationFormLayout.addWidget(DisplayBrainMaskButton)
    
    #
    # Carotid Segmentation items
    #
    
    # type of segmentation selector
    self.CarotidSegmTypeSelector = qt.QComboBox()
    CarSegmentationFormLayout.addRow("Type:", self.CarotidSegmTypeSelector)
    self.CarotidSegmTypeSelector.addItem('Automatic Carotid segmentation', 0)
    self.CarotidSegmTypeSelector.addItem('ROI Asisted Segmentation', 1)
    
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
    DisplaySegmentation.toolTip="Displays the selected carotid segmentation "
    DisplaySegmentation.connect('clicked(bool)',self.onDisplaySegmentation)
    CarSegmentationFormLayout.addWidget(DisplaySegmentation)

    #
    # pTAC estimation items
    #
    
    # pTAC  selector
    self.pTACSelector = qt.QComboBox()
    pTACestimationFormLayout.addRow("Type:", self.pTACSelector)
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
    getpTAC.toolTip="get selected pTAC estimation"
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
    
    #Voxelwise option checkbox 
    self.KMapVoxelwiseCheckBox = qt.QCheckBox()
    self.KMapVoxelwiseCheckBox.setChecked(1)
    label = qt.QLabel('Perform voxelwise Ki estimation')
    self.KMapFormLayout.addRow(label,self.KMapVoxelwiseCheckBox)

    #K-Map Ptac input options
    label = qt.QLabel('pTAC input options')
    self.KMapPtacOptionsBox = qt.QComboBox()
    self.KMapPtacOptionsBox.addItem('Use last estimated pTAC', 0)
    self.KMapPtacOptionsBox.addItem('Load pTAC estimation from .csv', 1)
    self.KMapFormLayout.addRow(label,self.KMapPtacOptionsBox)

    #K-Map input pTAC collapsible button parameters
    KMapPtacParameters = ctk.ctkCollapsibleButton()
    KMapPtacParameters.text = "pTAC input Parameters"
    KMapPtacParameters.collapsed = 1
    self.KMapFormLayout.addWidget(KMapPtacParameters)
    KMapPtacParametersLayout = qt.QFormLayout(KMapPtacParameters)
    
    self.KMapPtacParametersWidget=ParametersWidget(KMapPtacParameters)
    self.KMapPtacParametersWidget.CreateKMpTACParameters(0)
    self.KMapPtacOptionsBox.currentIndexChanged.connect(self.onKMapPtacOptionsChanged)
    
    #K-Map Region selection input options
    label = qt.QLabel('Region of interest input options')
    self.KMapMaskOptionsBox = qt.QComboBox()
    self.KMapMaskOptionsBox.addItem('Use Automatic Brain Mask', 0)
    self.KMapMaskOptionsBox.addItem('Input Labelmap', 1)
    self.KMapMaskOptionsBox.addItem('Input ROI', 2)
    self.KMapFormLayout.addRow(label,self.KMapMaskOptionsBox)
    #K-Map input Mask collapsible button parameters
    KMapMaskParameters = ctk.ctkCollapsibleButton()
    KMapMaskParameters.text = "Mask input Parameters"
    KMapMaskParameters.collapsed = 1
    self.KMapFormLayout.addWidget(KMapMaskParameters)
    KMapMaskParametersLayout = qt.QFormLayout(KMapMaskParameters)
    
    self.KMapMaskParametersWidget=ParametersWidget(KMapMaskParameters)
    self.KMapMaskParametersWidget.CreateKMapParameters(0)
    self.KMapMaskOptionsBox.currentIndexChanged.connect(self.onKMapMaskOptionsChanged)
    
    #
    # Apply KMap Estimation button
    #
    self.ApplyKMap = qt.QPushButton("Apply K-Map estimation")
    self.ApplyKMap.toolTip="Applies K-Map estimation"
    self.ApplyKMap.connect('clicked(bool)',self.onApplyKmap)
    self.KMapFormLayout.addWidget(self.ApplyKMap)
    
    #
    # pTAC estimation csv file output
    #
    self.pTACcsvOutputFileDialog = qt.QFileDialog()
    self.pTACcsvOutputFileDialog.setNameFilter("CSV (*.csv)")
    self.pTACcsvOutputFileDialog.setDefaultSuffix('csv')
    self.pTACcsvOutputFileDialog.fileSelected.connect(self.onpTACcsvOutputFileChanged)
    
    #Apply All
    self.ApplyKMap_all = qt.QPushButton("Apply K-Map estimation")
    self.ApplyKMap_all.toolTip="Applies K-Map estimation"
    self.ApplyKMap_all.enabled = True
    self.layout.addWidget(self.ApplyKMap_all)
    # connections
    self.ApplyKMap_all.connect('clicked(bool)', self.onApplyKmap)
    # Add vertical spacer
    self.layout.addStretch(1)

  def onImportVenousSampleButtonClicked(self):
    self.ImportVenousSampleFile.show()
      
  def onImportVenousSampleFileChanged(self,filename):
    t,pTAC =self.lastLogic.readCSVsamples(filename)
    self.VenousSamplepTAC=pTAC
    self.VenousSampleTime=t

        
  def onInputChanged(self):
    self.mvNode = self.mvSelector.currentNode()
    if self.mvNode != None:
      Helper.SetBgFgVolumes(self.mvNode.GetID(), None)
      nFrames = self.mvNode.GetNumberOfFrames()
      self.frameSlider.minimum = 0
      self.frameSlider.maximum = nFrames-1
      self.lastLogic.loadData(self.mvNode)
      self.onSliderChanged()
      self.onCarotidSegmSelector()
      self.onpTACestSelector()
  
  def onSliderChanged(self):
    nframe = int(self.frameSlider.value)
    if self.mvNode != None :
        mvDisplay = self.mvNode.GetDisplayNode()
        mvDisplay.SetFrameComponent(nframe)
        data=slicer.util.array(self.mvNode.GetID())
        minimumValue =numpy.int(data[:,:,:,nframe].min())
        maximumValue =numpy.int(data[:,:,:,nframe].max())  
        mvDisplay.SetAutoWindowLevel(0)
        mvDisplay.SetWindowLevelMinMax(minimumValue,maximumValue)
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
    if self.mvNode != None :
        Helper.SetBgFgVolumes(self.mvNode.GetID(), None)
        
    BrainMaskVolume = self.lastLogic.getBrainMaskVolume()
    BrainMaskVolume.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(BrainMaskVolume)
    
    self.foregroundVolumeNode=BrainMaskVolume
    self.setForeground()
    
    #3D volume
    logic = slicer.modules.volumerendering.logic()
    displayNode = logic.CreateVolumeRenderingDisplayNode()
    slicer.mrmlScene.AddNode(displayNode)
    displayNode.UnRegister(logic)
    logic.UpdateDisplayNodeFromVolumeNode(displayNode, BrainMaskVolume)
    BrainMaskVolume.AddAndObserveDisplayNodeID(displayNode.GetID())
          
  def onCarotidSegmSelector(self):
    self.CarSegmParameters.CSdestroy()
    index = self.CarotidSegmTypeSelector.currentIndex
    if index < 0:
            return
    self.CarSegmParameters.CreateCSParameters(index)
    if self.mvNode != None :
        Helper.SetBgFgVolumes(self.mvNode.GetID(), None)
        nFrames = self.mvNode.GetNumberOfFrames()
        self.CarSegmParameters.CSwidgets[-1].setChecked(1)
        self.CarSegmParameters.CSwidgets[-3].maximum = nFrames-1
    self.CarSegmType = index
          
  def onDisplaySegmentation(self):
    index = self.CarotidSegmTypeSelector.currentIndex
    if index == 0:
            roi = None
    if index == 1:
            roi = self.CarSegmParameters.CSwidgets[1].currentNode()
    FrameForSegm = None
    if self.CarSegmParameters.CSwidgets[-4].isChecked() :
        FrameForSegm = self.CarSegmParameters.CSwidgets[-3].value
        FrameForSegm = int(FrameForSegm)
        
    CarotidMask = self.lastLogic.applyCarotidSegmentation(self.mvNode,roi,FrameForSegm)
    CarotidMask.SetScene(slicer.mrmlScene)
    slicer.mrmlScene.AddNode(CarotidMask)
    self.csvSelector.setCurrentNode(CarotidMask)
    self.foregroundVolumeNode=CarotidMask
    self.setForeground()
    
    logic2 = slicer.modules.volumerendering.logic()
    displayNode2 = logic2.CreateVolumeRenderingDisplayNode()
    slicer.mrmlScene.AddNode(displayNode2)
    displayNode2.UnRegister(logic2)
    logic2.UpdateDisplayNodeFromVolumeNode(displayNode2,CarotidMask)
    CarotidMask.AddAndObserveDisplayNodeID(displayNode2.GetID())
    
    if self.CarSegmParameters.CSwidgets[-1].isChecked() :
            mCar = self.lastLogic.mCar
            mTis = self.lastLogic.mTis
            frameTime = self.lastLogic.frameTime
            if not(self.Chart):
                self.lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
                self.cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
                self.cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
                self.Chart = True
            else :
                self.cn.ClearArrays()  
            self.lastLogic.iniChart('Mean Activity of Tissue and Vascular regions','time (s)','value (Bq/ml)',self.lns,self.cvns,self.cn)
            self.lastLogic.addChart(frameTime,mTis,'Mean Tissue Activity',self.cn,self.cvns)
            self.lastLogic.addChart(frameTime,mCar,'Mean Vascular Activity',self.cn,self.cvns)

  def onpTACestSelector(self) :
    index = self.pTACSelector.currentIndex
    self.pTACestParameters.pTACdestroy()
    if index < 0:
            return
        
    self.pTACestParameters.CreatepTACParameters(index)
    #Caso IDIF
    if (self.lastLogic.Carotids_array_Mask != []) & (index == 0) :
            self.pTACestParameters.pTACwidgets[1].setChecked(1)
            if (self.VenousSamplepTAC != []) & (self.VenousSampleTime != []) :
                self.pTACestParameters.pTACwidgets[3].setChecked(1)
                
    self.pTACEstType = index
    
  def onGetpTAC(self) :
    index = self.pTACSelector.currentIndex
    if index < 0:
        return          
    
    #IDIF Estimation
    if (index == 0) :
        if (self.lastLogic == None) | (not(self.pTACestParameters.pTACwidgets[1].isChecked())) | (not(self.lastLogic.CarSegm)) :
            self.onDisplaySegmentation()
        
        #IDIF Initial Estimator
        InitEstimator = self.pTACestParameters.pTAC_IDIF_ButtG[1].checkedId()
        
        #Case +2 samples and no enough samples provided
        if (InitEstimator == 3) & (min(self.VenousSamplepTAC.size,self.VenousSampleTime.size)<2):
            print ('You must provide two or more samples')
            return
        
        #without venous samples
        if not(self.pTACestParameters.pTACwidgets[3].isChecked()) :
            frameTime, pTAC, name= self.lastLogic.pTACestimationIDIF(None,None,InitEstimator)
        #With venous samples
        else :
            if (self.VenousSamplepTAC.size == 0) | (self.VenousSampleTime.size == 0) :
                print('A venous sample file was not loaded')
                return
            frameTime, pTAC,name = self.lastLogic.pTACestimationIDIF(self.VenousSampleTime,self.VenousSamplepTAC,InitEstimator)
    #Hunter              
    if (index == 1) :
        if (self.VenousSamplepTAC.size == 0) | (self.VenousSampleTime.size == 0) :
            print('A venous sample file was not loaded')
            return
        Dosage = self.pTACestParameters.pTACwidgets[1].value
        LeanWeight = self.pTACestParameters.pTACwidgets[3].value
        frameTime, pTAC,name = self.lastLogic.PBIFhunter(Dosage, LeanWeight, self.VenousSamplepTAC,self.VenousSampleTime)
    
    #CHART
    if not(self.Chart):
        self.lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
        self.cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
        self.cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
        self.Chart = True
    else :
        self.cn.ClearArrays()
        
    self.lastLogic.iniChart('Estimated pTAC','time (s)','Activity (Bq/gr)',self.lns,self.cvns,self.cn)
    self.lastLogic.addChart(frameTime,pTAC,name,self.cn,self.cvns)
      
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
    t,pTAC =self.lastLogic.readCSVsamples(filename)
    self.KMappTACSamplespTAC=pTAC
    self.KMappTACSamplesTime=t
      
  def onKMapPtacOptionsChanged(self,index):
    self.KMapPtacParametersWidget.KMpTACDestroy()
    if index < 0:
      return
    self.KMapPtacParametersWidget.CreateKMpTACParameters(index)
    if index == 1: #Make the connections
        self.KMapPtacParametersWidget.KMwidgets[1].connect('clicked(bool)',self.oncsvInputKMapFileButtonClicked) #connect the button 
        self.KMapPtacParametersWidget.KMwidgets[2].fileSelected.connect(self.oncsvInputKMapFileChanged)
        
  def onKMapMaskOptionsChanged(self,index):
    self.KMapMaskParametersWidget.KMapdestroy()
    if index < 0:
      return
    self.KMapMaskParametersWidget.CreateKMapParameters(index)  
    
  def onApplyKmap(self):
    #Check if a pTAC estimation has been obtained
    if (self.lastLogic.pTAC_est.size == 0):
        self.onGetpTAC()
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
    if self.KMapMaskOptionsBox.currentIndex ==0: #automatic brain mask
        MaskOption='Auto'
    elif self.KMapMaskOptionsBox.currentIndex ==1: #Mask from labelmap
        MaskOption='Labelmap'
        Mask=self.KMapMaskParametersWidget.KMapwidgets[1].currentNode()
    elif self.KMapMaskOptionsBox.currentIndex ==2: #Mask from ROI
        MaskOption='ROI'
        Mask=self.KMapMaskParametersWidget.KMapwidgets[1].currentNode()
    bool_voxelwise=self.KMapVoxelwiseCheckBox.isChecked()
    KMap,h_v,h_i=self.lastLogic.applyKMapEstimation(pTACOption, pTAC,tpTAC, MaskOption, Mask,bool_voxelwise)

    KMap.SetScene(slicer.mrmlScene)
    KMap.SetName("Ki Estimation Volume")
    slicer.mrmlScene.AddNode(KMap)
    self.foregroundVolumeNode=KMap
    self.setForeground()
    
    
        #CHART
    if not(self.Chart):
        self.lns = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode')
        self.cvns = slicer.mrmlScene.GetNodesByClass('vtkMRMLChartViewNode')
        self.cn = slicer.mrmlScene.AddNode(slicer.vtkMRMLChartNode())
        self.Chart = True
    else :
        self.cn.ClearArrays()
    if bool_voxelwise:
        self.lastLogic.iniChart('Ki Histogram','Ki (10^-6/s) ','Probability density function',self.lns,self.cvns,self.cn)
        self.lastLogic.addChart(h_v,h_i,'Ki Histogram',self.cn,self.cvns)

      
  def onpTACcsvOutputFileChanged(self,t):
    self.outputcsvDir=t
      
  def onpTACcsvOutputFileButtonClicked(self):
    self.pTACcsvOutputFileDialog.show()
    
  def setForeground(self):
    # Set the background volume 
    redWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeRed")
    redWidgetCompNode.SetForegroundVolumeID(self.foregroundVolumeNode.GetID())
    redWidgetCompNode.SetForegroundOpacity(0.5)
    redNode=slicer.util.getNode("vtkMRMLSliceNodeRed")
    redNode.SetSliceVisible(True)

    greenWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeGreen")
    greenWidgetCompNode.SetForegroundVolumeID(self.foregroundVolumeNode.GetID())
    greenWidgetCompNode.SetForegroundOpacity(0.5)
    greenNode=slicer.util.getNode("vtkMRMLSliceNodeGreen")
    greenNode.SetSliceVisible(True)

    yellowWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeYellow")
    yellowWidgetCompNode.SetForegroundVolumeID(self.foregroundVolumeNode.GetID())
    yellowWidgetCompNode.SetForegroundOpacity(0.5)  
    yellowNode=slicer.util.getNode("vtkMRMLSliceNodeGreen")
    yellowNode.SetSliceVisible(True)
    
    dNode = self.foregroundVolumeNode.GetDisplayNode()
    data=vtk.util.numpy_support.vtk_to_numpy(self.foregroundVolumeNode.GetImageData().GetPointData().GetScalars())
    minimumValue =max(0,data[data>0].min()/2)
    maximumValue =data.max()  
    dNode.SetAutoWindowLevel(0)
    dNode.SetThreshold(minimumValue,maximumValue+0.5)
    dNode.SetWindowLevelMinMax(minimumValue,maximumValue+0.5)
    colorMapNode=slicer.util.getNode("ColdToHotRainbow")
    dNode.SetAndObserveColorNodeID(colorMapNode.GetID())
    dNode.ApplyThresholdOn()
      
class dPetBrainQuantificationLogic:

  def __init__(self, parent=None):
    self.parent = parent
    self.DataMatrix = numpy.array([])
    self.frameTime= numpy.array([])
    self.Dim = None 
    self.BrainMask = None
    self.Carotids_array_Mask = numpy.array([])
    self.mTis = numpy.array([])
    self.mCar = numpy.array([])
    self.pTAC_est = numpy.array([])
    self.scalarVolumeTemplate = None
    self.numInitshort=None
    self.numEndshort=None
    self.GainCC = 0
    self.CarSegm = False
    
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
    extract.SetInputData(mvImage)
    extract.SetComponents(frameId)
    extract.Update()
    frameVolume.SetAndObserveImageData(extract.GetOutput())
    
    #Set Name
    frameName = 'Frame_ref'+str(frameId)
    frameVolume.SetName(frameName)

    return frameVolume
  
  def applyCarotidSegmentation(self,mvNode,roi,FrameForSegm) :
    #Check mvNode
    if mvNode == None :
            print('No multivolume selected')
            return
    
    #segmentation type default Auto     
    segmType = 0
    
    #First frames min<90
    firstFr = self.frameTime[self.frameTime < self.frameTime [0] + 90].argmax()
    
    ##########################
    # Automatic Segmentation #
    ##########################
    
    if roi == None :
      #Mean Brain activity and Variance
      CVar = numpy.var(self.DataMatrix[:,self.BrainMask>0],axis = 1)
      #peak index
      peak_index = CVar[0:firstFr+1].argmax()
      
      ###############
      #Clasification#
      ###############
      #Generic pTAC
      pTAC_gen = self.genpTAC(self.frameTime,peak_index)
      #Acumulate until peak (or use specified frame) & get correlation of each voxel with pTAC_gen
      if FrameForSegm == None :
          acData = self.accumulate_array(self.DataMatrix,0,peak_index,None)
      else :
          acData = self.DataMatrix[FrameForSegm,:]

      
      #Otsu Double Threshold 
      OtsuDTFilter = SimpleITK.OtsuMultipleThresholdsImageFilter()
      OtsuDTFilter.SetNumberOfThresholds(2)
      OtsuDTFilter.SetNumberOfHistogramBins(300)
      Im_acData = numpy.reshape(acData,self.Dim)
      ITKImOtsu = OtsuDTFilter.Execute(SimpleITK.GetImageFromArray(Im_acData))
      DTOtsu_array = SimpleITK.GetArrayFromImage(ITKImOtsu)
      DTOtsu_array = DTOtsu_array.reshape(-1)
      
      #Correlation
      IntensityMask = numpy.zeros(DTOtsu_array.size)
      IntensityMask[(DTOtsu_array > 1)] = 1
      aCorrelation = self.corrDatapTAC(self.DataMatrix,IntensityMask,pTAC_gen)
      #Correlation threshold is 50% 
      CorrUm = 0.5
      Carotids_array_Mask = numpy.zeros(aCorrelation.size)
      Carotids_array_Mask[(aCorrelation>CorrUm) & (DTOtsu_array == 2)] = 1
            
            
    ##########################
    # ROI Based segmentation #
    ##########################
    
    if roi != None :
      #segmentatio type
      segmType = 1
      #Get ROI Data
      frameVolume = self.extractFrame(mvNode,0)
      array_ROIMask = self.Roi2MapArray(frameVolume,roi)
      array_ROIMask = array_ROIMask.reshape(-1)
      array_ROIData = numpy.zeros(self.DataMatrix.shape)
      array_ROIData[:] = self.DataMatrix
      array_ROIData[:,array_ROIMask == 0] = 0
      
      #find peak
      CVar = numpy.var(array_ROIData[:,array_ROIMask>0],axis = 1)
      #peak index
      peak_index = CVar[0:firstFr+1].argmax()
      #print('peak_index :',peak_index)
      #Acumulate until peak (or use specified frame) 
      if FrameForSegm == None :
          acData = self.accumulate_array(self.DataMatrix,0,peak_index,None)
      else :
          acData = self.DataMatrix[FrameForSegm,:]
      #Otsu     
      sigUm = self.OtsuThreshold(acData[(array_ROIMask>0) & (acData>0)] ,200,None,None)
      Carotids_array_Mask = numpy.zeros(array_ROIMask.shape)
      Carotids_array_Mask[(acData > sigUm) & (array_ROIMask>0)] = 1
    
    ###########        
    # Filters #
    ###########        
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

    Dilate = SimpleITK.BinaryDilateImageFilter()
    Dilate.Ball
    Dilate.SetKernelRadius([2,2,2])
    DilateImg = Dilate.Execute(SimpleITK.GetImageFromArray(Carotids_array_Mask))
    Dilate_array = SimpleITK.GetArrayFromImage(DilateImg)
    Dilate_array[Carotids_array_Mask > 0] = 2
    Carotids_array_Mask = Dilate_array.reshape(-1)
        
    self.mTis = numpy.mean(self.DataMatrix[:,Carotids_array_Mask==1],axis = 1)
    self.mCar = numpy.mean(self.DataMatrix[:,Carotids_array_Mask==2],axis = 1)
               
    #
    #Mask Volume
    #
    self.Carotids_array_Mask = Carotids_array_Mask
    Mask = self.extractFrame(mvNode,0)
    name = 'Carotid Mask'
    Mask.SetName(name)
    Mask_Image = Mask.GetImageData()
    Mask_array = vtk.util.numpy_support.vtk_to_numpy(Mask_Image.GetPointData().GetScalars())
    Mask_array[:] = self.Carotids_array_Mask
    Mask_Image.Modified()
    #Segmentation Done
    self.CarSegm = True
    
    #hot voxels index
    peak_index = self.mCar[0:firstFr+1].argmax()
    sortPeakCarotid = self.DataMatrix[peak_index,Carotids_array_Mask == 2].argsort()
    minIndex = -1 * int(sortPeakCarotid.size*0.05)
    self.hotvoxelsindex = sortPeakCarotid[minIndex:]
    
    return Mask
       
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
      self.DataMatrix[i,:] = DataArray.reshape(-1)
      self.frameTime[i] = float(frTimeStr[i])
      # DICOM multivolume doesnt specify scan start time, assume first frame = length than second
      if frameUnits == 'ms':
        self.frameTime[i] = self.frameTime[i] / 1000
    #FrameTime origin for DICOM
    if frameUnits == 'ms':
      deltaF1 = self.frameTime[1] - self.frameTime[0]
      self.frameTime = self.frameTime + deltaF1 - self.frameTime[0]
    self.frameTime = numpy.array(self.frameTime)
    #print('Frame times ', self.frameTime) 
    
    #
    # Get Brain Mask
    #
    
    #frame Delta
    frameDelta = numpy.zeros(self.frameTime.size)
    frameDelta[:] = self.frameTime
    frameDelta[1:] = frameDelta[1:] - self.frameTime[0:-1]
    frameDelta[0] = frameDelta[1]
    AcumulateBrain_array = self.accumulate_array(self.DataMatrix,self.frameTime.size-5,self.frameTime.size - 1,frameDelta)
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
    BrainMask_array[BrainMask_array < 2] = 0
    BrainMask_array[BrainMask_array == 2] = 1
    BrainMask_ITKim = SimpleITK.GetImageFromArray(BrainMask_array)
    
    
    #BinaryOpening By Reconstruction (eliminate small elements)
    BinOpRec = SimpleITK.BinaryOpeningByReconstructionImageFilter()
    BinOpRec.SetKernelType(BinOpRec.Ball)
    BinOpRec.SetKernelRadius([5,5,5])
    BinOpRec.SetForegroundValue(1)
    BinOpRec.SetBackgroundValue(0)
            
    BrainMask_ITKim = BinOpRec.Execute(BrainMask_ITKim)
    
    BrainMask_ITKim = SimpleITK.BinaryMorphologicalClosing(BrainMask_ITKim , [5, 5, 5])
    BrainMask_ITKim = SimpleITK.BinaryFillhole(BrainMask_ITKim)
    self.BrainMask = SimpleITK.GetArrayFromImage(BrainMask_ITKim)
    self.BrainMask = self.BrainMask.reshape(-1)
    
    #
    # GET scalarVolumeTemplate
    #
    
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
    return Um
  
  def accumulate_array(self,array,r_min,r_max,w) :
    if r_min == None :
            r_min = 0
    if r_max == None :
            r_max = array[:,1].size - 1
    if w == None :
            k = (r_max + 1 - r_min)
            w = numpy.ones(array[0,:].size)*k
            
    acArray = numpy.zeros(array[0,:].size)
    for i in range(r_min,r_max + 1) :
            acArray = acArray + (array[i,:]/w[i])
    return acArray
    
  def corrDatapTAC(self,array_Data,Mask,pTAC_gen) :
    Corr = numpy.zeros(array_Data[0,:].size)
    #Correlation Mask elements.
    CorrAux = numpy.zeros(Corr[Mask == 1].size)
    #Data Mask elements
    array_Data_aux = numpy.zeros(array_Data[:,Mask == 1].size)
    array_Data_aux = array_Data[:,Mask == 1]
    Ip = pTAC_gen.argmax()
    M = array_Data_aux[Ip,:].mean()
    pTAC_gen = M*pTAC_gen/pTAC_gen[Ip]
    for i in range(CorrAux.size) :
            CorrCoef = numpy.corrcoef(array_Data_aux[:,i],pTAC_gen)
            CorrAux[i] = CorrCoef[0,1]   
    CorrAux[numpy.isnan(CorrAux)] = -1;
    Corr[Mask == 1] = CorrAux
    #print('Termino de calcular correlacion correlacion va desde ',Corr.min(),'Hasta ',Corr.max())
    return Corr
      
  def genpTAC(self,Time,Ip):
      pTAC = numpy.zeros(Time.shape)
      Time = Time - Time[0]
      A1 = 30000
      A2 = 4637
      A3 = 8768
      b1 = -9/60
      b2 = -0.3/60
      b3 = -0.012/60
      for i  in range(Time.size) :
          
          #line to peak
          
          if (Time[i]<=Time[Ip]) &  (Time[i] >= (Time[Ip]-20)):
              pTAC[i] = (A1+A2+A3)*(Time[i] - Time[Ip] + 20)/20;
         #Tail      
          if (Time[i]> (Time[Ip])) :
              pTAC[i]  = A1* numpy.exp(b1*(Time[i]-Time[Ip])) + A2 * numpy.exp(b2*(Time[i]-Time[Ip])) + A3 * numpy.exp(b3*(Time[i]-Time[Ip]))
      return pTAC
    
  def iniChart(self,title,xlabel,ylabel,lns,cvns,cn):
    # Switch to a layout (24) that contains a Chart View to initiate the construction of the widget and Chart View Node
    lns.InitTraversal()
    ln = lns.GetNextItemAsObject()
    ln.SetViewArrangement(24)
    # Get the Chart View Node
    cvns.InitTraversal()
    cn.SetProperty('default', 'title', title)
    cn.SetProperty('default', 'xAxisLabel', xlabel)
    cn.SetProperty('default', 'yAxisLabel', ylabel)
    cvn = cvns.GetNextItemAsObject()
    cvn.SetChartNodeID(cn.GetID())
    
  def addChart(self,x,y,Name,cn,cvns):
    dn = self.setDoubleArrayNode(x, y,Name)    
    cn.AddArray(Name, dn.GetID())
    
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


  def pTACestimationIDIF(self,sampleTime,samples,InitEst) :
    #
    #Get Corrected HotVoxels
    #
    CarotidData = self.DataMatrix[:,self.Carotids_array_Mask == 2]
    hotVoxelvalues = numpy.mean(CarotidData[:,self.hotvoxelsindex] ,axis=1)
    hotVoxelvalues = self.correctHotVoxels(hotVoxelvalues,self.mTis,self.mCar)
    name = ' IDIF '
         
    nsamples = 0
    if (samples != None) & (sampleTime != None):
        nsamples = min(samples.size,sampleTime.size)
        samples = numpy.array(samples)
        sampleTime = numpy.array(sampleTime)
        
    ############################
    # HotVoxel or Hunters Tail #
    ############################
    
    if (samples == None) | (sampleTime == None) | (nsamples < 2) | (InitEst < 3):

        #Check if InitEst is 1 (HV) or 2 (Hunter tail).
        b_expTail = None
        if (InitEst == 2) :
            b_expTail = -float(0.0125/60)
            name = name + 'Hunter '
        else:
            name = name + 'HotVoxel'
            
        #pTAC Estimation.
        self.pTAC_est = self.estimatepTACgen(self.mTis,self.mCar,self.frameTime,hotVoxelvalues,b_expTail)
        
    ############################
    # Two or more samples Tail #
    ############################
    if (nsamples > 1) & (InitEst == 3) :
        Ip = hotVoxelvalues[self.frameTime<self.frameTime[0] + 90].argmax()
        a,b = self.fitOneExp((sampleTime - self.frameTime[Ip]), samples)
        self.pTAC_est = self.estimatepTACgen(self.mTis,self.mCar,self.frameTime,hotVoxelvalues,b)
        #self.pTAC_est = self.estimatepTACvSamples(self.mTis,self.mCar,self.frameTime,sampleTime,samples)
        name = name + ' w/+2 samples'
    
    ##############################################
    #Scale pTAC with venous samples (if provided).
    ##############################################
    if (nsamples > 0) :
        Ip = hotVoxelvalues[self.frameTime<self.frameTime[0] + 90].argmax()
        #Fit exp Tail
        TailIndex = self.frameTime>self.frameTime[Ip]+1200
        TailTimes = self.frameTime[TailIndex == 1]
        TailpTAC = self.pTAC_est[TailIndex == 1]
        a,b = self.fitOneExp(TailTimes,TailpTAC)
        #Calculate CC Gain
        G = samples/ (a*numpy.exp(b*sampleTime))
        G = numpy.mean(G)
        self.GainCC = G
        #Scale pTAC
        self.pTAC_est = G*self.pTAC_est
        
        if InitEst<3:
            name = name + 'w/ samples'
        
            
    return self.frameTime,self.pTAC_est,name
    
  def correctHotVoxels(self,hotvoxel,mTiss,mCar):
      Corr_HV = hotvoxel
      for i in range(hotvoxel.size) :
          if mTiss[i] > mCar[i] :
              Corr_HV[i] = hotvoxel[i]*mCar[i]/mTiss[i]
              
      return Corr_HV
                
  def estimatepTACgen(self,mTis,mCar,Time,hotVoxelvalues,b):
    #GET PEAK & TAIL INDEX 
    Ip = hotVoxelvalues[Time<Time[0] + 90].argmax()
    TailIndex = Time>Time[Ip]+1200
    
    #HotVoxels exponential Tail.
    aHV,bHV = self.fitOneExp(Time[TailIndex == 1] - Time[Ip],hotVoxelvalues[TailIndex == 1])
    
    #Possible spill in values
    K = numpy.linspace(0,1,300)
    DS = numpy.ones(K.shape)
    if b == None :
        b = bHV
    
    #Find the best K (SP)
    i = 0
    Positive = True
    while (i<K.size) &  (Positive) :
        ki = K[i]
        pTAC_est = (mCar - ki*mTis)
        if (pTAC_est[Ip:].min() > 0) :
            A,L = self.fitOneExp(Time[TailIndex == 1] - Time[Ip],pTAC_est[TailIndex == 1])
            DS[i] = abs(float(L) - float(b)) 
        else :
            Positive = False
        i = i + 1
    #Min SP#
    DSf = DS[0:i-1]
    Ind = DSf.argmin()
    SP = K[Ind]
    #Estimated pTAC / SP#
    pTAC_est = (mCar - SP * mTis)
    
    #Find RC
    A,L = self.fitOneExp(Time[TailIndex == 1] - Time[Ip],pTAC_est[TailIndex == 1])
    RC = hotVoxelvalues[TailIndex == 1]/ (A*numpy.exp(L*(Time[TailIndex == 1] - Time[Ip])))
    RC = numpy.mean(RC)
    pTAC_est = RC*pTAC_est
        
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
      #print('peak_index :',peak_index)
      PeakTime = self.frameTime[peak_index]
      #print('pico pico time: ',PeakTime)
      
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
    aux=self.frameTime<PeakTime
    pTAC[aux]=0
    #print('pTAC',pTAC)
    self.pTAC_est = numpy.array(pTAC)
    self.pTAC_est.reshape(-1)
    name = 'PBIF Hunter'
    
    return self.frameTime,self.pTAC_est,name

#Patlak Functions
# FUNCIONES  A PASAR 

  def cumtrapz(self,t,y):#Trapezoidal cumulative integral
    endt=t.size-1
    auxt1=numpy.concatenate(([0],t[0:endt]),axis=1)
    deltat=t-auxt1
    endy=y.size-1
    auxy1=numpy.concatenate(([0],y[0:endy]),axis=1)
    trapecio=(y+auxy1)/2
    trapecio=trapecio*deltat
    return trapecio.cumsum()

  def patlak_voxel(self,integral,pTAC,voxel):#
    ind=(integral>0)&(voxel>0)&(pTAC>0) 
    X=numpy.array(integral[ind]/pTAC[ind]) 
    Y=numpy.array(voxel[ind]/pTAC[ind]) 
    tolerance=0.2
    #Obtain initial estimator
    if len(X)<2:
        return 0
    A = numpy.vstack([X, numpy.ones(len(X))]).T      
    K, Vo = numpy.linalg.lstsq(A, Y)[0]
    deviation=numpy.abs((Y-K*X-Vo)/Vo)
    ind=deviation<tolerance
    #Final estimator
    Y_2=numpy.array(Y[ind])
    X_2=numpy.array(X[ind])
    
    if len(X_2)<2:
       return 0
    A = numpy.vstack([X_2, numpy.ones(len(X_2))]).T      
    K, Vo = numpy.linalg.lstsq(A, Y_2)[0]
    K=numpy.max([K,0])
    return K*10**6 
    
    
  def patlak(self,array,DataMatrix,time,pTAC,Mask,bool_voxelwise):
    #Obtain pTAC integral
    integral=self.cumtrapz(time,pTAC)
    lateFrame=time>=(20*60) # frames later than 20 minutes post injection, #time is assumed to be in seconds
    indFrame=lateFrame.argmax()
    integral=integral[indFrame:]
    pTAC=pTAC[indFrame:]
    
    if bool_voxelwise:
        #Operate
        voxel=numpy.zeros_like(DataMatrix[indFrame:,0])
        aux_Mask=Mask.astype(bool)
        for i in range(aux_Mask.size-1):
            if aux_Mask[i]:
                voxel=DataMatrix[indFrame:,i]
                array[i]=self.patlak_voxel(integral,pTAC,voxel)
            else:
                array[i]=0
        return array
    else:
        #Operate
        nLabels=Mask.max()
        K_vect=numpy.zeros(nLabels+1)
        for i in range(1,nLabels+1):
            region_mean=numpy.mean(DataMatrix[indFrame:,Mask==i],axis = 1)
            K_vect[i]=self.patlak_voxel(integral,pTAC,region_mean)
            array[Mask==i]=K_vect[i]
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
    #print ValueStr
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
  
  def applyKMapEstimation(self,pTACOption,pTAC,tpTAC,MaskOption,Mask,bool_voxelwise):
    #GetpTAC 
    pTAC=self.getpTAC(pTACOption,pTAC,tpTAC)
    #GetMask 
    Mask=self.getMask(MaskOption,Mask)
    #generate new ScalarVolume to store the output
    KMapScalarVolume=slicer.vtkMRMLScalarVolumeNode()
    KMapScalarVolume.Copy(self.scalarVolumeTemplate)
    
    vImageData = KMapScalarVolume.GetImageData()
    array = vtk.util.numpy_support.vtk_to_numpy(vImageData.GetPointData().GetScalars())
    
    array=self.patlak(array, self.DataMatrix, self.frameTime, pTAC, Mask, bool_voxelwise)
    KMapScalarVolume.GetImageData().Modified()
    
    #Fill Holes
    KMap2ITK = SimpleITK.GetImageFromArray(array.reshape([self.Dim[2],self.Dim[1],self.Dim[0]]))
    KMap2ITK = SimpleITK.GrayscaleFillhole(KMap2ITK)
    KMap2 = SimpleITK.GetArrayFromImage(KMap2ITK)
    KMap2=KMap2.reshape(-1)
    array[array == 0] = KMap2[array == 0]
    KMapScalarVolume.GetImageData().Modified()
    
    
    self.KMap_array = numpy.zeros(array.shape)
    self.KMap_array[:] = array
    
    #Generate PDF histogram
    Hist=numpy.histogram(self.KMap_array,50,(self.KMap_array[self.KMap_array>0].min(),self.KMap_array.max()))      
    h_v = Hist[1]
    h_i = Hist[0].astype('float')
    h_i=h_i/h_i.sum()
    step = (h_v[1]-h_v[0])/2
    h_v = h_v[0:h_v.shape[0]-1]+step
    
    return KMapScalarVolume,h_v,h_i
      
  def getpTAC(self,pTACOption,pTAC,tpTAC):
    if pTACOption == 'Auto':
      return self.pTAC_est
    elif pTACOption == 'FromFile':
      if not(numpy.allclose(tpTAC,self.frameTime,rtol=0.01)): #compare the time vectors to see if they match
        print 'WARNING, sample times do not match up with frame end times, attempting interpolation, this may compromise the estimation'
        #print pTAC
        print numpy.interp(self.frameTime, tpTAC, pTAC, left=0)
        return numpy.interp(self.frameTime, tpTAC, pTAC, left=0)
      else:
        return pTAC
          
  def getMask(self,MaskOption,Mask):
    if MaskOption == 'Auto':
      return self.BrainMask.astype('bool') #brute cast to boolean
    elif MaskOption == 'Labelmap':
      MaskArray = vtk.util.numpy_support.vtk_to_numpy(Mask.GetImageData().GetPointData().GetScalars())
      MaskArray=MaskArray.reshape(-1)
      return MaskArray.astype('bool')
    elif MaskOption == 'ROI':
      MaskArray = self.Roi2MapArray(self.scalarVolumeTemplate,Mask)
      MaskArray=MaskArray.reshape(-1)
      return MaskArray.astype('bool')


      
class ParametersWidget(object):
  def __init__(self, parent=None):
    self.parent = parent
    self.CSwidgets = []
    self.pTACwidgets = []
    self.pTAC_IDIF_ButtG = []
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
    if self.CSwidgets != [] :
      for w in self.CSwidgets:
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
      carSegCheckBox.setChecked(1)
      label = qt.QLabel('Use previous carotid segmentation')
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(carSegCheckBox)           
      parametersFormLayout.addRow(carSegCheckBox,label)

      UseVenousSamplesCheckBox = qt.QCheckBox()
      UseVenousSamplesCheckBox.setChecked(0)
      label = qt.QLabel('Use venous blood samples for scale')
      self.pTACwidgets.append(label)
      self.pTACwidgets.append(UseVenousSamplesCheckBox)           
      parametersFormLayout.addRow(UseVenousSamplesCheckBox,label)
      
      ##CHECK BOXES - BUTTON GROUP##
      chk1=qt.QCheckBox()
      chk1.toolTip='chk 1 texto'
      label1=qt.QLabel('HotVoxels Tail')
      
      chk2=qt.QCheckBox()
      chk2.toolTip='chk 2 texto'
      label2=qt.QLabel('Hunters Tail')
      
      chk3=qt.QCheckBox()
      chk3.toolTip='chk 3 texto'
      label3=qt.QLabel('Two or more vsamples Tail')
      
      buttongroup=qt.QButtonGroup()
      buttongroup.addButton(chk1)
      buttongroup.addButton(chk2)
      buttongroup.addButton(chk3)
      buttongroup.setExclusive(True)
      buttongroup.setId(chk1,1)
      buttongroup.setId(chk2,2)
      buttongroup.setId(chk3,3)
      labelB = qt.QLabel('ButtonInitEstimator') 
      self.pTAC_IDIF_ButtG.append(labelB)
      self.pTAC_IDIF_ButtG.append(buttongroup)
      
      label = qt.QLabel('')
      parametersFormLayout.addRow(label)
      self.pTACwidgets.append(label)
      label = qt.QLabel('Initial pTAC estimator :')
      parametersFormLayout.addRow(label)
      self.pTACwidgets.append(label)
      parametersFormLayout.addRow(chk1,label1)
      parametersFormLayout.addRow(chk2,label2)
      parametersFormLayout.addRow(chk3,label3)
      
      self.pTACwidgets.append(label1)
      self.pTACwidgets.append(chk1)
      self.pTACwidgets.append(label2)
      self.pTACwidgets.append(chk2)
      self.pTACwidgets.append(label3)
      self.pTACwidgets.append(chk3)
      chk1.setChecked(1)
      
  
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
          
    self.parent.collapsed = 0
    #print (self.pTACwidgets)

  def pTACdestroy(self):
    if self.pTACwidgets != [] :
      for w in self.pTACwidgets:
        self.parent.layout().removeWidget(w)
        w.deleteLater()
        w.setParent(None)
    self.pTACwidgets = []
    self.pTAC_IDIF_ButtG = []
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
        
  def  KMpTACDestroy(self):
    if self.KMwidgets != [] :
      for w in self.KMwidgets:
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
    if self.KMapwidgets != [] :
      for w in self.KMapwidgets:
        self.parent.layout().removeWidget(w)
        w.deleteLater()
        w.setParent(None)
      self.KMapwidgets = []
    self.parent.collapsed = 1
