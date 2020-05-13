# luffa.py
# by Jonathan E. Wright
#
# Save me from myself.

import sys
import os
import time
import glob
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
#from tokenize import tokenize, NUMBER, STRING, NAME, OP
import nltk

def ShowUsage( exitCode ):
    print( "LUFFA - Lua Utility For Finding Aggravations\n" )
    print( "Luffa requires you to not completely suck." )
    print( "USAGE: luffa <file name> ... [options]")
    print( "Currently there are no valid options." )
    print( "Not sucking is not optional.")
    sys.exit( exitCode )

def TokenizeFile( filename ):
#    with tokenize.open( filename ) as f:
#        return tokenize.generate_tokens( f.readline )
    with open(filename, 'r') as f:
        text = f.read()
    tokens = nltk.word_tokenize( text )
    return tokens

def IsTense( token1, token2 ):
    if ( token1[-1] == 'e' and token2[-1] == 'd' ):
        if ( token1 + 'd' == token2 ):
            return True
    elif ( token1[-1] == 'd' and token2[-1] == 'e' ):
        if ( token2 + 'd' == token1 ):
            return True
    return False

def IsPlural( token1, token2 ):
    token2p = token2 + 's'
    if ( token1 == token2p ):
        return True

    token1p = token1 + 's'
    if ( token1p == token2 ):
        return True

    return False

def AddLog( alreadyCompared, key, token ):
    if ( key in alreadyCompared ):
        log = alreadyCompared[key]
        log[token] = True
    else:
        log = { token : True }
        alreadyCompared[key] = log

def AlreadyCompared( alreadyCompared, token1, token2 ):
    if ( not token1 in alreadyCompared ):
        AddLog( alreadyCompared, token1, token2 )
        AddLog( alreadyCompared, token2, token1 )
        return False

    log = alreadyCompared[token1]
    if ( token2 in log ):
        return True
    else:
        log[token2] = True
        AddLog( alreadyCompared, token2, token1 )

    return False

def FindSimilarities( dict ):
    t0 = time.time()

    alreadyCompared = { }
    dictKeys = dict.keys()
    tokens = [ ]
    for token in dictKeys:
        tokens.append( token )

    i = 0
    for i in range( 0, len( tokens ) ):
        token1 = tokens[i]
        for j in range( i + 1, len( tokens ) ):
            token2 = tokens[j]
            if ( token1 != token2 ):
                if ( not IsPlural( token1, token2 ) and not IsTense( token1, token2 ) ):
                    if ( not AlreadyCompared( alreadyCompared, token1, token2 )):
                        #ratio = 0
                        ratio = fuzz.ratio( token1, token2 )
                        if ( ratio > 90 ):
                            print( "Token '" + token1 + "' is similar to '" + token2 + "': ratio = " + str( ratio ) )

    t1 = time.time()
    print( "FindSimilarities took " + str( t1 - t0 ) + " seconds." )

def AddFile( dict, filename ):
    startWordsInDict = len( dict )
    wordsInFile = 0

    tokens = TokenizeFile( filename )

    for token in tokens:
        wordsInFile = wordsInFile + 1
        try:
            existingVal = dict[token]
        except:
            d = { token : 0 }
            dict.update( d )
        else:
            dict[token] = existingVal + 1

    uniqueWordsAdded = len( dict ) - startWordsInDict
    print( "Parsed " + str( wordsInFile ) + " words from '" + filename + "'." )
    print( "Added " + str( uniqueWordsAdded ) + " words to dictionary." )

def AddFolder( dict, folderName, extension ):
    for path, _, files in os.walk( folderName ):
        for fileName in files:
            _, ext = os.path.splitext( fileName )
            if ( ext == extension ):
                AddFile( dict, path + "\\" + fileName )

def Main():
    print( "LUFFA version 0" )

    numParms = len( sys.argv )
    if ( numParms < 2 ):
        ShowUsage( 0 )

    dict = { }
    i = 0
    for parm in sys.argv:
        if ( i >= 1 ): # first arg is the script name
            if ( parm[0] == "-" ):
                print( "Parameter '" + parm + "' appears to be an option, of which there are none. Adding options is not an option. Omitting options is not optional." )
                ShowUsage( 1 )
            else:
                path, fileNameWithExt = os.path.split( parm )
                fileName, ext = os.path.splitext( fileNameWithExt )
                if ( '*' in fileName ):
                    AddFolder( dict, path, ext )
                else:
                    AddFile( dict, parm )
                print( "Total of " + str( len( dict ) ) + " words in dictionary." )
        i = i + 1

    FindSimilarities( dict )


if __name__ == "__main__":
    Main()
