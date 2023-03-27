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
- Cytoscape: https://cytoscape.org
- D3: https://observablehq.com/@d3 and https://observablehq.com/@d3/collapsible-tree and https://gist.github.com/d3noob/9de0768412ac2ce5dbec430bb1370efe
- Dendroscope: https://uni-tuebingen.de/fakultaeten/mathematisch-naturwissenschaftliche-fakultaet/fachbereiche/informatik/lehrstuehle/algorithms-in-bioinformatics/software/dendroscope/

Other interesting visualizations
- Exploring Family Trees: https://learnforeverlearn.com/ancestors/
- d3 family tree: https://github.com/trongthanh/family-tree

My thoughts are to have a graphical display of only differences, with branches (and individuals) highlighted for tree1 to tree2 and another display with changed branches from tree2 to tree1.
- User input to indicate a person who is the key to both trees (GEDCOM XREF, REFN, EXID, etc.)
- User options on the amount of variation in names and dates which constiutes a difference
- All non-changed branches pruned away
- Use an existing graphical interface for the display (such as yEd, D3.js, etc.), capable of large trees
- Collapsable branches are required in the display. IE. don't want to invent an interface.

A discussion is open for this project.

## Installation ##

- Requires python 3.6+
- Copy diff.py
- also requires gedcom library [readgedcom.py](https://github.com/johnandrea/readgedcom)

## Usage ##

Run the program with:
```
diff.py  family1.ged  xref1  family2.ged  xref2 >1-2.out
diff.py  family2.ged  xref2  family1.ged  xref1 >2-1.out
```

where the xref is the id in each gedcom file for a person who exists in both.
So far the program only outputs a simple text report.

Also note the second run in the reverse ordering because the program is designed to only compare the first tree against the second tree.

## Options ##

--iditem=value

Specify the item to identify the tester via each tester id. Default is "xref" which is the individual
XREF value in the GEDCOM file.
Other options might be "uuid", "refn", etc. If using a GEDCOM custom event specify it as "even dot" followed by
the event name, i.e. "even.extid", "even.myreference", etc.

Names, dates, etc. shouldn't be used because they might not be unique and have complex structures.

--person-name-diff=value

For determining if two people match, by comparing the name. 
Using difflib.SequenceMatcher.ratio, giving 0=very different, 1=exactly same.
Test fails if the match is less than this value. Default 0.92

--person-date-diff=value

Also for determining if two people match, by comparing life event (birth,death) dates.
Test fails if two dates differ by more than this number of daya. Default is 400

--person-place-diff=value

Also for determining if two people match, by comparing life event places.
Similar to the name comparison. Default is 0.90

--libpath=relative-path-to-library

The directory containing the readgedcom library, relative to the . Default is ".", the same location as this program file.

## Running ##

If the gedcom library is in a parallel directory
```
diff.py --libpath=../downloads  file1  xref1  file2  xref2
```

To change the start person selection by refn id
```
diff.py --iditem=refn  file1  refn1  file2  refn2
```

To change the person matching tolerances to be much tighter
```
diff.py --person-name-diff=0.96 --person-date-diff=90  file1 xref1 file2 xref2
```

To change the person matching tolernaces to be much looser
```
diff.py --person-name-diff=0.6 --person-data-diff=800  file1 xref1 file2 xref2
```

To ignore place name differences in person matching
```
diff.py --person-place-diff=1.0  file1 xref1 file2 xref2
```
