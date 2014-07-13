import os
import time
from __main__ import vtk, qt, ctk, slicer
from math import *
import AContrarioLogic as acl
from vtk.util import numpy_support
import numpy as np
import SimpleITK as sitk
import sitkUtils


class hdfe:
    def __init__(self):
        self.BASAL_VOLUME_NAME = 'P1_B'
        self.ICTAL_VOLUME_NAME = 'P1_Ic'
        self.MRI_VOLUME_NAME = 'P1_MRI_T2'
        self.MASK_VOLUME_NAME = 'Mask'
        
        # Get the numpy arrays
        self.inter = slicer.util.array(self.BASAL_VOLUME_NAME)
        self.ic = slicer.util.array(self.ICTAL_VOLUME_NAME)
        self.mask = slicer.util.array(self.BASAL_VOLUME_NAME)
        
        
    
    def binaryClosingWithBall (self, array, radius):
        sitkArray = sitk.GetImageFromArray(array)
        sitkClosed = sitk.BinaryMorphologicalClosing(sitkArray, radius)
        resultArray = sitk.GetArrayFromImage(sitkClosed)        
        return resultArray
      
    def binaryOpeningWithBall (self, array, radius):
        sitkArray = sitk.GetImageFromArray(array)
        sitkClosed = sitk.BinaryMorphologicalOpening(sitkArray, radius)
        resultArray = sitk.GetArrayFromImage(sitkClosed)        
        return resultArray
    
    def binaryConnectedComponents (self, array):
        sitkArray = sitk.GetImageFromArray(array)
        sitkLabels = sitk.ConnectedComponent(sitkArray, fullyConnected = True )
        resultArray = sitk.GetArrayFromImage(sitkLabels)        
        return resultArray
      
    def pushArrayToSlicer(self, array, nodeName='ArrayPushedFromCode', compositeView=0, overWrite=False):
        sitkImage = sitk.GetImageFromArray(array)
        sitkUtils.PushToSlicer(sitkImage, nodeName, compositeView, overWrite)
        
    def getArrayFromSlicer(self,nodeName):
        return (slicer.util.array(nodeName))
      
    
    def runTestRellenarMascara(self):
        matlabMask = self.getArrayFromSlicer('ictal_mask')
        self.pushArrayToSlicer(matlabMask, 'rellenar_mascara____MascaraNuevaDeMatlab', overWrite=True)
        
        rawMask = self.getArrayFromSlicer('ictal_mask_sinRellenar')
        mask = self.rellenar_mascara(rawMask, 4, 2)
        self.pushArrayToSlicer(mask, 'rellenar_mascara____MascaraNueva', overWrite=True)
        
        self.pushArrayToSlicer(matlabMask-mask, 'rellenar_mascara____DiferenciaCon MascaraDeMatlab', overWrite=True)
        
        
    
    def rellenar_mascara(self, mascara, metodo, radio):
        #function [mascara_nueva,vecindad]=rellenar_mascara(mascara,metodo,radio)
        
        #funcion que rellena los huecos que pueden quedar en las mascaras. 
        
        #mascara es mascara original
        #metodo puede ser:
            #1 para labeling
            #2 para primero  clausura y despues apertura (#cambio el orden en v6.2
            #3 para primero clausura-apertura y despues labeling #cambio el orden #en v6.2
            #4 para metodo iterativo (clausura, apertura, labeling) aumentando el
            #radio del elemento estructurante
        #radio es el radio usado para apertura y clausura, como elemento
        #estructurante se usa una esfera
        
        #si se elige metodo 1, la entrada radio puede ser cualquier cosa, no se tiene
        #en cuentas
        max_iter = 10;          # # de iteraciones maximas para el metodo 4
        delta_minimo = 9e-4;  # Resuelve conflicto de edad de pacientes pequenos (ninos)-Huecos
        
        [alto,ancho,capas]=mascara.shape;
#        [vecindad] = disco(radio);
        if metodo==1:
            pass
#            auxiliar = mascara<1;
#            [L,NUM] = bwlabeln(auxiliar,26);#se usa funcion labelling 3d de matlab
#            M=L;
#            ###cambio respecto a version anterior:
#            #en alguinos pocos casos  el fondo no queda en el cluster 1, queda en otro cluster y eso hace
#            ###que la mascara quede casi toda en 1. Lo que se hace es mirar las
#            ###puntas, si pertenecen al mismo cluster (fondo ) entonces se usa ese
#            ###valor. Si no pertenecen al mismo me la juego por el cluster 1
#            a=M(1,1,1;
#            b=M(1,1,end);
#            c=M(1,end,1);
#            d=M(end,1,1); #podria seguir, solo se usan las 4 esquinas
#            
#            
#            if a==b & b==c & c==d #si las 4 esquinas pertenecen al mismo cluster
#                M(find(L~=a))=0;
#            else #si son distintos me la juego por 1
#                M(find(L~=1))=0;
#            end
#            ###fin cambios  --> M(find(L~=1))=0;
#            mascara_nueva=M<1;
        elif metodo==2:
            pass
#                
#                se = vecindad;
#                #mascara_nueva = imopen (mascara,se);
#                #mascara_nueva = imclose(mascara_nueva,se);
#                mascara_nueva=imclose(mascara,se);#se aplica morfologia
#                mascara_nueva = imopen (mascara_nueva,se);
#                
        elif metodo==3:
            pass
