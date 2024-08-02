import os
import re
from enum import Enum
import tkinter as tk
from tkinter import ttk
class DebugTypes(Enum):
    UNDEFINED = 0
    NULLREFERENCEEXCEPTION = 1
    USERERRORLOG = 2
    USERWARNINGLOG = 3
    USERLOG = 4
class SectionData(object):
    logFile = ""
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

logSectionScriptAndData = dict(script = str(), selectionData = SectionData)
projectAssetsFolder = "C:/Users/Owner/Desktop/Github/Default/Untitled-Ghost-Game/Assets"
projectScripts = dict(script = str(), dir = str())

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
            data.debugMessage = lines[i - 2]
            if(len(lines) > i + 1):
                data.scriptAndFunction = str(re.search(r'\b\w+:\w+\b(?=\(.*?\))', lines[i+1]).group(0))
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
        
def GetSectionDebugType(content = ""):
    if(content == ""):
        return DebugTypes.UNDEFINED    
    if("NullReferenceException" in content):
        return DebugTypes.NULLREFERENCEEXCEPTION
    elif("Debug:LogError" in content):
        return DebugTypes.USERERRORLOG
    elif("Debug:LogWarning" in content):
        return DebugTypes.USERWARNINGLOG
    elif("Debug:Log" in content):
        return DebugTypes.USERLOG
    return DebugTypes.UNDEFINED

def NonErrors(section, logFile, freq):
    userLogSectionData = SectionData()
    userLogSectionData = GetDebugLogs(section)
    if(userLogSectionData == None):
        return
    userLogSectionData.logType = GetSectionDebugType(section)
            
    # Null reference exceptions will have the script name and function listed.
    if(userLogSectionData.logType != DebugTypes.NULLREFERENCEEXCEPTION):
        splitFunction = userLogSectionData.scriptAndFunction.split(":")
        scriptName = splitFunction[0]
        functionName = splitFunction[1]
        userLogSectionData.scriptAndFunction = functionName 
        userLogSectionData.logFile = logFile
        userLogSectionData.frequency = freq
        logSectionScriptAndData[scriptName] = userLogSectionData

def Errors(section, logFile, freq):
    for scriptAndFunction in GetScriptAndFunctionFromSection(section):
        splitFunction = str(scriptAndFunction).split(".")

        scriptName = splitFunction[0]
        functionName = splitFunction[1]

        if(scriptName == "UnityEngine"):
            continue

        logSectionData = SectionData()
        logSectionData.frequency = freq
        logSectionData.scriptAndFunction = functionName
        logSectionData.logType = GetSectionDebugType(section)
        logSectionData.logFile = logFile
        logSectionScriptAndData[scriptName] = logSectionData
def GetColorFromLogType(logType):
    if(logType == DebugTypes.NULLREFERENCEEXCEPTION):
        return bcolors.FAIL
    elif(logType == DebugTypes.USERERRORLOG):
        return bcolors.OKBLUE
    elif(logType == DebugTypes.USERWARNINGLOG):
        return bcolors.WARNING
    elif(logType == DebugTypes.USERLOG):
        return bcolors.OKCYAN
    else:
        return bcolors.ENDC

def StageOne():
    # Get list of valid Unity log files
    validatedUnityLogFiles = GetValidLogFiles()
    for file in validatedUnityLogFiles:
        # Get frequency of each section (Sorts out sections with less than 10 occurrences)
        for section, freq in GetFrequencyFromLogFile(file).items():
            print(section + "\n" + "\n")
            if(freq > 10):
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
    logSectionScriptAndData.pop("script")

    # Sort dictionary. This is to make sure the files are ready one after another, instead of randomly switching
    sorted_dict = dict(sorted(logSectionScriptAndData.items(), key=lambda item: item[1].logFile))

    # Loop through log file sections
    for script, data in sorted_dict.items():
        if(fileName != data.logFile):
            print(f"{bcolors.HEADER}{bcolors.UNDERLINE}Reading File: { data.logFile }..." + bcolors.ENDC + "\n")
            fileName = data.logFile
        for file, dir in projectScripts.items():
            if(dir != ""):
                if(script == file):
                    print(f"{bcolors.OKGREEN}Reading Script: {file}" + bcolors.ENDC + "\n") 
                    for i, lines  in enumerate(GetScriptContents(dir)):
                        if(lines != ""):
                            if(data.scriptAndFunction in lines):
                                if(data.debugMessage != ""):
                                    print(GetColorFromLogType(data.logType) + "User debug message: " + data.debugMessage)
                                print(GetColorFromLogType(data.logType) + file + ": " + dir + " " + str(i + 1) + "\n" + "Log type: " + str(data.logType) + "\n" + bcolors.ENDC)
                    print("Happened " + str(data.frequency) + " times.\n\n\n")
if __name__ == "__main__":
    StageOne()
    StageTwo()
    StageThree()