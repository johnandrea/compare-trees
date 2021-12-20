#!/usr/bin/python3

"""
Compare two gedcom trees.
Arguments: tree1file  person1xref   tree2file  person2xref

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2021 John A. Andrea
v0.0.2
"""

import sys
import re
import difflib
import readgedcom

# comparison thresholds to determine if a person has a difference
change_name_threshold = 0.91  #worse towards zero
change_year_threshold = 2

# but need to have different thresholds to determine if its a different person


def input_to_id( s ):
    # might have been given as just a number
    # convert to id style 'i58'
    result = ''
    if s:
       result = s.replace('@','').replace('i','').replace('I','')
    return 'i' + result


def get_name( t, p ):
    result = trees[t][ikey][p]['name'][0]['value']
    if readgedcom.UNKNOWN_NAME in result:
       result = 'unknown'
    else:
       # remove any suffix after the end slash
       result = re.sub( r'/[^/]*$', '', result ).replace('/','').strip()
    return result


def get_best_date( t, p, date_name ):
    best = None
    if date_name in trees[t][ikey][p]['best-events']:
       best = trees[t][ikey][p]['best-events'][date_name]
    return best


def get_a_year( t, p, date_name ):
    # return the year (int) of the dated event, or None
    result = None
    best = get_best_date( t, p, date_name )
    if best is not None:
       if trees[t][ikey][p][date_name][best]['date']['is_known']:
          # get the minimum date if its a range. if not a range min and max are equal
          result = trees[t][ikey][p][date_name][best]['date']['min']['year']
    return result


def get_a_date( t, p, date_name ):
    # return the date as given in the input file (or an empty string),
    # which might contain before/after/etc or be a range
    # not appropriate for comparison
    result = ''
    best = get_best_date( t, p, date_name )
    if best is not None:
       if trees[t][ikey][p][date_name][best]['date']['is_known']:
          result = trees[t][ikey][p][date_name][best]['date']['in']
    return result


def get_dates( t, p ):
    # for display purposes, not for comparison
    return [ get_a_date(t, p, 'birt'), get_a_date(t, p, 'deat') ]


def show_indi( t, p ):
    # show an person's important details
    dates = get_dates(t,p)
    return get_name(t,p) + ' (' + dates[0] + '-' + dates[1] + ')'


def get_other_partner( t, p, f ):
    result = None
    for partner in ['wife','husb']:
        if partner in trees[t][fkey][f]:
           partner_id = trees[t][fkey][f][partner][0]
           if partner_id != p:
              result = partner_id
    return result


def list_all_partners( t, p ):
    # return   [familyid] = partnerid
    # though partnerid might be unknown = None
    result = dict()
    if 'fams' in trees[t][ikey][p]:
       for fam in trees[t][ikey][p]['fams']:
           result[fam] = get_other_partner( t, p, fam )
    return result


def show_person_header( t, p ):
    print( '' )
    print( show_indi( t, p ) )


def get_name_match_value( n1, n2 ):
    return difflib.SequenceMatcher(None, n1, n2).ratio()


def compare_a_person( p1, p2 ):

    def compare_person_dates( p1, title, date1, date2 ):
        #print( title, date1, date2 )
        if date1:
           if date2:
              if abs( date1 - date2 ) >= change_year_threshold:
                 show_person_header(1,p1)
                 print( title, 'difference', date1, ' vs ', date2 )
           else:
              show_person_header(1,p1)
              print( title, 'not in tree2' )
        else:
           if date2:
              show_person_header(1,p1)
              print( title, 'not in tree1' )

    name1 = get_name( 1, p1 )
    name2 = get_name( 2, p2 )
    if get_name_match_value(name1,name2) < change_name_threshold:
       show_person_header(1,p1)
       print( 'Name difference:', name1, ' vs ', name2 )

    for d in ['birt','deat']:
        # first check whats given in the input file
        d1 = get_a_date( 1, p1, d )
        d2 = get_a_date( 2, p2, d )
        if d1 != d2:
           # then look closer at the parsed values
           d1 = get_a_year( 1, p1, d )
           d2 = get_a_year( 2, p2, d )
           compare_person_dates(p1, d, d1, d2 )


def person_match_value( t1, p1, t2, p2 ):
    # should also check dates
    name1 = get_name( t1, p1 )
    name2 = get_name( t2, p2 )
    value = get_name_match_value( name1, name2 )
    print( 'debug:sameness ', value, name1, ' vs ', name2 )
    return value


def is_same_person( t1, p1, t2, p2 ):
    # for now, the match valus is a magic number
    return person_match_value( t1, p1, t2, p2 ) >= 0.8


