import numpy as np
import math
import csv
import matplotlib.pyplot as plt

# --- Variables --- #

Frontier = np.array([]) # Create the frontier list which will be the buffer for storing the branches to be explored.
TotFrontier = np.array([]) # Creates a buffer of all states to check against looping.
Initial = np.array([0, 0]) # Starting location at coordinates 0,0.
Solution = np.array([10, 10]) # Goal location at coordinates 10,10.
Solution_Array = []
Solution_Parent = []
identity = 0
SolutionPath = []
complete = False
Parameter1 = np.array([0]) # Steps. Tracks the iteration the state was found, useful for cost function.
Parameter2 = np.array([0]) # Total distance traveled, used for cost function.
step = 0
ans = 0

# --- Data Entry --- #

while not (ans==1 or ans==2 or ans==3 or ans==4):
    ans = input(f'Please input the number of the algorithm to use to solve: \n[1] Breadth 1st\n[2] Depth 1st\n[3] Greedy\n[4] A* Distance\n')
    try:
        ans=int(ans)
    except:
        print('Please try again, input the number only.')

Data_List = []
try:
    with open('HW1data.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            Data_List.append(row)
except Exception as ex:
    print("Error during loading csv file", ex)

# --- Functions --- #

def Find_Parent_ID(Solution_Parent, Selected): # Search through the Solution Parent list and look up the parent id of the selected.
    for p in Solution_Parent:
        if (p[1]==Selected).all():
            Parent_ID = p[0]
            Distance = p[2]
            return Parent_ID, Distance

def Find_Parent(Solution_Array, I):
    for p in Solution_Array:
        if (p[0]==I):
            Parent = p[1]
            return Parent

def Cost_Function_Greedy(F, Parameter1):
    Cost_List = []
    P2_List = [] # Distance to Goal tracker. This is derived from F each time so no Parameter2 is needed to be passed through.
    F_Shape = F.shape
    P1_Shape = Parameter1.shape
    #print("F: ",F)
    for f in range(0,F_Shape[0],2): 
        Greed_Distance = math.sqrt((10-F[f])**2 + (10-F[f+1])**2)
        P2_List.append(Greed_Distance) # Add distance to Goal to list. Lowest distance will help identify next selection.

    for i in range(0,P1_Shape[0]): # Combine into 1 list with the different parameters weighted appropriately
        Cost_List.append(P2_List[i]) # Only using P2 for now
    Min_Value = min(Cost_List)
    Low_Loc = Cost_List.index(Min_Value) # Location of lowest scoring state in Step terms.
    Selected = np.array([F[(Low_Loc*2)],F[(Low_Loc*2+1)]])
    #print("Lowest Scoring State: ",Selected)
    return Selected, Low_Loc

def Cost_Function_A(F, Parameter1, Parameter2, Solution_Array, Solution_Parent):
    Cost_List = []
    Greed_List = [] # Distance to Goal tracker.
    P1_List = [] # Steps tracker.
    P2_List = [] # Distance traveled tracker.
    F_Shape = F.shape
    P1_Shape = Parameter1.shape
    P2_Shape = Parameter2.shape
    TotDistanceTraveled = 0
    TotDistanceTraveled_List = []
    Init = np.array([0,0])
#     print("F: ",F)
    for f in range(0,F_Shape[0],2): # Add distance to Goal to list. Lowest distance will help identify next selection.
        Greed_Distance = math.sqrt((10-F[f])**2 + (10-F[f+1])**2)
        Greed_List.append(Greed_Distance) 
    for s in range(0,P1_Shape[0]): # Add number of steps to list. Lowest step count will help identiy next selection.
        P1_List.append(Parameter1[s]) 
    for f in range(0,F_Shape[0],2): # Calculate total distance traveled for each state in the Frontier.
        TempSelected = np.array([F[f],F[f+1]])
        while not (TempSelected==Init).all():
            I, Distance = Find_Parent_ID(Solution_Parent, TempSelected)
            TempSelected = Find_Parent(Solution_Array, I)
            TotDistanceTraveled=TotDistanceTraveled+Distance # TotDistanceTraveled is all previous states sum. Need to add possible states to create P2.
        TotDistanceTraveled_List.append(TotDistanceTraveled)
    for d in range(0,P2_Shape[0]):
        P2_List.append(Parameter2[d]+TotDistanceTraveled_List[d]) # Add possible distance traveled to list. We'll use this to determine the next seletion.
    
    for i in range(0,P1_Shape[0]): # Combine into 1 list with the different parameters weighted appropriately
        Cost_List.append((Greed_List[i]+P1_List[i]+P2_List[i])) # Weighted characteristics here
#     print("Cost List", Cost_List)

    Min_Value = min(Cost_List)
    Low_Loc = Cost_List.index(Min_Value) # Location of lowest scoring state in Step terms.
    Selected = np.array([F[(Low_Loc*2)],F[(Low_Loc*2+1)]])
#     print("Lowest Scoring State: ",Selected)
    return Selected, Low_Loc

def CheckIfValidState(NewState, Selected, F, TotFrontier): # Assumes only 1 change in pitchers between states.
    # new state can not equal selected state.
    if np.array_equal(NewState,Selected): 
#         print("Not a valid state. States are the same.")
        return False

    # new state can not equal any previous states, i.e found in current Frontier.
    FShape = TotFrontier.shape
    for i in range(0,FShape[0],2):
        F1 = [TotFrontier[:][i],TotFrontier[:][i+1]]
        if np.array_equal(NewState,F1):
#             print("Not a valid state. This state has already been found.")
            return False
    return True

def Calculate_NewState(NewState, RowState): # Search through all states until one is found closer than 1.3 units from selected state.
    Distance = math.sqrt((RowState[0]-float(NewState[0]))**2 + (RowState[1]-float(NewState[1]))**2)
    if Distance<float(1.3):    
        NewState = RowState
#         print("Possible New State")
#         print(NewState)
        return True
    else:
        return False

def FindChildStates(F, Selected, step, TotFrontier, Parameter1, Parameter2, Data_List, Solution_Array, Solution_Parent, identity):
#     print("Selected State: ")
#     print(Selected)
    for row in Data_List:
        NewState = Selected.copy() # At each iteration reset NewState to Selected.
        RowState = np.array([float(row[0]),float(row[1])])
        if Calculate_NewState(NewState, RowState): # Search through all states until one is found closer than 1.3 units from selected state.
            NewState = RowState
            if CheckIfValidState(NewState, Selected, F, TotFrontier):
                Distance_To_Travel = math.sqrt((NewState[0]-Selected[0])**2 + (NewState[0]-Selected[0])**2)
#                 print("Good New State: ")
#                 print(NewState)
                F = np.append(F,NewState,axis=0) # Add good new states to end of Frontier.
                Parameter1 = np.append(Parameter1,step) # Add the step the NewState was found for the cost function selection process.
                Parameter2 = np.append(Parameter2,Distance_To_Travel) # Add the total distance traveled for the corresponding newstate.
                TotFrontier = np.append(TotFrontier,NewState,axis=0) # Collect all states to check against looping.
                Solution_Parent.append([identity, NewState, Distance_To_Travel]) # Add new states with a reference to their parent.                
    return F, step, TotFrontier, Parameter1, Parameter2, Solution_Array, Solution_Parent

def Search_Algo(F, step, TotFrontier, Parameter1, Parameter2, Data_List, Solution_Array, Solution_Parent, identity):
    Selected = 0
    
    # Checks if Frontier is out of branch states to explore.
    if ((F.size)==0):
        print("Failure. No more branches to explore and a solution has not been found.")
        complete = True
        return complete, F, step, TotFrontier, Selected, Parameter1, Parameter2, Solution_Array, Solution_Parent, identity
    
    # Selects a new branch state to explore and removes selected state from parameter tracker lists.
    if ans==1:
        Selected = F[np.s_[:2]] # Breadth 1st
        Solution_Array.append([identity, Selected]) # Save parent with its identity
        F = np.delete(F, np.s_[:2], axis=0)
        Parameter1 = np.delete(Parameter1, np.s_[:1], axis=0)
    if ans==2:
        Selected = F[np.s_[-2:]] # Depth 1st
        Solution_Array.append([identity, Selected]) # Save parent with its identity
        F = np.delete(F, np.s_[-2:], axis=0)
        Parameter1 = np.delete(Parameter1, np.s_[1:], axis=0)
    if ans==3:
        Selected, Low_Loc = Cost_Function_Greedy(F, Parameter1) # Modifies selection with greedy function.
        Solution_Array.append([identity, Selected]) # Save parent with its identity
        F = np.delete(F, 2*Low_Loc, axis=0)
        F = np.delete(F, 2*Low_Loc, axis=0)
        Parameter1 = np.delete(Parameter1, Low_Loc, axis=0)
    if ans==4:
        Selected, Low_Loc = Cost_Function_A(F, Parameter1, Parameter2, Solution_Array, Solution_Parent) # Modifies selection with A* function.
        Solution_Array.append([identity, Selected]) # Save parent with its identity
        F = np.delete(F, 2*Low_Loc, axis=0)
        F = np.delete(F, 2*Low_Loc, axis=0)
        Parameter1 = np.delete(Parameter1, Low_Loc, axis=0)
        Parameter2 = np.delete(Parameter2, Low_Loc, axis=0)

    # Check if selected state = solution.
    if np.array_equal(Selected,Solution):
        print("Success! Selected state matches solution.")
        complete = True
        return complete, F, step, TotFrontier, Selected, Parameter1, Parameter2, Solution_Array, Solution_Parent, identity
    
    # Expand selected state for possible branches and add them to Frontier.
    F, step, TotFrontier, Parameter1, Parameter2, Solution_Array, Solution_Parent = FindChildStates(F, Selected, step, TotFrontier, Parameter1, Parameter2, Data_List, Solution_Array, Solution_Parent, identity)
        
    complete = False # Make True to stop looping.
    identity+=1
    return complete, F, step, TotFrontier, Selected, Parameter1, Parameter2, Solution_Array, Solution_Parent, identity

# --- Main --- #
Frontier = TotFrontier = Initial

while not complete:
#     print("Step------------ ",step)
    complete, Frontier, step, TotFrontier, Selected, Parameter1, Parameter2, Solution_Array, Solution_Parent, identity = Search_Algo(Frontier, step, TotFrontier, Parameter1, Parameter2, Data_List, Solution_Array, Solution_Parent, identity)
    step+=1

# --- Print Outputs --- #
# print("Selected: ")
# print(Selected)
# print("Frontier: ")
# print(Frontier)
# print("Solution_Array: ")
# print(Solution_Array)
TotDistanceTraveled = 0
SolutionPath.append(Selected)
while not (Selected==Initial).all():
    I, Distance = Find_Parent_ID(Solution_Parent, Selected)
    Selected = Find_Parent(Solution_Array, I)
    SolutionPath.insert(0,Selected)
    TotDistanceTraveled=TotDistanceTraveled+Distance
print("Solution found in ",step-1," iterations, at a total distance of ",TotDistanceTraveled," traveled, and would require ",len(SolutionPath)," actions by the agent. \nSolution:")
for s in SolutionPath:
    print(s)

# --- Graphs --- #
#plt.subplot(121)
for i in range(0,len(Data_List)):
    for j in range(0,len(Data_List)):
        distance = math.sqrt((float(Data_List[i][0])-float(Data_List[j][0]))**2 + (float(Data_List[i][1])-float(Data_List[j][1]))**2)
        if distance<float(1.3):  
            XPoints = [float(Data_List[i][0]),float(Data_List[j][0])]
            YPoints = [float(Data_List[i][1]),float(Data_List[j][1])]
            plt.plot(XPoints,YPoints,)
#plt.subplot(122)
S_XPoints = np.array([])
S_YPoints = np.array([])
for p in range(0,len(SolutionPath)):
    S_XPoints = np.append(S_XPoints,SolutionPath[p][0])
    S_YPoints = np.append(S_YPoints,SolutionPath[p][1])
plt.plot(S_XPoints,S_YPoints,color="red",linewidth=3)
plt.show()