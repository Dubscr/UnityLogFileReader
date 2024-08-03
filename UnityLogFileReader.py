import os
import re
from enum import Enum
import tkinter as tk
from tkinter import ttk
class DebugTypes(Enum):
    UNDEFINED = 0,
    SYSTEMEXCEPTION = 1,
    SYSTEMSYSTEMEXCEPTION = 2,
    ARGUMENTEXCEPTION = 3,
    ARGUMENTNULLEXCEPTION = 4,
    ARGUMENTOUTOFRANGEEXCEPTION = 5,
    ARITHMETICEXCEPTION = 6,
    ARRAYTYPEMISMATCHEXCEPTION = 7,
    DIVIDEBYZEROEXCEPTION = 8,
    FORMATEXCEPTION = 9,
    INDEXOUTOFRANGEEXCEPTION = 10,
    INVALIDCASTEXCEPTION = 11,
    INVALIDOPERATIONEXCEPTION = 12,
    NULLREFERENCEEXCEPTION = 13,
    OUTOFMEMORYEXCEPTION = 14,
    OVERFLOWEXCEPTION = 15,
    STACKOVERFLOWEXCEPTION = 16,
    TYPEINITIALIZATIONEXCEPTION = 17,
    UNAUTHORIZEDACCESSEXCEPTION = 18,
    IOEXCEPTION = 19,
    FILENOTFOUNDEXCEPTION = 20,
    DIRECTORYNOTFOUNDEXCEPTION = 21,
    ENDOFSTREAMEXCEPTION = 22,
    PATHTOOLONGEXCEPTION = 23,
    UNITYEXCEPTION = 24,
    MISSINGCOMPONENTEXCEPTION = 25,
    MISSINGREFERENCEEXCEPTION = 26,
    UNASSIGNEDREFERENCEEXCEPTION = 27,
    PLAYERPREFSEXCEPTION = 28,
    ASSETBUNDLECREATEREQUEST = 29,
    ASSETBUNDLEREQUEST = 30,
    SCENEMANAGEMENTEXCEPTION = 31,
    EDITORAPPLICATIONEXCEPTION = 32,
    BUILDFAILEDEXCEPTION = 33,
    USERERRORLOG = 34,
    USERWARNINGLOG = 35,
    USERLOG = 36
class SectionData(object):
    debugMessage = ""
    scriptAndFunction = ""
    frequency = 0
    logType = DebugTypes.UNDEFINED
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
# Current working directory
thisDir = __file__.replace("\\", "/").replace(os.path.basename(__file__), "")
logsFolder = thisDir + "/unitylogs/"

logSectionScriptFromLogAndData = dict()
projectAssetsFolder = "C:\\Users\\Owner\\Desktop\\Github\\Default\\Murder Mystery\\Assets"
projectScripts = dict(script = str(), dir = str())
scriptsToIgnore = ["UnityEngine", "UnityEditor"]
errorsOnly = False

# Gets all consecutive alphanumeric substrings in string
def GetAlnumSubsets(line):
    line = str(line)
    possibleSubsets = []
    currentSubset = ""
    for c in line:
        if (c.isalnum()):
            currentSubset += c
        else:
            if (currentSubset != ""):
                possibleSubsets.append(currentSubset)
                currentSubset = ""
    return possibleSubsets

# Individual check for valid changeset
def IsValidChangeset(subset):
    if len(subset) == 12:
        return True
    else:
        return False

# If first line of log file has a valid changeset, return true
def HasValidChangeset(lines):
    for line in lines:
        subsets = GetAlnumSubsets(line)
        joinedSubsets = "".join(str(x) for x in subsets)
        if("Initializeengineversion" in joinedSubsets):
            for subset in subsets:
                if IsValidChangeset(subset):
                    return True
    return False

# Returns list of valid Unity log files
def GetValidLogFiles():
    # Get list of log files in logs folder
    listOfFiles = os.listdir(logsFolder)
    validLogFiles = []
    for file in listOfFiles:
        if file.endswith(".log"):
            with open(logsFolder + file) as f:
                # Check if file is valid Unity log file
                lines = f.readlines()
                if HasValidChangeset(lines):
                    validLogFiles.append(file)
    return validLogFiles

# Returns grouped sections of code
def GroupList(file):
    with open(logsFolder + file) as f:
        # Check if file is valid Unity log file
        lines = f.readlines()
        groupedLines = []
        currentLine = ""
        for line in lines:
            if(line != "\n"):
                currentLine += line
            else:
                groupedLines.append(currentLine)
                currentLine = ""
    return groupedLines
    

# Returns frequency of each section from dict
def GetFrequencyFromLogFile(logFile):
    definedSections = dict()
    for groupedLog in GroupList(logFile):
        if groupedLog not in definedSections.keys():
            definedSections[groupedLog] = 1
        else:
            definedSections[groupedLog] += 1
    return definedSections

# Returns script and function from section
def GetScriptAndFunctionFromSection(section):
    section = str(section)
    match = re.findall(r'at\s([^\s]+)\s\([^\)]*\)', section)
    if match is not None:
        return match
    else:
        return None

