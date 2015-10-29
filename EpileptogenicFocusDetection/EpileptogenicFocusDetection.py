import os
import unittest
import numpy
from __main__ import vtk, qt, ctk, slicer
import EpileptogenicFocusDetectionLogic
import threading, time

#
# EpileptogenicFocusDetectionSliceletWidget
#
class EpileptogenicFocusDetectionSliceletWidget:
  def __init__(self, parent=None):
    try:
      parent
      self.parent = parent

    except Exception, e:
      import traceback
      traceback.print_exc()
      print("ERROR: There is no parent to EpileptogenicFocusDetectionSliceletWidget!")

#
# SliceletMainFrame
#   Handles the event when the slicelet is hidden (its window closed)
#
class SliceletMainFrame(qt.QFrame):
  def setSlicelet(self, slicelet):
    self.slicelet = slicelet

  def hideEvent(self, event):
    self.slicelet.disconnect()

    import gc
    refs = gc.get_referrers(self.slicelet)
    if len(refs) > 1:
      print('Stuck slicelet references (' + repr(len(refs)) + '):\n' + repr(refs))

    self.slicelet.parent = None
    self.slicelet = None
    self.deleteLater()

#
# EpileptogenicFocusDetectionSlicelet
#
class EpileptogenicFocusDetectionSlicelet(object):
  def __init__(self, parent, widgetClass=None):
      
    self.backgroundVolumeNode = None
    self.SISCOMForegroundVolumeNode = None
    self.aContrarioForegroundVolumeNode = None  
      
    # Set up main frame
    self.parent = parent
    self.parent.setLayout(qt.QHBoxLayout())

    self.layout = self.parent.layout()
    self.layout.setMargin(0)
    self.layout.setSpacing(0)

    self.sliceletPanel = qt.QFrame(self.parent)
    self.sliceletPanelLayout = qt.QVBoxLayout(self.sliceletPanel)
    self.sliceletPanelLayout.setMargin(4)
    self.sliceletPanelLayout.setSpacing(0)
    self.layout.addWidget(self.sliceletPanel,1)

    # For testing only
    self.selfTestButton = qt.QPushButton("Run self-test")
    self.sliceletPanelLayout.addWidget(self.selfTestButton)
    self.selfTestButton.connect('clicked()', self.onSelfTestButtonClicked)
    self.selfTestButton.setVisible(False) # TODO: Should be commented out for testing so the button shows up

    # Initiate and group together all panels
    self.step0_layoutSelectionCollapsibleButton = ctk.ctkCollapsibleButton()
    #self.step1_loadDataCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step1_loadStudiesCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step2_RegistrationCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step3_fociDetectionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step4_saveResultsCollapsibleButton = ctk.ctkCollapsibleButton()

    self.collapsibleButtonsGroup = qt.QButtonGroup()
    self.collapsibleButtonsGroup.addButton(self.step0_layoutSelectionCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step1_loadStudiesCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step2_RegistrationCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step3_fociDetectionCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step4_saveResultsCollapsibleButton)

    self.step0_layoutSelectionCollapsibleButton.setProperty('collapsed', False)
    
    # Create module logic
    self.logic = EpileptogenicFocusDetectionLogic.EpileptogenicFocusDetectionLogic() 
    
    # Create an instance of a-contrario logic
    import EpileptogenicFocusDetectionLogic.AContrarioLogic as acl
    self.aContrarioDetection = acl.AContrarioDetection()
    
    # Set up step panels
    self.setup_Step0_LayoutSelection()
    #self.setup_Step1_LoadPlanningData()
    self.setup_Step1_LoadStudies() 
    self.setup_Step2_Registration()
    self.setup_Step3_FociDetection()
    self.setup_Step4_SaveResults()
    
    
    #creates a new layout
    self.customLayoutGridView3x3 = 1033
    self.logic.customCompareLayout(3,3,self.customLayoutGridView3x3)
    
    self.customLayoutGridView2x3 = 1023
    self.logic.customCompareLayout(2,3,self.customLayoutGridView2x3)
    
    self.logic.findEpilepsyDataInScene();
    self.aContrarioDetection.findAContrarioDataInScene();

    if widgetClass:
      self.widget = widgetClass(self.parent)
    self.parent.show()

  def __del__(self):
    self.cleanUp()
      
  def cleanUp(self):
    print('Cleaning up')   
    
  # Disconnect all connections made to the slicelet to enable the garbage collector to destruct the slicelet object on quit
  def disconnect(self):  
    print('Disconnect') 
    self.selfTestButton.disconnect('clicked()', self.onSelfTestButtonClicked)
    # Step 0
    self.step0_viewSelectorComboBox.disconnect('activated(int)', self.onViewSelect)  
    # Step 1
    self.step1_loadStudiesCollapsibleButton.disconnect('contentsCollapsed (bool)',self.onStep1_loadStudiesCollapsibleButtonClicked)
    self.activeVolumeNodeSelector.disconnect("nodeActivated (vtkMRMLNode*)", self.onActiveVolumeNodeSelectorClicked)
    self.loadBasalVolumeButton.disconnect("clicked()",self.onLoadBasalVolumeButtonClicked)
    self.loadIctalVolumeButton.disconnect("clicked()",self.onLoadIctalVolumeButtonClicked)
    self.loadMRIVolumeButton.disconnect("clicked()",self.onLoadMRIVolumeButtonClicked)
    self.resetSceneButton.disconnect('clicked()',self.onResetSceneButtonClicked)
    self.loadSceneButton.disconnect('clicked()',self.onLoadSceneButtonClicked)
    # Step 2
    self.step2_RegistrationCollapsibleButton.disconnect('contentsCollapsed (bool)',self.onStep2_RegistrationCollapsibleButtonClicked)
    self.compareBasalIctalMRIButton.disconnect('clicked()', self.onCompareBasalIctalMRIButtonClicked)
    self.registerIctalToBasalButton.disconnect('clicked()', self.onRegisterIctalToBasalButtonClicked)
    self.computeBasalAndIctalMaskButton.disconnect("clicked()",self.onComputeBasalAndIctalMaskButtonClicked)
    self.checkBasalAndIctalMaskButton.disconnect("clicked()",self.onCheckBasalAndIctalMaskButtonClicked)
    self.registerBasalToMRIButton.disconnect('clicked()', self.onRegisterBasalToMRIButtonClicked)
    # Step 3    
    self.step3_fociDetectionCollapsibleButton.disconnect('contentsCollapsed (bool)',self.onStep3_fociDetectionCollapsibleButtonClicked)
    self.step3A_SISCOMDetectionCollapsibleButton.disconnect('contentsCollapsed (bool)',self.onStep3A_SISCOMDetectionCollapsibleButtonClicked)
    self.step3B_AContrarioDetectionCollapsibleButton.disconnect('contentsCollapsed (bool)',self.onStep3B_AContrarioDetectionCollapsibleButtonClicked)
    self.step3C_CompareDetectionsCollapsibleButton.disconnect('contentsCollapsed (bool)',self.onStep3C_CompareDetectionsCollapsibleButtonClicked)
    self.aContrarioDetectionButton.disconnect('clicked()', self.onAContrarioDetectionButtonClicked)
    self.SISCOMDetectionButton.disconnect('clicked()', self.onSubtractionDetectionButtonClicked)
    self.compareDetectionsButton.disconnect('clicked()', self.onCompareDetectionsButtonClicked)
    self.stdDevSISCOMSlider.disconnect('valueChanged(double)', self.onStdDevSISCOMSliderClicked)
    self.siscomOverlayButton.disconnect('clicked()', self.onSiscomOverlayButtonClicked)
    self.siscomHideOverlayButton.disconnect('clicked()', self.onSiscomHideOverlayButtonClicked)
    self.aContrarioOverlayButton.disconnect('clicked()', self.onAContrarioOverlayButtonClicked)
    self.aContrarioHideOverlayButton.disconnect('clicked()', self.onAContrarioHideOverlayButtonClicked)
    self.cancelAContrarioButton.disconnect('clicked()', self.onCancelAContrarioButtonClicked)
    self.aContrarioDefaultParametersButton.disconnect('clicked',self.setAContrarioDefaultParameters())    
    # Step 4
    self.saveResultsButton.disconnect('clicked()',self.onSaveResultsButtonClicked)

  def setup_Step0_LayoutSelection(self):
    # Layout selection step
    self.step0_layoutSelectionCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step0_layoutSelectionCollapsibleButton.text = "Layout Selector"
    self.sliceletPanelLayout.addWidget(self.step0_layoutSelectionCollapsibleButton)
    self.step0_layoutSelectionCollapsibleButtonLayout = qt.QFormLayout(self.step0_layoutSelectionCollapsibleButton)
    self.step0_layoutSelectionCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step0_layoutSelectionCollapsibleButtonLayout.setSpacing(4)

    self.step0_viewSelectorComboBox = qt.QComboBox(self.step0_layoutSelectionCollapsibleButton)
    self.step0_viewSelectorComboBox.addItem("Four-up 3D + 3x2D view")
    self.step0_viewSelectorComboBox.addItem("Conventional 3D + 3x2D view")
    self.step0_viewSelectorComboBox.addItem("3D-only view")
    self.step0_viewSelectorComboBox.addItem("Axial slice only view")
    self.step0_viewSelectorComboBox.addItem("Double 3D view")
    self.step0_viewSelectorComboBox.addItem("3x3 compare view")
    self.step0_layoutSelectionCollapsibleButtonLayout.addRow("Layout: ", self.step0_viewSelectorComboBox)
    self.step0_viewSelectorComboBox.connect('activated(int)', self.onViewSelect)

    # Add layout widget
    self.layoutWidget = slicer.qMRMLLayoutWidget()
    self.layoutWidget.setMRMLScene(slicer.mrmlScene)
    self.parent.layout().addWidget(self.layoutWidget,2)
    self.onViewSelect(0)
    
    
  def setup_Step1_LoadStudies(self):
    # Step 1: Load studies panel
    self.step1_loadStudiesCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step1_loadStudiesCollapsibleButton.text = "1. Load studies"
    self.sliceletPanelLayout.addWidget(self.step1_loadStudiesCollapsibleButton)
    self.step1_loadStudiesCollapsibleButtonLayout = qt.QFormLayout(self.step1_loadStudiesCollapsibleButton)
    self.step1_loadStudiesCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step1_loadStudiesCollapsibleButtonLayout.setSpacing(4)
    

    
    # Step 1/A): Load the inter ictal SPECT    
    # Buttons to connect
    self.loadBasalVolumeButton = qt.QPushButton("Load basal volume")
    # Add to the widget
    self.step1_loadStudiesCollapsibleButtonLayout.addRow("Load basal volume:",self.loadBasalVolumeButton)

    # Step 1/B): Load ictal SPECT
    # Buttons to connect
    self.loadIctalVolumeButton = qt.QPushButton("Load ictal volume")    
    # Add to the widget
    self.step1_loadStudiesCollapsibleButtonLayout.addRow("Load ictal volume:", self.loadIctalVolumeButton)
    
    # Step 1/C): Load MRI
    # Buttons to connect
    self.loadMRIVolumeButton = qt.QPushButton("Load MRI volume")   
    # Add to the widget
    self.step1_loadStudiesCollapsibleButtonLayout.addRow("Load MRI volume:", self.loadMRIVolumeButton)
    
    self.visualizationFrame = qt.QFrame()
    self.visualizationFrame.setLayout(qt.QVBoxLayout())
    visualizationLayout = self.visualizationFrame.layout()
    
    # Active Volume Frame
    self.activeVolumeFrame = qt.QFrame()
    self.activeVolumeFrame.setLayout(qt.QHBoxLayout())
    # active volume label
    self.activeVolumeLabel = qt.QLabel("Active Volume: ")
    # active volume combo box
    self.activeVolumeNodeSelector = slicer.qMRMLNodeComboBox()
    self.activeVolumeNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.activeVolumeNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.activeVolumeNodeSelector.addEnabled = False
    self.activeVolumeNodeSelector.removeEnabled = False
    self.activeVolumeNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.activeVolumeNodeSelector.setToolTip( "Choose the volume to visualize" )
    # active volume layout
    self.activeVolumeFrame.layout().addWidget(self.activeVolumeLabel)
    self.activeVolumeFrame.layout().addWidget(self.activeVolumeNodeSelector)
    
    visualizationLayout.addWidget(self.activeVolumeFrame)
    self.step1_loadStudiesCollapsibleButtonLayout.addWidget(self.visualizationFrame)
    
    
    # Reset scene
    self.resetSceneButton = qt.QPushButton("Reset Scene")
    self.step1_loadStudiesCollapsibleButtonLayout.addRow("Reset Scene:",self.resetSceneButton)
    # Load Scene
    self.loadSceneButton = qt.QPushButton("Load Scene")
    self.step1_loadStudiesCollapsibleButtonLayout.addRow("Load Scene:",self.loadSceneButton)
    # Connections
    self.activeVolumeNodeSelector.connect("nodeActivated (vtkMRMLNode*)", self.onActiveVolumeNodeSelectorClicked)
    self.loadBasalVolumeButton.connect("clicked()",self.onLoadBasalVolumeButtonClicked)
    self.loadIctalVolumeButton.connect("clicked()",self.onLoadIctalVolumeButtonClicked)
    self.loadMRIVolumeButton.connect("clicked()",self.onLoadMRIVolumeButtonClicked)
    self.resetSceneButton.connect('clicked()',self.onResetSceneButtonClicked)
    self.loadSceneButton.connect('clicked()',self.onLoadSceneButtonClicked)
    
    self.step1_loadStudiesCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep1_loadStudiesCollapsibleButtonClicked)

 

    # Connections
    #self.step1_showDicomBrowserButton.connect('clicked()', self.logic.onDicomLoad)  

  def setup_Step2_Registration(self):
    # Step 2: Ictal to Basal and Basal to MRI registration panel
    self.step2_RegistrationCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step2_RegistrationCollapsibleButton.text = "2. Registration"
    self.sliceletPanelLayout.addWidget(self.step2_RegistrationCollapsibleButton)
    self.step2_RegistrationCollapsibleButtonLayout = qt.QFormLayout(self.step2_RegistrationCollapsibleButton)
    self.step2_RegistrationCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step2_RegistrationCollapsibleButtonLayout.setSpacing(4)
   
    
    # Basal to Ictal registration button
    self.registerIctalToBasalButton = qt.QPushButton("Perform registration")
    self.registerIctalToBasalButton.toolTip = "Register Ictal volume to Basal volume"
    self.registerIctalToBasalButton.name = "registerIctalToBasalButton"
    self.registerIctalToBasalButton.setEnabled(False)
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Register Basal to Ictal: ', self.registerIctalToBasalButton)
    
    # Compute and check basal to ictal mask buttons 
    self.computeBasalAndIctalMaskButton = qt.QPushButton("Compute basal and ictal mask")
    self.computeBasalAndIctalMaskButton.setEnabled(False)
    self.checkBasalAndIctalMaskButton = qt.QPushButton("Check basal and ictal mask")
    self.checkBasalAndIctalMaskButton.setEnabled(False)
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Compute Basal and Ictal mask: ', self.computeBasalAndIctalMaskButton)
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Check Basal and Ictal mask: ', self.checkBasalAndIctalMaskButton)
    
    
    # Basal to MRI registration button
    self.registerBasalToMRIButton = qt.QPushButton("Perform registration")
    self.registerBasalToMRIButton.toolTip = "Register Basal volume to MRI volume"
    self.registerBasalToMRIButton.name = "registerBasalToMRIButton"
    self.registerBasalToMRIButton.setEnabled(False)
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Register Basal to MRI: ', self.registerBasalToMRIButton)
    
    # Compare Basal, Ictal  and MRI button
    self.compareBasalIctalMRIButton = qt.QPushButton("Compare basal, ictal and MRI")
    self.compareBasalIctalMRIButton.toolTip = "Compare basal, ictal and MRI volumes"
    self.compareBasalIctalMRIButton.name = "compareBasalIctalMRIButton"
    self.compareBasalIctalMRIButton.setEnabled(False)
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Compare basal, ictal and MRI volumes: ', self.compareBasalIctalMRIButton)   

    # Connections
    self.step2_RegistrationCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep2_RegistrationCollapsibleButtonClicked)
    self.compareBasalIctalMRIButton.connect('clicked()', self.onCompareBasalIctalMRIButtonClicked)
    self.registerIctalToBasalButton.connect('clicked()', self.onRegisterIctalToBasalButtonClicked)
    self.computeBasalAndIctalMaskButton.connect("clicked()",self.onComputeBasalAndIctalMaskButtonClicked)
    self.checkBasalAndIctalMaskButton.connect("clicked()",self.onCheckBasalAndIctalMaskButtonClicked)
    self.registerBasalToMRIButton.connect('clicked()', self.onRegisterBasalToMRIButtonClicked)
    #self.registerObiToPlanCtButton.connect('clicked()', self.onObiToPlanCTRegistration)


  def setup_Step3_FociDetection(self):
    # Step 3: Foci Detection
    self.step3_fociDetectionCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step3_fociDetectionCollapsibleButton.text = "3. Foci Detection"
    self.sliceletPanelLayout.addWidget(self.step3_fociDetectionCollapsibleButton)
    self.step3_fociDetectionLayout = qt.QVBoxLayout(self.step3_fociDetectionCollapsibleButton)
    self.step3_fociDetectionLayout.setContentsMargins(12,4,4,4)
    self.step3_fociDetectionLayout.setSpacing(4)

    # Step 3/A): Select OBI fiducials on OBI volume
    self.step3A_SISCOMDetectionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step3A_SISCOMDetectionCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step3A_SISCOMDetectionCollapsibleButton.text = "3/A) SISCOM method"
    self.step3_fociDetectionLayout.addWidget(self.step3A_SISCOMDetectionCollapsibleButton)
    self.step3A_SISCOMDetectionCollapsibleButtonLayout = qt.QFormLayout(self.step3A_SISCOMDetectionCollapsibleButton)
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.setSpacing(4)
    
 
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Normalize registered images: ', self.createMaskButton)
    #SISCOM detection button
    self.SISCOMDetectionButton = qt.QPushButton("Perform subtraction of images")
    self.SISCOMDetectionButton.toolTip = "Perform the subtraction of the images: ictal - basal"
    self.SISCOMDetectionButton.name = "SISCOMDetectionButton"
    self.SISCOMDetectionButton.setEnabled(False)
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Foci detection: ', self.SISCOMDetectionButton)
    
    # SISCOM Threshold frame    
    self.stdDevSISCOMSlider=ctk.ctkSliderWidget()
    self.stdDevSISCOMSlider.setEnabled(False)
    
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Visualization threshold: ', self.thresholdSISCOMFrame)
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Standard deviations threshold: ', self.stdDevSISCOMSlider)
    
    
    # Overlay Widget
    self.siscomOverlayFrame = qt.QFrame()
    overlayLayout = qt.QHBoxLayout()
    self.siscomOverlayButton = qt.QPushButton("Generate")
    self.siscomOverlayButton.setEnabled(False)
    self.siscomOverlayFrame.setLayout(overlayLayout)
    rowsLabel=qt.QLabel("Rows:")
    colsLabel=qt.QLabel("Cols:") 
    self.siscomRowsText=qt.QLineEdit("3")
    self.siscomRowsText.setFixedWidth(50)
    self.siscomColsText=qt.QLineEdit("3")
    self.siscomColsText.setFixedWidth(50)
    self.siscomHideOverlayButton = qt.QPushButton("Hide")
    self.siscomHideOverlayButton.setEnabled(False)
    overlayLayout.addWidget(self.siscomOverlayButton)
    overlayLayout.addWidget(rowsLabel)
    overlayLayout.addWidget(self.siscomRowsText)
    overlayLayout.addWidget(colsLabel) 
    overlayLayout.addWidget(self.siscomColsText)
    overlayLayout.addWidget(self.siscomHideOverlayButton)
    
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow(self.siscomOverlayFrame)
   
    # Step 3/B): AContrario detection
    self.step3B_AContrarioDetectionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step3B_AContrarioDetectionCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step3B_AContrarioDetectionCollapsibleButton.text = "3/B) A Contrario method"
    self.step3_fociDetectionLayout.addWidget(self.step3B_AContrarioDetectionCollapsibleButton)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout = qt.QFormLayout(self.step3B_AContrarioDetectionCollapsibleButton)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.setSpacing(4)
    


    #A-contrario detection button
    self.aContrarioDetectionButton = qt.QPushButton("Perform a-contrario detection")
    self.aContrarioDetectionButton.toolTip = "Perform a-contrario detection"
    self.aContrarioDetectionButton.name = "aContrarioDetectionButton"
    self.aContrarioDetectionButton.setEnabled(False)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('Foci detection: ', self.aContrarioDetectionButton)
    
    #
    # Status and Progress
    #
    self.currentStatusLabel = qt.QLabel("Idle")
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('Status:',self.currentStatusLabel)

    
    self.aContrarioProgressFrame = qt.QFrame()
    self.aContrarioProgressFrame.setLayout(qt.QHBoxLayout())
    self.aContrarioProgressLayout = self.aContrarioProgressFrame.layout()    
    
    self.aContrarioProgressBar = qt.QProgressBar()
    self.aContrarioProgressBar.setRange(0,1000)
    self.aContrarioProgressBar.setValue(0)
    self.aContrarioProgressBar.show()
    self.aContrarioProgressBar.setMinimum(0)
    self.aContrarioProgressBar.setMaximum(0)
    
    self.cancelAContrarioButton = qt.QPushButton("Cancel") 
    self.suspendAContrario = False
    
    self.aContrarioProgressLayout.addWidget(self.aContrarioProgressBar)
    self.aContrarioProgressLayout.addWidget(self.cancelAContrarioButton)
    self.aContrarioProgressFrame.hide()
    
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow(self.aContrarioProgressFrame)
    
    
    
    self.aContrarioOverlayFrame = qt.QFrame()
    overlayLayout = qt.QHBoxLayout()
    self.aContrarioOverlayButton = qt.QPushButton("Generate overlay")
    self.aContrarioOverlayButton.setEnabled(False)
    self.aContrarioOverlayFrame.setLayout(overlayLayout)
    rowsLabel=qt.QLabel("Rows:")
    colsLabel=qt.QLabel("Cols:") 
    self.aContrarioRowsText=qt.QLineEdit("3")
    self.aContrarioRowsText.setFixedWidth(50)
    self.aContrarioColsText=qt.QLineEdit("3")
    self.aContrarioColsText.setFixedWidth(50)
    self.aContrarioHideOverlayButton = qt.QPushButton("Hide")
    self.aContrarioHideOverlayButton.setEnabled(False)
    overlayLayout.addWidget(self.aContrarioOverlayButton)
    overlayLayout.addWidget(rowsLabel)
    overlayLayout.addWidget(self.aContrarioRowsText)
    overlayLayout.addWidget(colsLabel) 
    overlayLayout.addWidget(self.aContrarioColsText)
    overlayLayout.addWidget(self.aContrarioHideOverlayButton)
     
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow(self.aContrarioOverlayFrame)
    
    #self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('Overlay: ', self.overlayFrame)
    self.advanced_AContrarioDetectionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.advanced_AContrarioDetectionCollapsibleButton.setProperty('collapsedHeight', 4)
    self.advanced_AContrarioDetectionCollapsibleButton.text = "Advanced"
    self.advanced_AContrarioDetectionCollapsibleButton.setProperty('collapsed', True)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow(self.advanced_AContrarioDetectionCollapsibleButton)
    #self.step3_fociDetectionLayout.addWidget(self.step3B_AContrarioDetectionCollapsibleButton)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout = qt.QFormLayout(self.advanced_AContrarioDetectionCollapsibleButton)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.setSpacing(4)
    
    # Number of scales
    self.numberOfScalesOption = qt.QDoubleSpinBox()
    self.numberOfScalesOption.setMaximum(10)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('Number of scales', self.numberOfScalesOption)
    
    self.scalesInMatrix = qt.QLineEdit()
    self.scalesOutMatrix = qt.QLineEdit()
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('Scales in:', self.scalesInMatrix)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('Scales out:', self.scalesOutMatrix)
    
    self.gridStepLineEdit = qt.QLineEdit()
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('Grid step:', self.gridStepLineEdit)
    
    self.maskThresholdParameter = qt.QDoubleSpinBox()
    self.maskThresholdParameter.setMaximum(20)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('Mask threshold', self.maskThresholdParameter)
    
    # A-contrario global parameters
    self.rKernelNoiseGlobalLineEdit = qt.QLineEdit() 
    self.epsilonMachineLineEdit = qt.QLineEdit() 
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('radio kernel noise:', self.rKernelNoiseGlobalLineEdit)
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('epsilon machine:', self.epsilonMachineLineEdit)
    
    # A-contrario local parameters
    self.rKernelNoiseLocalLineEdit = qt.QLineEdit()
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('radio kernel noise local:', self.rKernelNoiseLocalLineEdit)
    
    # Spots NFA parameters
    self.epsilonSpotsNFALineEdit = qt.QLineEdit()
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow('epsilon spots nfa:', self.epsilonSpotsNFALineEdit)
    
    self.aContrarioDefaultParametersButton = qt.QPushButton('Set default parameters')
    self.advanced_AContrarioDetectionCollapsibleButtonLayout.addRow(self.aContrarioDefaultParametersButton)
    
    self.setAContrarioDefaultParameters()
  
    
    # Step 3/C): Compare detections
    self.step3C_CompareDetectionsCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step3C_CompareDetectionsCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step3C_CompareDetectionsCollapsibleButton.text = "3/C) Compare detections"
    self.step3_fociDetectionLayout.addWidget(self.step3C_CompareDetectionsCollapsibleButton)
    self.step3C_CompareDetectionsCollapsibleButtonLayout = qt.QFormLayout(self.step3C_CompareDetectionsCollapsibleButton)
    self.step3C_CompareDetectionsCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step3C_CompareDetectionsCollapsibleButtonLayout.setSpacing(4)
    
    #A-contrario detection button
    self.compareDetectionsButton = qt.QPushButton("Compare detections")
    self.compareDetectionsButton.toolTip = "Compare SISCOM and A-contrario detections"
    self.compareDetectionsButton.name = "compareDetectionsButton"
    self.compareDetectionsButton.setEnabled(False)
    self.step3C_CompareDetectionsCollapsibleButtonLayout.addRow('Compare SISCOM and A-contrario detections: ', self.compareDetectionsButton)
    
    
     # Add substeps in a button group
    self.step3_FociDetectionCollapsibleButtonGroup = qt.QButtonGroup()
    self.step3_FociDetectionCollapsibleButtonGroup.addButton(self.step3A_SISCOMDetectionCollapsibleButton)
    self.step3_FociDetectionCollapsibleButtonGroup.addButton(self.step3B_AContrarioDetectionCollapsibleButton)
    self.step3_FociDetectionCollapsibleButtonGroup.addButton(self.step3C_CompareDetectionsCollapsibleButton)
    
    # Connections
    self.step3_fociDetectionCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep3_fociDetectionCollapsibleButtonClicked)
    self.step3A_SISCOMDetectionCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep3A_SISCOMDetectionCollapsibleButtonClicked)
    self.step3B_AContrarioDetectionCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep3B_AContrarioDetectionCollapsibleButtonClicked)
    self.cancelAContrarioButton.connect('clicked()', self.onCancelAContrarioButtonClicked)
    self.step3C_CompareDetectionsCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep3C_CompareDetectionsCollapsibleButtonClicked)
    self.aContrarioDetectionButton.connect('clicked()', self.onAContrarioDetectionButtonClicked)
    self.SISCOMDetectionButton.connect('clicked()', self.onSubtractionDetectionButtonClicked)
    self.compareDetectionsButton.connect('clicked()', self.onCompareDetectionsButtonClicked)
    self.stdDevSISCOMSlider.connect('valueChanged(double)', self.onStdDevSISCOMSliderClicked)
    self.siscomOverlayButton.connect('clicked()', self.onSiscomOverlayButtonClicked)
    self.siscomHideOverlayButton.connect('clicked()', self.onSiscomHideOverlayButtonClicked)
    self.aContrarioOverlayButton.connect('clicked()', self.onAContrarioOverlayButtonClicked)
    self.aContrarioHideOverlayButton.connect('clicked()', self.onAContrarioHideOverlayButtonClicked)
    self.aContrarioDefaultParametersButton.connect('clicked',self.setAContrarioDefaultParameters())

    # Open OBI fiducial selection panel when step is first opened
    self.step3A_SISCOMDetectionCollapsibleButton.setProperty('collapsed', False)
    
    
  def setAContrarioDefaultParameters(self):
    self.numberOfScalesOption.value = 3      
    self.scalesInMatrix.text = '1,2,1,2,3,1,3,4,1'
    self.scalesOutMatrix.text = '2,3,1,3,4,1,4,5,1'
    self.gridStepLineEdit.text = 0.3
    self.maskThresholdParameter.value = 6
    self.rKernelNoiseGlobalLineEdit.text = '3,3,1'
    self.epsilonMachineLineEdit.text = '1e-323'
    self.rKernelNoiseLocalLineEdit.text = '2,2,1'
    self.epsilonSpotsNFALineEdit.text = 0.3333334
    
  
  def setup_Step4_SaveResults(self):
    # Step 1: Load studies panel
    self.step4_saveResultsCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step4_saveResultsCollapsibleButton.text = "4. Save Results"
    self.sliceletPanelLayout.addWidget(self.step4_saveResultsCollapsibleButton)
    self.step4_saveResultsCollapsibleButtonLayout = qt.QFormLayout(self.step4_saveResultsCollapsibleButton)
    self.step4_saveResultsCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step4_saveResultsCollapsibleButtonLayout.setSpacing(4)
      
    # Buttons to connect
    self.saveResultsButton = qt.QPushButton("Save Scene")
    # Add to the widget
    self.step4_saveResultsCollapsibleButtonLayout.addRow("Save results:",self.saveResultsButton)          
    
    self.saveResultsButton.connect('clicked()',self.onSaveResultsButtonClicked)

  ### Callbacks  #####
  ## STEP 1 #######
  def onLoadBasalVolumeButtonClicked(self):
    if slicer.app.ioManager().openAddVolumeDialog():
      self.logic.setActiveVolumeAsBasal();
      basalNode = slicer.util.getNode(self.logic.BASAL_VOLUME_NAME)
      self.activeVolumeNodeSelector.setCurrentNodeID(basalNode.GetID())
      self.logic.displaySlicesIn3D()
  #------------------------------------------------------------------------------------------------    
  def onLoadIctalVolumeButtonClicked(self):
    if slicer.app.ioManager().openAddVolumeDialog():
      self.logic.setActiveVolumeAsIctal();
      ictalNode = slicer.util.getNode(self.logic.ICTAL_VOLUME_NAME)
      self.activeVolumeNodeSelector.setCurrentNodeID(ictalNode.GetID())
      self.logic.displaySlicesIn3D()
  #------------------------------------------------------------------------------------------------    
  def onLoadMRIVolumeButtonClicked(self):
    if slicer.app.ioManager().openAddVolumeDialog():
      self.logic.setActiveVolumeAsMRI(); 
      mriNode = slicer.util.getNode(self.logic.MRI_VOLUME_NAME)
      self.activeVolumeNodeSelector.setCurrentNodeID(mriNode.GetID())
      self.logic.displaySlicesIn3D()
  #------------------------------------------------------------------------------------------------
  def onActiveVolumeNodeSelectorClicked(self, node):
    if node is not None: 
      self.logic.displayVolume(node.GetName())
      self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)  
      self.logic.displaySlicesIn3D()
      slicer.util.resetSliceViews()
      slicer.util.resetThreeDViews()
  #------------------------------------------------------------------------------------------------
  def onResetSceneButtonClicked(self):
    replay=qt.QMessageBox.question(self.parent, 'Epileptogenic Focus Detection', 'Are you sure you want to start again?', qt.QMessageBox.Ok , qt.QMessageBox.Cancel)   
    if replay==qt.QMessageBox.Cancel:
      return     
    elif replay==qt.QMessageBox.Ok: 
      self.logic.cleanEpilepsyDataFromScene()   
      self.aContrarioDetection.cleanAContrarioDataInScene();
      
      
  #------------------------------------------------------------------------------------------------    
  def onLoadSceneButtonClicked(self):
    from os import listdir
    print "Loading the scene"    
    slicerScene = qt.QFileDialog.getOpenFileName(self.parent,"Select a slicer scene")  
    print 'Slicer scene filename = ' + slicerScene
    slicer.util.loadScene(slicerScene)
    self.logic.findEpilepsyDataInScene();
    self.aContrarioDetection.findAContrarioDataInScene();
    
    subtractionOutputVolumeNode = slicer.util.getNode(self.logic.ICTAL_BASAL_SUBTRACTION)
    if subtractionOutputVolumeNode is not None:
      mriVolumeNode = slicer.util.getNode(self.logic.MRI_VOLUME_NAME)
      if mriVolumeNode is not None:
        backgroundVolumeNode = mriVolumeNode
      else:
        ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
        if ictalVolumeNode is not None:
          backgroundVolumeNode = ictalVolumeNode
      foregroundVolumeNode = subtractionOutputVolumeNode
      self.backgroundVolumeNode = backgroundVolumeNode
      self.SISCOMForegroundVolumeNode = foregroundVolumeNode  
      self.showActivations(backgroundVolumeNode, foregroundVolumeNode, 0)
      
    aContrarioOutput = slicer.util.getNode(self.aContrarioDetection.ACONTRARIO_OUTPUT)
    if aContrarioOutput is not None:
      self.aContrarioForegroundVolumeNode = aContrarioOutput   
    
    
  #------------------------------------------------------------------------------------------------    
  ### STEP 2 #######
  def onCompareBasalIctalMRIButtonClicked(self):
    self.layoutWidget.setLayout(self.customLayoutGridView3x3)  
    basalVolumeName = self.logic.BASAL_VOLUME_NAME
    node = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
    if node is not None:
      ictalVolumeName = self.logic.REGISTERED_ICTAL_VOLUME_NAME    
    else:
      ictalVolumeName = self.logic.ICTAL_VOLUME_NAME
    mriVolumeName = self.logic.MRI_VOLUME_NAME
    self.logic.compareBasalIctalMRI(basalVolumeName,ictalVolumeName,mriVolumeName)  
    slicer.util.resetSliceViews()
    
  #------------------------------------------------------------------------------------------------          
  def onRegisterIctalToBasalButtonClicked(self):  
    if self.logic.registerIctalToBasal():    
      self.computeBasalAndIctalMaskButton.setEnabled(self.logic.IsBasalIctalRegistered)
      
  #------------------------------------------------------------------------------------------------          
  def onComputeBasalAndIctalMaskButtonClicked(self):
    basalVolumeName = self.logic.BASAL_VOLUME_NAME  
    basalVolumeNode = slicer.util.getNode(basalVolumeName)
    ictalVolumeName = self.logic.REGISTERED_ICTAL_VOLUME_NAME    
    registeredIctalNode = slicer.util.getNode(ictalVolumeName)
    if registeredIctalNode is not None:
      self.info = qt.QDialog()
      self.infoLayout = qt.QVBoxLayout()
      self.info.setLayout(self.infoLayout)
      self.label = qt.QLabel("Generating mask. Please wait...")
      self.infoLayout.addWidget(self.label)
      l = threading.Thread(target=self.logic.generateMask, args=(basalVolumeNode,registeredIctalNode,0.4,1, ))
      l.setDaemon(True)
      l.start()
      self.info.show()
      while (self.logic.IsBasalIctalMaskComputed == False):
        slicer.app.processEvents()  
        #time.sleep(1) 
      #self.logic.runGenerateMask(basalVolumeNode,registeredIctalNode,0.4,1)
      self.info.hide() 
      self.logic.displayVolume(self.logic.BASAL_ICTAL_MASK_NAME)
      slicer.app.processEvents()
      self.checkBasalAndIctalMaskButton.setEnabled(self.logic.IsBasalIctalMaskComputed)
    else:
      print "It was not possible to find the registered-ictal node!"  
  #------------------------------------------------------------------------------------------------    
  
  
  def onCheckBasalAndIctalMaskButtonClicked(self):
    basalVolumeName = self.logic.BASAL_VOLUME_NAME  
    ictalVolumeName = self.logic.REGISTERED_ICTAL_VOLUME_NAME    
    basalIctalMaskName = self.logic.BASAL_ICTAL_MASK_NAME  
    self.layoutWidget.setLayout(self.customLayoutGridView3x3)  
    self.logic.compareBasalIctalMask(basalVolumeName, ictalVolumeName, basalIctalMaskName )   
    slicer.util.resetSliceViews() 
   
   #--------------------------------------------------------------------------------------------- 
  def onRegisterBasalToMRIButtonClicked(self):    
    if self.logic.registerBasalToMRI():
      self.compareBasalIctalMRIButton.setEnabled(self.logic.IsBasalMRIRegistered)  
      self.onCompareBasalIctalMRIButtonClicked() 
  
  #------------------------------------------------------------------------------------------------------------------
  
  def onStep1_loadStudiesCollapsibleButtonClicked(self, collapsed):
    self.onSiscomHideOverlayButtonClicked()
  
  #------------------------------------------------------------------------------------------------------------------
  
  def onStep2_RegistrationCollapsibleButtonClicked(self, collapsed):
    self.onSiscomHideOverlayButtonClicked()
    if collapsed == False:
      self.registerIctalToBasalButton.setEnabled(self.logic.IsBasalVolume and self.logic.IsIctalVolume)
      self.registerBasalToMRIButton.setEnabled(self.logic.IsBasalVolume and self.logic.IsMRIVolume)    
      self.computeBasalAndIctalMaskButton.setEnabled(self.logic.IsBasalIctalRegistered)
      self.checkBasalAndIctalMaskButton.setEnabled(self.logic.IsBasalIctalMaskComputed)
      self.compareBasalIctalMRIButton.setEnabled(self.logic.IsBasalMRIRegistered)

      
  #-----------------------------------------------------------------------------------
  
  def onStep3_fociDetectionCollapsibleButtonClicked(self, collapsed):   
    self.onSiscomHideOverlayButtonClicked()
    self.siscomOverlayButton.setEnabled(self.logic.IsSISCOMOutput)
    if collapsed == False:
      self.SISCOMDetectionButton.setEnabled(self.logic.IsBasalIctalMaskComputed)
      self.stdDevSISCOMSlider.setEnabled(self.logic.IsBasalIctalMaskComputed)    
      self.aContrarioDetectionButton.setEnabled(self.logic.IsBasalIctalMaskComputed)
      if self.logic.IsSISCOMOutput == True:
        subtractionOutputVolumeNode = slicer.util.getNode(self.logic.ICTAL_BASAL_SUBTRACTION)  
        maskVolumeNode = slicer.util.getNode(self.logic.BASAL_ICTAL_MASK_NAME)
        if (subtractionOutputVolumeNode is not None) and (maskVolumeNode is not None):
          self.computeStdDevSISCOMSliderBounds(subtractionOutputVolumeNode,maskVolumeNode )
          self.showActivations(self.backgroundVolumeNode, self.SISCOMForegroundVolumeNode) 
      print "End of onStep3_fociDetectionCollapsibleButtonClicked"
          
  def onStep3A_SISCOMDetectionCollapsibleButtonClicked(self, collapsed):
    self.onSiscomHideOverlayButtonClicked()
    self.siscomOverlayButton.setEnabled(self.logic.IsSISCOMOutput)
    if collapsed == False:  
      if (self.backgroundVolumeNode is not None) and (self.SISCOMForegroundVolumeNode is not None):
        self.showActivations(self.backgroundVolumeNode, self.SISCOMForegroundVolumeNode) 


    
  def onStep3B_AContrarioDetectionCollapsibleButtonClicked(self, collapsed):
    self.onAContrarioHideOverlayButtonClicked() 
    self.aContrarioOverlayButton.setEnabled(self.aContrarioDetection.IsAContrarioOutput)
    if collapsed == False:   
      if (self.backgroundVolumeNode is not None) and (self.aContrarioForegroundVolumeNode is not None):
        self.showActivations(self.backgroundVolumeNode, self.aContrarioForegroundVolumeNode) 

  def onCancelAContrarioButtonClicked(self):
    self.suspendAContrario = True
      
  def onStep3C_CompareDetectionsCollapsibleButtonClicked(self, collapsed):     
    if collapsed == False: 
      self.compareDetectionsButton.setEnabled(self.logic.IsSISCOMOutput and self.aContrarioDetection.IsAContrarioOutput)      
        
                           
  #------------------------------------------------------------------------------------------------------------------      
  def onSubtractionDetectionButtonClicked(self): 
