cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(VolumePlaneCut)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/VolumePlaneCut")
set(EXTENSION_CATEGORY "Utilities")
set(EXTENSION_CONTRIBUTORS "Li Bin Song (University of Alberta), Antarpuneet Singh (University of Alberta)")
set(EXTENSION_DESCRIPTION "This Extension is used for volume rendering. By using this extension, you can use a plane to cut the volume and show you interaction of the volume rendering.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/VolumePlaneCut.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/VolumePlaneCut/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(PlaneCut)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
