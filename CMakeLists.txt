cmake_minimum_required(VERSION 2.8.9)

project(PetSpectAnalysis)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://gti-fing.github.io/PetSpectAnalysis")
set(EXTENSION_CATEGORY "Epilepsy")
set(EXTENSION_CONTRIBUTORS "Martín Bertran, Natalia Martínez Gil, Guillermo Carbajal, Álvaro Gómez (Facultad de Ingeniería, Uruguay)")
set(EXTENSION_DESCRIPTION "First Version of the Pet Spect Analysis Extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/PetSpectAnalysis.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/PetSpectAnalysis/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(CarotidSegmentation)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