#     basalVolumeNode = slicer.util.getNode(self.logic.BASAL_VOLUME_NAME)
#     ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
#     subtractionOutputVolumeNode=slicer.vtkMRMLScalarVolumeNode()
#     slicer.mrmlScene.AddNode(subtractionOutputVolumeNode)
#     subtractionOutputVolumeNode.SetName("Ictal-Basal Subtraction") 
    if self.logic.normalizedBasalArray is None:  # the normalizedBasalArray is generated when the mask is created
      self.onComputeBasalAndIctalMaskButtonClicked()
    
    result =self.logic.subtractImages()  
    #result= self.logic.subtractImages(ictalVolumeNode,basalVolumeNode, subtractionOutputVolumeNode) 
    if result==True:
      maskVolumeNode=slicer.util.getNode(self.logic.BASAL_ICTAL_MASK_NAME)
      subtractionOutputVolumeNode=slicer.util.getNode(self.logic.ICTAL_BASAL_SUBTRACTION)
      if maskVolumeNode is not None:
        self.logic.applyMaskToVolume(subtractionOutputVolumeNode,maskVolumeNode,subtractionOutputVolumeNode)  
      self.computeStdDevSISCOMSliderBounds(subtractionOutputVolumeNode,maskVolumeNode)
      # creates a new colormap
      self.logic.configureColorMap(subtractionOutputVolumeNode)
      
      mriVolumeNode = slicer.util.getNode(self.logic.MRI_VOLUME_NAME)
      if mriVolumeNode is not None:
        backgroundVolumeNode = mriVolumeNode
      else:
        ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
        if ictalVolumeNode is not None:
          backgroundVolumeNode = ictalVolumeNode
      foregroundVolumeNode = subtractionOutputVolumeNode
      self.showActivations(backgroundVolumeNode, foregroundVolumeNode)
      
      self.backgroundVolumeNode = backgroundVolumeNode
      self.SISCOMForegroundVolumeNode = foregroundVolumeNode
      
      self.siscomOverlayButton.setEnabled(self.logic.IsSISCOMOutput)
  #---------------------------------------------------------------------------------------
  
  def computeStdDevSISCOMSliderBounds(self, subtractionOutputVolumeNode,maskVolumeNode ):
    data=slicer.util.array(subtractionOutputVolumeNode.GetName())
    maximumValue = numpy.int(data.max())          
    stddev=data.std()
    print 'standard deviation = ' + str(stddev)
    stddevInside_mask = self.logic.computeStdDevInsideMask(subtractionOutputVolumeNode, maskVolumeNode)
    print 'standard deviation inside mask = ' + str(stddevInside_mask)
    self.stdDevSISCOMSlider.minimum = 0;
    self.stdDevSISCOMSlider.maximum = maximumValue / stddevInside_mask;      
    self.stdDevSISCOMSlider.singleStep = 0.5
    
    
  def onStdDevSISCOMSliderClicked(self, value): 
    subtractionOutputVolumeNode = slicer.util.getNode(self.logic.ICTAL_BASAL_SUBTRACTION)    
    maskVolumeNode= slicer.util.getNode(self.logic.BASAL_ICTAL_MASK_NAME)
    data=slicer.util.array(subtractionOutputVolumeNode.GetName())
    stddevInside_mask = self.logic.computeStdDevInsideMask(subtractionOutputVolumeNode, maskVolumeNode)
    minimumValue = numpy.int(data.min())
    maximumValue = numpy.int(data.max())  
    negativeValuesToHide = numpy.int(value*stddevInside_mask)
    positiveValuesToHide = numpy.int(value*stddevInside_mask)
    self.logic.showDifferencesBiggerThanStdThreshold(minimumValue, maximumValue, negativeValuesToHide, positiveValuesToHide)  
    slicer.app.processEvents()
  
  #---------------------------------------------------------------------------------------------------------------
  def onSiscomOverlayButtonClicked (self):
    rows = self.siscomRowsText.text 
    cols = self.siscomColsText.text
    if (rows.isnumeric() and cols.isnumeric()):
      rows = int(rows)
      cols = int(cols)
      self.generateOverlay(rows, cols)   
      self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView) 
      self.siscomHideOverlayButton.setEnabled(True)
  #---------------------------------------------------------------------------------------------------------------  
   
  def onSiscomHideOverlayButtonClicked(self):
    self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)   
    self.generateOverlay(1, 1)  
    self.siscomHideOverlayButton.setEnabled(False)       
    
  #---------------------------------------------------------------------------------------------------------------
  def onAContrarioOverlayButtonClicked (self):
    rows = self.aContrarioRowsText.text  
    cols = self.aContrarioColsText.text
    if (rows.isnumeric() and cols.isnumeric()):
      rows = int(rows)
      cols = int(cols)
      self.generateOverlay(rows, cols) 
      self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)      
      self.aContrarioHideOverlayButton.setEnabled(True)
  #---------------------------------------------------------------------------------------------------------------  
  
  def onAContrarioHideOverlayButtonClicked(self):
    self.generateOverlay(1, 1)  
    self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)   
    self.aContrarioHideOverlayButton.setEnabled(False)  
                   
                   
  def updateAContrarioParameters(self):
    scalesInText = self.scalesInMatrix.text 
    scIn = scalesInText.split(',')
    numberOfScalesIn = numpy.size(scIn)
    if (numberOfScalesIn != (self.numberOfScalesOption.value * 3)):  
      print ('Please check the number of scales and the scalesIn parameters and try again')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Please check the number of scales and the scalesIn parameters', qt.QMessageBox.Ok , qt.QMessageBox.Ok )
      return False
    scalesOutText = self.scalesOutMatrix.text
    scOut = scalesOutText.split(',')
    numberOfScalesOut = numpy.size(scOut)
    if (numberOfScalesOut != (self.numberOfScalesOption.value * 3)):  
      print ('Please check the number of scales and the scalesOut parameters and try again')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Please check the number of scales and the scalesOut parameters', qt.QMessageBox.Ok , qt.QMessageBox.Ok )
      return False
    
    gridStep = self.gridStepLineEdit.text
    if self.logic.isDouble(gridStep)==False:
      print('Grid step must be double')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Grid step format must be double', qt.QMessageBox.Ok , qt.QMessageBox.Ok )
      return False
  
    M = self.maskThresholdParameter.value
    if self.logic.isDouble(M)==False:
      print('M must be double!')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'M must be a double!', qt.QMessageBox.Ok , qt.QMessageBox.Ok )
      return False
  
    kernelGlobal =numpy.fromstring(self.rKernelNoiseGlobalLineEdit.text   , dtype=int, sep=',')
    if kernelGlobal.size != 3:
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Three comma separated values must be indicated in the global kernel radio parameter ', qt.QMessageBox.Ok , qt.QMessageBox.Ok )  
      print('Three comma separated values must be indicated in the global kernel radio parameter ')
      return False
    
    kernelLocal =numpy.fromstring(self.rKernelNoiseLocalLineEdit.text   , dtype=int, sep=',')
    if kernelLocal.size != 3:
      print('Three comma separated values must be indicated in the local kernel radio parameter ')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Three comma separated values must be indicated in the local kernel radio parameter ', qt.QMessageBox.Ok , qt.QMessageBox.Ok ) 
      return False

    epsilonMachine = self.epsilonMachineLineEdit.text
    if self.logic.isDouble(epsilonMachine)==False:
      print('Epsilon machine must be double!')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Epsilon machine must be a double!', qt.QMessageBox.Ok , qt.QMessageBox.Ok )
      return False
  
  
    epsilonSpotsNFA = self.epsilonSpotsNFALineEdit.text
    if self.logic.isDouble(epsilonSpotsNFA)==False:
      print('Epsilon spots NFA must be double!')
      ret=qt.QMessageBox.warning(self.parent, 'A-contrario parameters', 'Epsilon spots NFA must be a double!', qt.QMessageBox.Ok , qt.QMessageBox.Ok )
      return False  
    
    print "Parameters were properly set!"
    
    self.aContrarioDetection.numberOfScales = self.numberOfScalesOption.value
    self.aContrarioDetection.scalesIn = numpy.array([[scIn[0], scIn[1], scIn[2]], [scIn[3], scIn[4], scIn[5]], [scIn[6], scIn[7], scIn[8]]],numpy.uint32);                       
    self.aContrarioDetection.scalesOut = numpy.array([[scOut[0], scOut[1], scOut[2]], [scOut[3], scOut[4], scOut[5]], [scOut[6], scOut[7], scOut[8]]],numpy.uint32);   
    self.aContrarioDetection.gridStep = numpy.double(gridStep)
    self.aContrarioDetection.M = numpy.double(M)
    self.aContrarioDetection.rKernelNoiseGlobal = kernelGlobal
    self.aContrarioDetection.epsilonMachine = numpy.double(epsilonMachine)
    

    self.aContrarioDetection.rKernelNoiseLocal = kernelLocal
    self.aContrarioDetection.epsilonSpotsNFA = numpy.double(epsilonSpotsNFA)
       
    return True               
  #---------------------------------------------------------------------------------------------------------------     
  def onAContrarioDetectionButtonClicked(self):   