def GetDebugLogs(section):
    lines = section.splitlines()
    for i, line in enumerate(lines):
        if "Debug:Log" in line:
            data = SectionData()
            if(str(re.search(r'\S+\.\s*\S*\s*\(.*\)', section).group(0))):
                data.debugMessage = lines[i - 2]
            if(len(lines) > i + 1):
                result2 = re.search(r'\b\w+:\w+\b(?=\(.*?\))', lines[i+1])
                if(result2 is not None):
                    data.scriptAndFunction = str(result2.group(0))
                return data
    return None

# Returns list of scripts
def GetScriptsFromDir(rootFolder):
    cs_files = []
    for root, dirs, files in os.walk(rootFolder):
        for filename in files:
            if str(filename).endswith('.cs'):
                cs_files.append(os.path.join(root, filename).replace("\\", "/"))
    return cs_files


def GetScriptContents(file):
    with open(file, encoding="utf8") as f:
        contents = f.readlines()
        if(contents != ""):
            return contents
        
def GetSectionDebugType(content=""):
    if content == "":
        print(f"Could not find debug type at content:\n{content}\nempty content??")
        return DebugTypes.UNDEFINED
    
    if "NullReferenceException" in content:
        return DebugTypes.NULLREFERENCEEXCEPTION
    elif "ArgumentOutOfRangeException" in content:
        return DebugTypes.ARGUMENTOUTOFRANGEEXCEPTION
    elif "UnityException" in content:
        return DebugTypes.UNITYEXCEPTION
    elif "MissingComponentException" in content:
        return DebugTypes.MISSINGCOMPONENTEXCEPTION
    elif "MissingReferenceException" in content:
        return DebugTypes.MISSINGREFERENCEEXCEPTION
    elif "UnassignedReferenceException" in content:
        return DebugTypes.UNASSIGNEDREFERENCEEXCEPTION
    elif "SystemException" in content:
        return DebugTypes.SYSTEMEXCEPTION
    elif "SystemSystemException" in content:
        return DebugTypes.SYSTEMSYSTEMEXCEPTION
    elif "ArgumentException" in content:
        return DebugTypes.ARGUMENTEXCEPTION
    elif "ArgumentNullException" in content:
        return DebugTypes.ARGUMENTNULLEXCEPTION
    elif "ArithmeticException" in content:
        return DebugTypes.ARITHMETICEXCEPTION
    elif "ArrayTypeMismatchException" in content:
        return DebugTypes.ARRAYTYPEMISMATCHEXCEPTION
    elif "DivideByZeroException" in content:
        return DebugTypes.DIVIDEBYZEROEXCEPTION
    elif "FormatException" in content:
        return DebugTypes.FORMATEXCEPTION
    elif "IndexOutOfRangeException" in content:
        return DebugTypes.INDEXOUTOFRANGEEXCEPTION
    elif "InvalidCastException" in content:
        return DebugTypes.INVALIDCASTEXCEPTION
    elif "InvalidOperationException" in content:
        return DebugTypes.INVALIDOPERATIONEXCEPTION
    elif "OutOfMemoryException" in content:
        return DebugTypes.OUTOFMEMORYEXCEPTION
    elif "OverflowException" in content:
        return DebugTypes.OVERFLOWEXCEPTION
    elif "StackOverflowException" in content:
        return DebugTypes.STACKOVERFLOWEXCEPTION
    elif "TypeInitializationException" in content:
        return DebugTypes.TYPEINITIALIZATIONEXCEPTION
    elif "UnauthorizedAccessException" in content:
        return DebugTypes.UNAUTHORIZEDACCESSEXCEPTION
    elif "IOException" in content:
        return DebugTypes.IOEXCEPTION
    elif "FileNotFoundException" in content:
        return DebugTypes.FILENOTFOUNDEXCEPTION
    elif "DirectoryNotFoundException" in content:
        return DebugTypes.DIRECTORYNOTFOUNDEXCEPTION
    elif "EndOfStreamException" in content:
        return DebugTypes.ENDOFSTREAMEXCEPTION
    elif "PathTooLongException" in content:
        return DebugTypes.PATHTOOLONGEXCEPTION
    elif "AssetBundleCreateRequest" in content:
        return DebugTypes.ASSETBUNDLECREATEREQUEST
    elif "AssetBundleRequest" in content:
        return DebugTypes.ASSETBUNDLEREQUEST
    elif "SceneManagementException" in content:
        return DebugTypes.SCENEMANAGEMENTEXCEPTION
    elif "EditorApplicationException" in content:
        return DebugTypes.EDITORAPPLICATIONEXCEPTION
    elif "BuildFailedException" in content:
        return DebugTypes.BUILDFAILEDEXCEPTION
    elif "Debug:LogError" in content:
        return DebugTypes.USERERRORLOG
    elif "Debug:LogWarning" in content:
        return DebugTypes.USERWARNINGLOG
    elif "Debug:Log" in content:
        return DebugTypes.USERLOG
    
    print(f"Could not find debug type at content:\n{content}")
    return DebugTypes.UNDEFINED


