#@PydevCodeAnalysisIgnore
import numpy as np
import vtk, qt, ctk, slicer
import SimpleITK as sitk
import sitkUtils




class PruebasNumpy:
    def __init__(self):
      pass
    
    def pruebas(self):
      #Pruebas numpy
      
      
      X=np.array([[1, 2], [3, 0]])
      Y=np.array([[1, 0], [0, 1]])
      
      #media de todos
      X.mean()
      
      # indices de los elementos positivos
      nonZeroIndices=X.nonzero()
      
      # media de los positivos
      X[nonZeroIndices].mean()
      # lo mismo
      X[X>0].mean()
      
      # element-wise logical op
      (X>0) & (Y>0)
      
      # create an array with the shape of X
      size=X.shape
      M=np.zeros(size,np.uint8)

class AContrarioDetection:
    def __init__(self):
        self.BASAL_VOLUME_NAME = 'P1_B'
        self.ICTAL_VOLUME_NAME = 'P1_Ic'
        self.MRI_VOLUME_NAME = 'P1_MRI_T2'
        self.MASK_VOLUME_NAME = 'Mask'
        
        # Get the numpy arrays
        self.inter = slicer.util.array(self.BASAL_VOLUME_NAME)
        self.ic = slicer.util.array(self.ICTAL_VOLUME_NAME)
        self.mask = slicer.util.array(self.BASAL_VOLUME_NAME)
        self.ra = 3; self.rb = 2; self.rc = 1;
        
        self.interNormalized = self.inter
        self.icNormalized = self.ic
        self.Substraction = self.inter
        
        
        self.customLayoutGridView3x3 = 23
        
        pass
    
        
    def runTestErosion(self):
        pulso=np.zeros((100,100,100))
        pulso[30:70,30:70,30:70]=1
        #pulso[40:60,40:60,40:60]=0
        
        elipseKernel = self.elipse3D(7,5,3)
        
        self.pushArrayToSlicer(pulso,'runTestErosion_Cuadrado',overWrite=True)
        
        eroded = self.erosion(pulso, elipseKernel)
        
        self.pushArrayToSlicer(eroded,'runTestErosion_cuadrado_erosionado',overWrite=True)
        
        
        
        
    def runTestConvolution(self):
        pulso=np.zeros((100,100,100))
        pulso[30:70,30:70,30:70]=1
        sitkPulso = sitk.GetImageFromArray(pulso)
        sitkUtils.PushBackground(sitkPulso, 'Pulso',overwrite = True)
        
        elipseKernel = self.elipse3D(15,10,5)
        sitkElipseKernel = sitk.GetImageFromArray(elipseKernel)
        
        #convolucion espacial, muy lento 
        #Image itk::simple::Convolution   (   const Image &    image1,
        #  const Image &    image2,
        #  bool    normalize = false,
        #  ConvolutionImageFilter::BoundaryConditionType    boundaryCondition = itk::simple::ConvolutionImageFilter::ZERO_FLUX_NEUMANN_PAD,
        #  ConvolutionImageFilter::OutputRegionModeType    outputRegionMode = itk::simple::ConvolutionImageFilter::SAME 
        #)     
               
        # sitkPulsoConvElipse=sitk.Convolution(sitkPulso,sitkElipseKernel)
        # sitkUtils.PushBackground(sitkPulsoConvElipse, 'PulsoConvElipse',overwrite = True)
        
        # Convolucion en fourier
        
        #Image itk::simple::FFTConvolution   (   const Image &    image1,
        #    const Image &    image2,
        #    bool    normalize = false,
        #    FFTConvolutionImageFilter::BoundaryConditionType    boundaryCondition = itk::simple::FFTConvolutionImageFilter::ZERO_FLUX_NEUMANN_PAD,
        #    FFTConvolutionImageFilter::OutputRegionModeType    outputRegionMode = itk::simple::FFTConvolutionImageFilter::SAME 
        #  )           
        sitkPulsoConvElipse=sitk.FFTConvolution(sitkPulso,sitkElipseKernel)
        sitkUtils.PushBackground(sitkPulsoConvElipse, 'PulsoConElipse',overwrite = True)
        
        pulsoConvElipse=self.convolutionWithFFT(pulso, elipseKernel)
        self.pushArrayToSlicer(pulsoConvElipse)
        
        
    def runTestKernels(self):
        
        elipse=self.elipse3D(30,20,10)
        sitkElipse = sitk.GetImageFromArray(elipse)
        sitkUtils.PushBackground(sitkElipse, 'Elipse',overwrite = True)
        
        #PARA VER: El kernel gaussiano tiene siempre sigma=1
        
        g=self.gaussKernel(3,2,1)
        sitkGauss = sitk.GetImageFromArray(g)
        sitkUtils.PushBackground(sitkGauss, 'Gauss kernel',overwrite = True)
        
        
        pass
              
    def runTestAContrario(self):
        
        #ic=self.ic[0:64,0:64,0:64].copy()
        #inter=self.inter[0:64,0:64,0:64].copy()
        self.acontrario_detection(ic, inter, debug=True)
        
        sitkIcNormalized = sitk.GetImageFromArray(self.icNormalized)
        sitkUtils.PushBackground(sitkIcNormalized, 'P1_Ic_normalized',overwrite = True)
        
        sitkSubtstraction = sitk.GetImageFromArray(self.Substraction)
        sitkUtils.PushBackground(sitkSubtstraction, 'Normalized_substraction',overwrite = True)
        
        #self.create_mask(self.ic, self.inter, self.ra, self.rb, self.rc, debug=True)
        #slicer.app.layoutManager().setLayout(self.customLayoutGridView3x3)
        #self.compareMasks()
        
        pass
        
    def runTestAContrarioGlobal(self):
        pulso=np.zeros((100,100,100))
        pulso[30:70,30:70,30:70]=1
        
        dif=pulso
        mask_in=pulso
        T_eff=pulso
        ra1=3; rb1=3; rc1=2
        self.acontrario_global(dif,mask_in,T_eff,ra1,rb1,rc1)
        
    def runTestCreateMask(self):
        
        self.create_mask(self.ic, self.inter, self.ra, self.rb, self.rc, debug=True)
        slicer.app.layoutManager().setLayout(self.customLayoutGridView3x3)
        self.compareMasks()
        
        pass
        
        #-----------------------------------------------------    
    #def convolution (self, array1, array2, normalize=False, boundaryCondition = 1, outputRegionMode = 0 ):
    def convolution (self, array1, array2, normalize=False, boundaryCondition = sitk.ConvolutionImageFilter.ZERO_FLUX_NEUMANN_PAD, outputRegionMode = sitk.ConvolutionImageFilter.SAME ):
        sitkArray1 = sitk.GetImageFromArray(array1)
        sitkArray2 = sitk.GetImageFromArray(array2)
        sitkConvolution = sitk.Convolution(sitkArray1,sitkArray2,normalize,boundaryCondition,outputRegionMode)
        resultArray = sitk.GetArrayFromImage(sitkConvolution)        
        return resultArray
      
    def convolutionWithFFT (self, array1, array2, normalize=False, boundaryCondition = sitk.ConvolutionImageFilter.ZERO_FLUX_NEUMANN_PAD, outputRegionMode = sitk.ConvolutionImageFilter.SAME ):
        sitkArray1 = sitk.GetImageFromArray(array1)
        sitkArray2 = sitk.GetImageFromArray(array2)
        sitkConvolution = sitk.FFTConvolution(sitkArray1,sitkArray2,normalize,boundaryCondition,outputRegionMode)
        resultArray = sitk.GetArrayFromImage(sitkConvolution)        
        return resultArray
        
        
    def erosion(self,array, strel):        
        print array.shape, array.dtype
        print strel.shape, strel.dtype
        
        arrayConvStrel = self.convolutionWithFFT(array, strel);
        eroded = np.zeros(arrayConvStrel.shape, np.uint8)
        eroded[np.abs(arrayConvStrel-strel.sum())<0.001]=1  
        return eroded
        
