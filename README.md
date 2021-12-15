# compare-trees
Compare two genealogy trees via their GEDCOM files.

When getting a tree from a cousin its tedious to compare their tree to yours when names, dates, children, etc. don't match exactly.

A discussion was initiated on the Facebook group Technology for Genealogy by Enno Borgsteede
( https://www.facebook.com/groups/techgen/posts/4657049764387623/ ) 
which peaked my interest, again, in creating a tool.

Some existing tools mentioned there:
- gedcom-cleanup: https://github.com/francoisforster/gedcom-cleanup
- Gramps: https://gramps-project.org
- TreeView: https://treeview.co.uk
- yEd: https://www.yworks.com/products/yed
- Gephi: https://gephi.org
- D3: https://observablehq.com/@d3 and https://observablehq.com/@d3/collapsible-tree

My thoughts are to have a graphical display of only differences, with branches (and individuals) highlighted for tree1 to tree2 and another display with changed branches from tree2 to tree1.
- User input to indicate a person who is the key to both trees (GEDCOM XREF id?)
- User options on the amount of variation in names and dates which constiutes a difference
- All non-changed branches pruned away
- Use an existing graphical interface for the display (such as yEd, D3.js, etc.), capable of large trees
- Collapsable branches are required in the display

A discussion is open for this project.
