import streamlit as st
import time
import numpy as np
import subprocess as sp
import os
import shutil

#TODO:
#1 implement rotation for already flattened files
#2 test color
#fix upload success message
#add progress bars
#3 reevaluate run lock and roi requirements based on process
#4 white sample?
#5 streamlit caching?

    ##functions##

def run(): #must check all transformation parameters are selected

    runBar = optionsContainer.progress(0.0, "Creating Directories")
    settings()
    
    runBar.progress(0.1, "Creating Directories")
    #removes left over Transform directory if files not re-uploaded
    try:
        transformPath = "JubPalProcess/data/" + st.session_state.projectName + "/" + st.session_state.compositeName + "/Transform"
        if os.path.isdir(transformPath):
            shutil.rmtree(transformPath)
            print("flushed Transform directory")
    except Exception:
        print("exception while attempting to flush transform directory")
        
    runBar.progress(0.3, "Processing")

    print("Start processing...")
    #25 minute timeout for processs.py given
    processOut = sp.run(["venv/bin/python3", "JubPalProcess/process.py", "JubPalProcess/options.yaml", "noninteractive"], timeout=None, capture_output=True)
   
    print(processOut.stdout)

    if st.session_state.color != None:
        runBar.progress(0.6, "Generating 12-Band Color")
        colorOut = sp.run(["venv/bin/python3", "JubPalProcess/color.py"], timeout=None, capture_output=True)
    
    runBar.progress(0.7, "Transfering Files")

    relocate("JubPalProcess/data/" + st.session_state.projectName + "/" + st.session_state.compositeName + "/Transform", "Transform/"+ st.session_state.projectName + "/" + st.session_state.compositeName+"/")#copys contents of Transform directory to out directory
    
    runBar.progress(1.0, "Finishing")

    print("--Finished--")
   
    optionsContainer.success("Success")

    runBar.empty()
    #set project meta-data and file directories
def settings():
    writeOptions()
    writeProjectData()
    
    
    #create options.yaml
def writeOptions():
    f = open("JubPalProcess/options.yaml", "w")
    f.write("document: processing options and data sources\n")
    f.write("tip: options may be reordered per need\noptions:\n")
    f.write("  interactive:\n    - False\n")
    f.write("  sigmas:\n" + formatOption(st.session_state.sigma))
    f.write("  skipuvbp:\n    - " + str(st.session_state.skipUV) + "\n")
    f.write("  methods:\n" + formatOption(st.session_state.process))
    f.write("  n_components:\n    - "+ st.session_state.components + "\n")
    f.write("output:\n")
    f.write("  histograms:\n" + formatOption(st.session_state.histogram))
    f.write("  fileformats:\n" + formatOption(st.session_state.fileFormat))
    f.write("settings:\n")
    f.write("  fica_max_iter: " + st.session_state.ficaIter + "\n")
    f.write("  fica_tol: " + st.session_state.ficaTol + "\n")
    f.write("  cachepath: \"JubPalProcess/cache/\"" + "\n")
    f.write("  logfile: \"JubPalProcess/logs/jubpalprocess.log\"" + "\n")
    f.write("  loglevel: " + st.session_state.logLevel.upper() + "\n")
    f.write("  color: \n    illuminant: D65\n")
    f.write("basepaths:\n  - \"JubPalProcess/data/" + st.session_state.projectName + "/\"\n")
    f.close()
    
    
    #creates project and raw or flattened directories 
def makeDirectories():
    projectDir = "JubPalProcess/data" 
    
    #trash old data directory
    try:
        path = os.path.join("", projectDir)
        shutil.rmtree(path)
    except Exception:
        print("Project directory error 1")
     
    #make data directory  
    try:
        os.mkdir(projectDir)
    except FileExistsError:
        print("Project directory already exists.")
    except PermissionError:
        print("Project directory Permission denied")
    except Exception:
        print("Project directory error 2")
    
        
    projectDir += "/" + st.session_state.projectName
    
    #make project directory
    try:
        os.mkdir(projectDir)
    except FileExistsError:
        print("Project directory already exists.")
    except PermissionError:
        print("Project directory Permission denied")
    except Exception:
        print("Project directory error 3")

    #make calibration directory
    try:
        os.mkdir(projectDir + "/calibration")
    except FileExistsError:
        print("Page directory already exists.")
    except PermissionError:
        print("Page directory Permission denied")
    except Exception:
        print("Page directory error 4")
        
    #make target directory 
    try:
        os.mkdir(projectDir + "/" + st.session_state.compositeName)
    except FileExistsError:
        print("Page directory already exists.")
    except PermissionError:
        print("Page directory Permission denied")
    except Exception:
        print("Page directory error 5")
        
        #make imageset directory
    try:
        os.mkdir(projectDir + "/" + st.session_state.compositeName + "/" + st.session_state.inputType)
    except FileExistsError:
        print("Page directory already exists.")
    except PermissionError:
        print("Page directory Permission denied")
    except Exception:
        print("Page directory error 6")
    
 
    #create project.yaml
