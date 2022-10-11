import numpy as np

BorD = np.s_[:3] # Uncomment for Breadth 1st analysis. # Breadth 1st looks at oldest possible branch 1st.
#BorD = np.s_[-3:] # Uncomment for Depth 1st analysis. # Depth 1st looks at newest possible branch 1st.

Frontier = np.array([]) # Create the frontier list which will be the buffer for storing the branches to be explored.
TotFrontier = np.array([]) # Creates a buffer of all states to check against looping.
Initial = np.array([[1, 0, 0], [1, 0, 0], [1, 0, 0]]) # All rings located at first peg.
Solution = np.array([[0, 0, 1], [0, 0, 1], [0, 0, 1]])
complete = False
step = 0

def CheckIfValidState(NewState, Selected, F, TotFrontier): # Assumes only 1 change in ring position between states.
    # new state can not equal selected state.
    if np.array_equal(NewState,Selected): 
        #print("Not a valid state. States are the same.")
        return False
    
    # There must still be 3 rings in the new state.
    if not (np.sum(NewState)==3): 
        #print("Not a valid state. There aren't 3 rings in the state.")
        return False
    
    # new state can not equal any previous states, i.e found in current Frontier.
    FShape = TotFrontier.shape
    for i in range(0,FShape[0],3):
        F1 = [TotFrontier[:][i],TotFrontier[:][i+1],TotFrontier[:][i+2]]
        if np.array_equal(NewState,F1):
            print("Not a valid state. This state has already been found.")
            return False
    
    return True

def FindChildStates(F, Selected, step, TotFrontier):
    print("Selected State: ")
    print(Selected)
    
    CurrentLocs = np.where(Selected) # Find location of existing 1's
    ListOfLocs = list(zip(CurrentLocs[0], CurrentLocs[1]))
    for cor in ListOfLocs:
        for i in range(0,3):            
            # Check if ring moved with a ring above (blocking). If the spot above is free then we can move ring. Otherwise we can not.
            # Check if ring moved onto smaller ring. If larger ring is moved, check it doesn't land on a column with an existing smaller ring.
                
            # We'll check if we are on the first row. Nothing is above the first row so we can proceed with the swaps.
            # First row rings can not be placed on a smaller ring by definition so no check for smaller ring is needed.
            if (cor[0]==0): 
                NewState = Selected.copy() # At each iteration reset NewState to Selected
                NewState[cor] = 0 # Set the current existing 1 to 0.
                NewState[cor[0]][i] = 1

                if CheckIfValidState(NewState, Selected, F, TotFrontier):

                    print("Good New State: ")
                    print(NewState)
                    F = np.append(F,NewState,axis=0) # Add good new states to end of Frontier.
                    TotFrontier = np.append(TotFrontier,NewState,axis=0) 

            # If we are on a row deeper than the first, check the space above equals 0 before proceeding with the swaps.
            # Check for a larger ring being placed under a smaller one.
            if (cor[0]>0): 
                
                AboveSumEscape = [] # This list will be used to confirm there are no rings above the about to be moved ring.
                for r in range(0,cor[0]):
                    AboveSumEscape.append(Selected[r][cor[1]])
                
                AboveSumDrop = [] # This list will be used to confirm there are no rings above the about to be placed ring's location.
                for r in range(0,cor[0]):
                    AboveSumDrop.append(Selected[r][i])
                
                if (sum(AboveSumEscape)==0): # If space above selected ring is clear.
                    NewState = Selected.copy() # At each iteration reset NewState to Selected
                    if (sum(AboveSumDrop)==0): # If space above potential drop location is clear.
                        NewState[cor] = 0
                        NewState[cor[0]][i] = 1
                
                        if CheckIfValidState(NewState, Selected, F, TotFrontier):
                            print("Good New State: ")
                            print(NewState)
                            F = np.append(F,NewState,axis=0) # Add good new states to end of Frontier.
                            TotFrontier = np.append(TotFrontier,NewState,axis=0) 
                            

    return F, step, TotFrontier

def Breadth_DepthFirst(F, step, TotFrontier):
    
    # Checks if Frontier is out of branch states to explore.
    if ((F.size)==0):
        print("Failure. No more branches to explore and a solution has not been found.")
        complete = True
        return complete, F, step, TotFrontier
    
    # Selects a new branch state to explore.
    Selected = F[BorD] # Depending on the slice BorD (established at beginning of file) function will execute Breadth or Depth 1st.
    
    # Remove previously selected branch (cols) of F as they have been grabbed already for expansion.
    F = np.delete(F, np.s_[BorD], axis=0) # Depending on the slice BorD (established at beginning of file) function will execute Breadth or Depth 1st.

    # Check if selected state = solution.
    if np.array_equal(Selected,Solution):
        print("Success! Selected state matches solution.")
        complete = True
        return complete, F, step, TotFrontier
    
    # Expand selected state for possible branches and add them to Frontier.
    F, step, TotFrontier = FindChildStates(F, Selected, step, TotFrontier)
    
    complete = False # Make True to stop looping.
    return complete, F, step, TotFrontier
    
Frontier = TotFrontier = Initial

while not complete:
    print("Step------------ ",step)
    complete, Frontier, step, TotFrontier = Breadth_DepthFirst(Frontier, step, TotFrontier)
#     print("Frontier: ")
#     print(Frontier)
    step+=1
