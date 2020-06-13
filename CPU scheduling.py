#takahiry 2020/6/11
#OS homework2:CPU Scheduling

import queue
import copy

class Process() :
    def __init__(self, processID, cpuBurst, arrivalTime, priority) :
        self.processID = processID
        self.cpuBurst = cpuBurst 
        self.originalCpuBurst = cpuBurst #The cpuBurst may be modified
        self.arrivalTime = arrivalTime
        self.priority = priority 
        self.turnAroundTime = 0 
        self.waitingTime = 0 
        self.arrivaled = False 
        self.used = False 
        self.ready = False 

def readFile() :
    filename = input("Which file do you want to open?:")
    try:
        file = open(filename, 'r')
        method, timeSlice = [int(char) for char in file.readline().split()]
        file.readline() # Rid the title line

        processList = []
        while True :
            temp = file.readline().split()
            if not temp : # temp is empty
                break 
            tempProcess = Process(int(temp[0]), int(temp[1]), int(temp[2]), int(temp[3]) )
            processList.append(tempProcess)
        
    except FileNotFoundError:
        print('無法打開指定的文件!')
    finally :
        file.close()
    
    return method, timeSlice, processList, filename

def processIDBubblesort(processList) :
    length = len(processList)
    for i in range(length) :
        for j in range ( length - i - 1 ) :
            if processList[j].processID > processList[j+1].processID :
                temp = processList[j]
                processList[j] = processList[j+1]
                processList[j+1] = temp
    
    return processList
            
def insertGanttChart(ganttChart, process) :
    if process.processID < 10 :
        temp = process.processID
    else :
        temp = chr(process.processID-10+ord('A'))
    
    ganttChart.append(temp)
    return ganttChart 

def FCFS(processList) :
    ganttChart = []
    sortProcessList = arrivalBubbleSort(processList)
    currentTime = 1 
    for i in range(len(sortProcessList)) :
        currentTime += sortProcessList[i].cpuBurst
        for j in range(sortProcessList[i].cpuBurst) :
            ganttChart = insertGanttChart(ganttChart, sortProcessList[i])

        sortProcessList[i].turnAroundTime = currentTime - sortProcessList[i].arrivalTime
        sortProcessList[i].waitingTime = sortProcessList[i].turnAroundTime - sortProcessList[i].cpuBurst

    processList = processIDBubblesort(sortProcessList)

    return processList,ganttChart
    

def arrivalBubbleSort(processList) :
    length = len(processList)
    for i in range(length) :
        for j in range ( length - i - 1 ) :
            if processList[j].arrivalTime > processList[j+1].arrivalTime :
                temp = processList[j]
                processList[j] = processList[j+1]
                processList[j+1] = temp
            if processList[j].arrivalTime == processList[j+1].arrivalTime : # if the arrival time is equal, compare the ID
                if processList[j].processID > processList[j+1].processID :
                    temp = processList[j]
                    processList[j] = processList[j+1]
                    processList[j+1] = temp
    
    return processList

def writeFile(processList,filename,ganttChart) :
    filename = "output_" + filename
    try :
        file = open(filename, 'w')

        ### write Gantt Chart
        file.write("Gantt Chart\n")
        file.write("-")
        for i in range(len(ganttChart)) :
            file.write(str(ganttChart[i]))
        file.write("\n")
        ### write Gantt Chart Done

        ### write wating time and turnaround time
        file.write("Waiting Time\n")
        file.write("ID\tWaiting Time\n")
        file.write("============================\n")
        for i in range(len(processList)) :
            file.write(str(processList[i].processID))
            file.write("\t")
            file.write(str(processList[i].waitingTime))
            file.write("\n")
        file.write("============================\n")

        file.write("Turnaround Time\n")
        file.write("ID\tTurnaround Time\n")
        file.write("============================\n")
        for i in range(len(processList)) :
            file.write(str(processList[i].processID))
            file.write("\t")
            file.write(str(processList[i].turnAroundTime))
            file.write("\n")
        file.write("============================\n")
        ### write wating time and turnaround time done!
    except IOError as ex:
        print('寫入文件發生錯誤！')
    finally:
        file.close()
    print("操作完成!")