def writeProjectData():
    if(st.session_state.roiSize == None):
        st.session_state.roiSize = 0;
    if(st.session_state.noiseSize == None):
        st.session_state.noiseSize = 0;
    if(st.session_state.whiteSize == None):
        st.session_state.whiteSize = 0;
    
    path = "JubPalProcess/data/" + st.session_state.projectName + "/"
    f = open(path + st.session_state.projectName+".yaml", "w")
    f.write("default:\n")
    f.write("  imagesets:\n    - " + st.session_state.inputType + "\n")
    f.write("  flats: \"/calibration/\"\n")
    f.write("  visibleBands: \n")
    f.write(findVisibleBands())
    f.write("  white:\n    w: " + str(st.session_state.whiteSize) + "\n    h: " + str(st.session_state.whiteSize) + "\n")
    f.write(st.session_state.compositeName + ":\n  rois:\n    roi1:\n")
    f.write("      x: " + str(st.session_state.roiX) + "\n      y: " + str(st.session_state.roiY) + "\n")
    f.write("      w: " + str(st.session_state.roiSize) + "\n      h: " + str(st.session_state.roiSize) + "\n")
    f.write("      label: \"Dead Center\"\n")
    f.write("  noisesamples:\n    noise01:\n")
    f.write("      x: " + str(st.session_state.noiseX) + "\n      y: " + str(st.session_state.noiseY) + "\n")
    f.write("      w: " + str(st.session_state.noiseSize) + "\n      h: " + str(st.session_state.noiseSize) + "\n")
    f.write("      label: \"Left Margin Generally\"\n")
    f.write("  rotation: " + st.session_state.rotation[:-1] + "\n")
    f.write("  white:\n    x: " + str(st.session_state.whiteX) + "\n    y: " + str(st.session_state.whiteY))
    f.close()
    
    
   #called on upload click to reset input files
def fileUpload(): 
    print("Uploading files...")

    st.session_state.uploadBar = uploadContainer.progress(0.0, "Creating Directories")
    makeDirectories()
    #if 'uploadProgress' not in st.session_state:
    st.session_state.uploadProgress = 0.001

    st.session_state.uploadBar.progress(st.session_state.uploadProgress, "Uploading")
    
    #save uploaded files to new directories
    uploadCount = len(st.session_state.images)
    if st.session_state.flats != None:
        uploadCount += len(st.session_state.flats)
    
    st.session_state.inc = round(1.0/uploadCount, 6)

    saveUpload(("JubPalProcess/data/" + st.session_state.projectName + "/" + st.session_state.compositeName + "/" + st.session_state.inputType), st.session_state.images)
    if st.session_state.flats != None:
        saveUpload("JubPalProcess/data/" + st.session_state.projectName + "/calibration", st.session_state.flats)
        
    
    st.session_state.uploadBar.progress(1.0, "Finishing")
    uploadContainer.success("Success")
    time.sleep(.1)
    st.session_state.uploadBar.empty()
    
    #save files to path
def saveUpload(path, files):
    for file in files:
        #print("saved: " + file.name + " to " + path)
        with open(os.path.join(path,file.name),"wb") as f:
            f.write(file.getbuffer())
        if st.session_state.uploadProgress+st.session_state.inc <= 1.0:
            st.session_state.uploadProgress+=st.session_state.inc
        st.session_state.uploadBar.progress(st.session_state.uploadProgress, "Uploading")
    print("saved uploads to: "+ path)


    #relocate files in src to dst
def relocate(src, dst):
    #try:
    stdout = shutil.copytree(src, dst, dirs_exist_ok = True)
    print("saved: " + str(stdout) + " to X:/JubPalProcessVE/Transform")
    #except Exception:
    #    print("Transform relocate failed")
 
 
    #empties cache directory
def clearCache():
    try:
        shutil.rmtree("JubPalProcess/cache")
        os.mkdir("JubPalProcess/cache")
        print("cache cleared")  
    except Exception:
        print("Exception while attempting to clear cache")
        
        
    #called on raw process toggle