def NonErrors(section, logFile, freq):
    userLogSectionData = SectionData()
    newData = GetDebugLogs(section)
    if(newData is None):
        return
    userLogSectionData.debugMessage = newData.debugMessage
    userLogSectionData.scriptAndFunction = newData.scriptAndFunction
    userLogSectionData.logType = GetSectionDebugType(section)
            
    # Null reference exceptions will have the script name and function listed.
    if(userLogSectionData.logType != DebugTypes.NULLREFERENCEEXCEPTION):
        splitFunction = userLogSectionData.scriptAndFunction.split(":")
        scriptName = splitFunction[0]
        functionName = splitFunction[1]
        userLogSectionData.scriptAndFunction = functionName
        userLogSectionData.frequency = freq
        logSectionScriptFromLogAndData[scriptName + ":" + logFile] = userLogSectionData

def Errors(section, logFile, freq):
    for scriptAndFunction in GetScriptAndFunctionFromSection(section):
        splitFunction = str(scriptAndFunction).split(".")

        scriptName = splitFunction[0]
        functionName = splitFunction[1]
        for scriptToIgnore in scriptsToIgnore:
            if(scriptName == scriptToIgnore):
                continue

        logSectionData = SectionData()
        logSectionData.frequency = freq
        logSectionData.scriptAndFunction = functionName
        logSectionData.logType = GetSectionDebugType(section)
        logSectionScriptFromLogAndData[scriptName + ":" + logFile] = logSectionData
def GetColorFromLogType(logType):
    if(logType == DebugTypes.USERERRORLOG):
        return bcolors.OKBLUE
    elif(logType == DebugTypes.USERWARNINGLOG):
        return bcolors.WARNING
    elif(logType == DebugTypes.USERLOG):
        return bcolors.OKCYAN
    elif(logType is not None):
        return bcolors.FAIL
    else:
        return bcolors.ENDC
def sort_key(item):
    key, value = item
    return key.split(":")[1]
def ListToString(s):

    # initialize an empty string
    str1 = ""

    # traverse in the string
    for ele in s:
        str1 += ele

    # return string
    return str1
def StageOne():
    # Get list of valid Unity log files
    validatedUnityLogFiles = GetValidLogFiles()
    for file in validatedUnityLogFiles:
        # Get frequency of each section (Sorts out sections with less than 10 occurrences)
        for section, freq in GetFrequencyFromLogFile(file).items():
            if(freq > 6):
                Errors(section, file, freq)
                NonErrors(section, file, freq)
        

# Gets all project scripts and dirs
def StageTwo():
    for file in GetScriptsFromDir(projectAssetsFolder):
        projectScripts[os.path.basename(file.replace(".cs", ""))] = file

# Finds functions inside of scripts and match them to log files
def StageThree():
    fileName = ""
    # Remove empty script
    #logSectionScriptFromLogAndData.pop("script")

    # Sort dictionary. This is to make sure the files are ready one after another, instead of randomly switching
    sorted_dict = dict(sorted(logSectionScriptFromLogAndData.items(), key=sort_key))
    #sorted_dict = dict(sorted(logSectionScriptFromLogAndData.keys(), key=lambda key: key.split(":")[0]))

    # Loop through log file sections
    for scriptFromFile, data in sorted_dict.items():
        if(fileName != scriptFromFile.split(":")[1]):
            print(f"{bcolors.HEADER}{bcolors.UNDERLINE}Reading File: { scriptFromFile.split(":")[1] }..." + bcolors.ENDC + "\n")
            fileName = scriptFromFile.split(":")[1]
        for file, dir in projectScripts.items():
            if(dir != ""):
                if(scriptFromFile.split(":")[0] == file):
                    print(f"{bcolors.OKGREEN}Reading Script: {file}" + bcolors.ENDC + "\n") 
                    if(data.debugMessage != ""):
                        print(bcolors.ENDC + GetColorFromLogType(data.logType) + "Debug message: " + data.debugMessage + bcolors.ENDC)
                    scriptContents = GetScriptContents(dir)
                    scriptContentsString = ListToString(scriptContents)
                    print(bcolors.ENDC + GetColorFromLogType(data.logType) + "Happened at function: " + data.scriptAndFunction + bcolors.ENDC)
                    if(data.scriptAndFunction in scriptContentsString):
                        for i, lines  in enumerate(scriptContents):
                            if(lines != ""):
                                if(data.scriptAndFunction in lines):
                                    print(GetColorFromLogType(data.logType) + file + ": " + dir + " " + bcolors.ENDC + str(i + 1))
                    else:
                        print(bcolors.FAIL +"Could not find function in script from log. Usually because it is a coroutine." + bcolors.ENDC)
                    print("\n" + bcolors.ENDC + "Log type: " + str(data.logType) + "\n\n" + bcolors.ENDC + "Happened " + str(data.frequency) + " times.\n\n\n")
if __name__ == "__main__":
    StageOne()
    StageTwo()
    StageThree()