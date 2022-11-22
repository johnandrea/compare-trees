#!/usr/bin/python3

"""
Compare two gedcom trees.
Arguments: tree1file  person1xref   tree2file  person2xref

A person (child,partnermparent) which gets added in tree2 is not deteched,
in order to do that run the program again reversing the order of the trees.

This code is released under the MIT License: https://opensource.org/licenses/MIT
Copyright (c) 2021 John A. Andrea
v0.1.0
"""

import sys
import os
import re
import difflib
import argparse
import importlib.util


show_debug = False

# how much change for a structure/branch difference
branch_name_threshold = 0.88
branch_date_threshold = 750 #days

# how much change to report a person details difference
report_name_threshold = 0.92
report_date_threshold = 400  #days


def load_my_module( module_name, relative_path ):
    """
    Load a module in my own single .py file. Requires Python 3.6+
    Give the name of the module, not the file name.
    Give the path to the module relative to the calling program.
    Requires:
        import importlib.util
        import os
    Use like this:
        readgedcom = load_my_module( 'readgedcom', '../libs' )
        data = readgedcom.read_file( input-file )
    """
    assert isinstance( module_name, str ), 'Non-string passed as module name'
    assert isinstance( relative_path, str ), 'Non-string passed as relative path'

    file_path = os.path.dirname( os.path.realpath( __file__ ) )
    file_path += os.path.sep + relative_path
    file_path += os.path.sep + module_name + '.py'

    assert os.path.isfile( file_path ), 'Module file not found at ' + str(file_path)

    module_spec = importlib.util.spec_from_file_location( module_name, file_path )
    my_module = importlib.util.module_from_spec( module_spec )
    module_spec.loader.exec_module( my_module )

    return my_module


def get_program_options():
    results = dict()

    results['libpath'] = '.'
    results['format'] = 'text'
    results['iditem'] = 'xref'

    results['file1'] = None
    results['id1'] = None
    results['file2'] = None
    results['id2'] = None

    arg_help = 'Display gedcom differences.'
    parser = argparse.ArgumentParser( description=arg_help )

    # maybe this should be changed to have a type which better matched a directory
    arg_help = 'Location of the gedcom library. Default is current directory.'
    parser.add_argument( '--libpath', default=results['libpath'], type=str, help=arg_help )

    formats = [results['format']]
    arg_help = 'Output format. One of: ' + str(formats) + ', Default: ' + results['format']
    parser.add_argument( '--format', default=results['format'], choices=formats, type=str, help=arg_help )

    arg_help = 'How to find the person. Default is the gedcom id "xref".'
    arg_help += ' Othewise choose "exid", "refnum", etc.'
    parser.add_argument( '--iditem', default=results['iditem'], type=str, help=arg_help )

    parser.add_argument('file1', type=argparse.FileType('r') )
    parser.add_argument('id1', type=str )
    parser.add_argument('file2', type=argparse.FileType('r') )
    parser.add_argument('id2', type=str )

    args = parser.parse_args()

    results['libpath'] = args.libpath
    results['format'] = args.format.lower()
    results['iditem'] = args.iditem.lower()
    results['file1'] = args.file1.name
    results['id1'] = args.id1
    results['file2'] = args.file2.name
    results['id2'] = args.id2

    return results


def check_config( start_ok ):
    ok = start_ok

    def check_val( start_ok, wanted_type, x_name, x ):
        ok = start_ok
        if isinstance( x, wanted_type ):
           if x < 0:
              print( x_name, 'cannot be less than zero', file=sys.stderr )
              ok = False
        else:
           print( x_name, 'must be a', wanted_type, file=sys.stderr )
           ok = False
        return ok

    ok = check_val( ok, float, 'branch_name_threshold', branch_name_threshold )
    ok = check_val( ok, float, 'report_name_threshold', report_name_threshold )
    ok = check_val( ok, int,   'branch_date_threshold', branch_date_threshold )
    ok = check_val( ok, int,   'report_date_threshold', report_date_threshold )

    return ok


