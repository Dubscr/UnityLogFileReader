import os
import re
# Current working directory
thisDir = __file__.replace("\\", "/").replace(os.path.basename(__file__), "")
logsFolder = thisDir + "/unitylogs/"

logSectionScriptAndFunctions = dict(script = "", function = "")
projectAssetsFolder = "C:/Users/Owner/Desktop/Github/Default/Murder Mystery/Assets"
projectScripts = dict(script = "", dir = "")
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

# If specified subset is a valid changeset, return true
def IsValidChangeset(subset):
    if len(subset) == 12:
        return True
    else:
        return False

# If first line of log file has a valid changeset, return true
def HasValidChangeset(line):
    subsets = GetAlnumSubsets(line)
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
                firstLine = f.readline()
                if HasValidChangeset(firstLine):
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
def StageOne():
    # Get list of valid Unity log files
    validatedUnityLogFiles = GetValidLogFiles()

    # Get frequency of each section (Sorts out sections with less than 10 occurrences)
    for section, freq in GetFrequencyFromLogFile(validatedUnityLogFiles[0]).items():
        if(freq > 10):
            for scriptAndFunction in GetScriptAndFunctionFromSection(section):
                splitFunction = str(scriptAndFunction).split(".")
                scriptName = splitFunction[0]
                functionName = splitFunction[1]
                if(scriptName == "UnityEngine"):
                    continue
                logSectionScriptAndFunctions[scriptName] = functionName

# Gets all project scripts and dirs
def StageTwo():
    for file in GetScriptsFromDir(projectAssetsFolder):
        projectScripts[os.path.basename(file.replace(".cs", ""))] = file

# Finds functions inside of scripts
def StageThree():
    # Loop through log file sections
    for script, function in logSectionScriptAndFunctions.items():
        for file, dir in projectScripts.items():
            if(dir != ""):
                if(script == file):
                    for i, lines  in enumerate(GetScriptContents(dir)):
                        if(lines != ""):
                            if(function in lines):
                                print(file + ": " + dir + "\n" + str(i))

if __name__ == "__main__":
    StageOne()
    StageTwo()
    StageThree()