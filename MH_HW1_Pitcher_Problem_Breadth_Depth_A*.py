import numpy as np

Frontier = np.array([]) # Create the frontier list which will be the buffer for storing the branches to be explored.
TotFrontier = np.array([]) # Creates a buffer of all states to check against looping.
Initial = np.array([0, 0]) # All pitchers empty [p3, p5].
Solution = np.array([0, 4]) # P5 has 4 L of water in it.
Solution_Array = []
Solution_Parent = []
identity = 0
SolutionPath = []
complete = False
Steps = np.array([0])
Waste = np.array([0])
step = 0
WasteTemp = 0
ans = 0
while not (ans==1 or ans==2 or ans==3):
    ans = input(f'Please input the number of the algorithm to use to solve: \n[1] Breadth 1st\n[2] Depth 1st\n[3] A*\n')
    try:
        ans=int(ans)
    except:
        print('Please try again, input the number only.')
        
def Find_Parent_ID(Solution_Parent, Selected): # Search through the Solution Parent list and look up the parent id of the selected.
    for p in Solution_Parent:
        if (p[1]==Selected).all():
            Parent_ID = p[0]
            return Parent_ID

def Find_Parent(Solution_Array, I):
    for p in Solution_Array:
        if (p[0]==I):
            Parent = p[1]
            return Parent

def Cost_Steps_Fill(F, Steps, Waste):
    Cost_List = []
    Cost_List1 = []
    Cost_List2 = []
    Cost_List3 = []
    FShape = F.shape
    WShape = Waste.shape
    SShape = Steps.shape
#     print("F: ",F)
    for w in range(0,WShape[0]):
        Cost_List1.append(Waste[w]) # Add waste values to list. Lowest waste will help identify next selection.
    for s in range(0,SShape[0]):
        Cost_List2.append(Steps[s]) # Add number of steps to list. Lowest step count will help identiy next selection.
    for p in range(1,FShape[0],2): 
        Cost_List3.append(F[(p)]-4) # Add P5 values from Frontier to list. Subtract the desired goal 4 to help identify minimum (closest to 4).
    
    for i in range(0,SShape[0]):
        Cost_List.append(5*Cost_List1[i]+Cost_List2[i])
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

def Fill_Empty_Pour(NewState, i, j): # 3 options for each pitcher, fill it up completely, empty completely, pour into other pitcher.
    WasteTemp = 0
    if i==0: # If i is 0 this is the P3 pitcher, only capable of receiving 3 L or emptying 3 L or pouring contents into other.
        if j==0:
            WasteTemp = NewState[i]
            NewState[i] = 0 # Empty contents
        if j==1:
            NewState[i] = 3 # Fill completely
        if j==2:
            TempVol = NewState.copy()
            NewState[i+1] = NewState[i+1] + NewState[i] # Pour contents into next pitcher
            NewState[i] = NewState[i] - (5 - TempVol[i+1]) # Set p3 volume equal to remainder.
            if NewState[i]<0: # If filling other pitcher empties p3, set it to 0.
                NewState[i] = 0
            if NewState[i+1] > 5: # If filling other pitcher, can not exceed 5 L
                WasteTemp = NewState[i+1]-5
                NewState[i+1] = 5
    if i==1: # If i is 1 this is the P5 pitcher
        if j==0:
            WasteTemp = NewState[i]
            NewState[i] = 0 # Empty contents
        if j==1:
            NewState[i] = 5 # Fill completely
        if j==2:
            TempVol = NewState.copy()
            NewState[i-1] = NewState[i-1] + NewState[i] # Pour contents into next pitcher
            NewState[i] = NewState[i] - (3 - TempVol[i-1]) # Set p5 volume equal to remainder.
            if NewState[i]<0: # If filling other pitcher empties p5, set it to 0.
                NewState[i] = 0
            if NewState[i-1] > 3: # If filling other pitcher, can not exceed 3 L
                WasteTemp = NewState[i-1]-3
                NewState[i-1] = 3
#     print("Possible New State")
#     print(NewState)
    return NewState, WasteTemp