#     basalVolumeNode = slicer.util.getNode(self.logic.BASAL_VOLUME_NAME)
#     ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)  
#     result = self.logic.detectFociAContrario(basalVolumeNode,ictalVolumeNode)
#     nfaOutputVolumeNode = slicer.util.getNode("NFA Output Volume Node")  
#     backgroundVolumeNode = ictalVolumeNode
#     foregroundVolumeNode = nfaOutputVolumeNode
#     self.showActivations(backgroundVolumeNode, foregroundVolumeNode)

    if self.updateAContrarioParameters() == False:
      return
  
    self.aContrarioDetectionButton.setEnabled(False)
    self.aContrarioDetection.getInputDataFromScene()
    
    
    l = threading.Thread(target=self.aContrarioDetection.runAContrario)
    l.setDaemon(True)
    l.start()  
    self.aContrarioProgressFrame.show()  
    while ((self.aContrarioDetection.IsAContrarioOutput == False) and (self.suspendAContrario == False)):
      time.sleep(0.3)  
      self.currentStatusLabel.setText(self.aContrarioDetection.userMessage)    
      slicer.app.processEvents()  
     
     
    if self.suspendAContrario == True:
      l._Thread__stop()   
        
    self.aContrarioProgressFrame.hide()
    self.currentStatusLabel.setText('Idle')
    self.suspendAContrario = False   
      
    #self.aContrarioDetection.runAContrario()  
    mriVolumeNode = slicer.util.getNode(self.logic.MRI_VOLUME_NAME)
    if mriVolumeNode is not None:
      backgroundVolumeNode = mriVolumeNode
    else:
      ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
      backgroundVolumeNode = ictalVolumeNode
    foregroundVolumeNode = slicer.util.getNode(self.aContrarioDetection.ACONTRARIO_OUTPUT)
    
    if((backgroundVolumeNode is not None) and (foregroundVolumeNode is not None) ):
      self.showActivations(backgroundVolumeNode, foregroundVolumeNode)
      self.backgroundVolumeNode = backgroundVolumeNode
      self.aContrarioForegroundVolumeNode = foregroundVolumeNode
    
    self.aContrarioDetectionButton.setEnabled(True)  
    self.aContrarioOverlayButton.setEnabled(self.aContrarioDetection.IsAContrarioOutput)
      
  def onCompareDetectionsButtonClicked(self):
    mriVolumeNode = slicer.util.getNode(self.logic.MRI_VOLUME_NAME)  
    aContrarioVolumeNode = slicer.util.getNode(self.aContrarioDetection.ACONTRARIO_OUTPUT)
    subtractionOutputVolumeNode = slicer.util.getNode(self.logic.ICTAL_BASAL_SUBTRACTION)  
    self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeOverThreeView)  
    self.logic.compareAContrarioSISCOM(subtractionOutputVolumeNode.GetName(), aContrarioVolumeNode.GetName(), mriVolumeNode.GetName())     
    slicer.util.resetSliceViews() 
  
  #----------------------------------------------------------------------------------------------
  
  def generateOverlay(self,rows, cols):
     redNode=slicer.util.getNode("vtkMRMLSliceNodeRed")
     if ((redNode.GetLayoutGridRows()!=rows) or (redNode.GetLayoutGridColumns()!=cols)):
       redNode.SetLayoutGrid(rows,cols)
       
  #----------------------------------------------------------------------------------------------
  def showActivations(self,backgroundVolumeNode,foregroundVolumeNode, opacity=1):
    # Set the background volume 
    redWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeRed")
    redWidgetCompNode.SetBackgroundVolumeID(backgroundVolumeNode.GetID())
    redWidgetCompNode.SetForegroundVolumeID(foregroundVolumeNode.GetID())
    redWidgetCompNode.SetForegroundOpacity(opacity)
    redNode=slicer.util.getNode("vtkMRMLSliceNodeRed")
    redNode.SetSliceVisible(True)
    
    greenWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeGreen")
    greenWidgetCompNode.SetBackgroundVolumeID(backgroundVolumeNode.GetID())
    greenWidgetCompNode.SetForegroundVolumeID(foregroundVolumeNode.GetID())
    greenWidgetCompNode.SetForegroundOpacity(opacity)
    greenNode=slicer.util.getNode("vtkMRMLSliceNodeGreen")
    greenNode.SetSliceVisible(True)
    
    yellowWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeYellow")
    yellowWidgetCompNode.SetBackgroundVolumeID(backgroundVolumeNode.GetID())
    yellowWidgetCompNode.SetForegroundVolumeID(foregroundVolumeNode.GetID())
    yellowWidgetCompNode.SetForegroundOpacity(opacity)  
    yellowNode=slicer.util.getNode("vtkMRMLSliceNodeYellow")
    yellowNode.SetSliceVisible(True)
    
    self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)  
    slicer.util.resetSliceViews()
  
  #----------------------------------------------------------------------------------------------
  def onSaveResultsButtonClicked(self):
    #sceneDirectory = qt.QFileDialog.getExistingDirectory(self.parent,"Select directory")  
    #dstFile = sceneDirectory + '/EpilepsyScene.mrb'   #os.path.join(sceneDirectory, 'EpilepsyScene')
    #slicer.util.saveScene(dstFile)    
    slicer.app.ioManager().openSaveDataDialog()  
  #-----------------------------------------------------------------------------------------------    
  #
  # Event handler functions
  #
  def onViewSelect(self, layoutIndex):
    if layoutIndex == 0:
       self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutFourUpView)
    elif layoutIndex == 1:
       self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)
    elif layoutIndex == 2:
       self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUp3DView)
    elif layoutIndex == 3:
       self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutTabbedSliceView)
    elif layoutIndex == 4:
       self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutDual3DView)
    elif layoutIndex == 5:
       self.layoutWidget.setLayout(self.customLayoutGridView3x3) 
    elif layoutIndex == 6:
       self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutThreeOverThreeView)       

  #
  # Testing related functions
  #
  def onSelfTestButtonClicked(self):
    print "Test Button Clicked"



