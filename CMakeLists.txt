cmake_minimum_required(VERSION 2.8.9)

project(PetSpectAnalysis)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://gti-fing.github.io/SlicerPetSpectAnalysis")
set(EXTENSION_CATEGORY "Nuclear Medicine")
set(EXTENSION_CONTRIBUTORS "Martin Bertran, Natalia Martinez Gil, Guillermo Carbajal, Alvaro Gomez (Facultad de Ingenieria, Uruguay)")
# set(EXTENSION_DESCRIPTION "Pet Spect Analysis Extension contains two modules: dPetBrainQuantification and EpileptogenicFocusDetection")
set(EXTENSION_DESCRIPTION "First Version of the Pet Spect Analysis Extension")
set(EXTENSION_ICONURL "https://www.slicer.org/slicerWiki/images/b/b1/DPetBrainQuantification.png")
set(EXTENSION_SCREENSHOTURLS "https://www.slicer.org/slicerWiki/images/e/e4/ProcessingBlocks.png https://www.slicer.org/slicerWiki/images/7/76/InformationPanel.png https://www.slicer.org/slicerWiki/images/2/2a/VisualizationPanel.png https://www.slicer.org/slicerWiki/images/2/24/CarotidSegmentation.png https://www.slicer.org/slicerWiki/images/b/bb/CarotidSegmentationROI.png https://www.slicer.org/slicerWiki/images/5/51/PTACEstimationIDIF.png https://www.slicer.org/slicerWiki/images/9/98/PTACEstimationPBIF.png https://www.slicer.org/slicerWiki/images/9/90/KMap.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(dPetBrainQuantification)
# add_subdirectory(SlicerEpilepsyToolkit/EpileptogenicFocusDetection)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