#    def erosion(self,array1, ): 
#        #Image   BinaryDilate (const Image &, const std::vector< uint32_t > vectorRadius, KernelEnum kernel=sitkBall, double backgroundValue=0.0, double foregroundValue=1.0, bool boundaryToForeground=false)  
#        sitkArray1 = sitk.GetImageFromArray(array1)
#        sitkArray2 = sitk.GetImageFromArray(array2)
#        sitkEroded = sitk.BinaryErode(sitkArray1,sitkArray2,normalize,boundaryCondition,outputRegionMode)
#        resultArray = sitk.GetArrayFromImage(sitkConvolution)        
#        return resultArray
#         
    def pushArrayToSlicer(self, array, nodeName='ArrayPushedFromCode', compositeView=0, overWrite=False):
        sitkImage = sitk.GetImageFromArray(array)
        sitkUtils.PushToSlicer(sitkImage, nodeName, compositeView, overWrite)
        
    def ksdensity(self,a):
        nbins=100;
        range=None; normed=False; weights=None; density=True
        [hist, bin_edges] = np.histogram(a, nbins, range, normed, weights,density)
        
        # histogram returns bin_edges (nbins+1 values), we need bin centers (nbins values)
        bin_centers=(bin_edges[0:-1]+bin_edges[1:])/2.0 
        
        return hist, bin_centers
    
    def acontrario_det_scale(self,esc,scales_in,scales_out,ldif,dif,mask,grid_step):
                
        # Scale of the inner kernel.
        ra1 = scales_in[esc,0];
        rb1 = scales_in[esc,1];
        rc1 = scales_in[esc,2];
        # Scale of the outer patch.
        ra2 = scales_out[esc,0];
        rb2 = scales_out[esc,1];
        rc2 = scales_out[esc,2];
        
        # Local test
        print 'Performing local test...'
        [ pfaL_Pos, T_eff, Ntest ] = self.acontrario_local(ldif,mask,ra1,rb1,rc1,ra2,rb2,rc2,grid_step);
        
        # Global test
        print 'Performing global test...'
        pfaG_Pos = self.acontrario_global(dif,mask,T_eff,ra1,rb1,rc1);
        
        # Combined measurement
        pfaPos = pfaG_Pos + pfaL_Pos;
        
        # Compute relative number of false alarms (explained in article:
        # "A-contrario detectability of spots in textured backgrounds",
        # B. Grosjean and L. Moisan.
        Ntest_exp = Ntest/(np.ceil(grid_step*ra1)+1)**2;
        
        # Compute NFA from PFA and Ntest_exp.
        nfaPos = pfaPos + np.log(Ntest_exp);
        
        return nfaPos
      
            
    def acontrario_local(self,dif,mask,ra1,rb1,rc1,ra2,rb2,rc2,grid_step):
        #function [ pfaPos, T_eff, Ntest ] = acontrario_local(dif,mask,ra1,rb1,rc1,ra2,rb2,rc2,grid_step)
        #
        #%==========================================================================
        #%                           Variable definition
        #%==========================================================================
        #Ntest = 0;
        #pfaPos = ones(size(dif))*100;
        #[n,p,q] = size(dif);
        #
        #% Measurement kernel.
        #kernel = elipse3D(ra1,rb1,rc1);
        #kernel = kernel/sum(kernel(:));
        #
        #rKernelNoise1 = 2;
        #rKernelNoise2 = 2;
        #rKernelNoise3 = 1;
        #
        #sizeMask = (2*ra2+1) * (2*rb2+1) * (2*rc2+1);
        #sizeKernel = (2*ra1+1) * (2*rb1+1) * (2*rc1+1);
        #
        #%==========================================================================
        #%                           Main Function
        #%==========================================================================
        #
        #% Define the testing grid T.
        #stepA = ceil(grid_step*ra1)+1;
        #stepB = ceil(grid_step*rb1)+1;
        #stepC = ceil(grid_step*rc1);
        #T = zeros(n,p,q);
        #T(1:stepA:n,1:stepB:p,1:stepC:q) = 1;
        #T(mask<=0) = 0;
        #T_eff = T;
        #
        #% Gaussian smooth applied to the sustraction image in order to diminish the 
        #% effect of the foci in the computation of the Gaussian density parameters. 
        #% The sustraction image includes the foci, thus we must smooth it before
        #% computing the parameters. 
        #gaussKernel = gaussianKernel(rKernelNoise1,rKernelNoise2,rKernelNoise3);
        #
        #% For each pixel, if it is a valid test pixel: 
        #% 1) T(i,j,k) = 1  and 2) the kernel of radii (ra1,rb1,rc1) centered at the
        #%                         pixel is completely inside the mask.
        #for i=1:n
        #    disp(['Processing pixel i = ' num2str(i)])
        #    for j=1:p
        #        for k=1:q
        #            
        #            if ( T(i,j,k) == 1 && elipse_in_mask(i,j,k,ra1,rb1,rc1,mask) ) % if it is a valid test pixel.
        #                
        #                if in_mask(i,j,k,ra2,rb2,rc2,mask)  % If the exterior neighborhood is inside the mask.
        #                    
        #                    patch = dif(i-ra2:i+ra2,j-rb2:j+rb2,k-rc2:k+rc2);
        #                    
        #                    patchS = imfilter(patch,gaussKernel,'symmetric','same','conv');
        #                    patchMS = imfilter(patchS,kernel,'symmetric','same','conv');
        #                    norm_phi = std(patchMS(:));
        #                    mediaPatch = mean(patchMS(:));
        #                    
        #                    kernel_padded = padarray(kernel,[(ra2-ra1) (rb2-rb1) (rc2-rc1)],'both');
        #                    measure1 = mean(patch( kernel_padded > 0 ));
        #                    
        #                    pfaPos(i,j,k) = log(0.5*erfc((measure1-mediaPatch)/norm_phi/sqrt(2)));                   
        #                    
        #                    Ntest = Ntest + 1;
        #                    
        #                else  % If the exterior neighborhood is not completely included in the mask.
        #                    
        #                    patch_incomplet = dif(i-ra2:i+ra2,j-rb2:j+rb2,k-rc2:k+rc2);
        #                    patch_mask = mask(i-ra2:i+ra2,j-rb2:j+rb2,k-rc2:k+rc2);
        #                    total_full = sum(patch_mask(:));     % Total number of pixels with an assigned value.
        #                    total_empty = sizeMask - total_full; % Total number of pixels assigned zero.
        #                    
        #                    if total_full >= 1.5*sizeKernel  % Verify that the patch has assigned values (non zero) 
        #                                                     % in at least 1.5 times the kernel's pixels.
        #                        % If not, it makes no sense to compute the
        #                        % parameters in that neighborhood.
        #                        % That condition ensures: total_empty < total_full.
        #                        
        #                        % Randomly choose total_empty values from the
        #                        % total_full to fill in the null part of the patch.
        #                        candidates = patch_incomplet(patch_mask == 1);
        #                        index_sort = randsample(total_full,total_empty);
        #                        sorteados = candidates(index_sort);
        #                        
        #                        % Assign to the null part of the incomplete patch
        #                        % the drawn values. That way generate a full patch
        #                        % to compute the parameteres.
        #                        patch = patch_incomplet;
        #                        patch(patch_mask == 0) = sorteados;
        #                        
        #                        patchS = imfilter(patch,gaussKernel,'symmetric','same','conv');
        #                        patchMS = imfilter(patchS,kernel,'symmetric','same','conv');
        #                        norm_phi = std(patchMS(:));
        #                        mediaPatch = mean(patchMS(:));
        #                        
        #                        kernel_padded = padarray(kernel,[(ra2-ra1) (rb2-rb1) (rc2-rc1)],'both');
        #                        measure1 = mean(patch( kernel_padded > 0 ));
        #                        
        #                        pfaPos(i,j,k) = log(0.5*erfc((measure1-mediaPatch)/norm_phi/sqrt(2)));                       
        #                        
        #                        Ntest = Ntest + 1;
        #                        
        #                    else
        #                        
        #                        T_eff(i,j,k) = 0;
        #                        
        #                    end                        
        #                                        
        #                end
        #                
        #            else
        #                
        #                T_eff(i,j,k) = 0;
        #                
        #            end
        #            
        #        end
        #    end
        #end
        #end
        #%==========================================================================
        #%                           Auxiliar functions
        #%==========================================================================
        #
        #%--------------------------------------------------------------------------
        #% Test whether the kernel centered at pixel (i,j,k) is inside the mask.
        #%--------------------------------------------------------------------------
        #function bool = elipse_in_mask(i,j,k,ra,rb,rc,mask)
        #        
        #    patch = mask(i-ra:i+ra,j-rb:j+rb,k-rc:k+rc);
        #    kernel = elipse3D(ra,rb,rc);
        #        
        #    aux = patch.*kernel;
        #        
        #    bool = (sum(aux(:)) == sum(kernel(:)));
        #        
        #end
        #
        #%--------------------------------------------------------------------------
        #% Tests whether the a patch centered in pixel (i,j,k) is inside the mask.
        #%--------------------------------------------------------------------------
        #function bool = in_mask(i,j,k,ra,rb,rc,mask)
        #
        #    patch = mask(i-ra:i+ra,j-rb:j+rb,k-rc:k+rc);
        #    [a,b,c] = size(patch);
        #    bool = (sum(patch(:)) == a*b*c);
        #
        #end      

        #==========================================================================
        #                           Variable definition
        #==========================================================================
        Ntest = 0;
        pfaPos = np.ones(dif.shape)*100;
        [n,p,q] = dif.shape;
        
        # Measurement kernel.
        kernel = self.elipse3D(ra1,rb1,rc1);
        kernel = kernel/kernel.sum();
        
        
        # kernel_padded = padarray(kernel,[(ra2-ra1) (rb2-rb1) (rc2-rc1)],'both');
        kernel_padded = np.zeros((2*ra2+1,2*rb2+1,2*rc2+1))
        kernel_padded[ra2-ra1:ra2+ra1+1,rb2-rb1:rb2+rb1+1,rc2-rc1:rc2+rc1+1]=kernel
        
        rKernelNoise1 = 2;
        rKernelNoise2 = 2;
        rKernelNoise3 = 1;
        
        sizeMask = (2*ra2+1) * (2*rb2+1) * (2*rc2+1);
        sizeKernel = (2*ra1+1) * (2*rb1+1) * (2*rc1+1);
        
        #==========================================================================
        #                           Main Function
        #==========================================================================
        
        # Define the testing grid T.
        stepA = np.ceil(grid_step*ra1)+1;
        stepB = np.ceil(grid_step*rb1)+1;
        stepC = np.ceil(grid_step*rc1);
        T = np.zeros((n,p,q));
        T[0::stepA,0::stepB,0::stepC] = 1;
        T[mask<=0] = 0;
        T_eff = T;
        
        # Gaussian smooth applied to the sustraction image in order to diminish the 
        # effect of the foci in the computation of the Gaussian density parameters. 
        # The sustraction image includes the foci, thus we must smooth it before
        # computing the parameters. 
        gaussKernel = self.gaussKernel(rKernelNoise1,rKernelNoise2,rKernelNoise3);
        
        
        #AG nuevo  
        print mask.shape
        precomputedElipseInMask = self.precompute_elipse_in_mask_AG(ra1, rb1, rc1, mask)
        precomputedPatchInMask = self.precompute_patch_in_mask_AG(ra2, rb2, rc2, mask)
        
        
        
        
        # For each pixel, if it is a valid test pixel: 
        # 1) T(i,j,k) = 1  and 2) the kernel of radii (ra1,rb1,rc1) centered at the
        #                         pixel is completely inside the mask.
        II,JJ,KK = T.nonzero()
        NN=II.size
        for n in range(0,NN):
            i=II[n]; j=JJ[n]; k=KK[n];
            if np.mod(n,3000)==0 :
                print 'Processing: ', n , 'of', NN