def RR(processList, timeSlice) :
    ganttChart = []
    processList = arrivalBubbleSort(processList)
    currentTime = 1 
    readyState = queue.Queue() 

    for i in range(len(processList)) :
        if ( processList[i].arrivalTime <= currentTime ) :
            if (processList[i].arrivaled == False) :
                readyState.put(processList[i])
                processList[i].arrivaled = True 

    while(readyState.empty() == False) :
        runningProcess = readyState.get()
        if runningProcess.cpuBurst > timeSlice : #Timeout
            currentTime += timeSlice
            runningProcess.cpuBurst -= timeSlice 
            for i in range(timeSlice) :
                ganttChart = insertGanttChart(ganttChart, runningProcess)
        else : #runningProcess terminated
            currentTime += runningProcess.cpuBurst
            for i in range(runningProcess.cpuBurst) :
                ganttChart = insertGanttChart(ganttChart, runningProcess)
            runningProcess.cpuBurst -= runningProcess.cpuBurst
            runningProcess.turnAroundTime = currentTime - runningProcess.arrivalTime

        for i in range(len(processList)) :
            if( processList[i].arrivalTime <= currentTime ) :
                if (processList[i].arrivaled == False) :
                    readyState.put(processList[i])
                processList[i].arrivaled = True 
        if (runningProcess.cpuBurst != 0) :
            readyState.put(runningProcess)
        else :
            for i in range(len(processList)) :
                if (processList[i].processID == runningProcess.processID) :
                    processList[i].turnAroundTime = runningProcess.turnAroundTime
                    processList[i].waitingTime = processList[i].turnAroundTime - processList[i].originalCpuBurst
    #Done, replace the processList with the right ID
    processList = processIDBubblesort(processList)
    return processList, ganttChart
        
def PSJF(processList, timeSlice) :
    ganttChart = []
    readyState = []
    processList = arrivalBubbleSort(processList)
    currentTime = 1 
    finish = False
    
    while(finish == False) :
        for i in range(len(processList)) :
            if (processList[i].arrivalTime <= currentTime) :
                if (processList[i].ready == False ) :
                    readyState.append(processList[i])
                    processList[i].ready = True
        
        temp = 0
        #determine who to use CPU
        for i in range(len(readyState)) :
            if readyState[i].cpuBurst < readyState[temp].cpuBurst : #cpuBurst short, become temp
                temp = i
            elif readyState[i].cpuBurst == readyState[temp].cpuBurst : # cpuBurst same
                if( readyState[temp].used == True and readyState[i].used == False ) : #not used, become temp
                    temp = i
                else : #all of them had used cpu or all of them didnt used 
                    if ( readyState[i].arrivalTime < readyState[temp].arrivalTime ) : #compare the arrival time
                        temp = i
                    elif ( readyState[i].arrivalTime == readyState[temp].arrivalTime ) :#same, compare the ID
                        if (readyState[i].processID < readyState[temp].processID ) :
                            temp = i
        #determined
        readyState[temp].used = True 
        finish = True 
        getOut = False 
        for i in range(readyState[temp].cpuBurst) :
            if getOut == True :
                continue

            currentTime += 1 
            readyState[temp].cpuBurst -= 1
            for j in range(len(processList)) :
                if (processList[j].arrivalTime == currentTime) :
                    if comparePriority(readyState[temp], processList[j]) :
                        finish = False 
                        getOut = True

            ganttChart = insertGanttChart(ganttChart, readyState[temp])
            if ( readyState[temp].cpuBurst == 0 ) :
                readyState[temp].turnAroundTime = currentTime - readyState[temp].arrivalTime
                readyState[temp].waitingTime = readyState[temp].turnAroundTime - readyState[temp].originalCpuBurst
                for x in range(len(processList)) :
                    if ( processList[x].processID == readyState[temp].processID ) :
                        processList[x].turnAroundTime = readyState[temp].turnAroundTime 
                        processList[x].waitingTime = readyState[temp].waitingTime
                        processList[x].cpuBurst = 0 
                readyState.pop(temp)

        for i in range(len(processList)) :
            if (processList[i].cpuBurst != 0 ) :
                finish = False   

    #Done, replace the processList with the right ID
    processList = processIDBubblesort(processList)
    return processList, ganttChart 
    

def comparePriority(temp, process) :
    if ( temp.cpuBurst > process.cpuBurst ) :
        return True

    return False