def updateImportType():
    if st.session_state.mode:
        st.session_state.inputType = "raw"
    else:
        st.session_state.inputType = "flattened"
        
        
    #formats selected control panel options for options.yaml
def formatOption(options):
    str = ""
    for option in options:
        str+= "    - "+option.lower()+"\n"
    return str


    #finds visible band names in image upload
def findVisibleBands():
    visible = ""
    try:
        for image in st.session_state.images:
                band = image.name.split("_")
                
                if st.session_state.mode: # raw processing
                    band = band[-1].split(".")[0]
                else:   #flattened processing
                    band = band[-2]
                    
                if int(band) > 7 and int(band) < 20:
                    name = image.name.split("+")[1].split(".")[0]
                    
                    if not st.session_state.mode: #shears _F on flattened files
                        name = name[:-2]
        
                    visible += "    - \'" + name + "\'\n"
    except Exception:
        print("Exception: File names could not be parsed") 
    return visible
        

    #disables file upload submit button if misssing requirements
def uploadLock():
    if (st.session_state.projectName != "" and st.session_state.pageName !="" and st.session_state.images != [] and
        not (st.session_state.mode and st.session_state.flats == [])):
        st.session_state.fileRequirements = True
        return False
    else:
        st.session_state.fileRequirements = False
        uploadContainer.info("Satisfy upload fields first")
        return True
    
    
    #disables control panel submit button if missing requirements
def optionsLock():
    if (st.session_state.sigma != [] and st.session_state.process != [] and 
            st.session_state.components != None and st.session_state.histogram != [] and
            st.session_state.fileFormat != [] and st.session_state.ficaIter != None and 
            st.session_state.ficaTol != None and st.session_state.logLevel != None and 
            st.session_state.fileRequirements):
        if "PCA" in st.session_state.process and st.session_state.roiSize == None:
            optionsContainer.warning("PCA requires a ROI selection")
            return True
        elif "MNF" in st.session_state.process and (st.session_state.roiSize == None or st.session_state.noiseSize == None):
            optionsContainer.warning("MNF requires a ROI and noise sample selection")
            return True
        else:
            return False #all options satisfied
    else:
        optionsContainer.info("Select all parameters first")         
        return True


def resetInput():
    #st.session_state.projectName = ""
    if st.session_state.resetCharacter == "":
        st.session_state.resetCharacter = " "
    else:
        st.session_state.resetCharacter = ""

    

#returns size of path directory
def getSize(path):
    size = 0
    with os.scandir(path) as contents:
        for item in contents:
            if os.path.isfile(item):
                size += item.stat().st_size
            elif os.path.isdir(item):
                size += getSize(item.path)
    return size

#attempting to cache uploads
#@st.cache_data TODO check this
def cacheUploads():
    
    st.session_state.images = st.session_state.imageUploads
    return st.session_state.images


    ##UI elements##

st.set_page_config(layout="wide")
st.subheader("JubPalProcessVE", divider="gray")
uploadTab, settingsTab, controlTab = st.columns(3, gap="medium")


    #file upload selection
with uploadTab:
    st.subheader("File Input - 1")

    if 'inputType' not in st.session_state:
        st.session_state.inputType = 'flattened'
        
    if 'fileRequirements' not in st.session_state:
        st.session_state.fileRequirements = False
    
    titleContainer = st.container(border=True)
    
    with titleContainer:
        st.text_input("Project Name", placeholder="Ambrosiana", key="projectName")
        
        st.toggle("Raw Processing", key="mode", on_change=updateImportType)
        
   
    uploadContainer = st.container(key="uploadContainer", border=True)
    
   
    uploadContainer.text_input("Page Name", placeholder="00r", key="pageName")
    
    #compositeName
    st.session_state.compositeName = st.session_state.projectName + "_" + st.session_state.pageName
    

    
    #used to reset file uploader name 
    if 'resetCharacter' not in st.session_state:
        st.session_state.resetCharacter = ""

    #uploadContainer.file_uploader("Import " + st.session_state.inputType + " files here:", accept_multiple_files=True, type=['tif','dng'], key="imageUploads", on_change=cacheUploads)
    uploadContainer.file_uploader("Import " + st.session_state.inputType + " files here:" + st.session_state.resetCharacter, accept_multiple_files=True, type=['tif','dng'], key="images")

   # if "images" not in st.session_state:
    #    st.session_state.images = cacheUploads(imageUploads)
   # else:
   #     st.session_state.images = cacheUploads(imageUploads)
    
    if st.session_state.mode:
       uploadContainer.file_uploader("Import flats here:" + st.session_state.resetCharacter, accept_multiple_files=True, type=['dng'], key="flats")
    else:
        st.session_state.flats = None
        
    upload, clear = uploadContainer.columns(2)
    upload.button("Upload", disabled=uploadLock(), on_click=fileUpload)
    clear.button("Clear Files", use_container_width=True, on_click=resetInput)

    #project roi data and settings