def FindChildStates(F, Selected, step, TotFrontier, Steps, Waste, Solution_Array, Solution_Parent, identity):
#     print("Selected State: ")
#     print(Selected)
    
    S_Shape = Selected.shape
    for i in range(0,S_Shape[0]):
        for j in range(0,3):
            NewState = Selected.copy() # At each iteration reset NewState to Selected.
            NewState, WasteTemp = Fill_Empty_Pour(NewState, i, j) # Fill, Empty, or Pour depending on j
            if CheckIfValidState(NewState, Selected, F, TotFrontier):
#                 print("Good New State: ")
#                 print(NewState)
                F = np.append(F,NewState,axis=0) # Add good new states to end of Frontier.
                Steps = np.append(Steps,step) # Add the step the NewState was found for the A* cost function selection process.
                Waste = np.append(Waste,WasteTemp) # Add the waste created when the NewState was found for the A* cost function selection process.
                TotFrontier = np.append(TotFrontier,NewState,axis=0) # Collect all states to check against looping.
                Solution_Parent.append([identity, NewState]) # Add new states with a reference to their parent.
    return F, step, TotFrontier, Steps, Waste, Solution_Array, Solution_Parent

def Breadth_Depth_First(F, step, TotFrontier, Steps, Waste, Solution_Array, Solution_Parent, identity):
    # Checks if Frontier is out of branch states to explore.
    if ((F.size)==0):
        print("Failure. No more branches to explore and a solution has not been found.")
        complete = True
        return complete, F, step, TotFrontier, Selected, Steps, Waste, Solution_Array, Solution_Parent, identity
    
    # Selects a new branch state to explore and removes selected state from F & Steps.
    if ans==1:
        Selected = F[np.s_[:2]] # Breadth 1st
        Solution_Array.append([identity, Selected]) # Save parent with its identity
        F = np.delete(F, np.s_[:2], axis=0)
        Steps = np.delete(Steps, np.s_[:1], axis=0)
    if ans==2:
        Selected = F[np.s_[-2:]] # Depth 1st
        Solution_Array.append([identity, Selected])
        F = np.delete(F, np.s_[-2:], axis=0)
        Steps = np.delete(Steps, np.s_[1:], axis=0)
    if ans==3:
        Selected, Low_Loc = Cost_Steps_Fill(F, Steps, Waste) # Modifies selection with A* cost function.
        Solution_Array.append([identity, Selected])
        F = np.delete(F, 2*Low_Loc, axis=0)
        F = np.delete(F, 2*Low_Loc, axis=0)
        Steps = np.delete(Steps, Low_Loc, axis=0)
        Waste = np.delete(Waste, Low_Loc, axis=0)
        
    # Check if selected state = solution.
    if np.array_equal(Selected,Solution):
        print("Success! Selected state matches solution.")
        complete = True
        return complete, F, step, TotFrontier, Selected, Steps, Waste, Solution_Array, Solution_Parent, identity
    
    # Expand selected state for possible branches and add them to Frontier.
    F, step, TotFrontier, Steps, Waste, Solution_Array, Solution_Parent = FindChildStates(F, Selected, step, TotFrontier, Steps, Waste, Solution_Array, Solution_Parent, identity)

    complete = False # Make True to stop looping.
    identity+=1
    return complete, F, step, TotFrontier, Selected, Steps, Waste, Solution_Array, Solution_Parent, identity
    
Frontier = TotFrontier = Initial

while not complete:
#     print("Step------------ ",step)
    complete, Frontier, step, TotFrontier, Selected, Steps, Waste, Solution_Array, Solution_Parent, identity  = Breadth_Depth_First(Frontier, step, TotFrontier, Steps, Waste, Solution_Array, Solution_Parent, identity)
#     print("Frontier: ")
#     print(Frontier)
    step+=1
# print("Selected: ")
# print(Selected)
# print("Frontier: ")
# print(Frontier)
# Gather solution
SolutionPath.append(Selected)
while not (Selected==Initial).all():
    I = Find_Parent_ID(Solution_Parent, Selected)
    Selected = Find_Parent(Solution_Array, I)
    SolutionPath.insert(0,Selected)
print("Solution found in ",step-1," iterations and would require ",len(SolutionPath)," actions by the agent. \nSolution:")
for s in SolutionPath:
    print(s)
    
