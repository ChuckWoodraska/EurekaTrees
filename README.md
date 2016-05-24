EurekaTrees
==============

This program was made to visualize MLLib Random Forests. Running this program with a supplied trees file generates 
visual version of the trees. You can get this from printing out the debug string of the generated model. In python that is:
`model.toDebugString()`

**Run:**<br>
`python eurekatrees.py --trees ./sample_files/trees.txt`

**If you have a csv with the names of your features you can run that command with the columns switch.**<br>
`python eurekatrees.py --trees ./sample_files/trees.txt --columns ./sample_files/columns.csv`

The output are a bunch of HTML files. If you open up the file home.html it should allow you to easily 
navigate to each of your trees.

**Example Tree:**
![Example Tree](ExampleTree.png)