with settingsTab:
    st.subheader("Project Data - 2")
   
   #Interest Regions
    st.subheader("Interest Regions", divider="gray")
    
    
    roiContainer = st.container(border=True)
    label, size, x, y = roiContainer.columns(4)
    label.write("ROI:")
    size.number_input("size (px)", placeholder="required", min_value=0, value=None, step=None, key="roiSize")
    x.number_input("x", min_value=0, value="min", step=None, key="roiX")
    y.number_input("y", min_value=0, value="min", step=None, key="roiY")
    
    noiseContainer = st.container(border=True)
    label, size, x, y = noiseContainer.columns(4)
    label.write("Noise Sample:")
    size.number_input("size (px)", placeholder="required", min_value=0, value=None, step=None, key="noiseSize")
    x.number_input("x", min_value=0, value="min", step=None, key="noiseX")
    y.number_input("y", min_value=0, value="min", step=None, key="noiseY")
    
    whiteContainer = st.container(border=True)
    label, size, x, y = whiteContainer.columns(4)
    label.write("White Sample:")
    size.number_input("size (px)", placeholder="none", min_value=0, value=None, step=None, key="whiteSize")
    x.number_input("x", min_value=0, value="min", step=None, key="whiteX")
    y.number_input("y", min_value=0, value="min", step=None, key="whiteY")
    
    
    st.subheader("Advanced Settings", divider="gray")
    
    settingsContainer = st.container(border=True)
    with settingsContainer:
        rotationOptions = ["0˚", "90˚", "180˚", "270˚"]
        st.segmented_control("Clockwise Rotation", rotationOptions, default="0˚", selection_mode="single", disabled = not st.session_state.mode, key="rotation")
        

        ficaIterOptions = ["100", "1000", "10000"]
        st.segmented_control("Fica Max Iteration", ficaIterOptions, default="100", selection_mode="single", key="ficaIter")
        
        ficaTolOptions = [".01", ".001", ".0001", ".00001"]
        st.segmented_control("Fica Tolerance", ficaTolOptions, default=".001", selection_mode="single", key="ficaTol")
        
        logOptions = ["Debug", "Info", "Warning", "Critical"]
        st.segmented_control("Log Level", logOptions, default="Info", selection_mode="single", key="logLevel")
        
        st.button("Clear Cache", type="secondary", on_click=clearCache)
        
        
    #control panel for transformation options
with controlTab:
    st.subheader("Control Panel - 3")
    
    optionsContainer = st.container(key="optionsContainer", border=True)
    optionsContainer.subheader("Options", divider="gray")
    
   
    left, right = optionsContainer.columns([2,1])

    processOptions = ["PCA", "MNF", "Fica"] #add color
    left.segmented_control("Process", processOptions, selection_mode="multi", label_visibility= "visible", key="process")
    #optionsContainer.write(st.session_state.process)
    
    right.segmented_control("Process", ['Color'], selection_mode="single", disabled = not st.session_state.mode, label_visibility= "hidden", key="color")
   
     
    sigmaOptions = ["1000", "500", "300", "100", "50", "0"]
    optionsContainer.segmented_control("Blur-Divide Sigma", sigmaOptions, selection_mode="multi", key="sigma")
    #optionsContainer.write(st.session_state.sigma)
    
    histogramOptions = ["Equalize", "Adaptive", "Rescale"]
    optionsContainer.segmented_control("Histograms", histogramOptions, selection_mode="multi", key="histogram")
    #optionsContainer.write(st.session_state.histogram)
    
    optionsContainer.checkbox("Skip UVB/P files?", key="skipUV")
    #optionsContainer.write(st.session_state.skipUV)
    
    optionsContainer.subheader("Output", divider="gray")
    
  
    componentOptions = ["20", "10", "5", "max"]
    optionsContainer.segmented_control("Component number", componentOptions, selection_mode="single", key="components")
    #optionsContainer.write(st.session_state.components)

    formatOptions = ["jpg", "png", "tif"]
    optionsContainer.segmented_control("File Format", formatOptions, selection_mode="multi", key="fileFormat")
    #optionsContainer.write(st.session_state.fileFormat)
    
  
    optionsContainer.button("Run", type="primary", disabled=optionsLock(), on_click=run)
    