# compare-trees
Compare two genealogy trees via their GEDCOM files.

When getting a tree from a cousin its tedious to compare their tree to yours when names, dates, children, etc. don't match.

A discussion was initiated on the Facebook group Technology for Genealogy by Enno Borgsteede
( https://www.facebook.com/groups/techgen/posts/4657049764387623/ ) 
which peaked my interest, again, in creating a tool.

Some existing tools mentioned there:
- gedcom-cleanup https://github.com/francoisforster/gedcom-cleanup
- yEd https://www.yworks.com/products/yed
- Gramps https://gramps-project.org/blog/
- TreeView https://treeview.co.uk

My toughts are to have a graphical display of only differences, with branches (and individuals) highlighted for tree1 to tree2 and another display with changed branches from tree2 to tree1.
- All non-changed branches pruned away
- User options on the amount of change in names and dates which constiutes a difference
- Use an existing graphical interface as for the display (such as yEd, D3.js, etc.)
- Collapsable branches are required in the display

I will open a discussion for this project.
