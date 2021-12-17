#!/usr/bin/python3

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


def get_name( individual ):
    result = individual['name'][0]['value']
    if readgedcom.UNKNOWN_NAME in result:
       result = 'unknown'
    else:
       # remove any suffix after the end slash
       result = re.sub( r'/[^/]*$', '', result ).replace('/','').strip()
    return result


def get_a_year( individual, date_name ):
    # return the year (int) of the dated event, or None
    result = None
    if date_name in individual['best-events']:
       best = individual['best-events'][date_name]
       if individual[date_name][best]['date']['is_known']:
          # get the minimum date if its a range. if not a range min and max are equal
          result = individual[date_name][best]['date']['min']['year']
    return result


def get_a_date( individual, date_name ):
    # return the date as given in the input file (or an empty string),
    # which might contain before/after/etc or be a range
    # not appropriate for comparison
    result = ''
    if date_name in individual['best-events']:
       best = individual['best-events'][date_name]
       if individual[date_name][best]['date']['is_known']:
          result = individual[date_name][best]['date']['in']
    return result


def get_dates( individual ):
    # for display purposes, not for comparison
    return [ get_a_date( individual, 'birt' ), get_a_date( individual, 'deat' ) ]


def show_indi( individual ):
    # show an person's important details
    dates = get_dates(individual)
    birth = dates[0]
    death = dates[1]
    return get_name(individual) + ' (' + birth + '-' + death + ')'


def get_other_partner( indi, family ):
    result = None
    for partner in ['wife','husb']:
        if partner in family:
           partner_id = family[partner][0]
           if partner_id != indi:
              result = partner_id
    return result


def list_all_partners( indi, individual, families ):
    # return   [familyid] = partnerid
    # though partnerid might be unknown = None
    result = dict()
    if 'fams' in individual:
       for fam in individual['fams']:
           result[fam] = get_other_partner( indi, families[fam] )
    return result


def show_person_header( already_shown, indi ):
    if not already_shown:
       print( '' )
       print( show_indi( indi ) )
    return True


def get_name_match_value( n1, n2 ):
    return difflib.SequenceMatcher(None, n1, n2).ratio()


def compare_a_person( indi1, indi2 ):
    # return header_shown which will indicate fo there was a difference

    header_shown = False

    def compare_person_dates( shown, indi1, title, date1, date2 ):
        #print( title, date1, date2 )
        if date1:
           if date2:
              if abs( date1 - date2 ) >= change_year_threshold:
                 shown = show_person_header(shown,indi1)
                 print( title, 'difference', date1, ' vs ', date2 )
           else:
              shown = show_person_header(shown,indi1)
              print( title, 'not in tree2' )
        else:
           if date2:
              shown = show_person_header(shown,indi1)
              print( title, 'not in tree1' )
        return shown

    name1 = get_name( indi1 )
    name2 = get_name( indi2 )
    if get_name_match_value(name1,name2) < change_name_threshold:
       header_shown = show_person_header( header_shown, indi1 )
       print( 'Name difference:', name1, ' vs ', name2 )

    for d in ['birt','deat']:
        # first check whats given in the input file
        d1 = get_a_date( indi1, d )
        d2 = get_a_date( indi2, d )
        if d1 != d2:
           # then look closer at the parsed values
           d1 = get_a_year( indi1, d )
           d2 = get_a_year( indi2, d )
           header_shown = compare_person_dates( header_shown, indi1, d, d1, d2 )

    return header_shown


def is_same_person( indi1, indi2 ):
    # should also check on dates
    #get_name_match_value( name1, name2 ) >= change_name_threshold:
    name1 = get_name( indi1 )
    name2 = get_name( indi2 )
    return get_name_match_value( name1, name2 ) >= 0.8


