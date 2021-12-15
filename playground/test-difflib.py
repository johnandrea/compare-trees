import sys
import difflib

def run_test( s1, s2 ):
    print( '' )
    print( s1, ' vs ', s2 )
    print( difflib.SequenceMatcher(None, s1, s2).ratio() )

run_test( 'Philip Mountbatten', 'Phillip Mountbaten' )
run_test( 'Prince William Windsor', 'William Windsor' )
run_test( 'Elizabeth II', 'HRH Elizabeth Windsor' )
run_test( 'The Queen Mum', 'Elizabeth Bowes-Lyon ' )
run_test( 'Charles Philip Arthur George Windsor', 'Charles Windsor' )