#
# EpileptogenicFocusDetection
#
class EpileptogenicFocusDetection:
  def __init__(self, parent):
    parent.title = "Epileptogenic Focus Detection"
    parent.categories = ["Slicelets"]
    parent.dependencies = []
    parent.contributors = ["Guillermo Carbajal and Alvaro Gomez (Facultad de Ingenieria, Uruguay)"] # replace with "Firstname Lastname (Org)"
    parent.helpText = "Slicelet for epileptogenic focus detection"
    parent.acknowledgementText = """
    This file was originally developed by Guillermo Carbajal and Alvaro Gomez (Facultad de Ingenieria, Uruguay).
    """
    self.parent = parent

#
# EpileptogenicFocusDetectionWidget
#
class EpileptogenicFocusDetectionWidget:
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
    self.mainFrame = None  

  def setup(self):
    # Reload panel
    reloadCollapsibleButton = ctk.ctkCollapsibleButton()
    reloadCollapsibleButton.text = "Reload"
    self.layout.addWidget(reloadCollapsibleButton)
    reloadFormLayout = qt.QFormLayout(reloadCollapsibleButton)

    # Reload button
    self.reloadButton = qt.QPushButton("Reload")
    self.reloadButton.toolTip = "Reload this module."
    self.reloadButton.name = "EpileptogenicFocusDetection Reload"
    reloadFormLayout.addWidget(self.reloadButton)
    self.reloadButton.connect('clicked()', self.onReload)

    # Show slicelet button
    launchSliceletButton = qt.QPushButton("Show slicelet")
    launchSliceletButton.toolTip = "Launch the slicelet"
    reloadFormLayout.addWidget(launchSliceletButton)
    launchSliceletButton.connect('clicked()', self.onShowSliceletButtonClicked)

  def onReload(self,moduleName="EpileptogenicFocusDetection"):
    """Generic reload method for any scripted module.
    ModuleWizard will subsitute correct default moduleName.
    """
    globals()[moduleName] = slicer.util.reloadScriptedModule(moduleName)

  def onShowSliceletButtonClicked(self): 
    if not self.mainFrame:   
      self.mainFrame = SliceletMainFrame()
      self.mainFrame.setMinimumWidth(1200)
      self.mainFrame.connect('destroyed()', self.onSliceletClosed)
      slicelet = EpileptogenicFocusDetectionSlicelet(self.mainFrame)
      self.mainFrame.setSlicelet(slicelet)

    # Make the slicelet reachable from the Slicer python interactor for testing
    # TODO: Should be uncommented for testing
    # slicer.gelDosimetrySliceletInstance = slicelet

  def onSliceletClosed(self):
    print('Slicelet closed')

    # ---------------------------------------------------------------------------
class EpileptogenicFocusDetectionTest(unittest.TestCase):
  """
  This is the test case for your scripted module.
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()

#
# Main
#
if __name__ == "__main__":
  # TODO: need a way to access and parse command line arguments
  # TODO: ideally command line args should handle --xml

  import sys
  print( sys.argv )

  mainFrame = qt.QFrame()
  slicelet = EpileptogenicFocusDetectionSlicelet(mainFrame)