#                
#                se = vecindad;
#                #mascara_nueva = imopen (mascara,se);
#                #mascara_nueva=imclose(mascara_nueva,se);
#                mascara_nueva=imclose(mascara,se);#se aplica morfologia
#                mascara_nueva = imopen (mascara_nueva,se);
#                auxiliar=mascara_nueva<1;
#                [L,NUM] = bwlabeln(auxiliar,26);#luego se aplica labeling
#                M=L;
#                ###cambio respecto a version anterior:
#            #en alguinos pocos casos  el fondo no queda en el cluster 1, queda en otro cluster y eso hace
#                ###que la mascara quede casi toda en 1. Lo que se hace es mirar las
#                ###puntas, si pertenecen al mismo cluster (fondo ) entonces se usa ese
#                ###valor. Si no pertenecen al mismo me la juego por el cluster 1
#                a=M(1,1,1);
#                b=M(1,1,capas);
#                c=M(1,ancho,1);
#                d=M(alto,1,1);#podria seguir, solo se usan las 4 esquinas
#                
#                if a==b & b==c & c==d
#                    
#                    M(find(L~=a))=0;
#                else #si son distintos me la juego por 1
#                    M(find(L~=1))=0;
#                end
#                ###fin cambios -->  M(find(L~=1))=0;
#                mascara_nueva=M<1;
        elif metodo==4: #metodo iterativo
            indicador = 1;
            [x,y,z] = mascara.shape;
            ind_previo = np.inf;
            delta = np.inf;
            for it in range(0,max_iter):    #se repite este paso, se va agrandando el radio hasta que el metodo "converge"
                
                mascara_nueva = self.binaryClosingWithBall(mascara,radio) # imclose(mascara,se);
                mascara_nueva = self.binaryOpeningWithBall(mascara_nueva,radio) #imopen(mascara_nueva,se);
                
                self.pushArrayToSlicer( mascara_nueva ,'rellenar_mascara_____LuegodeMorfologia' ,  overWrite=True)
                
                auxiliar=mascara_nueva.copy(); auxiliar[mascara_nueva<1]=1; auxiliar[mascara_nueva>0]=0; # invert the mask (now the brain is 0 and the background and holes is 1
                L = self.binaryConnectedComponents(auxiliar)  #[L,NUM] = bwlabeln(auxiliar,26);
                
                self.pushArrayToSlicer( L ,'rellenar_mascara_____Labels' ,  overWrite=True)
                
                M=L.copy();
                a=M[0,0,0];
                b=M[0,0,capas-1];
                c=M[0,ancho-1,0];
                d=M[alto-1,1,1];
                #podria seguir, me quedo con estos nomas
                if a==b and  b==c and c==d :
                    #'entro al if'
                    M[L!=a]=0;
                else :#si son distintos me la juego por 1
                    M[L!=1]=0;
                
                #M(find(L~=1))=0;
                mascara_nueva[M<1]=1; mascara_nueva[M>0]=0;  #undo the inversion (now the brain is 1)
                
                # Calculo del indicador
                indicador = ((mascara_nueva>0).sum())/(x*y*z); #indicador=voxeles no zero / volumen img
                radio = radio+1  ;               
                # print it
                delta = abs(indicador-ind_previo);
                if delta<=delta_minimo : #si se llega al umbral para, sino sigue
                    break
                
                ind_previo = indicador;
                
                
        else:
                mascara_nueva=0;
                'metodo solo puede valer 1,2,3 o 4'
        
        return mascara_nueva
                
        
        