#        for i in range(0,n):
#            print 'Processing: ', i , 'of', n 
#            for j in range(0,p):
#                for k in range(0,q):
#                    
#                    if ( T[i,j,k] == 1 and self.elipse_in_mask(i,j,k,ra1,rb1,rc1,mask) ): # if it is a valid test pixel.
            #if ( self.elipse_in_mask(i,j,k,ra1,rb1,rc1,mask) ): # if it is a valid test pixel.
            if precomputedElipseInMask[i,j,k]>0 :
                #if self.in_mask(i,j,k,ra2,rb2,rc2,mask):  # If the exterior neighborhood is inside the mask.
                if precomputedPatchInMask[i,j,k]>0 :   
                    patch = dif[i-ra2:i+ra2+1,j-rb2:j+rb2+1,k-rc2:k+rc2+1];
                    
                    patchS = self.convolution(patch, gaussKernel) 
                    patchMS = self.convolution(patchS, kernel) 
                    norm_phi = patchMS.std();
                    mediaPatch = patchMS.mean();
                    
                    ## kernel_padded = padarray(kernel,[(ra2-ra1) (rb2-rb1) (rc2-rc1)],'both');
                    #kernel_padded = np.zeros((2*ra2+1,2*rb2+1,2*rc2+1))
                    #kernel_padded[ra2-ra1:ra2+ra1+1,rb2-rb1:rb2+rb1+1,rc2-rc1:rc2+rc1+1]=kernel
                    
                    
                    measure1 = patch[ kernel_padded > 0 ].mean();
                    
                    pfaPos[i,j,k] = np.log(0.5*np.math.erfc((measure1-mediaPatch)/norm_phi/np.sqrt(2)));                   
                    
                    Ntest = Ntest + 1;
                    
                else : # If the exterior neighborhood is not completely included in the mask.
                    
                    patch_incomplet = dif[i-ra2:i+ra2+1,j-rb2:j+rb2+1,k-rc2:k+rc2+1];
                    patch_mask = mask[i-ra2:i+ra2+1,j-rb2:j+rb2+1,k-rc2:k+rc2+1];
                    total_full = patch_mask.sum();     # Total number of pixels with an assigned value.
                    total_empty = sizeMask - total_full; # Total number of pixels assigned zero.
                    
                    if total_full >= 1.5*sizeKernel :  # Verify that the patch has assigned values (non zero) 
                                                     # in at least 1.5 times the kernel's pixels.
                        # If not, it makes no sense to compute the
                        # parameters in that neighborhood.
                        # That condition ensures: total_empty < total_full.
                        
                        # Randomly choose total_empty values from the
                        # total_full to fill in the null part of the patch.
                        candidates = patch_incomplet[patch_mask == 1];
                        index_sort = np.random.random_integers(0,total_full-1,total_empty) #index_sort = randsample(total_full,total_empty);
                        sorteados = candidates[index_sort];
                        
                        # Assign to the null part of the incomplete patch
                        # the drawn values. That way generate a full patch
                        # to compute the parameteres.
                        patch = patch_incomplet;
                        patch[patch_mask == 0] = sorteados;
                        
                        patchS = self.convolution(patch, gaussKernel)  #patchS = imfilter(patch,gaussKernel,'symmetric','same','conv');
                        patchMS = self.convolution(patchS, kernel) #patchMS = imfilter(patchS,kernel,'symmetric','same','conv');
                        norm_phi = patchMS.std();
                        mediaPatch = patchMS.mean();
                        
                        ##kernel_padded = padarray(kernel,[(ra2-ra1) (rb2-rb1) (rc2-rc1)],'both');
                        #kernel_padded = np.zeros((2*ra2+1,2*rb2+1,2*rc2+1))
                        #kernel_padded[ra2-ra1:ra2+ra1+1,rb2-rb1:rb2+rb1+1,rc2-rc1:rc2+rc1+1]=kernel
                                                        
                        measure1 = patch[ kernel_padded > 0 ].mean();
                        
                        pfaPos[i,j,k] = np.log(0.5*np.math.erfc((measure1-mediaPatch)/norm_phi/np.sqrt(2)));                       
                        
                        Ntest = Ntest + 1;
                      
                    else:
                        T_eff[i,j,k] = 0;
                        
            else :
                T_eff[i,j,k] = 0;
                  
        return  pfaPos, T_eff, Ntest 
                        
        
        
    #==========================================================================
    #                           Auxiliar functions
    #==========================================================================
    
    #--------------------------------------------------------------------------
    # Test whether the kernel centered at pixel (i,j,k) is inside the mask.
    #--------------------------------------------------------------------------
    def elipse_in_mask(self,i,j,k,ra,rb,rc,mask):    
        patch = mask[i-ra:i+ra+1,j-rb:j+rb+1,k-rc:k+rc+1];
        kernel = self.elipse3D(ra,rb,rc);
        aux = patch*kernel;
        bool = (aux.sum() == kernel.sum());
        return bool
        
    #--------------------------------------------------------------------------
    # Tests whether the a patch centered in pixel (i,j,k) is inside the mask.
    #--------------------------------------------------------------------------
    def in_mask(self,i,j,k,ra,rb,rc,mask):
        patch = mask[i-ra:i+ra+1,j-rb:j+rb+1,k-rc:k+rc+1];
        [a,b,c] = patch.shape;
        bool = (patch.sum() == a*b*c);
        return bool
    
    def precompute_elipse_in_mask_AG(self,ra,rb,rc,mask):
        elipseKernel = self.elipse3D(ra,rb,rc);
        precomputed_elipse_in_mask = self.erosion(np.double(mask), np.double(elipseKernel))
        return precomputed_elipse_in_mask
   
    def precompute_patch_in_mask_AG(self,ra,rb,rc,mask):
        patchKernel = np.ones((2*ra+1,2*rb+1,2*rc+1))
        precomputed_patch_in_mask = self.erosion(np.double(mask), np.double(patchKernel))
        return precomputed_patch_in_mask
    
    
    
    
    def acontrario_global(self,dif,mask_in,T_eff,ra1,rb1,rc1):
        #function pfaPos = acontrario_global(dif,mask_in,T_eff,ra1,rb1,rc1)
        #
        #%==========================================================================
        #%                           Variable definition
        #%==========================================================================
        #[n,p,q] = size(dif);
        #rKernelNoise1 = 3;
        #rKernelNoise2 = 3;
        #rKernelNoise3 = 1;
        #epsilon_machine = 1e-323;
        #
        #%==========================================================================
        #%                           Main Function
        #%==========================================================================
        #
        #% Adapt the mask in order to remove the border that in the convolution will
        #% be computed including zeros. That mask will be used to compute the
        #% empirical density, so that not to include this values computed including
        #% zeros in the convolution.
        #kernel_aux = elipse3D(ra1,rb1,rc1);
        #mask_aux = imfilter(mask_in,kernel_aux,'same','conv');
        #mask = mask_aux == sum(kernel_aux(:));
        #
        #% Gaussian smooth applied to the sustraction image in order to diminish the 
        #% effect of the foci in the computation of the empirical histogram. 
        #% The sustraction image includes the foci, thus we must smooth it before
        #% computing the empirical histogram. Otherwise, the empirical histogram
        #% includes foci values as "normal" values.
        #gaussKernel = gaussianKernel(rKernelNoise1,rKernelNoise2,rKernelNoise3);
        #% difS = convn_home(dif,gaussKernel,'same');
        #difS = imfilter(dif,gaussKernel,'symmetric','same','conv');
        #
        #% Compute the measurement image with the smoothed sustraction image.
        #kernel1 = elipse3D(ra1,rb1,rc1);
        #kernel1 = kernel1/sum(kernel1(:));
        #% difM_suav = convn_home(difS,kernel1,'same');
        #difM_suav = imfilter(difS,kernel1,'symmetric','same','conv');
        #
        #% Since the pixels are correlated, I must subsample the measurement image 
        #% in order to compute the empirical histogram. TsubSample is the grid of
        #% pixels that will be used to compute the empirical histgram.
        #sSub1 = max(ra1,rKernelNoise1);
        #sSub2 = max(rb1,rKernelNoise2);
        #sSub3 = max(rc1,rKernelNoise3);
        #
        #TsubSample = zeros(n,p,q);
        #TsubSample(1:sSub1:n,1:sSub2:p,1:sSub3:q) = 1;
        #TsubSample(mask<=0) = 0;
        #
        #% Compute the empirical density with the measurement image difM_suav in the
        #% pixels defined by the grid TsubSample. Work with the logarithm of the
        #% density for precision reasons.
        #difM_subSampled = difM_suav(TsubSample>0);
        #log_density = log((ksdensity(difM_subSampled(:)) + epsilon_machine));
        #
        #% The following step is done only to obtain the bins were the density was
        #% computed. They cannot be obtained in the previous step because we want
        #% to obtain directly the log(density).
        #[aux,bins] = ksdensity(difM_subSampled(:)); % Esto lo hago solo para obtenere los bins para poder tener directo el log del resultado en el paso anterior.
        #pasoBin = abs(bins(2) - bins(1));
        #
        #log_density = log_density + log(pasoBin);
        #
        #% Compute the real measurement image (without smoothness)
        #% difM = convn_home(dif,kernel1,'same');
        #difM = imfilter(dif,kernel1,'symmetric','same','conv');
        #
        #% Initialize pfa variable
        #pfaPos = ones(size(dif));
        #
        #% For each pixel in the image, if it is in the test grid (T_eff), compute
        #% the pfa.
        #for j=1:n
        #    for k=1:p
        #        for l=1:q
        #            if T_eff(j,k,l)==1  % Here I do not test that the kernel is inside the mask
        #                                % because I only test pixels in the grid
        #                                % T_eff, that is the result of the local
        #                                % testing where that condition was already
        #                                % tested.                               
        #                                
        #                if sum(bins >= difM(j,k,l)) > 0
        #                    pfaPos(j,k,l) = log(sum(exp(log_density(bins >= difM(j,k,l)) - max(log_density(bins >= difM(j,k,l)))))) + max(log_density(bins >= difM(j,k,l)));                    
        #                else
        #                    pfaPos(j,k,l) = -1e308; % Minimum value not -Inf
        #                end
        #                
        #
        #            end
        #        end
        #    end
        #end          



        #==========================================================================
        #                           Variable definition
        #==========================================================================
        [n,p,q] = dif.shape;
        rKernelNoise1 = 3;
        rKernelNoise2 = 3;
        rKernelNoise3 = 1;
        epsilon_machine = 1e-323;
        
        #==========================================================================
        #                           Main Function
        #==========================================================================
        
        # Adapt the mask in order to remove the border that in the convolution will
        # be computed including zeros. That mask will be used to compute the
        # empirical density, so that not to include this values computed including
        # zeros in the convolution.
               
        kernel_aux = self.elipse3D(ra1,rb1,rc1)
        mask_aux = self.convolutionWithFFT(np.double(mask_in), np.double(kernel_aux));
        mask = np.zeros(mask_aux.shape)
        mask[np.abs(mask_aux-kernel_aux.sum())<0.001]=1  #Esto parece ser una erosion mas que un filtrado
        
        self.pushArrayToSlicer(mask_in, 'acontrario_global___mask_in', overWrite=True)
        self.pushArrayToSlicer(mask, 'acontrario_global___mask', overWrite=True)
        
        # Gaussian smooth applied to the sustraction image in order to diminish the 
        # effect of the foci in the computation of the empirical histogram. 
        # The sustraction image includes the foci, thus we must smooth it before
        # computing the empirical histogram. Otherwise, the empirical histogram
        # includes foci values as "normal" values.
        gaussKernel = self.gaussKernel(rKernelNoise1,rKernelNoise2,rKernelNoise3);
        difS = self.convolutionWithFFT(dif, gaussKernel); 
        
        
        # Compute the measurement image with the smoothed sustraction image.
        kernel1 = self.elipse3D(ra1,rb1,rc1);
        kernel1 = kernel1/kernel1.sum();
        
        difM_suav = self.convolutionWithFFT(difS, kernel1)
        
        # Since the pixels are correlated, I must subsample the measurement image 
        # in order to compute the empirical histogram. TsubSample is the grid of
        # pixels that will be used to compute the empirical histgram.
        sSub1 = max(ra1,rKernelNoise1);
        sSub2 = max(rb1,rKernelNoise2);
        sSub3 = max(rc1,rKernelNoise3);
        
        TsubSample = np.zeros((n,p,q));
        TsubSample[0::sSub1,0::sSub2,0::sSub3] = 1;  #TsubSample(1:sSub1:n,1:sSub2:p,1:sSub3:q) = 1;
        TsubSample[mask<=0] = 0;
        
        # Compute the empirical density with the measurement image difM_suav in the
        # pixels defined by the grid TsubSample. Work with the logarithm of the
        # density for precision reasons.
        difM_subSampled = difM_suav[TsubSample>0];
        hist, bin_edges = self.ksdensity(difM_subSampled.ravel())
        #log_density = np.log((ksdensity(difM_subSampled(:)) + epsilon_machine));
        log_density = np.log(hist + epsilon_machine);
        
        # The following step is done only to obtain the bins were the density was
        # computed. They cannot be obtained in the previous step because we want
        # to obtain directly the log(density).
        #[aux,bins] = ksdensity(difM_subSampled(:)); # Esto lo hago solo para obtenere los bins para poder tener directo el log del resultado en el paso anterior.
        pasoBin = np.abs(bin_edges[1] - bin_edges[0]);
        
        log_density = log_density + np.log(pasoBin);
        
        # Compute the real measurement image (without smoothness)
        #difM = imfilter(dif,kernel1,'symmetric','same','conv');
        difM = self.convolutionWithFFT(dif, kernel1);  
        
        # Initialize pfa variable
        pfaPos = np.ones(dif.shape);
        
        # For each pixel in the image, if it is in the test grid (T_eff), compute
        # the pfa.
        for j in range(0,n):
            for k in range(0,p):
                for l in range(0,q):
                    if T_eff[j,k,l]==1: 
                        # Here I do not test that the kernel is inside the mask
                        # because I only test pixels in the grid
                        # T_eff, that is the result of the local
                        # testing where that condition was already
                        # tested.                               
                          
                        if np.sum(bin_edges >= difM[j,k,l]) > 0 :
                            pfaPos[j,k,l] = np.log(np.sum(np.exp(log_density[bin_edges >= difM[j,k,l]] - max(log_density[bin_edges >= difM[j,k,l]]) ))) + max(log_density[bin_edges >= difM[j,k,l]]);                                 
                        else :
                            pfaPos[j,k,l] = -1e308; # Minimum value not -Inf
                            
        return pfaPos
          
                        
    def acontrario_detection(self, icOriginal, interOriginal, debug=False):
        #   Output: spots_pos = binary 3D image of size equal to that of the
        #                       input scans, taking value 1 in the detected 
        #                       a-contrario EZ spot candidates and 0 otherwise. 
        #                       The size of each spot is that of the detected most
        #                       meaningful scale.
        #       nfaValues_pos = is a 3D image of size equal to that of the input 
        #                       scans, where each spot takes its corresponding 
        #                       log(nfa) value. The background takes value 1.
        
        #==========================================================================
        #                           Variable definition
        #==========================================================================
        #
        # Tested scales
        #scales_in = [2 1 1;3 2 1;4 3 1];     # Scales for the tested spots.
        #scales_out = [3 2 1;4 3 1;5 4 1];    # Scales for defining the corresponding neighbourhoods.
        #total_esc = size(scales_in,1);
        #grid_step = 0.3;        
        scales_in = np.array([[2, 1, 1], [3, 2, 1], [4, 3, 1]],np.uint32);
        scales_out = np.array([[3, 2, 1],[4, 3, 1],[5, 4, 1]],np.uint32);
        total_esc = scales_in.shape[1];
        grid_step = 0.3;  
        
        #==========================================================================
        #                           Main Program
        #==========================================================================
        # AG: Asegurar que los datos son double (REVISAR)
        ic=np.double(icOriginal.copy())
        inter=np.double(interOriginal.copy())
               
        # Sanity check:  If there are any negative values (it shouldn't happen, but
        # has appeared), set them to 1 as if only one photon was counted.
        # ic(ic<0) = 1; 
        # inter(inter<0) = 1;
        ic[ic<0]=1
        inter[inter<0]=1
        
        # Generate the brain mask.
        #mask = create_mask(ic,inter,scales_in(2,1),scales_in(2,2),scales_in(2,3));
        #ra=scales_in[1,0]; rb= scales_in[1,1]; rc=scales_in[1,2]
        ra=3; rb=2; rc=1; #PROVISORIO (NO ME ANDA BIEN sitkMaskClosedFilled = sitk.BinaryFillhole(sitkMaskClosed) si le paso scale_in
        mask = self.create_mask(ic, inter, ra,rb,rc, debug)
        
        # Normalize the scans to have relative photon counts.
        ic, inter = self.normalization(ic,inter,mask);
        
        #
        print "Luego de la normalizacion"
        print 'ic.min()=',ic.min(),'ic.max()=',ic.max()
        print 'inter.min()=',inter.min(),'inter.max()=',inter.max()   
        self.icNormalized=ic;
        self.interNormalized=inter;
        
        
        # Take logarithm of the images.
        lic = ic.copy();
        lic[mask>0] = np.log(ic[mask>0]);
        lic[(mask>0) & (ic==0)] = 0;
        lin = inter.copy();
        lin[mask>0] = np.log(inter[mask>0]);
        lin[(mask>0) & (inter==0)] = 0;
        
        # Compute the sustraction images.
        dif = ic - inter;
        ldif = lic - lin;
        
        # Make tests for each scale.
        #
        #disp(['Processing scale = 1 of ' num2str(total_esc)]);
        print 'Processing scale = 1 of ',  total_esc
        nfaPos_1 = self.acontrario_det_scale(0,scales_in,scales_out,ldif,dif,mask,grid_step);
        
        #disp(['Processing scale = 2 of ' num2str(total_esc)]);
        print 'Processing scale = 2 of ',  total_esc, ' COMENTADO'
        #nfaPos_2 = self.acontrario_det_scale(1,scales_in,scales_out,ldif,dif,mask,grid_step);
        nfa_Pos2=nfaPos_1.copy()
        
        #disp(['Processing scale = 3 of ' num2str(total_esc)]);
        print 'Processing scale = 3 of ',  total_esc, ' COMENTADO'
        #nfaPos_3 = self.acontrario_det_scale(2,scales_in,scales_out,ldif,dif,mask,grid_step);
        nfa_Pos3=nfaPos_1.copy()
        
        # Draw a spot of the correct scale in each meaningful detection. The
        # correct scale is that of minimun NFA.
        [ spots_pos, nfaValues_pos ] = self.spots_nfa(nfaPos_1, nfaPos_2, nfaPos_3, scales_in);
        
        
        self.pushArrayToSlicer(spots_pos, 'a_contrario_detection____spots_pos', overWrite=True)
        self.pushArrayToSlicer(nfaValues_pos, 'a_contrario_detection____nfaValues_pos', overWrite=True)
        
        
        self.icNormalized = ic
        self.interNormalized = inter
        self.Substraction = ic-inter
        
        return spots_pos, nfaValues_pos
        
        pass  # End of the principal function.
        
    def spots_nfa(self,nfaPos_1, nfaPos_2, nfaPos_3, escalas_in):
        #function [ nfaPos_spots, nfaPos_values ] = spots_nfa(nfaPos_1, nfaPos_2, nfaPos_3, escalas_in)
        
        # Epsilon is set to 1/3 in order to obtain epsilon 1 in the complete test
        # (we are testing 3 scales).
        epsilon = 1/3;
        
        nfa_spotsPos = np.zeros(nfaPos_1.shape);
        nfa_valsPos = np.ones(nfaPos_1.shape);
        
        [n,p,q] = nfaPos_1.shape;
        
        for i in range(0,n):
            for j in range(0,p): 
                for k in range(0,q):
                    # Compare the nfa for each scale and choose the minimum.
                    nfaPos = [ nfaPos_1[i,j,k], nfaPos_2[i,j,k] , nfaPos_3[i,j,k] ];
                    val,ind = min(nfaPos) , argmin(nfaPos) ;
                    
                    # If the choosen value is lower than epsilon, then assign the
                    # scale indicator (ind) in nfa_spots and the real nfa value
                    # (val) in nfa_valsPos.
                    if val <= log(epsilon):
                        nfa_spotsPos[i,j,k] = ind;
                        nfa_valsPos[i,j,k] = val;
                    
        
        # With nfa_spotsPos we can draw a spot of the corresponding scale size in
        # each meaningful detected spot.
        nfaPos_spots = self.spots_display_multiScale(nfa_spotsPos,escalas_in);
        # The same spot image is generated with the nfa values assigned to each
        # spot pixel.
        #nfaPos_values = self.values_display_multiScale(nfa_spotsPos,nfa_valsPos,escalas_in);
        nfaPos_values = nfaPos_spots.copy()
        
        return nfaPos_spots,nfaPos_values
        
    def spots_display_multiScale(self,nfa_umb,scales):
        #function nfa_out = spots_display_multiScale(nfa_umb,scales)
        
        [n,p,q] = nfa_umb.shape;
        
        nfa_out = np.zeros(nfa_umb.shape);
        
        for i in range(0,n):
            for j in range(0,p): 
                for k in range(0,q):
                    
                    if nfa_umb[i,j,k] > 0:
                        
                        ra1 = scales(nfa_umb[i,j,k],0);
                        rb1 = scales(nfa_umb[i,j,k],1);
                        rc1 = scales(nfa_umb[i,j,k],2);
        
                        kernel = self.elipse3D(ra1,rb1,rc1);
                        
                        nfa_out[i-ra1:i+ra1+1,j-rb1:j+rb1+1,k-rc1:k+rc1+1] = kernel + nfa_out[i-ra1:i+ra1+1,j-rb1:j+rb1+1,k-rc1:k+rc1+1];
                        
        nfa_out[nfa_out.nonzero()] = 1;
        return nfa_out