def NSJF(processList, timeSlice) :
    ganttChart = []
    readyState = []
    processList = arrivalBubbleSort(processList)
    currentTime = 1 
    finish = False
    
    while(finish == False) :
        for i in range(len(processList)) :
            if (processList[i].arrivalTime <= currentTime) :
                if (processList[i].ready == False ) :
                    readyState.append(processList[i])
                    processList[i].ready = True
        
        temp = 0
        #determine who to use CPU
        for i in range(len(readyState)) :
            if readyState[i].cpuBurst < readyState[temp].cpuBurst : #cpuBurst short, become temp
                temp = i
            elif readyState[i].cpuBurst == readyState[temp].cpuBurst : # cpuBurst same
                if ( readyState[i].arrivalTime < readyState[temp].arrivalTime ) : #compare the arrival time
                    temp = i
                elif ( readyState[i].arrivalTime == readyState[temp].arrivalTime ) :#same, compare the ID
                    if (readyState[i].processID < readyState[temp].processID ) :
                        temp = i
        #determined
        readyState[temp].used = True 
        finish = True 

        for i in range(readyState[temp].cpuBurst) :
            currentTime += 1 
            readyState[temp].cpuBurst -= 1
            ganttChart = insertGanttChart(ganttChart, readyState[temp])

            if ( readyState[temp].cpuBurst == 0 ) :
                readyState[temp].turnAroundTime = currentTime - readyState[temp].arrivalTime
                readyState[temp].waitingTime = readyState[temp].turnAroundTime - readyState[temp].originalCpuBurst
                for x in range(len(processList)) :
                    if ( processList[x].processID == readyState[temp].processID ) :
                        processList[x].turnAroundTime = readyState[temp].turnAroundTime 
                        processList[x].waitingTime = readyState[temp].waitingTime
                        processList[x].cpuBurst = 0 
                readyState.pop(temp)

        for i in range(len(processList)) :
            if (processList[i].cpuBurst != 0 ) :
                finish = False   

    #Done, replace the processList with the right ID
    processList = processIDBubblesort(processList)
    return processList, ganttChart 

def lineUp(readyState, process) :
    insert = False 
    for i in range(len(readyState)) :
        if process.priority < readyState[i].priority : #priority bigger
            readyState.insert(i,process) 
            insert = True
        elif process.priority == readyState[i].priority : # priority same, compare used
            if ( readyState[i].used == True and process.used == False ) : 
                readyState.insert(i,process)
                insert = True
            elif ( readyState[i].used == False and process.used == True ) :#if process had used,find next
                insert = False
            else : # can't have compared result
                if ( process.arrivalTime < readyState[i].arrivalTime ) :
                    readyState.insert(i,process)
                    insert = True
                elif ( process.arrivalTime == readyState[i].arrivalTime ) :
                    if ( process.processID < readyState[i].processID ) :
                        readyState.insert(i,process)
                        insert = True
    
    if ( insert == False ) :
        readyState.append(process)

    return readyState



def PP(processList, timeSlice) :
    ganttChart = []
    currentTime = 1 
    readyState = []

    for i in range(len(processList)) :
        if processList[i].arrivalTime <= currentTime :
            processList[i].ready = True 
            readyState = lineUp(readyState, processList[i])
    #initial lineup end
    while( len(readyState)!=0 ) :
        runningProcess = readyState.pop(0)
       
        if runningProcess.cpuBurst != 0 :
            terminated = False
        else :
            terminated = True

        getOut = False 
        for i in range(runningProcess.cpuBurst) :
            if getOut == True :
                continue

            runningProcess.used = True 
            currentTime += 1
            runningProcess.cpuBurst -= 1
            insertGanttChart(ganttChart, runningProcess)

            if( runningProcess.cpuBurst == 0 ) : #terminated
                for x in range(len(processList)) :
                    if (processList[x].processID == runningProcess.processID) :
                        processList[x].turnAroundTime = currentTime - processList[x].arrivalTime
                        processList[x].waitingTime = processList[x].turnAroundTime - processList[x].originalCpuBurst
                        terminated = True
                        break

            #check loot
            for j in range(len(processList)) :
                if processList[j].arrivalTime == currentTime and processList[j].ready == False : #loot occur
                    if processList[j].priority >= runningProcess.priority : #priority smaller, go to readyqueue
                            readyState = lineUp(readyState, processList[j])
                            processList[j].ready = True
                    else : #priority bigger than current running process
                        readyState.insert(0, processList[j])
                        processList[j].ready = True 
                        getOut = True
            #check loot end

        if (terminated == False ) :
            readyState = lineUp(readyState, runningProcess)


    processList = processIDBubblesort(processList)
    return processList, ganttChart