def follow_parents( p1, p2 ):
    print( 'debug:follow parents of', get_name(1,p1) )

    def get_famc( t, p ):
        result = None
        if 'famc' in trees[t][ikey][p]:
           result = trees[t][ikey][p]['famc'][0]
        return result

    def get_partner( t, f, partner ):
        result = None
        if partner in trees[t][fkey][f]:
           result = trees[t][fkey][f][partner][0]
        return result

    fam1 = get_famc( 1, p1 )
    fam2 = get_famc( 2, p2 )

    if fam1:
       if fam2:
          # this is going the be trouble for same sex couples
          for partner in ['wife','husb']:
              partner1 = get_partner( 1, fam1, partner )
              partner2 = get_partner( 2, fam2, partner )

              if partner1:
                 if partner2:
                    if is_same_person( 1, partner1, 2, partner2 ):
                       # now what
                       print( 'debug:matched parent', partner, get_name(1,partner1) )
                       follow_person( partner1, partner2 )
                    else:
                       show_person_header( 1, p1 )
                       print( 'Parent(', partner, ') different from tree1 to tree2' )
                 else:
                    show_person_header( 1, p1 )
                    print( 'Parent(', partner, ') removed in tree2' )
              else:
                 if partner2:
                    show_person_header( 1, p1 )
                    print( 'Parent(', partner, ') added in tree2' )
       else:
          show_person_header( 1, p1 )
          print( 'Parent(s) removed in tree2' )

    else:
      if fam2:
         show_person_header( 1, p1 )
         print( 'Parent(s) added in tree2' )


def follow_children( f1, f2 ):
    print( 'debug:follow children' )

    children1 = trees[1][fkey][f1]['chil']
    children2 = trees[2][fkey][f2]['chil']
    if children1:
       if children2:
          # look harder at child details
          if len(children1) != len(children2):
             print( 'Children different from tree1 to tree2' )
       else:
         print( 'All children removed in tree2' )
    else:
       if children2:
          print( 'All children added in tree2' )


def follow_partners( p1, p2 ):
    print( 'debug:in follow partners', get_name(1,p1) )

    def max_in_matrix( m ):
        # should be a pythonic way to do this
        x = -1
        for i in m:
            for j in m[i]:
                x = max( x, m[i][j] )
        return x

    def match_partners( partners1, partners2 ):
        # make a matrix of tree1 people to tree2 people
        # in order to find the best matches

        match_values = dict()

        for fam1 in partners1:
            partner1 = partners1[fam1]
            match_values[fam1] = dict()
            for fam2 in partners2:
                partner2 = partners2[fam2]
                match_values[fam1][fam2] = person_match_value( 1, partner1, 2, partner2 )

        # find the best match for each,
        # so long as it isn't a better match for someone else

        matched1 = dict()
        matched2 = dict()

        best = max_in_matrix( match_values )

        while best >= 0.88: #magic value for now
            # where did it occur
            # there might be a pythonic way to do this
            for fam1 in partners1:
                if fam1 not in matched1:
                   for fam2 in partners2:
                       if fam2 not in matched2:
                          #print( 'compare', match_values[fam1][fam2], best )
                          if match_values[fam1][fam2] >= best:
                             match_values[fam1][fam2] = -1
                             matched1[fam1] = fam2
                             matched2[fam2] = fam1
            best = max_in_matrix( match_values )

        for fam1 in partners1:
            partner1 = partners1[fam1]
            if fam1 in matched1:
               fam2 = matched1[fam1]
               follow_person( partner1, partners2[fam2] )

               # now that families, do children
               follow_children( fam1, fam2 )

            else:
               print( 'debug:didnt match any partners', get_name(1,partner1), 'tree1 to tree2' )


    # check all the partners that person 1 might share with person 2
    partners1 = list_all_partners( 1, p1 )
    partners2 = list_all_partners( 2, p2 )

    if partners1:
       if partners2:
          match_partners( partners1, partners2 )

       else:
          show_person_header( 1, p1 )
          print( 'Partner(s) removed in tree2' )
    else:
       if partners2:
          show_person_header( 1, p1 )
          print( 'Partner(s) added in tree2' )



def follow_person( p1, p2 ):
    global visited
    if p1 in visited:
       return

    visited.append( p1 )
    print( 'debug:following person', show_indi( 1, p1 ) )
    follow_parents( p1, p2 )
    follow_partners( p1, p2 )



ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

# the tree data will be globals
trees = []
starts = []

# add an initial zero'th element so that the rest of the program uses 1 and 2
trees.append(0)
starts.append(0)

trees.append( readgedcom.read_file( sys.argv[1] ) )
starts.append( input_to_id( sys.argv[2] ) )

trees.append( readgedcom.read_file( sys.argv[3] ) )
starts.append( input_to_id( sys.argv[4] ) )

ok = True
for p in [1,2]:
    if starts[p] not in trees[p][ikey]:
       print( 'Given key', starts[p], 'not in tree', p, sys.argv[2], file=sys.stderr )
       ok = False

if not ok:
   sys.exit(1)

print( 'Starting with', show_indi( 1, starts[1] ) )
print( 'and          ', show_indi( 2, starts[2] ) )

# match the trees

# prevent double visitations of the same person
visited = []

# first, look at the start person
compare_a_person( starts[1], starts[2] )

follow_person( starts[1], starts[2] )
