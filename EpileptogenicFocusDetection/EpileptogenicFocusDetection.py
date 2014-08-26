import os
import unittest
import numpy
from __main__ import vtk, qt, ctk, slicer
import EpileptogenicFocusDetectionLogic

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

    self.collapsibleButtonsGroup = qt.QButtonGroup()
    self.collapsibleButtonsGroup.addButton(self.step0_layoutSelectionCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step1_loadStudiesCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step2_RegistrationCollapsibleButton)
    self.collapsibleButtonsGroup.addButton(self.step3_fociDetectionCollapsibleButton)

    self.step0_layoutSelectionCollapsibleButton.setProperty('collapsed', False)
    
    # Create module logic
    self.logic = EpileptogenicFocusDetectionLogic.EpileptogenicFocusDetectionLogic() 
    
    # Set up step panels
    self.setup_Step0_LayoutSelection()
    #self.setup_Step1_LoadPlanningData()
    self.setup_Step1_LoadStudies() 
    self.setup_Step2_Registration()
    self.setup_Step3_FociDetection()
    
    #creates a new layout
    self.customLayoutGridView3x3 = 1033
    self.logic.customCompareLayout(3,3,self.customLayoutGridView3x3)
    

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
    self.loadBasalVolumeButton.disconnect("clicked()",self.onLoadBasalVolumeButtonClicked)
    self.rotateBasalISButton.disconnect("clicked()",self.onRotateBasalISButtonClicked)
    self.rotateBasalAPButton.disconnect("clicked()",self.onRotateBasalAPButtonClicked)
    self.rotateBasalLRButton.disconnect("clicked()",self.onRotateBasalLRButtonClicked)
    self.loadIctalVolumeButton.disconnect("clicked()",self.onLoadIctalVolumeButtonClicked)
    self.rotateIctalISButton.disconnect("clicked()",self.onRotateIctalISButtonClicked)
    self.rotateIctalAPButton.disconnect("clicked()",self.onRotateIctalAPButtonClicked)
    self.rotateIctalLRButton.disconnect("clicked()",self.onRotateIctalLRButtonClicked)
    self.loadMRIVolumeButton.disconnect("clicked()",self.onLoadMRIVolumeButtonClicked)
    self.rotateMRIISButton.disconnect("clicked()",self.onRotateMRIISButtonClicked)
    self.rotateMRIAPButton.disconnect("clicked()",self.onRotateMRIAPButtonClicked)
    self.rotateMRILRButton.disconnect("clicked()",self.onRotateMRILRButtonClicked)
    # Step 2
    self.compareBasalIctalMRIButton.disconnect('clicked()', self.onCompareBasalIctalMRIButtonClicked)
    self.registerIctalToBasalButton.disconnect('clicked()', self.onRegisterIctalToBasalButtonClicked)
    self.computeBasalAndIctalMaskButton.disconnect("clicked()",self.onComputeBasalAndIctalMaskButtonClicked)
    self.checkBasalAndIctalMaskButton.disconnect("clicked()",self.onCheckBasalAndIctalMaskButtonClicked)
    self.registerBasalToMRIButton.disconnect('clicked()', self.onRegisterBasalToMRIButtonClicked)
    # Step 3
    self.aContrarioDetectionButton.disconnect('clicked()', self.onAContrarioDetectionButtonClicked)
    self.createMaskButton.disconnect('clicked()', self.onCreateMaskButtonClicked)
    self.SISCOMDetectionButton.disconnect('clicked()', self.onSubtractionDetectionButtonClicked)


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
    self.step1A_loadBasalCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step1A_loadBasalCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step1A_loadBasalCollapsibleButton.text = "1/A) Load inter ictal (basal) SPECT"
    self.step1_loadStudiesCollapsibleButtonLayout.addWidget(self.step1A_loadBasalCollapsibleButton)
    loadBasalCollapsibleButtonLayout = qt.QFormLayout(self.step1A_loadBasalCollapsibleButton)
    loadBasalCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    loadBasalCollapsibleButtonLayout.setSpacing(4)
    
    # Buttons to connect
    self.loadBasalVolumeButton = qt.QPushButton("Load basal volume")
    self.rotateBasalISButton = qt.QPushButton("Rotate around the IS axis")
    self.rotateBasalAPButton = qt.QPushButton("Rotate around the AP axis")
    self.rotateBasalLRButton = qt.QPushButton("Rotate around the LR axis")
    
    # Add to the widget
    loadBasalCollapsibleButtonLayout.addRow("Load basal volume:",self.loadBasalVolumeButton)
    loadBasalCollapsibleButtonLayout.addRow("Rotate IS axis:", self.rotateBasalISButton)
    loadBasalCollapsibleButtonLayout.addRow("Rotate AP axis:", self.rotateBasalAPButton)
    loadBasalCollapsibleButtonLayout.addRow("Rotate LR axis:", self.rotateBasalLRButton)
    
    
    # Connections
    self.loadBasalVolumeButton.connect("clicked()",self.onLoadBasalVolumeButtonClicked)
    self.rotateBasalISButton.connect("clicked()",self.onRotateBasalISButtonClicked)
    self.rotateBasalAPButton.connect("clicked()",self.onRotateBasalAPButtonClicked)
    self.rotateBasalLRButton.connect("clicked()",self.onRotateBasalLRButtonClicked)

    # Step 1/B): Load ictal SPECT
    self.step1B_loadIctalCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step1B_loadIctalCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step1B_loadIctalCollapsibleButton.text = "1/B) Load ictal SPECT"
    self.step1_loadStudiesCollapsibleButtonLayout.addWidget(self.step1B_loadIctalCollapsibleButton)
    loadIctalCollapsibleButtonLayout = qt.QFormLayout(self.step1B_loadIctalCollapsibleButton)
    loadIctalCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    loadIctalCollapsibleButtonLayout.setSpacing(4)

   # Buttons to connect
    self.loadIctalVolumeButton = qt.QPushButton("Load ictal volume")
    self.rotateIctalISButton = qt.QPushButton("Rotate around the IS axis")
    self.rotateIctalAPButton = qt.QPushButton("Rotate around the AP axis")
    self.rotateIctalLRButton = qt.QPushButton("Rotate around the LR axis")
    
    # Add to the widget
    loadIctalCollapsibleButtonLayout.addRow("Load ictal volume:", self.loadIctalVolumeButton)
    loadIctalCollapsibleButtonLayout.addRow("Rotate IS:", self.rotateIctalISButton)
    loadIctalCollapsibleButtonLayout.addRow("Rotate AP:", self.rotateIctalAPButton)
    loadIctalCollapsibleButtonLayout.addRow("Rotate LR:", self.rotateIctalLRButton)
    
    # Connections
    self.loadIctalVolumeButton.connect("clicked()",self.onLoadIctalVolumeButtonClicked)
    self.rotateIctalISButton.connect("clicked()",self.onRotateIctalISButtonClicked)
    self.rotateIctalAPButton.connect("clicked()",self.onRotateIctalAPButtonClicked)
    self.rotateIctalLRButton.connect("clicked()",self.onRotateIctalLRButtonClicked)
    
    
    # Step 1/C): Load MRI
    self.step1C_loadMRICollapsibleButton = ctk.ctkCollapsibleButton()
    self.step1C_loadMRICollapsibleButton.setProperty('collapsedHeight', 4)
    self.step1C_loadMRICollapsibleButton.text = "1/C) Load MRI"
    self.step1_loadStudiesCollapsibleButtonLayout.addWidget(self.step1C_loadMRICollapsibleButton)
    loadMRICollapsibleButtonLayout = qt.QFormLayout(self.step1C_loadMRICollapsibleButton)
    loadMRICollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    loadMRICollapsibleButtonLayout.setSpacing(4)

   # Buttons to connect
    self.loadMRIVolumeButton = qt.QPushButton("Load MRI volume")
    self.rotateMRIISButton = qt.QPushButton("Rotate IS")
    self.rotateMRIAPButton = qt.QPushButton("Rotate AP")
    self.rotateMRILRButton = qt.QPushButton("Rotate LR")
    
    # Add to the widget
    loadMRICollapsibleButtonLayout.addRow("Load ictal volume:", self.loadMRIVolumeButton)
    loadMRICollapsibleButtonLayout.addRow("Rotate IS:", self.rotateMRIISButton)
    loadMRICollapsibleButtonLayout.addRow("Rotate AP:", self.rotateMRIAPButton)
    loadMRICollapsibleButtonLayout.addRow("Rotate LR:", self.rotateMRILRButton)
    
    
    # Connections
    self.loadMRIVolumeButton.connect("clicked()",self.onLoadMRIVolumeButtonClicked)
    self.rotateMRIISButton.connect("clicked()",self.onRotateMRIISButtonClicked)
    self.rotateMRIAPButton.connect("clicked()",self.onRotateMRIAPButtonClicked)
    self.rotateMRILRButton.connect("clicked()",self.onRotateMRILRButtonClicked)

 

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

    # Basal volume node selector
    self.basalVolumeNodeSelector = slicer.qMRMLNodeComboBox()
    self.basalVolumeNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.basalVolumeNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.basalVolumeNodeSelector.addEnabled = False
    self.basalVolumeNodeSelector.removeEnabled = False
    self.basalVolumeNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.basalVolumeNodeSelector.setToolTip( "Pick the basal volume for registration." )
    #self.step2_RegistrationCollapsibleButtonLayout.addRow('Basal volume: ', self.basalVolumeNodeSelector)

    # Ictal volume node selector
    self.ictalVolumeNodeSelector = slicer.qMRMLNodeComboBox()
    self.ictalVolumeNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.ictalVolumeNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.ictalVolumeNodeSelector.addEnabled = False
    self.ictalVolumeNodeSelector.removeEnabled = False
    self.ictalVolumeNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.ictalVolumeNodeSelector.setToolTip( "Pick the ictal volume for registration." )
    #self.step2_RegistrationCollapsibleButtonLayout.addRow('Ictal volume: ', self.ictalVolumeNodeSelector)

  
    # MRI node selector
    self.MRISelector = slicer.qMRMLNodeComboBox()
    self.MRISelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRISelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.MRISelector.addEnabled = False
    self.MRISelector.removeEnabled = False
    self.MRISelector.setMRMLScene( slicer.mrmlScene )
    self.MRISelector.setToolTip( "Pick the MRI volume for registration." )
    #self.step2_RegistrationCollapsibleButtonLayout.addRow('MRI volume: ', self.MRISelector)
   
    
    # Basal to Ictal registration button
    self.registerIctalToBasalButton = qt.QPushButton("Perform registration")
    self.registerIctalToBasalButton.toolTip = "Register Ictal volume to Basal volume"
    self.registerIctalToBasalButton.name = "registerIctalToBasalButton"
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Register Basal to Ictal: ', self.registerIctalToBasalButton)
    
    # Compute and check basal to ictal mask buttons 
    self.computeBasalAndIctalMaskButton = qt.QPushButton("Compute basal and ictal mask")
    self.checkBasalAndIctalMaskButton = qt.QPushButton("Check basal and ictal mask")
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Compute Basal and Ictal mask: ', self.computeBasalAndIctalMaskButton)
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Check Basal and Ictal mask: ', self.checkBasalAndIctalMaskButton)
    
    
    # Basal to MRI registration button
    self.registerBasalToMRIButton = qt.QPushButton("Perform registration")
    self.registerBasalToMRIButton.toolTip = "Register Basal volume to MRI volume"
    self.registerBasalToMRIButton.name = "registerBasalToMRIButton"
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Register Basal to MRI: ', self.registerBasalToMRIButton)
    
    # Compare Basal, Ictal  and MRI button
    self.compareBasalIctalMRIButton = qt.QPushButton("Compare basal, ictal and MRI")
    self.compareBasalIctalMRIButton.toolTip = "Compare basal, ictal and MRI volumes"
    self.compareBasalIctalMRIButton.name = "compareBasalIctalMRIButton"
    self.step2_RegistrationCollapsibleButtonLayout.addRow('Compare basal, ictal and MRI volumes: ', self.compareBasalIctalMRIButton)   

    # Connections
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
    
    # Basal volume node selector
    self.basalVolumeSISCOMNodeSelector = slicer.qMRMLNodeComboBox()
    self.basalVolumeSISCOMNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.basalVolumeSISCOMNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.basalVolumeSISCOMNodeSelector.addEnabled = False
    self.basalVolumeSISCOMNodeSelector.removeEnabled = False
    self.basalVolumeSISCOMNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.basalVolumeSISCOMNodeSelector.setToolTip( "Pick the basal volume for a-contrario detection." )
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Basal volume: ', self.basalVolumeSISCOMNodeSelector)

    # Ictal volume node selector
    self.ictalVolumeSISCOMNodeSelector = slicer.qMRMLNodeComboBox()
    self.ictalVolumeSISCOMNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.ictalVolumeSISCOMNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.ictalVolumeSISCOMNodeSelector.addEnabled = False
    self.ictalVolumeSISCOMNodeSelector.removeEnabled = False
    self.ictalVolumeSISCOMNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.ictalVolumeSISCOMNodeSelector.setToolTip( "Pick the ictal volume for a-contrario detection." )
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Ictal volume: ', self.ictalVolumeSISCOMNodeSelector)
  
    # MRI node selector
    self.MRISISCOMSelector = slicer.qMRMLNodeComboBox()
    self.MRISISCOMSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRISISCOMSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.MRISISCOMSelector.addEnabled = False
    self.MRISISCOMSelector.removeEnabled = False
    self.MRISISCOMSelector.setMRMLScene( slicer.mrmlScene )
    self.MRISISCOMSelector.setToolTip( "Pick the MRI volume for a-contrario detection." )
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('MRI volume: ', self.MRISISCOMSelector)
    
    # Normalization of images
    self.createMaskButton = qt.QPushButton("Creates the mask")
    self.createMaskButton.toolTip = "Compute the mask"
    self.createMaskButton.name = "createMaskButton"
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Normalize registered images: ', self.createMaskButton)
    #SISCOM detection button
    self.SISCOMDetectionButton = qt.QPushButton("Perform subtraction of images")
    self.SISCOMDetectionButton.toolTip = "Perform the subtraction of the images: ictal - basal"
    self.SISCOMDetectionButton.name = "SISCOMDetectionButton"
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Foci detection: ', self.SISCOMDetectionButton)
    
    # SISCOM Threshold frame    
    self.stdDevSISCOMSlider=ctk.ctkSliderWidget()
    self.stdDevSISCOMSlider.setEnabled('False')
    
    #self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Visualization threshold: ', self.thresholdSISCOMFrame)
    self.step3A_SISCOMDetectionCollapsibleButtonLayout.addRow('Standard deviations threshold: ', self.stdDevSISCOMSlider)


   
    # Step 3/C): Select MEASURED fiducials on MEASURED dose volume
    self.step3B_AContrarioDetectionCollapsibleButton = ctk.ctkCollapsibleButton()
    self.step3B_AContrarioDetectionCollapsibleButton.setProperty('collapsedHeight', 4)
    self.step3B_AContrarioDetectionCollapsibleButton.text = "3/B) A Contrario method"
    self.step3_fociDetectionLayout.addWidget(self.step3B_AContrarioDetectionCollapsibleButton)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout = qt.QFormLayout(self.step3B_AContrarioDetectionCollapsibleButton)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.setContentsMargins(12,4,4,4)
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.setSpacing(4)
    
    # Basal volume node selector
    self.basalVolumeAContrarioNodeSelector = slicer.qMRMLNodeComboBox()
    self.basalVolumeAContrarioNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.basalVolumeAContrarioNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.basalVolumeAContrarioNodeSelector.addEnabled = False
    self.basalVolumeAContrarioNodeSelector.removeEnabled = False
    self.basalVolumeAContrarioNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.basalVolumeAContrarioNodeSelector.setToolTip( "Pick the basal volume for a-contrario detection." )
    #self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('Basal volume: ', self.basalVolumeAContrarioNodeSelector)

    # Ictal volume node selector
    self.ictalVolumeAContrarioNodeSelector = slicer.qMRMLNodeComboBox()
    self.ictalVolumeAContrarioNodeSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.ictalVolumeAContrarioNodeSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.ictalVolumeAContrarioNodeSelector.addEnabled = False
    self.ictalVolumeAContrarioNodeSelector.removeEnabled = False
    self.ictalVolumeAContrarioNodeSelector.setMRMLScene( slicer.mrmlScene )
    self.ictalVolumeAContrarioNodeSelector.setToolTip( "Pick the ictal volume for a-contrario detection." )
    #self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('Ictal volume: ', self.ictalVolumeAContrarioNodeSelector)

  
    # MRI node selector
    self.MRIAContrarioSelector = slicer.qMRMLNodeComboBox()
    self.MRIAContrarioSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.MRIAContrarioSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.MRIAContrarioSelector.addEnabled = False
    self.MRIAContrarioSelector.removeEnabled = False
    self.MRIAContrarioSelector.setMRMLScene( slicer.mrmlScene )
    self.MRIAContrarioSelector.setToolTip( "Pick the MRI volume for a-contrario detection." )
    #self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('MRI volume: ', self.MRIAContrarioSelector)

    #A-contrario detection button
    self.aContrarioDetectionButton = qt.QPushButton("Perform a-contrario detection")
    self.aContrarioDetectionButton.toolTip = "Perform a-contrario detection"
    self.aContrarioDetectionButton.name = "aContrarioDetectionButton"
    self.step3B_AContrarioDetectionCollapsibleButtonLayout.addRow('Foci detection: ', self.aContrarioDetectionButton)


    # Add substeps in a button group
    self.step3D_FociDetectionCollapsibleButtonGroup = qt.QButtonGroup()
    self.step3D_FociDetectionCollapsibleButtonGroup.addButton(self.step3A_SISCOMDetectionCollapsibleButton)
    self.step3D_FociDetectionCollapsibleButtonGroup.addButton(self.step3B_AContrarioDetectionCollapsibleButton)

    
    # Connections
    self.step3A_SISCOMDetectionCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep3A_SISCOMDetectionCollapsibleButtonClicked)
    self.step3B_AContrarioDetectionCollapsibleButton.connect('contentsCollapsed (bool)',self.onStep3B_AContrarioDetectionCollapsibleButtonClicked)
    self.aContrarioDetectionButton.connect('clicked()', self.onAContrarioDetectionButtonClicked)
    self.createMaskButton.connect('clicked()', self.onCreateMaskButtonClicked)
    self.SISCOMDetectionButton.connect('clicked()', self.onSubtractionDetectionButtonClicked)
    self.stdDevSISCOMSlider.connect('valueChanged(double)', self.onStdDevSISCOMSliderClicked)

    # Open OBI fiducial selection panel when step is first opened
    self.step3A_SISCOMDetectionCollapsibleButton.setProperty('collapsed', False)
    



  ### Callbacks  #####
  ## STEP 1 #######
  def onLoadBasalVolumeButtonClicked(self):
    if slicer.app.ioManager().openAddVolumeDialog():
      self.logic.setActiveVolumeAsBasal();
  #------------------------------------------------------------------------------------------------    
  def onRotateBasalISButtonClicked(self):
    self.logic.rotateBasal('IS');
  #------------------------------------------------------------------------------------------------    
  def onRotateBasalAPButtonClicked(self):
    self.logic.rotateBasal('AP');  
  #------------------------------------------------------------------------------------------------    
  def onRotateBasalLRButtonClicked(self):
    self.logic.rotateBasal('LR');
  #------------------------------------------------------------------------------------------------    
  def onLoadIctalVolumeButtonClicked(self):
    if slicer.app.ioManager().openAddVolumeDialog():
      self.logic.setActiveVolumeAsIctal();
  #------------------------------------------------------------------------------------------------    
  def onRotateIctalISButtonClicked(self):
    self.logic.rotateIctal('IS');
  #------------------------------------------------------------------------------------------------    
  def onRotateIctalAPButtonClicked(self):
    self.logic.rotateIctal('AP');  
  #------------------------------------------------------------------------------------------------    
  def onRotateIctalLRButtonClicked(self):
    self.logic.rotateIctal('LR');
  #------------------------------------------------------------------------------------------------    
  def onLoadMRIVolumeButtonClicked(self):
    if slicer.app.ioManager().openAddVolumeDialog():
      self.logic.setActiveVolumeAsMRI();
  #------------------------------------------------------------------------------------------------    
  def onRotateMRIISButtonClicked(self):
    self.logic.rotateMRI('IS');
  #------------------------------------------------------------------------------------------------    
  def onRotateMRIAPButtonClicked(self):
    self.logic.rotateMRI('AP');  
  #------------------------------------------------------------------------------------------------    
  def onRotateMRILRButtonClicked(self):
    self.logic.rotateMRI('LR');
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
    
  #------------------------------------------------------------------------------------------------          
  def onRegisterIctalToBasalButtonClicked(self):  
    if self.logic.registerIctalToBasal():    
      print('Registrooooooo!')
      
  #------------------------------------------------------------------------------------------------          
  def onComputeBasalAndIctalMaskButtonClicked(self):
    basalVolumeName = self.logic.BASAL_VOLUME_NAME  
    basalVolumeNode = slicer.util.getNode(basalVolumeName)
    ictalVolumeName = self.logic.REGISTERED_ICTAL_VOLUME_NAME    
    registeredIctalNode = slicer.util.getNode(ictalVolumeName)
    if registeredIctalNode is not None:
      self.logic.generateMask(basalVolumeNode,registeredIctalNode,0.4,1) 
      self.logic.displayVolume(self.logic.BASAL_ICTAL_MASK_NAME)
    else:
      print "It was not possible to find the registered-ictal node!"  
  #------------------------------------------------------------------------------------------------    
  
  
  def onCheckBasalAndIctalMaskButtonClicked(self):
    basalVolumeName = self.logic.BASAL_VOLUME_NAME  
    ictalVolumeName = self.logic.REGISTERED_ICTAL_VOLUME_NAME    
    basalIctalMaskName = self.logic.BASAL_ICTAL_MASK_NAME  
    self.layoutWidget.setLayout(self.customLayoutGridView3x3)  
    self.logic.compareBasalIctalMask(basalVolumeName, ictalVolumeName, basalIctalMaskName )    
   
   #--------------------------------------------------------------------------------------------- 
  def onRegisterBasalToMRIButtonClicked(self):    
    if self.logic.registerBasalToMRI():
      print('Registrooooooo!')   
   #---------------------------------------------------------------------------------------------     
  def onCreateMaskButtonClicked(self):
    basalVolumeNode = slicer.util.getNode(self.logic.BASAL_VOLUME_NAME)
    ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME) 
    volLogic=slicer.modules.volumes.logic()
    normalizedBasalVolumeNode = volLogic.CloneVolume(basalVolumeNode,basalVolumeNode.GetName() + '_normalized')
    normalizedIctalVolumeNode = volLogic.CloneVolume(ictalVolumeNode,ictalVolumeNode.GetName() + '_normalized')
    self.logic.getNormalizedImages(basalVolumeNode,ictalVolumeNode,0.4,1,normalizedBasalVolumeNode,normalizedIctalVolumeNode)  
    self.logic.generateMask(normalizedBasalVolumeNode,normalizedIctalVolumeNode)
    pass
  
  #------------------------------------------------------------------------------------------------------------------
  
  def onStep3A_SISCOMDetectionCollapsibleButtonClicked(self, collapsed):
    if collapsed == True:
      print "SISCOM is collapsed!"
    else: 
      if (self.backgroundVolumeNode is not None) and (self.SISCOMForegroundVolumeNode is not None):
        self.showActivations(self.backgroundVolumeNode, self.SISCOMForegroundVolumeNode) 
    
  def onStep3B_AContrarioDetectionCollapsibleButtonClicked(self, collapsed):
    if collapsed == True:
      print "AContrario is collapsed!"
    else:
      if (self.backgroundVolumeNode is not None) and (self.aContrarioForegroundVolumeNode is not None):
        self.showActivations(self.backgroundVolumeNode, self.aContrarioForegroundVolumeNode) 
                      
  #------------------------------------------------------------------------------------------------------------------      
  def onSubtractionDetectionButtonClicked(self): 
