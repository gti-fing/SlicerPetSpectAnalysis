cmake_minimum_required(VERSION 2.8.9)

project(EpilepsyToolkit)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://guillermocarbajal.github.io/SlicerEpilepsyToolkit")
set(EXTENSION_CATEGORY "Epilepsy")
set(EXTENSION_CONTRIBUTORS "Guillermo Carbajal, Álvaro Gómez (Facultad de Ingeniería, Uruguay)")
set(EXTENSION_DESCRIPTION "First Version of the Epilepsy Toolkit Extension")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/EpilepsyToolkit.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/EpilepsyToolkit/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(EpilepsyCppModule)
add_subdirectory(EpilepsyPythonModule)
add_subdirectory(EpilepsyCLI)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
