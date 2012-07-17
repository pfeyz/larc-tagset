import csv
import re
import sys

from talkbank_parser.talkbank_parser import MorParser

def tagequiv_from_csv(filename):
    """ Creates a tagset equivalency list from a csv file

    args:
      `filename`: the name of the csv file to read.

    returns: a list of lists. each nested list contains a 'sparse
      mor_token' as its first element, and a pos tag as its second.
      a sparse mor token is a mor token with no required fields. a
      blank dict would count as a valid sparse token.

        [
          [{sparse-mor-token-dict}: 'rewrite-tag'],
          [{}, ''],
          ...
        ]

     the entries in filename must match the following regular
     expression: \w*?(:\w+?)*(&\w+?)*(-\w+?)(\|\w+)?,\w+?
       aka
                 pos:feature&fusion-suffix|wordform, newtag
       where all parts besides pos and |wordform can occur more than
       once, and newtag is arbitrary.

    """


    translation = []

    with open(filename) as cvsfile:
        lines = csv.reader(cvsfile)
        for pattern, newtag in lines:
            patternDict = {}
            parts = re.findall("(?:^|[:&-]|\|)\w+", pattern)
            priority = len(parts)
            patternDict['pos'] = parts[0]
            for part in parts[1:]:
                if part[0] == "|":
                    patternDict['stem'] = part[1:]
                elif part[0] == ";":
                    patternDict[''] = part[1:]
                    patternDict['wordform'] = part[1:]
                else:
                    for symbol, key in [("&","sxfx"), ("-", "sfx"),
                                        (":", "subPos")]:
                        if part[0] == symbol:
                            if key not in patternDict:
                                patternDict[key] = []
                            patternDict[key].append(part[1:])
            translation.append((priority, patternDict, newtag))

    return [i[1:3] for i in
            sorted(translation, key=lambda x: x[0], reverse=True)]

def translator(mapping):
    """ Accepts a list of tuples specifying mappings, returns a function that
    accepts a MorWord and returns a slash/tag version of it"""

    def translate(mor_word):
        for ruledict, replacement in mapping:
            for attr, expected in ruledict.iteritems():
                if mor_word.__getattribute__(attr) != expected:
                    break
            else:
                return (mor_word.word, replacement)
        return (mor_word.word, mor_word.pos)
    return translate

def main(mappingfn, corpora):
    mapping = tagequiv_from_csv(mappingfn)
    slash_tagger = translator(mapping)
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    for fn in corpora:
        try:
            for speaker, utterance in parser.parse(fn):
                print "{0}:".format(speaker),
                for morWord in utterance:
                    word, tag = slash_tagger(morWord)
                    print "{0}/{1}".format(word, tag),
                print
        except IOError, e:
            print e

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Script requires at least one xml corpus file as an argument"
    else:
        main("larc-tags.csv", sys.argv[1:])