#     basalVolumeNode = slicer.util.getNode(self.logic.BASAL_VOLUME_NAME)
#     ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
#     subtractionOutputVolumeNode=slicer.vtkMRMLScalarVolumeNode()
#     slicer.mrmlScene.AddNode(subtractionOutputVolumeNode)
#     subtractionOutputVolumeNode.SetName("Ictal-Basal Subtraction") 
    result =self.logic.subtractImages()  
    #result= self.logic.subtractImages(ictalVolumeNode,basalVolumeNode, subtractionOutputVolumeNode) 
    if result==True:
      maskVolumeNode=slicer.util.getNode(self.logic.BASAL_ICTAL_MASK_NAME)
      subtractionOutputVolumeNode=slicer.util.getNode(self.logic.ICTAL_BASAL_SUBTRACTION)
      if maskVolumeNode is not None:
        maskVolumeNode.SetLabelMap(True)  
        self.logic.applyMaskToVolume(subtractionOutputVolumeNode,maskVolumeNode,subtractionOutputVolumeNode)  
      data=slicer.util.array(subtractionOutputVolumeNode.GetName())
      minimumValue = numpy.int(data.min())
      maximumValue = numpy.int(data.max())      
      
      stddev=data.std()
      print 'standard deviation = ' + str(stddev)
      stddevInside_mask = self.logic.computeStdDevInsideMask(subtractionOutputVolumeNode, maskVolumeNode)
      print 'standard deviation inside mask = ' + str(stddevInside_mask)
      self.stdDevSISCOMSlider.minimum = 0;
      self.stdDevSISCOMSlider.maximum = maximumValue / stddevInside_mask; 
      # creates a new colormap
      self.logic.createFociVisualizationColorMap(minimumValue,maximumValue)
      colorMapNode=slicer.util.getNode("FociDetectionColorMap")
      dnode=subtractionOutputVolumeNode.GetDisplayNode()
      dnode.SetAutoWindowLevel(0)
      dnode.SetWindowLevelMinMax(minimumValue,maximumValue)
      dnode.SetAndObserveColorNodeID(colorMapNode.GetID())
      
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
  
  #---------------------------------------------------------------------------------------
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
  def onAContrarioDetectionButtonClicked(self):   
