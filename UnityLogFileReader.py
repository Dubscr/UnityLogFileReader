import os
# Current working directory
cwd = os.getcwd().replace("\\", "/")
logsFolder = cwd + "/unitylogs/"
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

validatedUnityLogFiles = GetValidLogFiles()

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

def GetFrequencyFromLogFile(logFile):
    definedSections = dict()
    for groupedLog in GroupList(logFile):
        if groupedLog not in definedSections.keys():
            definedSections[groupedLog] = 1
        else:
            definedSections[groupedLog] += 1
    return definedSections

for string, freq in GetFrequencyFromLogFile(validatedUnityLogFiles[1]).items():
    if(freq > 10):
            print(string + "\n" + str(freq) + "\n")