#
# EpileptogenicFocusDetectionLogic
#
class EpileptogenicFocusDetectionLogic:
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget
  """

  def __init__(self):
    # Define constants
    self.BASAL_VOLUME_NAME = 'basalVolume'
    self.ICTAL_VOLUME_NAME = 'ictalVolume'
    self.MRI_VOLUME_NAME = 'mriVolume'
    
    self.REGISTERED_ICTAL_VOLUME_NAME = 'ictalVolume_basalVolume'
    
    self.BASAL_ICTAL_MASK_NAME = 'basalIctalMaskVolume'
    self.MRI_BRAIN_MASK_NAME = 'mriBrainMaskVolume'
    
    self.BASAL_TRANSFORM_NAME = 'basalTransform'
    self.ICTAL_TRANSFORM_NAME = 'ictalTransform'
    self.MRI_TRANSFORM_NAME = 'mriTransform'
    
    self.ICTAL_TO_BASAL_REGISTRATION_TRANSFORM_NAME = 'ictalToBasalTransform'
    self.BASAL_TO_MRI_REGISTRATION_TRANSFORM_NAME = 'basalToMRITransform'
    
    self.obiToPlanTransformName = 'obiToPlanTransform'
    self.obiToMeasuredTransformName = "obiToMeasuredTransform"
    
    self.FOCI_DETECTION_COLORMAP_NAME = "FociDetectionColorMap"

    # Declare member variables (mainly for documentation)
    self.pddDataArray = None
    self.calculatedDose = None # Computed from Pdd usinf RDF and Electron MUs
    self.calibrationDataArray = None
    self.calibrationDataAlignedArray = None # Calibration array registered (X shift and Y scale) to the Pdd curve
    self.opticalDensityVsDoseFunction = None
    self.calibrationPolynomialCoefficients = None

  # ---------------------------------------------------------------------------
  # Use BRAINS registration to register PlanCT to OBI volume
  # and apply the result to the PlanCT and PlanDose
  def registerObiToPlanCt(self, obiVolumeID, planCtVolumeID, planDoseVolumeID, planStructuresID):
    try:
      qt.QApplication.setOverrideCursor(qt.QCursor(qt.Qt.BusyCursor))
      parametersRigid = {}
      parametersRigid["fixedVolume"] = planCtVolumeID
      parametersRigid["movingVolume"] = obiVolumeID
      parametersRigid["useRigid"] = True
      parametersRigid["initializeTransformMode"] = "useMomentsAlign"
      #parametersRigid["backgroundFillValue"] = -1000.0

      # Set output transform
      obiToPlanTransformNode = slicer.util.getNode(self.obiToPlanTransformName)
      if obiToPlanTransformNode == None:
        obiToPlanTransformNode = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(obiToPlanTransformNode)
        obiToPlanTransformNode.SetName(self.obiToPlanTransformName)
      parametersRigid["linearTransform"] = obiToPlanTransformNode.GetID()

      # Runs the brainsfit registration
      brainsFit = slicer.modules.brainsfit
      cliBrainsFitRigidNode = None
      cliBrainsFitRigidNode = slicer.cli.run(brainsFit, None, parametersRigid)

      waitCount = 0
      while cliBrainsFitRigidNode.GetStatusString() != 'Completed' and waitCount < 200:
        self.delayDisplay( "Register OBI to PlanCT using rigid registration... %d" % waitCount )
        waitCount += 1
      self.delayDisplay("Register OBI to PlanCT using rigid registration finished")
      qt.QApplication.restoreOverrideCursor()
      
      # Invert output transform (planToObi) to get the desired obiToPlan transform
      obiToPlanTransformNode.GetMatrixTransformToParent().Invert()

      # Apply transform to plan CT and plan dose
      planCtVolumeNode = slicer.mrmlScene.GetNodeByID(planCtVolumeID)
      planCtVolumeNode.SetAndObserveTransformNodeID(obiToPlanTransformNode.GetID())
      if planCtVolumeID != planDoseVolumeID:
        planDoseVolumeNode = slicer.mrmlScene.GetNodeByID(planDoseVolumeID)
        planDoseVolumeNode.SetAndObserveTransformNodeID(obiToPlanTransformNode.GetID())
      else:
        print('WARNING: The selected nodes are the same for plan CT and plan dose!')
      # The output transform was automatically applied to the moving image (the OBI), undo that
      obiVolumeNode = slicer.mrmlScene.GetNodeByID(obiVolumeID)
      obiVolumeNode.SetAndObserveTransformNodeID(None)
      
      # Apply transform to plan structures
      planStructuresNode = slicer.mrmlScene.GetNodeByID(planStructuresID)
      childrenContours = vtk.vtkCollection()
      planStructuresNode.GetAssociatedChildrenNodes(childrenContours)
      for contourIndex in xrange(0, childrenContours.GetNumberOfItems()):
        contour = childrenContours.GetItemAsObject(contourIndex)
        if contour.IsA('vtkMRMLContourNode'): # There is one color table node in the collection, ignore it
          contour.SetAndObserveTransformNodeID(obiToPlanTransformNode.GetID())

    except Exception, e:
      import traceback
      traceback.print_exc()
    
  # ---------------------------------------------------------------------------
  def registerObiToMeasured(self, obiFiducialListID, measuredFiducialListID):
    try:
      qt.QApplication.setOverrideCursor(qt.QCursor(qt.Qt.BusyCursor))
      parametersFiducial = {}
      parametersFiducial["fixedLandmarks"] = obiFiducialListID
      parametersFiducial["movingLandmarks"] = measuredFiducialListID
      
      # Create linear transform which will store the registration transform
      obiToMeasuredTransformNode = slicer.util.getNode(self.obiToMeasuredTransformName)
      if obiToMeasuredTransformNode == None:
        obiToMeasuredTransformNode = slicer.vtkMRMLLinearTransformNode()
        slicer.mrmlScene.AddNode(obiToMeasuredTransformNode)
        obiToMeasuredTransformNode.SetName(self.obiToMeasuredTransformName)
      parametersFiducial["saveTransform"] = obiToMeasuredTransformNode.GetID()
      parametersFiducial["transformType"] = "Rigid"

      # Run fiducial registration
      fiducialRegistration = slicer.modules.fiducialregistration
      cliFiducialRegistrationRigidNode = None
      cliFiducialRegistrationRigidNode = slicer.cli.run(fiducialRegistration, None, parametersFiducial)

      waitCount = 0
      while cliFiducialRegistrationRigidNode.GetStatusString() != 'Completed' and waitCount < 200:
        self.delayDisplay( "Register MEASURED to OBI using fiducial registration... %d" % waitCount )
        waitCount += 1
      self.delayDisplay("Register MEASURED to OBI using fiducial registration finished")
      qt.QApplication.restoreOverrideCursor()
      
      # Apply transform to MEASURED fiducials
      measuredFiducialsNode = slicer.mrmlScene.GetNodeByID(measuredFiducialListID)
      measuredFiducialsNode.SetAndObserveTransformNodeID(obiToMeasuredTransformNode.GetID())

      return cliFiducialRegistrationRigidNode.GetParameterAsString('rms')
    except Exception, e:
      import traceback
      traceback.print_exc()

  # ---------------------------------------------------------------------------
  def displayVolume(self, volumeName):
    # automatically select the volume to display
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    volumeNode = slicer.util.getNode(volumeName)
    if not volumeNode == None:
      volumeID = volumeNode.GetID()
    else:
      volumeID = None
    selectionNode.SetReferenceActiveVolumeID( volumeID )
    slicer.app.applicationLogic().PropagateVolumeSelection()
  
  # ---------------------------------------------------------------------------
  # tomado de EditUtil.py
  def getCompositeNode(self,layoutName='Red'):
    """ use the Red slice composite node to define the active volumes """
    count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
    for n in xrange(count):
      compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceCompositeNode')
      if compNode.GetLayoutName() == layoutName:
        return compNode
    
  # ---------------------------------------------------------------------------  
  def getSliceNode(self,sliceName='Red'):
    """ use the Red slice composite node to define the active volumes """
    count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
    for n in xrange(count):
      sliceNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceNode')
      if sliceNode.GetName() == sliceName:
        return sliceNode
  
  # ---------------------------------------------------------------------------
  def getSliceWidget(self,layoutName='Red'):
    """ use the Red slice widget as the default"""
    layoutManager = slicer.app.layoutManager()
    sliceWidget = layoutManager.sliceWidget(layoutName)
    return sliceWidget

  # ---------------------------------------------------------------------------
  def getSliceLogic(self,layoutName='Red'):
    """ use the Red slice logic as the default for operations that are
    not specific to a slice widget"""
    sliceWidget = self.getSliceWidget(layoutName)
    return sliceWidget.sliceLogic()
  
  # ---------------------------------------------------------------------------
  def toggleCrosshair(self):
    """Turn on or off the crosshair and enable navigation mode
    by manipulating the scene's singleton crosshair node.
    """
    crosshairNode = slicer.util.getNode('vtkMRMLCrosshairNode*')
    if crosshairNode:
      if crosshairNode.GetCrosshairMode() == 0:
        crosshairNode.SetCrosshairMode(1)
      else:
        crosshairNode.SetCrosshairMode(0)
  
  # ---------------------------------------------------------------------------      
  def displayVolumeInSlice(self,volumeName, sliceLayoutName, sliceOrientation = "Axial"):
    compositeNode = self.getCompositeNode(sliceLayoutName)
    sliceNode = self.getSliceNode(sliceLayoutName)
    volumeNode = slicer.util.getNode(volumeName)
    if not compositeNode == None and not volumeNode == None:
      compositeNode.SetBackgroundVolumeID(volumeNode.GetID())
    else:
      print("displayVolumeInSlice failed")
    if not sliceNode==None:
      sliceNode.SetOrientation(sliceOrientation)
  
  # ---------------------------------------------------------------------------
  def getLayoutNode(self):
    layoutNode = slicer.mrmlScene.GetNodesByClass('vtkMRMLLayoutNode').GetItemAsObject(0)
    return layoutNode
  
  # ---------------------------------------------------------------------------  
  def compareBasalIctalMRI(self, basalVolumeName, ictalVolumeName, mriVolumeName):
    self.displayVolumeInSlice(basalVolumeName, 'Compare1', 'Axial')
    self.displayVolumeInSlice(basalVolumeName, 'Compare2', 'Sagittal')
    self.displayVolumeInSlice(basalVolumeName, 'Compare3', 'Coronal')    
    
    self.displayVolumeInSlice(ictalVolumeName, 'Compare4', 'Axial')
    self.displayVolumeInSlice(ictalVolumeName, 'Compare5', 'Sagittal')
    self.displayVolumeInSlice(ictalVolumeName, 'Compare6', 'Coronal')
    
    self.displayVolumeInSlice(mriVolumeName, 'Compare7', 'Axial')
    self.displayVolumeInSlice(mriVolumeName, 'Compare8', 'Sagittal')
    self.displayVolumeInSlice(mriVolumeName, 'Compare9', 'Coronal')
    
    crosshairNode = slicer.util.getNode('vtkMRMLCrosshairNode*')
    crosshairNode.SetCrosshairMode(1)
    crosshairNode.SetNavigation(True)

  # ---------------------------------------------------------------------------
  def compareBasalIctalMask(self, basalVolumeName, ictalVolumeName, basalIctalMaskName):
       
    self.displayVolumeInSlice(basalVolumeName, 'Compare1', 'Axial')
    self.displayVolumeInSlice(basalVolumeName, 'Compare2', 'Sagittal')
    self.displayVolumeInSlice(basalVolumeName, 'Compare3', 'Coronal')
    
    self.displayVolumeInSlice(ictalVolumeName, 'Compare4', 'Axial')
    self.displayVolumeInSlice(ictalVolumeName, 'Compare5', 'Sagittal')
    self.displayVolumeInSlice(ictalVolumeName, 'Compare6', 'Coronal')
    
    self.displayVolumeInSlice(basalIctalMaskName , 'Compare7', 'Axial')
    self.displayVolumeInSlice(basalIctalMaskName, 'Compare8', 'Sagittal')
    self.displayVolumeInSlice(basalIctalMaskName, 'Compare9', 'Coronal')
    
    crosshairNode = slicer.util.getNode('vtkMRMLCrosshairNode*')
    crosshairNode.SetCrosshairMode(1)
    crosshairNode.SetNavigation(True)
  
  # ---------------------------------------------------------------------------  
  def setActiveVolumeAsBasal(self):
      self.setActiveVolumeName(self.BASAL_VOLUME_NAME);
      self.initializeVolumeTransform(self.BASAL_VOLUME_NAME, self.BASAL_TRANSFORM_NAME)
  
  # ---------------------------------------------------------------------------    
  def setActiveVolumeAsIctal(self):
      self.setActiveVolumeName(self.ICTAL_VOLUME_NAME);
      self.initializeVolumeTransform(self.ICTAL_VOLUME_NAME, self.ICTAL_TRANSFORM_NAME)
  
  # ---------------------------------------------------------------------------    
  def setActiveVolumeAsMRI(self):
      self.setActiveVolumeName(self.MRI_VOLUME_NAME);            
      self.initializeVolumeTransform(self.MRI_VOLUME_NAME, self.MRI_TRANSFORM_NAME)
  
  # ---------------------------------------------------------------------------
  def rotateBasal(self, axis):
      self.add180RotationAroundAxis(self.BASAL_TRANSFORM_NAME, axis)
  
  # ---------------------------------------------------------------------------
  def rotateIctal(self, axis):
      self.add180RotationAroundAxis(self.ICTAL_TRANSFORM_NAME, axis)
  
  # ---------------------------------------------------------------------------
  def rotateMRI(self, axis):
      self.add180RotationAroundAxis(self.MRI_TRANSFORM_NAME, axis)
  
  # ---------------------------------------------------------------------------
  def registerIctalToBasal(self):
    return self.registerVolumes(self.BASAL_VOLUME_NAME, self.BASAL_TRANSFORM_NAME, self.ICTAL_VOLUME_NAME, self.ICTAL_TRANSFORM_NAME, self.ICTAL_TO_BASAL_REGISTRATION_TRANSFORM_NAME)

  # ---------------------------------------------------------------------------
  def registerBasalToMRI(self):
    ret = self.registerVolumes(self.MRI_VOLUME_NAME, self.MRI_TRANSFORM_NAME, self.BASAL_VOLUME_NAME, self.BASAL_TRANSFORM_NAME, self.BASAL_TO_MRI_REGISTRATION_TRANSFORM_NAME)
    if ret:
      #concatenate with IctalToBasal
      ictalToBasalTransformNode = slicer.util.getNode(self.ICTAL_TO_BASAL_REGISTRATION_TRANSFORM_NAME);
      basalToMRITransformNode = slicer.util.getNode(self.BASAL_TO_MRI_REGISTRATION_TRANSFORM_NAME);
      if not ictalToBasalTransformNode == None and not basalToMRITransformNode == None:
        ictalToBasalTransformNode.SetAndObserveTransformNodeID(basalToMRITransformNode.GetID())
      else:
        print('registerBasalToMRI: ictalToBasalTransformNode.SetAndObserveTransformNodeID(basalToMRITransformNode.GetID()) failed') 
        
    return ret
  
  # ---------------------------------------------------------------------------      
  def setActiveVolumeName(self, newName):
      vl = slicer.modules.volumes
      vl = vl.logic()
      """ get the active node """
      activeVolumeNode = vl.GetActiveVolumeNode()
      """ if there exists a node with name=newName, then remove it"""  
      volumeNodeToDelete = slicer.util.getNode(newName);
      if not volumeNodeToDelete == None:
          slicer.mrmlScene.RemoveNode(volumeNodeToDelete)          
      """ set the name of the active node """
      activeVolumeNode.SetName(newName);      

  # ---------------------------------------------------------------------------
  def initializeVolumeTransform(self, volumeName, transformName):
      """ if there exists a node with name=transformName, 
             then remove it, 
          create and set the volume to this transform
      """ 
      transformNode = slicer.util.getNode(transformName);
      if not transformNode == None:
          slicer.mrmlScene.RemoveNode(transformNode)   
      
      transformNode = slicer.vtkMRMLLinearTransformNode()
      transformNode.SetName(transformName)
      slicer.mrmlScene.AddNode(transformNode)
      
      """ connect the transform node with the matrix """
      matrix = transformNode.GetMatrixTransformToParent()
      transformNode.SetAndObserveMatrixTransformToParent(matrix)
      
      """ connect the volume with the transform node"""
      volumeNode = slicer.util.getNode(volumeName);
      if not volumeNode == None:
          volumeNode.SetAndObserveTransformNodeID(transformNode.GetID())
   
  # ---------------------------------------------------------------------------    
  def add180RotationAroundAxis(self, transformName, axis):
      rotationMatrix = vtk.vtkMatrix4x4()
      if axis == 'IS':
          rotationMatrix.SetElement(0, 0, -1);
          rotationMatrix.SetElement(1, 1, -1);
          rotationMatrix.SetElement(2, 2, 1);
      elif axis == 'AP' or axis == 'PA':
          rotationMatrix.SetElement(0, 0, -1);
          rotationMatrix.SetElement(1, 1, 1);
          rotationMatrix.SetElement(2, 2, -1);
      elif axis == 'LR':
          rotationMatrix.SetElement(0, 0, 1);
          rotationMatrix.SetElement(1, 1, -1);
          rotationMatrix.SetElement(2, 2, -1);          
      pass
  
      transformNode = slicer.util.getNode(transformName);
      if not transformNode == None:
          transformMatrixToParent = transformNode.GetMatrixTransformToParent()
          newTransformMatrixToParent = vtk.vtkMatrix4x4()
          vtk.vtkMatrix4x4.Multiply4x4(rotationMatrix, transformMatrixToParent, newTransformMatrixToParent)
          transformNode.SetAndObserveMatrixTransformToParent(newTransformMatrixToParent)

  # ---------------------------------------------------------------------------
  def registerVolumes(self, fixedVolumeName, fixedTransformName, movingVolumeName, movingTransformName, registrationTransformName):
      #self.Registered = False
      
      # get the nodes
      fixedTransformNode = slicer.util.getNode(fixedTransformName)
      movingTransformNode = slicer.util.getNode(movingTransformName)   
      fixedVolumeNode = slicer.util.getNode(fixedVolumeName)
      movingVolumeNode = slicer.util.getNode(movingVolumeName)
      
      # check volumes
      if not fixedVolumeNode or not movingVolumeNode:
        print('Registration failed: the volume nodes are not set correctly')
        return False
      
      # setup the brainsfit CLI module
      parameters = {}
      parameters["fixedVolume"] = fixedVolumeNode.GetID()
      parameters["movingVolume"] = movingVolumeNode.GetID()
      parameters["useRigid"] = True
      
      transformNode = slicer.util.getNode(registrationTransformName);
      if not transformNode == None:
          slicer.mrmlScene.RemoveNode(transformNode) 
          
      registrationTransformNode = slicer.vtkMRMLLinearTransformNode()
      registrationTransformNode.SetName(registrationTransformName)
      slicer.mrmlScene.AddNode(registrationTransformNode)
      parameters["linearTransform"] = registrationTransformNode.GetID()
      parameters["initializeTransformMode"] = "useCenterOfHeadAlign"
      
      outputVolumeNode = slicer.vtkMRMLScalarVolumeNode()
      slicer.mrmlScene.AddNode(outputVolumeNode)
      outputVolumeNode.SetName(movingVolumeNode.GetName()+"_"+fixedVolumeNode.GetName())
      parameters["outputVolume"] = outputVolumeNode.GetID()
      brainsfit = slicer.modules.brainsfit
      
      # run the registration
      cliBrainsFitRigidNode = slicer.cli.run(brainsfit, None, parameters)  
      #cliBrainsFitRigidNode = slicer.cli.run(brainsfit, None, parameters, True)  # El ultimo true es para que espere hasta la finalizacion
      
      waitCount = 0
      while cliBrainsFitRigidNode.GetStatusString() != 'Completed' and waitCount < 20:
        self.delayDisplay( "Register " + movingVolumeNode.GetName()+ "to " + fixedVolumeNode.GetName() +  "... %d" % waitCount )
        waitCount += 1
      self.delayDisplay("Register " + movingVolumeNode.GetName()+ "to " + fixedVolumeNode.GetName() + " finished")
      qt.QApplication.restoreOverrideCursor()
      
      if not cliBrainsFitRigidNode:
         slicer.mrmlScene.RemoveNode(registrationTransformNode.GetID()) 
         print('Registration failed: Brainsfit module failed')
      else:  
         # attach the transform to the moving volume
         movingVolumeNode.SetAndObserveTransformNodeID(registrationTransformNode.GetID())
         pass
         
      return cliBrainsFitRigidNode
  
  # ---------------------------------------------------------------------------
  def otsuThresholdVolume(self, inputVolumeName, maskVolumeName, thresholdedVolumeName, insideValue=0, outsideValue=1,numberOfBins=128):
      thresholded = False
      
      # get the nodes
      inputVolumeNode = slicer.util.getNode(inputVolumeName)
      maskVolumeNode = slicer.util.getNode(maskVolumeName)
      thresoldedVolumeNode = slicer.util.getNode(thresholdedVolumeName)
      
      # check volumes
      if not inputVolumeNode or not maskVolumeNode:
        print('otsuThresholdVolume failed: the volume nodes are not set correctly')
        return False
      
      # check output volume node
      if not thresoldedVolumeNode:
        thresoldedVolumeNode = slicer.vtkMRMLScalarVolumeNode()
        thresoldedVolumeNode.SetName(thresholdedVolumeName)
        slicer.mrmlScene.AddNode(thresoldedVolumeNode)
        
      # setup the CLI module
      parameters = {}
      parameters["insideValue"] = insideValue
      parameters["outsideValue"] = outsideValue;
      parameters["numberOfBins"] = numberOfBins;
      
      parameters["inputVolume"] = inputVolumeNode.GetID();
      parameters["outputVolume"] = thresoldedVolumeNode.GetID();
      
      
      otsuImageFilter = slicer.modules.otsuthresholdimagefilter
      
      # run the registration
      thresholded = slicer.cli.run(otsuImageFilter, None, parameters, True)  # El ultimo true es para que espere hasta la finalizacion
      
      if not thresholded:
        print('OTSU failed')
      
         
      return thresholded

  # ---------------------------------------------------------------------------
  def computeBasalIctalMask(self, basalVolumeName, ictalVolumeName, basalIctalMaskVolumeName):
    self.computeBasalIctalMaskImplementation(basalVolumeName, ictalVolumeName, basalIctalMaskVolumeName,3,2,1)
  
  # ---------------------------------------------------------------------------
  def computeStdDevInsideMask(self, subtractionOutputVolumeNode, maskVolumeNode):
    subtractionArray = slicer.util.array(subtractionOutputVolumeNode.GetName())
    maskArray = slicer.util.array(maskVolumeNode.GetName())      
    mask_GreaterThanZeroIndices = (maskArray > 0).nonzero();
    std_inside_mask = subtractionArray[mask_GreaterThanZeroIndices].std()
    return std_inside_mask
    
  # ---------------------------------------------------------------------------
  def getNormalizedImages(self,basalVolumeNode, ictalVolumeNode, threshold, zmax, normalizedBasalVolumeNode, normalizedIctalVolumeNode ):
    basalArray = slicer.util.array(basalVolumeNode.GetName())
    ictalArray = slicer.util.array(ictalVolumeNode.GetName())
    normalizedBasalArray = slicer.util.array(normalizedBasalVolumeNode.GetName())
    normalizedIctalArray = slicer.util.array(normalizedIctalVolumeNode.GetName())
    # Create an auxiliar mask using the threshold value
    maxBasal = basalArray.max() 
    maxIctal = ictalArray.max()     
    basal_mask=basalArray>threshold*maxBasal
    ictal_mask=ictalArray>threshold*maxIctal   
    # Compute mean and std in pixels inside the mask
    basal_mask_GreaterThanZeroIndices = (basal_mask > 0).nonzero();
    mean_basal_inside_mask = basalArray[basal_mask_GreaterThanZeroIndices].mean()
    std_basal_inside_mask = basalArray[basal_mask_GreaterThanZeroIndices].std()
    ictal_mask_GreaterThanZeroIndices = (ictal_mask > 0).nonzero();
    mean_ictal_inside_mask = ictalArray[ictal_mask_GreaterThanZeroIndices].mean()
    std_ictal_inside_mask = ictalArray[ictal_mask_GreaterThanZeroIndices].std()
    # Compute the z scores maps
    basal_map = np.zeros(basalArray.shape,np.bool) # maps initialized to zero
    ictal_map = np.zeros(basalArray.shape,np.bool)
    z_basal = abs(basalArray - mean_basal_inside_mask)/std_basal_inside_mask  # 
    z_ictal = abs(ictalArray - mean_ictal_inside_mask)/std_ictal_inside_mask
    z_basal_below_zmax = z_basal < zmax
    z_ictal_below_zmax = z_ictal < zmax
    basal_map[z_basal_below_zmax]=1
    basal_map = basal_map * basal_mask  # Remove the z<z_max outside the mask
    ictal_map[z_ictal_below_zmax]=1
    ictal_map = ictal_map * ictal_mask  # Remove the z<z_max outside the mask
    # Compute the intersection of the maps
    intersection_map = basal_map * ictal_map
    intersection_region = intersection_map>0 
    basal_normalization_factor = basalArray[intersection_region].mean()
    ictal_normalization_factor = ictalArray[intersection_region].mean()
    normalizedBasalArray[:] = basalArray/basal_normalization_factor
    normalizedIctalArray[:] = ictalArray/ictal_normalization_factor
    normalizedBasalVolumeNode.GetImageData().Modified()
    normalizedBasalVolumeNode.GetImageData().Modified()
    
    
  # ---------------------------------------------------------------------------  
  def generateMask(self, normalizedBasalVolumeNode, normalizedIctalVolumeNode):  
    normalizedBasalArray = slicer.util.array(normalizedBasalVolumeNode.GetName())
    normalizedIctalArray = slicer.util.array(normalizedIctalVolumeNode.GetName())   
    max_norm_basal =  normalizedBasalArray.max()    
    max_norm_ictal =  normalizedIctalArray.max()  
    basalMask = normalizedBasalArray>0.4* max_norm_basal
    ictalMask = normalizedIctalArray>0.4* max_norm_ictal
    # Create the masks
    mask = basalMask * ictalMask
    volLogic=slicer.modules.volumes.logic()
    maskVolumeNode = volLogic.CloneVolume(normalizedBasalVolumeNode,'intersection_mask')
    maskArray = slicer.util.array(maskVolumeNode.GetName())
    maskArray[:]=mask
    maskVolumeNode.GetImageData().Modified()
    maskVolumeNode.SetLabelMap(True)  
    
    
  # ---------------------------------------------------------------------------  
  def computeBasalIctalMaskImplementation(self,basalVolumeName, ictalVolumeName, basalIctalMaskVolumeName,ra,rb,rc):
      
      # get the nodes
      basalVolumeNode = slicer.util.getNode(basalVolumeName)
      ictalVolumeNode = slicer.util.getNode(ictalVolumeName)
      basalIctalMaskVolumeNode = slicer.util.getNode(basalIctalMaskVolumeName)
      
      # check volumes
      if not basalVolumeNode or not ictalVolumeNode:
        print('computeBasalIctalMask failed: the volume nodes are not set correctly')
        return False
      
      # check output volume node
      if not basalIctalMaskVolumeNode:
        basalIctalMaskVolumeNode = slicer.vtkMRMLScalarVolumeNode()
        basalIctalMaskVolumeNode.SetName(basalIctalMaskVolumeName)
        slicer.mrmlScene.AddNode(basalIctalMaskVolumeNode)
        
      # setup the CLI module
      parameters = {}
      parameters["ra"] = ra
      parameters["rb"] = rb
      parameters["rc"] = rc
      
      
      parameters["ictalinputvolume"] = ictalVolumeNode.GetID();
      parameters["interictalinputvolume"] = basalVolumeNode.GetID();
      parameters["maskoutputvolume"] = basalIctalMaskVolumeNode.GetID();
      
      
      create_mask_module=slicer.modules.matlabbridge_acontrario_create_mask

      clinode=slicer.cli.run(create_mask_module, None, parameters, True) # El ultimo true es para que espere hasta la finalizacion
      
      if not clinode:
        print('CREATE_MASK failed')
        return False
      else:
        return True
      
      
         
  # ---------------------------------------------------------------------------
  def computeMRIBrainMask(self, mriVolumeName, brainMaskVolumeName):
    #TODO
    pass
  
  # ---------------------------------------------------------------------------
  def normalizeBasalIctal(self, basalVolumeName, ictalVolumeName):
    #TODO
    pass
  
  # --------------------------------------------------------------------------
  def applyMaskToVolume(self,inputVolumeNode,labelMaskNode,outputVolumeNode):
    "Trying to apply mask to volume..."  
    parameters = {} 
    parameters['InputVolume'] = inputVolumeNode.GetID() 
    parameters['MaskVolume'] = labelMaskNode.GetID() 
    parameters['Label'] = 1 
    parameters['Replace'] = 0 
    parameters['OutputVolume'] = outputVolumeNode.GetID() 
    clinode = slicer.cli.run( slicer.modules.maskscalarvolume, None, parameters, wait_for_completion=True )
    if not clinode:
      print('Mask scalar volume failed')
      return False
    else:
      print "Mask succesfully applied"  
      return True      
  
  # ---------------------------------------------------------------------------
  def subtractImages(self,ictalVolumeNode,basalVolumeNode, outputVolumeNode):
    parameters = {} 
    parameters['inputVolume1'] = ictalVolumeNode.GetID() 
    parameters['inputVolume2'] = basalVolumeNode.GetID() 
    parameters['outputVolume'] = outputVolumeNode.GetID() 
    clinode = slicer.cli.run( slicer.modules.subtractscalarvolumes, None, parameters, wait_for_completion=True )
    if not clinode:
      print('Differential detection failed')
      return False
    else:
      return True

  # ---------------------------------------------------------------------------
  def detectFociAContrario(self,basalVolumeNode,ictalVolumeNode, diffOutputVolumeNode, nfaOutputVolumeNode):
    # setup the CLI module
    parameters = {}    
    # INPUT
    parameters["ictalinputvolume"] = ictalVolumeNode.GetID();
    parameters["interictalinputvolume"] = basalVolumeNode.GetID();
    # OUTPUT
    parameters["diffoutputvolume"] = diffOutputVolumeNode.GetID();
    parameters["nfaoutputvolume"] = nfaOutputVolumeNode.GetID();
    
    acontrario_detection_module = slicer.modules.matlabbridge_acontrario_detection

    clinode=slicer.cli.run(acontrario_detection_module, None, parameters, True) # El ultimo true es para que espere hasta la finalizacion
      
    if not clinode:
      print('A contrario detection failed')
      return False
    else:
      return True
    pass

  # ---------------------------------------------------------------------------
  def customCompareLayout(self, rows, cols, customLayoutNumber):
    # Grid compare viewers
    compareViewGrid = "<layout type=\"vertical\" split=\"true\" >" +"\n" \
    #  " <item>" +"\n" \
    #  "  <layout type=\"horizontal\">" +"\n" \
    #  "   <item>" +"\n" \
    #  "    <view class=\"vtkMRMLSliceNode\" singletontag=\"Red\">" +"\n" \
    #  "     <property name=\"orientation\" action=\"default\">Axial</property>" +"\n" \
    #  "     <property name=\"viewlabel\" action=\"default\">R</property>" +"\n" \
    #  "     <property name=\"viewcolor\" action=\"default\">#F34A33</property>" +"\n" \
    #  "    </view>" +"\n" \
    #  "   </item>" +"\n" \
    #  "   <item>" +"\n" \
    #  "    <view class=\"vtkMRMLViewNode\" singletontag=\"1\"/>" +"\n" \
    #  "   </item>" +"\n" \
    #  "  </layout>" +"\n" \
    #  " </item>" +"\n" \
    " <item>" +"\n" \
    "  <layout type=\"vertical\">"
    
    k=1
    for i in range(1,rows+1):
      compareViewGrid += "\n" \
      "   <item>" +"\n" \
      "    <layout type=\"horizontal\">"
      for j in range(1,cols+1):
        compareViewGrid += "\n" \
        "     <item>" +"\n" \
        "      <view class=\"vtkMRMLSliceNode\" singletontag=\"Compare" + str(k) + "\">" +"\n" \
        "       <property name=\"orientation\" action=\"default\">Axial</property>" +"\n" \
        "       <property name=\"viewlabel\" action=\"default\">" + str(k) +"</property>" +"\n" \
        "       <property name=\"viewcolor\" action=\"default\">#E17012</property>" +"\n" \
        "       <property name=\"lightboxrows\" action=\"default\">1</property>" +"\n" \
        "       <property name=\"lightboxcolumns\" action=\"default\">1</property>" +"\n" \
        "       <property name=\"lightboxrows\" action=\"relayout\">1</property>" +"\n" \
        "       <property name=\"lightboxcolumns\" action=\"relayout\">1</property>" +"\n" \
        "      </view>" +"\n" \
        "     </item>"
        k+=1
      compareViewGrid += "\n" \
      "     </layout>" +"\n" \
      "    </item>"
    
    compareViewGrid += "\n" \
    "  </layout>" +"\n" \
    " </item>" +"\n" \
    "</layout>"
    
    #print compareViewGrid
    #Add to the layout node
    layoutNode=self.getLayoutNode() #self.getLayoutManager().layoutLogic().GetLayoutNode()   #slicer.util.getNode("Layout")
    if layoutNode.IsLayoutDescription(customLayoutNumber):
      layoutNode.SetLayoutDescription(customLayoutNumber, compareViewGrid)
    else:
      layoutNode.AddLayoutDescription(customLayoutNumber, compareViewGrid)


  # ---------------------------------------------------------------------------
  # Utility functions
  # ---------------------------------------------------------------------------
  def delayDisplay(self,message,msec=1000):
    """This utility method displays a small dialog and waits.
    This does two things: 1) it lets the event loop catch up
    to the state of the test so that rendering and widget updates
    have all taken place before the test continues and 2) it
    shows the user/developer/tester the state of the test
    so that we'll know when it breaks.
    """
    print(message)
    self.info = qt.QDialog()
    self.infoLayout = qt.QVBoxLayout()
    self.info.setLayout(self.infoLayout)
    self.label = qt.QLabel(message,self.info)
    self.infoLayout.addWidget(self.label)
    qt.QTimer.singleShot(msec, self.info.close)
    self.info.exec_()
    

  def createFociVisualizationColorMap(self,minimumValue,maximumValue):
    if (minimumValue<0):  
      numberOfCoolColors = -(minimumValue)
    else:
      numberOfCoolColors = 0
    if (maximumValue>0):  
      numberOfHotColors =  maximumValue+1 # includes zero
    else:
      numberOfHotColors = 0  
      
    print "number of cool colors = " + str(numberOfCoolColors)  
    print "number of hot colors (including zero) = " + str(numberOfHotColors)
    
    colorNode = slicer.util.getNode(self.FOCI_DETECTION_COLORMAP_NAME)
    if colorNode is None:
      colorNode = slicer.vtkMRMLColorTableNode() 
      slicer.mrmlScene.AddNode(colorNode)
      colorNode.SetName(self.FOCI_DETECTION_COLORMAP_NAME)
      
    colorNode.SetTypeToUser()   
    colorNode.SetNumberOfColors(numberOfCoolColors + numberOfHotColors);
    #colorNode.SetColor(0, "zero", 0.0, 0.0, 0.0, 1.0);
    #colorNode.SetColor(1, "one", 1.0, 0.0, 0.0, 1.0);
    #colorNode.SetColor(2, "two", 0.0, 1.0, 0.0, 1.0);
    colorNode.SetNamesFromColors()
    
    
    ''' cool color map in Matlab     
    r = (0:m-1)'/max(m-1,1);
    c = [r 1-r ones(m,1)]; 
    '''
    for colorIndex in xrange(0,numberOfCoolColors):
      r = np.double(numberOfCoolColors -1 - colorIndex) / (numberOfCoolColors)  
      colorNode.SetColor(colorIndex, r, 1-r, 1, 1.0);  
      print "cool color index = " + str(colorIndex)
    '''   hot color table in Matlab
     r = [(1:n)'/n; ones(m-n,1)];
     g = [zeros(n,1); (1:n)'/n; ones(m-2*n,1)];
     b = [zeros(2*n,1); (1:m-2*n)'/(m-2*n)]; 
    '''  
    n=3*numberOfHotColors/8  # fix
    for colorIndex in xrange(0,numberOfHotColors+1):
      if colorIndex < n:
        r=np.double(colorIndex)/n    
        g=0.0   
        b=0.0
      elif colorIndex < 2*n :
        r=1.0  
        g=np.double((colorIndex-n+1))/n 
        b=0.0
      else: 
        r=1.0    
        g=1.0
        b=np.double((colorIndex-2*n+1))/(numberOfHotColors-2*n)
      colorNode.SetColor(numberOfCoolColors + colorIndex, r, g, b, 1.0); 
      print "hot color index = " + str(numberOfCoolColors + colorIndex)

     
             
  def showDifferencesBiggerThanStdThreshold(self, minimumValue, maximumValue, negativeValuesToHide, positiveValuesToHide):
    if (minimumValue<0):  
      numberOfCoolColors = -(minimumValue)
    else:
      numberOfCoolColors = 0
    if (maximumValue>0):  
      numberOfHotColors =  maximumValue+1 # includes zero
    else:
      numberOfHotColors = 0  
      
    colorNode = slicer.util.getNode(self.FOCI_DETECTION_COLORMAP_NAME)
    
    
    ''' cool color map in Matlab     
    r = (0:m-1)'/max(m-1,1);
    c = [r 1-r ones(m,1)]; 
    '''
    for colorIndex in xrange(0,numberOfCoolColors - negativeValuesToHide):
      colorNode.SetOpacity(colorIndex,1);  
    for colorIndex in xrange(numberOfCoolColors - negativeValuesToHide,numberOfCoolColors):
      colorNode.SetOpacity(colorIndex,0);    
 
    for colorIndex in xrange(0,positiveValuesToHide+1):
      colorNode.SetOpacity(numberOfCoolColors + colorIndex,0);  
    for colorIndex in xrange(positiveValuesToHide+1,numberOfHotColors+1 ):  
      colorNode.SetOpacity(numberOfCoolColors + colorIndex,1);  
    