def days_between( d1, d2 ):
    # expecting two dates as strings yyyymmdd
    # return the approximate number of days between
    # this is only for approximate comparisons, not date manipulations
    # Assuming dates are C.E. Gregorian

    def extract_parts( date ):
        # yyyymmdd
        # 01234567
        return [ date[0:4], date[4:6], date[6:8] ]

    def total_days( date ):
        # [0]=year [1]=month [2]=day
        return int(date[0]) * 365 + int(date[1]) * 30 + int(date[2])

    parts = []
    for date in [d1, d2]:
        parts.append(extract_parts( date ))
    return abs( total_days(parts[0]) - total_days(parts[1]) )


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


def get_full_date( t, p, date_name ):
    # return the yyyymmdd value for the person's dated event, or None
    result = None
    best = get_best_date( t, p, date_name )
    if best is not None:
       if trees[t][ikey][p][date_name][best]['date']['is_known']:
          # get the minimum date if its a range. if not a range min and max are equal
          result = trees[t][ikey][p][date_name][best]['date']['min']['value']
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
    # in any given family, return the partner of the given person
    result = None
    for partner in ['wife','husb']:
        if partner in trees[t][fkey][f]:
           partner_id = trees[t][fkey][f][partner][0]
           if partner_id != p:
              result = partner_id
    return result


def list_all_partners( t, p ):
    # for the given person in all the families in which they are a partner
    # return   [family-id] = the-other-partner-id
    # though partnerid might be unknown i.e. None
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
        if date1:
           if date2:
              if days_between( date1, date2 ) >= report_date_threshold:
                 show_person_header(1,p1)
                 print( title, 'difference', date1, ' vs ', date2 )
           else:
              show_person_header(1,p1)
              print( title, 'not in second tree' )
        else:
           if date2:
              show_person_header(1,p1)
              print( title, 'not in first tree' )

    name1 = get_name( 1, p1 )
    name2 = get_name( 2, p2 )

    if get_name_match_value(name1,name2) < report_name_threshold:
       show_person_header(1,p1)
       print( 'Name difference:', name1, ' vs ', name2 )

    for d in ['birt','deat']:
        # first check whats given in the input file
        d1 = get_a_date( 1, p1, d )
        d2 = get_a_date( 2, p2, d )
        if d1 != d2:
           # then look closer at the parsed values
           d1 = get_full_date( 1, p1, d )
           d2 = get_full_date( 2, p2, d )
           compare_person_dates(p1, d, d1, d2 )


def person_match_value( t1, p1, t2, p2 ):
    # should also check dates
    name1 = get_name( t1, p1 )
    name2 = get_name( t2, p2 )
    value = get_name_match_value( name1, name2 )
    if show_debug:
       print( 'debug:sameness ', value, name1, ' vs ', name2 )
    return value


def is_same_person( t1, p1, t2, p2 ):
    return person_match_value( t1, p1, t2, p2 ) >= branch_name_threshold


def follow_parents( p1, p2 ):
    if show_debug:
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
                       # now what, check details
                       if show_debug:
                          print( 'debug:matched parent', partner, get_name(1,partner1) )
                       follow_person( partner1, partner2 )
                    else:
                       show_person_header( 1, p1 )
                       print( 'Parent(', partner, ') different from first to second' )
                 else:
                    show_person_header( 1, p1 )
                    print( 'Parent(', partner, ') removed in second' )
              else:
                 if partner2:
                    show_person_header( 1, p1 )
                    print( 'Parent(', partner, ') added in second' )
       else:
          show_person_header( 1, p1 )
          print( 'Parent(s) removed in second' )

    else:
      if fam2:
         show_person_header( 1, p1 )
         print( 'Parent(s) added in second' )


def max_in_matrix( m ):
    # should be a pythonic way to do this
    x = -1
    for i in m:
        for j in m[i]:
            x = max( x, m[i][j] )
    return x


