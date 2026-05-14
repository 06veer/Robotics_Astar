Flowchart Description
---------------------

1. Start
2. Initialize grid and UI
3. Wait for user input (place obstacles, start, end)
4. On SPACE: run A*
   - Initialize open set with start
   - While open set not empty:
       - Pop node with lowest f
       - If goal reached: reconstruct path
       - Else expand neighbors and update costs
5. Return path or failure
6. Animate robot along path
7. End