def check_children( p1, people1, fams1, p2, people2, fams2 ):
    header_shown = False

    # checking all the families that person1/tree1 might share with person2/tree2
    partners1 = list_all_partners( p1, people1[p1], fams1 )
    partners2 = list_all_partners( p2, people2[p2], fams2 )

    if partners1 and partners2:
       for fam1 in partners1:
           partner1 = partners1[fam1]
           match_fam = None
           partner2 = None
           for fam2 in partners2:
               partner2 = partners2[fam2]
               if is_same_person( people1[partner1], people2[partner2] ):
                  # that is fam1/tree1 is the same as fam2/tree2
                  match_fam = fam2
                  break

           if match_fam:
              n_children1 = len( fams1[fam1]['chil'] )
              n_children2 = len( fams2[match_fam]['chil'] )

              # need to look deeper, if children details changed
              if n_children1 != n_children2:
                 name2 = get_name( people2[partner2] )
                 header_shown = show_person_header( header_shown, people1[p1] )
                 print( 'Children differ with', name2, 'from tree1 to tree2' )

    return header_shown


def check_spouses( p1, people1, fams1, p2, people2, fams2 ):
    header_shown = False

    # check all the partners that person 1 might share with person 2
    partners1 = list_all_partners( p1, people1[p1], fams1 )
    partners2 = list_all_partners( p2, people2[p2], fams2 )

    if partners1:
       if partners2:
          # need to look deeper, if partner details changed
          if len(partners1) != len(partners2):
             header_shown = show_person_header( header_shown, people1[p1] )
             print( 'Partner(s) differ from tree1 to tree2' )

       else:
          header_shown = show_person_header( header_shown, people1[p1] )
          print( 'Partner(s) removed in tree2' )
    else:
       if partners2:
          header_shown = show_person_header( header_shown, people1[p1] )
          print( 'Partner(s) added in tree2' )

    return header_shown


def check_parents( p1, people1, fams1, p2, people2, fams2 ):
    header_shown = False
    if 'famc' in people1[p1]:
       fam1 = people1[p1]['famc'][0]
       if 'famc' in people2[p2]:
          fam2 = people2[p2]['famc'][0]
          # this is going the be trouble for same sex couples
          for partner in ['wife','husb']:
              partner1 = None
              partner2 = None
              if partner in fams1[fam1]:
                 partner1 = fams1[fam1][partner]
              if partner in fams2[fam2]:
                 partner2 = fams2[fam2][partner]
              if partner1:
                 if partner2:
                    if not is_same_person( people1[partner1], people2[partner2] ):
                       header_shown = show_person_header( header_shown, people1[p1] )
                       print( 'Parent(', partner, ') different from tree1 to tree2' )
                 else:
                    header_shown = show_person_header( header_shown, people1[p1] )
                    print( 'Parent(', partner, ') removed in tree2' )
              else:
                 if partner2:
                    header_shown = show_person_header( header_shown, people1[p1] )
                    print( 'Parent(', partner, ') added in tree2' )
       else:
          header_shown = show_person_header( header_shown, people1[p1] )
          print( 'Parent(s) removed in tree2' )

    else:
      if 'famc' in people2[p2]:
         header_shown = show_person_header( header_shown, people1[p1] )
         print( 'Parent(s) added in tree2' )

    return header_shown


ikey = readgedcom.PARSED_INDI
fkey = readgedcom.PARSED_FAM

tree1 = readgedcom.read_file( sys.argv[1] )
start1 = input_to_id( sys.argv[2] )
tree2 = readgedcom.read_file( sys.argv[3] )
start2 = input_to_id( sys.argv[4] )


if start1 not in tree1[ikey]:
   print( 'Given key not in first tree', sys.argv[2], file=sys.stderr )
   sys.exit(1)
if start2 not in tree2[ikey]:
   print( 'Given key not in second tree', sys.argv[4], file=sys.stderr )
   sys.exit(1)


print( 'Starting with', show_indi( tree1[ikey][start1] ) )
print( 'and          ', show_indi( tree2[ikey][start2] ) )

# match the trees

# look at the current person
has_diff = compare_a_person( tree1[ikey][start1], tree2[ikey][start2] )

has_diff = check_spouses( start1, tree1[ikey], tree1[fkey], start2, tree2[ikey], tree2[fkey] )

has_diff = check_children( start1, tree1[ikey], tree1[fkey], start2, tree2[ikey], tree2[fkey] )

has_diff = check_parents( start1, tree1[ikey], tree1[fkey], start2, tree2[ikey], tree2[fkey] )
