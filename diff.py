import sys
import re
import metaphone
import readgedcom


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


def get_a_date( individual, name ):
    result = ''
    if name in individual['best-events']:
       best = individual['best-events'][name]
       if individual[name][best]['date']['is_known']:
          result = individual[name][best]['date']['in'].lower()
    return result


def get_dates( individual ):
    return [ get_a_date( individual, 'birt' ), get_a_date( individual, 'deat' ) ]


def show_indi( individual ):
    #print( individual )
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


def compare_children( t1_id, t1_indis, t1_fams, t2_id, t2_indis, t2_fams ):
    partners1 = list_all_partners( t1_id, t1_indis[t1_id], t1_fams )
    if partners1:
       partners2 = list_all_partners( t2_id, t2_indis[t2_id], t2_fams )
       for fam1 in partners1:
           partner1 = partners1[fam1]
           if partner1:
              name1 = get_name( t1_indis[partner1] )
              phonetic1 = metaphone.doublemetaphone( name1 )
              # find the same partner in the other tree
              for fam2 in partners2:
                  partner2 = partners2[fam2]
                  if partner2:
                     name2 = get_name( t2_indis[partner2] )
                     phonetic2 = metaphone.doublemetaphone( name2 )
                     if phonetic1 == phonetic2:
                        print( 'matched', name1, name2 )
                     else:
                        print( 'no match', name1, '=', phonetic1, 'vs', name2, '=', phonetic2 )


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

print( 'Starting with', show_indi( first[readgedcom.PARSED_INDI][start_first] ) )
print( 'and', show_indi( second[readgedcom.PARSED_INDI][start_second] ) )

# match the trees

compare_children( start_first, first[readgedcom.PARSED_INDI], first[readgedcom.PARSED_FAM], start_second, second[readgedcom.PARSED_INDI], second[readgedcom.PARSED_FAM] )

# children
# sort by their approximate string value