def writeFileMethod6(filename,FCFSganttChart, RRganttChart, PSJFganttChart, NSJFganttChart, PPganttChart, \
    FCFSprocessList,RRprocessList,PSFJprocessList,NSJFprocessList,PPprocessList ) :
    filename = "output_" + filename
    try :
        file = open(filename, 'w')

        ### write Gantt Chart
        file.write("==    FCFS==\n")
        file.write("-")
        for i in range(len(FCFSganttChart)) :
            file.write(str(FCFSganttChart[i]))
        file.write("\n")

        file.write("==      RR==\n")
        file.write("-")
        for i in range(len(RRganttChart)) :
            file.write(str(RRganttChart[i]))
        file.write("\n")

        file.write("==    PSJF==\n")
        file.write("-")
        for i in range(len(PSJFganttChart)) :
            file.write(str(PSJFganttChart[i]))
        file.write("\n")

        file.write("==Non-PSJF==\n")
        file.write("-")
        for i in range(len(NSJFganttChart)) :
            file.write(str(NSJFganttChart[i]))
        file.write("\n")

        file.write("== Priority==\n")
        file.write("-")
        for i in range(len(PPganttChart)) :
            file.write(str(PPganttChart[i]))
        file.write("\n")
        ### write Gantt Chart Done
        file.write("===========================================================\n")
        ### write turnAround and waiting Time
        file.write("\nWaiting Time\n")
        file.write("ID\t\tFCFS\tRR\t\tPSJF\tNPSJF\tPriority\n")
        file.write("===========================================================\n")
        for i in range(len(RRprocessList)) :
            file.write(str(RRprocessList[i].processID))
            file.write("\t\t")
            file.write(str(FCFSprocessList[i].waitingTime))
            file.write("\t\t")
            file.write(str(RRprocessList[i].waitingTime))
            file.write("\t\t")
            file.write(str(PSFJprocessList[i].waitingTime))
            file.write("\t\t")
            file.write(str(NSJFprocessList[i].waitingTime))
            file.write("\t\t")
            file.write(str(PPprocessList[i].waitingTime))
            file.write("\n")
        file.write("===========================================================\n")

        file.write("\nTurnaround Time\n")
        file.write("ID\t\tFCFS\tRR\t\tPSJF\tNPSJF\tPriority\n")
        file.write("===========================================================\n")
        for i in range(len(RRprocessList)) :
            file.write(str(RRprocessList[i].processID))
            file.write("\t\t")
            file.write(str(FCFSprocessList[i].turnAroundTime))
            file.write("\t\t")
            file.write(str(RRprocessList[i].turnAroundTime))
            file.write("\t\t")
            file.write(str(PSFJprocessList[i].turnAroundTime))
            file.write("\t\t")
            file.write(str(NSJFprocessList[i].turnAroundTime))
            file.write("\t\t")
            file.write(str(PPprocessList[i].turnAroundTime))
            file.write("\n")
        file.write("===========================================================\n")
        #### wrting end

    except IOError as ex:
        print('寫入文件發生錯誤！')
    finally:
        file.close()
    print("操作完成!")

def main() :
    method, timeSlice, processList, filename = readFile() 
    if method == 1 : 
        processList, ganttChart = FCFS(processList) # now the processList has turnAroundTime and waitingTime
        writeFile(processList,filename,ganttChart)
    elif method == 2 :
        processList, ganttChart = RR(processList,timeSlice)
        writeFile(processList,filename,ganttChart)
    elif method == 3 :
        processList, ganttChart = PSJF(processList, timeSlice)
        writeFile(processList,filename,ganttChart)
    elif method == 4 :
        processList, ganttChart = NSJF(processList, timeSlice)
        writeFile(processList, filename, ganttChart)
    elif method == 5 :
        processList, ganttChart = PP(processList, timeSlice)
        writeFile(processList, filename, ganttChart)
    elif method == 6 :
        backUpProcessList = copy.deepcopy(processList)
        FCFSprocessList, FCFSganttChart = FCFS(processList)
        processList = copy.deepcopy(backUpProcessList)
        RRprocessList, RRganttChart = RR(processList,timeSlice)
        processList = copy.deepcopy(backUpProcessList)
        PSFJprocessList, PSJFganttChart = PSJF(processList, timeSlice)
        processList = copy.deepcopy(backUpProcessList)
        NSJFprocessList, NSJFganttChart = NSJF(processList, timeSlice)
        processList = copy.deepcopy(backUpProcessList)
        PPprocessList, PPganttChart = PP(processList, timeSlice)
        writeFileMethod6(filename, FCFSganttChart, RRganttChart, PSJFganttChart, NSJFganttChart, PPganttChart, \
            FCFSprocessList,RRprocessList,PSFJprocessList,NSJFprocessList,PPprocessList )

if __name__ == '__main__' :
    main() 