def follow_children( p1, partner1, f1, f2 ):
    global visited_fam
    if f1 in visited_fam:
       return
    visited_fam.append(f1)

    def match_children( p1, partner_name, children1, children2 ):
        # make a matrix of matches to try gettimg the closest pairings
        match_values = dict()
        for c1 in children1:
            match_values[c1] = dict()
            for c2 in children2:
                match_values[c1][c2] = person_match_value( 1, c1, 2, c2 )

        matched1 = dict()
        matched2 = dict()

        best = max_in_matrix( match_values )

        while best >= branch_name_threshold:
            # where did it occur
            # there might be a pythonic way to do this
            for c1 in children1:
                if c1 not in matched1:
                   for c2 in children2:
                       if c2 not in matched2:
                          if match_values[c1][c2] >= best:
                             match_values[c1][c2] = -1
                             matched1[c1] = c2
                             matched2[c2] = c1
            best = max_in_matrix( match_values )

        for c1 in children1:
            if c1 in matched1:
               follow_person( c1, matched1[c1] )

            else:
               show_person_header( 1, p1 )
               print( 'with', partner_name, 'didnt match child', get_name(1,c1), 'first to second' )

    partner_name = get_name(1,partner1)

    if show_debug:
       print( 'debug:follow children', get_name(1,p1),' and ', partner_name )

    children1 = trees[1][fkey][f1]['chil']
    children2 = trees[2][fkey][f2]['chil']
    if children1:
       if children2:
          match_children( p1, partner_name, children1, children2 )

       else:
         show_person_header( 1, p1 )
         print( 'All children with',partner_name,'removed in second' )
    else:
       if children2:
          show_person_header( 1, p1 )
          print( 'All children with',partner_name,'added in second' )


def follow_partners( p1, p2 ):
    if show_debug:
       print( 'debug:in follow partners', get_name(1,p1) )

    def match_partners( p1, partners1, partners2 ):
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

        while best >= branch_name_threshold:
            # where did it occur
            # there might be a pythonic way to do this
            for fam1 in partners1:
                if fam1 not in matched1:
                   for fam2 in partners2:
                       if fam2 not in matched2:
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

               # now that families are known, do children within the family
               follow_children( p1, partner1, fam1, fam2 )

            else:
               show_person_header( 1, p1 )
               print( 'Didnt match partner', get_name(1,partner1), 'first to second' )


    # check all the partners that person 1 might share with person 2
    partners1 = list_all_partners( 1, p1 )
    partners2 = list_all_partners( 2, p2 )

    if partners1:
       if partners2:
          match_partners( p1, partners1, partners2 )

       else:
          show_person_header( 1, p1 )
          print( 'Partner(s) removed in second' )
    else:
       if partners2:
          show_person_header( 1, p1 )
          print( 'Partner(s) added in second' )



def follow_person( p1, p2 ):
    global visited
    if p1 in visited:
       return
    visited.append( p1 )

    if show_debug:
       print( 'debug:following person', show_indi( 1, p1 ) )

    compare_a_person( p1, p2 )

    follow_parents( p1, p2 )
    follow_partners( p1, p2 )


# the tree data will be globals
trees = []
starts = []
file_names = []

# add an initial zero'th element so that the rest of the program uses 1 and 2
trees.append(0)
starts.append(0)
file_names.append(0)

options = get_program_options()

if not os.path.isdir( options['libpath'] ):
   print( 'Path to readgedcom is not a directory', file=sys.stderr )
   sys.exit( 1 )

readgedcom = load_my_module( 'readgedcom', options['libpath'] )

ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

file_names.append( options['file1'] )
starts.append( options['id1'] )
file_names.append( options['file2'] )
starts.append( options['id2'] )

ok = True

# not good for o/s with significant case files
if file_names[1].lower() == file_names[2].lower():
   print( 'Identical files', file=sys.stderr )
   sys.exit(1)

# this will cause exit if the input data is very bad
for i in [1,2]:
    trees.append( readgedcom.read_file( file_names[i] ) )

print( 'Starting points' )
for i in [1,2]:
    if isinstance( trees[i], dict ) and ikey in trees[i]:
       selected = readgedcom.find_individuals( trees[i], options['iditem'], starts[i] )
       n = len(selected)
       if n == 1:
          starts[i] = selected[0]
          print( i, '=', show_indi( i, starts[i] ) )
       else:
          ok = False
          mess = 'Given person id ' + str(starts[i]) + ' '
          if n < 1:
             mess += 'not in tree:'
          else:
             mess += 'matched more than 1 person:'
          print( mess, file_names[i], file=sys.stderr )
    else:
       print( 'Tree', i, 'not fully parsed data:', file_names[i], file=sys.stderr )
       ok = False

ok = check_config( ok )

if not ok:
   sys.exit(1)

# match the trees

# prevent double visitations of the same person
visited = []
visited_fam = []

follow_person( starts[1], starts[2] )
