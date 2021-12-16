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


def compare_person( indi1, indi2 ):
    # return header_shown which will indicate fo there was a difference

    header_shown = False

    def show_person_header( shown ):
        if not shown:
           show_indi( indi1 )
        return True

    def compare_person_dates( shown, title, date1, date2 ):
        #print( title, date1, date2 )
        if date1:
           if date2:
              if abs( date1 - date2 ) >= change_year_threshold:
                 shown = show_person_header(shown)
                 print( title, 'difference', date1, ' vs ', date2 )
           else:
              shown = show_person_header(shown)
              print( title, 'not in tree2' )
        else:
           if date2:
              shown = show_person_header(shown)
              print( title, 'not in tree1' )
        return shown


    name1 = get_name( indi1 )
    name2 = get_name( indi2 )
    name_diff = difflib.SequenceMatcher(None, name1, name2).ratio()
    if name_diff < change_name_threshold:
       header_shown = show_person_header( header_shown )
       print( 'Name difference:', name1, ' vs ', name2 )

    for d in ['birt','deat']:
        # first check whats given in the input file
        d1 = get_a_date( indi1, d )
        d2 = get_a_date( indi2, d )
        if d1 != d2:
           # then look closer at the parsed values
           d1 = get_a_year( indi1, d )
           d2 = get_a_year( indi2, d )
           header_shown = compare_person_dates( header_shown, d, d1, d2 )

    return header_shown


first = readgedcom.read_file( sys.argv[1] )
start_first = input_to_id( sys.argv[2] )
second = readgedcom.read_file( sys.argv[3] )
start_second = input_to_id( sys.argv[4] )

if start_first not in first[readgedcom.PARSED_INDI]:
   print( 'Given key not in first tree', sys.argv[2], file=sys.stderr )
   sys.exit(1)
if start_second not in second[readgedcom.PARSED_INDI]:
   print( 'Given key not in second tree', sys.argv[4], file=sys.stderr )
   sys.exit(1)

ikey = readgedcom.PARSED_INDI

print( 'Starting with', show_indi( first[ikey][start_first] ) )
print( 'and          ', show_indi( second[ikey][start_second] ) )

# match the trees

# look at the current person
has_diff = compare_person( first[ikey][start_first], second[ikey][start_second] )