#    def values_display_multiScale(self,nfa_umb,nfa_vals,scales):
#    #function nfa_out = values_display_multiScale(nfa_umb,nfa_vals,scales)
#        
#        nfa_out = np.ones(nfa_umb.shape);
#        nfa_gz = sort(nfa_vals(nfa_vals<=0),'descend');
#        
#        for i=1:length(nfa_gz)
#            
#            aux = find(nfa_vals == nfa_gz(i));
#            total = length(aux);
#            
#            for j=1:total
#        
#                ra1 = scales(nfa_umb(aux(j)),1);
#                rb1 = scales(nfa_umb(aux(j)),2);
#                rc1 = scales(nfa_umb(aux(j)),3);
#                
#                [x,y,z] = ind2sub(size(nfa_vals),aux(j));
#                
#                actual = nfa_out(x-ra1:x+ra1,y-rb1:y+rb1,z-rc1:z+rc1);
#                kernel = elipse3D(ra1,rb1,rc1);
#                
#                after = actual;
#                after(kernel>0) = nfa_gz(i);
#                
#                nfa_out(x-ra1:x+ra1,y-rb1:y+rb1,z-rc1:z+rc1) = after;
#            end
#        end    

    def gaussKernel(self, ra2, rb2, rc2):
        #function gaussKernel = gaussianKernel(ra2,rb2,rc2)
        #
        #    SigmaSquared = 1;
        #    amplitude = (2*pi)^(3/2)*sqrt(1);
        #    
        #    gaussKernel = zeros(2*ra2+1,2*rb2+1,2*rc2+1);
        #    
        #    for x = -ra2:ra2
        #        for y= -rb2:rb2
        #            for z= -rc2:rc2
        #                radiusSquared = (x)^2 + (y)^2 + (z)^2;
        #                gaussKernel(x+ra2+1, y+rb2+1, z+rc2+1) = amplitude * exp(-radiusSquared/(2*SigmaSquared));
        #            end
        #        end
        #    end
        #    
        #    gaussKernel = gaussKernel/sum(gaussKernel(:));
        #
        #end
        SigmaSquared = 1;
        amplitude = (2*np.pi)**(3/2)*np.sqrt(1);
        
        gaussK = np.zeros((2*ra2+1,2*rb2+1,2*rc2+1));
        
        for x in range(-ra2,ra2+1):
            for y in range(-rb2,rb2+1):
                for z in range(-rc2,rc2+1):
                    radiusSquared = (x)**2 + (y)**2 + (z)**2
                    gaussK[x+ra2, y+rb2, z+rc2] = amplitude * np.exp(-radiusSquared/(2*SigmaSquared))
        
        gaussK = gaussK/(gaussK.sum());
        
        return gaussK
        
    
    def elipse3D(self, ra, rb, rc):
        #function c = elipse3D(ra,rb,rc)
        #
        #Na=2*ra+1;
        #Nb=2*rb+1;
        #Nc=2*rc+1;
        #c = zeros(Na,Nb,Nc);
        #
        #for i=1:Na;
        #    for j=1:Nb,
        #        for z=1:Nc,
        #        
        #            if ((i-round(Na/2))^2/ra^2+(j-round(Nb/2))^2/rb^2+(z-round(Nc/2))^2/rc^2<=1)
        #                c(i,j,z)=1;
        #            end
        #
        #        end
        #    end
        #end
        Na=2*ra+1;
        Nb=2*rb+1;
        Nc=2*rc+1;
        c = np.zeros((Na,Nb,Nc));
        
        for i in range(0,Na):
            for j in range (0,Nb):
                for z in range(0,Nc):
                    if ((i-round(Na/2))**2/ra**2+(j-round(Nb/2))**2/rb**2+(z-round(Nc/2))**2/rc**2<=1):
                        c[i,j,z]=1;
        
        return c
                          
    
    def normalization(self,ic,inter,mask):
        #--------------------------------------------------------------------------
        # Function to normalize an image to relative counts.
        #--------------------------------------------------------------------------
        #function [orig, mod] = normalization(ic,in,mask)
        #    
        #    cuentasIn = sum(in(mask>0));
        #    cuentasIc = sum(ic(mask>0));
        #    in = in/cuentasIn;
        #    ic = ic/cuentasIc;
        #    # Scale variance for it not to be too little.
        #    min_in = abs(min(in(in~=0)));
        #    min_ic = abs(min(ic(ic~=0)));
        #    f = min(min_in,min_ic);
        #    ic = ic/f;
        #    in = in/f;    
        #    
        #    orig = ic;
        #    mod = in;
        #
        #end
        
        cuentasIn = inter[mask>0].sum();
        cuentasIc = ic[mask>0].sum();
        inter = inter/cuentasIn;
        ic = ic/cuentasIc;
        # Scale variance for it not to be too little.
        min_in =  abs(inter[inter.nonzero()].min()) #PARA QUE ESTA EL ABS !!!!!!!
        min_ic = abs(ic[ic.nonzero()].min())  #PARA QUE ESTA EL ABS !!!!!!!
        f = min(min_in,min_ic);
        ic = ic/f;
        inter = inter/f;    
        
        print cuentasIn, cuentasIc, min_ic, min_in, f
        return ic,inter
        
    def create_mask(self, ic_, inter_, ra, rb, rc, debug=False):
        # CREATE_MASK Creates a brain mask for the realigned images ic (ictal SPECT
        # scan) and in (inter-ictal SPECT scan).
        #
        #   CREATE_MASK(ic,in,ra,rb,rc) Returns a binary mask of the brain, suited
        #   to the realigned images ic (ictal SPECT scan) and in (inter-ictal SPECT 
        #   scan). The mask is morphologically closed using an elliptical
        #   structuring element of radii (ra,rb,rc). Then possible holes are filled
        #   using the Matlab function imfill.
        
        # Generate an auxiliary mask as all pixels above the mean/M for both scans.
        #    M = 6;
        #    mean_ic = mean2(ic(ic.*in > 0));
        #    mean_in = mean2(in(ic.*in > 0));
        #    mask_aux = find(ic > mean_ic / M & in > mean_in / M);
        
        M = 6;
        
        ic=ic_.copy();
        inter=inter_.copy();
        
        
        #----------COMPUTE AUX MAS------------------------------------
        IctalTimesInterictal = ic * inter;  # element-wise multiplication
        IctalTimesInterictalGreaterThanZeroIndices = (IctalTimesInterictal > 0).nonzero();
        mean_ic = ic[IctalTimesInterictalGreaterThanZeroIndices].mean()
        mean_in = inter[IctalTimesInterictalGreaterThanZeroIndices].mean()
        MaskAuxIndices = ((ic > mean_ic / M) & (inter > mean_in / M)).nonzero()
        
        mask = np.zeros(ic.shape, np.uint8)
        
        
        # The scans histograms are computed inside the auxiliary mask and the user
        # is asked to choose a threshold. The threshold must be close to the value
        # separating the bimodal histogram.
        
        # automatic threshold uses Otsu
        #    mask_ic = automatic_threshold(ic, mask_aux);
        #    mask_in = automatic_threshold(in, mask_aux);
        #    mask = mask_ic.*mask_in;
        #    
        
        BasalMasked = inter[MaskAuxIndices]  # array with only the pixels in the mask_aux
        IctalMasked = ic[MaskAuxIndices]  # array with only the pixels in the mask_aux
        
        
        
        #----------OTSU THRESHOLDING------------------------------------
        # move to SimpleITK to compute OTSU ( need to have a 2D array at least in GetImageFromArray, that's why the vstack)
        sitkBasalMasked = sitk.GetImageFromArray(np.vstack((BasalMasked, BasalMasked)))
        sitkIctalMasked = sitk.GetImageFromArray(np.vstack((BasalMasked, BasalMasked)))
        
        # compute otsu for both masked images
        sitkBasalMaskedOtsu = sitk.OtsuThreshold(sitkBasalMasked, 0, 1)
        sitkIctalMaskedOtsu = sitk.OtsuThreshold(sitkIctalMasked, 0, 1)
        
        # back to numpy
        BasalMaskedOtsu = sitk.GetArrayFromImage(sitkBasalMaskedOtsu)
        IctalMaskedOtsu = sitk.GetArrayFromImage(sitkIctalMaskedOtsu)
        
        # intersect the masks
        BasalIctalMaskedOtsuIntersection = BasalMaskedOtsu * IctalMaskedOtsu
        BasalIctalMaskedOtsuIntersection = BasalIctalMaskedOtsuIntersection[0, :]  # undo the vstack (keepo only the first row)
        
        # Fill indices computed before 
        mask[MaskAuxIndices] = BasalIctalMaskedOtsuIntersection
        
        
        #----------MORPHOLOGY------------------------------------
        # Morphology is used to close the obtained mask.
        # mask = morpho_ellipse(mask, ra, rb, rc);
        # Possible remaining holes are filled.
        # mask = imfill(mask);    
        
        
        # move to SimpleITK to  do some morphology
        sitkMask = sitk.GetImageFromArray(mask)
        
        if debug:
            sitkUtils.PushBackground(sitkMask, 'create_mask_Mask_After_Otsu',overwrite = True)
          
        
        
        # closing with an ellipsoid ra,rb,rc 
        sitkMaskClosed = sitk.BinaryMorphologicalClosing(sitkMask, [ra, rb, rc])
        
        if debug:
            sitkUtils.PushBackground(sitkMask, 'create_mask_Mask_After_Otsu_And_Closing',overwrite = True)
            
        # fill holes
        sitkMaskClosedFilled = sitk.BinaryFillhole(sitkMaskClosed)
        
        if debug:
            sitkUtils.PushBackground(sitkMaskClosedFilled, 'Mask',overwrite = True)
        
        # back to numpy
        mask = sitk.GetArrayFromImage(sitkMaskClosedFilled)
        
        
        return mask    
  #
  
  
  # tomado de EditUtil.py
    def getCompositeNode(self, layoutName='Red'):
        """ use the Red slice composite node to define the active volumes """
        count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceCompositeNode')
        for n in xrange(count):
            compNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceCompositeNode')
            if compNode.GetLayoutName() == layoutName:
                return compNode
    def getSliceNode(self, sliceName='Red'):
        """ use the Red slice composite node to define the active volumes """
        count = slicer.mrmlScene.GetNumberOfNodesByClass('vtkMRMLSliceNode')
        for n in xrange(count):
            sliceNode = slicer.mrmlScene.GetNthNodeByClass(n, 'vtkMRMLSliceNode')
            if sliceNode.GetName() == sliceName:
                return sliceNode
        
    def displayVolumeInSlice(self, volumeName, sliceLayoutName, sliceOrientation="Axial"):
        compositeNode = self.getCompositeNode(sliceLayoutName)
        sliceNode = self.getSliceNode(sliceLayoutName)
        volumeNode = slicer.util.getNode(volumeName)
        if not compositeNode == None and not volumeNode == None:
            compositeNode.SetBackgroundVolumeID(volumeNode.GetID())
        else:
            print("displayVolumeInSlice failed")
        if not sliceNode == None:
            sliceNode.SetOrientation(sliceOrientation)
            
    def compareMasks(self):
        self.displayVolumeInSlice(self.BASAL_VOLUME_NAME, 'Compare1', 'Axial')
        self.displayVolumeInSlice(self.BASAL_VOLUME_NAME, 'Compare2', 'Sagittal')
        self.displayVolumeInSlice(self.BASAL_VOLUME_NAME, 'Compare3', 'Coronal')
        
        self.displayVolumeInSlice(self.ICTAL_VOLUME_NAME, 'Compare4', 'Axial')
        self.displayVolumeInSlice(self.ICTAL_VOLUME_NAME, 'Compare5', 'Sagittal')
        self.displayVolumeInSlice(self.ICTAL_VOLUME_NAME, 'Compare6', 'Coronal')
        
        self.displayVolumeInSlice(self.MASK_VOLUME_NAME, 'Compare7', 'Axial')
        self.displayVolumeInSlice(self.MASK_VOLUME_NAME, 'Compare8', 'Sagittal')
        self.displayVolumeInSlice(self.MASK_VOLUME_NAME, 'Compare9', 'Coronal')
        
        crosshairNode = slicer.util.getNode('vtkMRMLCrosshairNode*')
        crosshairNode.SetCrosshairMode(1)
        crosshairNode.SetNavigation(True)
#-----------------------------------------------------   