#     basalVolumeNode = slicer.util.getNode(self.logic.BASAL_VOLUME_NAME)
#     ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)  
#     result = self.logic.detectFociAContrario(basalVolumeNode,ictalVolumeNode)
#     nfaOutputVolumeNode = slicer.util.getNode("NFA Output Volume Node")  
#     backgroundVolumeNode = ictalVolumeNode
#     foregroundVolumeNode = nfaOutputVolumeNode
#     self.showActivations(backgroundVolumeNode, foregroundVolumeNode)

    import EpileptogenicFocusDetectionLogic.AContrarioLogic as acl
    self.aContrarioDetection = acl.AContrarioDetection()
    self.aContrarioDetection.runAContrario()  
    mriVolumeNode = slicer.util.getNode(self.logic.MRI_VOLUME_NAME)
    if mriVolumeNode is not None:
      backgroundVolumeNode = mriVolumeNode
    else:
      ictalVolumeNode = slicer.util.getNode(self.logic.REGISTERED_ICTAL_VOLUME_NAME)
      backgroundVolumeNode = ictalVolumeNode
    foregroundVolumeNode = slicer.util.getNode(self.aContrarioDetection.ACONTRARIO_OUTPUT)
    self.showActivations(backgroundVolumeNode, foregroundVolumeNode)
    
    self.backgroundVolumeNode = backgroundVolumeNode
    self.aContrarioForegroundVolumeNode = foregroundVolumeNode
      
  #----------------------------------------------------------------------------------------------
  def showActivations(self,backgroundVolumeNode,foregroundVolumeNode):
    # Set the background volume 
    redWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeRed")
    redWidgetCompNode.SetBackgroundVolumeID(backgroundVolumeNode.GetID())
    redWidgetCompNode.SetForegroundVolumeID(foregroundVolumeNode.GetID())
    redWidgetCompNode.SetForegroundOpacity(1)
    redNode=slicer.util.getNode("vtkMRMLSliceNodeRed")
    redNode.SetSliceVisible(True)
    
    greenWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeGreen")
    greenWidgetCompNode.SetBackgroundVolumeID(backgroundVolumeNode.GetID())
    greenWidgetCompNode.SetForegroundVolumeID(foregroundVolumeNode.GetID())
    greenWidgetCompNode.SetForegroundOpacity(1)
    greenNode=slicer.util.getNode("vtkMRMLSliceNodeGreen")
    greenNode.SetSliceVisible(True)
    
    yellowWidgetCompNode = slicer.mrmlScene.GetNodeByID("vtkMRMLSliceCompositeNodeYellow")
    yellowWidgetCompNode.SetBackgroundVolumeID(backgroundVolumeNode.GetID())
    yellowWidgetCompNode.SetForegroundVolumeID(foregroundVolumeNode.GetID())
    yellowWidgetCompNode.SetForegroundOpacity(1)  
    yellowNode=slicer.util.getNode("vtkMRMLSliceNodeGreen")
    yellowNode.SetSliceVisible(True)
    
    self.layoutWidget.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutConventionalView)  
    
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
    mainFrame = SliceletMainFrame()
    mainFrame.setMinimumWidth(1200)
    mainFrame.connect('destroyed()', self.onSliceletClosed)
    slicelet = EpileptogenicFocusDetectionSlicelet(mainFrame)
    mainFrame.setSlicelet(slicelet)

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
