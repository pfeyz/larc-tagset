#!/usr/bin/env python2

import argparse
import csv
import re
from os import path

from talkbank_parser.talkbank_parser import MorParser

here = path.dirname(path.abspath(__file__))

def split_mor_pattern(pattern):
    """ Accepts a string describing a mor tag, breaks up its parts and returns
    it as a dictionary.

    the pattern format is

      pos:feature&fusion-suffix|wordform

    >>> split_mor_pattern("pro")
    {'pos': 'pro'}
    >>> split_mor_pattern("neo|weekaweela")
    {'pos': 'neo', 'stem': 'weekaweela'}
    >>> split_mor_pattern("pro:indef-PL")
    {'sfx': ['PL'], 'pos': 'pro', 'subPos': ['indef']}

    """
    match_components = {}
    parts = re.findall("(?:^|[:&-]|\|)\w+", pattern)
    match_components['pos'] = parts[0]
    for part in parts[1:]:
        if part.startswith("|"):
            match_components['stem'] = part[1:]
            continue
        for symbol, key in [("&","sxfx"), ("-", "sfx"),
                            (":", "subPos")]:
            if part[0] == symbol:
                if key not in match_components:
                    match_components[key] = []
                match_components[key].append(part[1:])
    return match_components

def tagequiv_from_csv(filename):
    """ Creates a list of mortag-to-larctag mappings.

    args:
      `filename: the name of the csv file to read.
                 the entries in filename must match the following regular
                 expression:

                 \w*?(:\w+?)*(&\w+?)*(-\w+?)(\|\w+)?,\w+?
       aka
                 pos:feature&fusion-suffix|wordform, newtag

       where all parts besides pos and |wordform can occur more than once, and
       newtag is arbitrary.

    returns: a list of lists. each nested list contains a 'sparse mor tag' as
      its first element, and a string pos tag as its second.  a 'sparse mor tag'
      is a dict of key:value pairs for each part of a composite mor tag. a blank
      dict would count as a valid sparse mor tag, and would match anything not
      otherwise matched.

        [
          [{sparse-mor-token-dict}: 'rewrite-tag'],
          [{}, ''],
          ...
        ]
    """

    with open(filename) as cvsfile:
        lines = csv.reader(cvsfile)
        return [(split_mor_pattern(pattern), newtag)
                for (pattern, newtag) in lines]


def translator(mapping):
    """ Accepts a list of mortag-to-larctag mappings, returns a function that
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

def translate_document(corpora, mappingfn, target_speaker=None,
                       label_speakers=True):
    mapping = tagequiv_from_csv(mappingfn)
    slash_tagger = translator(mapping)
    parser = MorParser("{http://www.talkbank.org/ns/talkbank}")
    for fn in corpora:
        try:
            for speaker, utterance in parser.parse(fn):
                if target_speaker is not None and speaker != target_speaker:
                    continue
                words = [slash_tagger(morWord) for morWord in utterance]
                sent = " ".join(["{0}/{1}".format(*mw) for mw in words])
                if label_speakers:
                    yield "{0}: {1}".format(speaker, sent)
                else:
                    yield sent
        except IOError, e:
            print e

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=("Convert an XML Talkbank file to slash/tag "
                     "format in an alternate tagset"))
    parser.add_argument("filenames", nargs="+", help="Talbank XML files.")
    parser.add_argument("-s", "--speaker", metavar="SPEAKER",
                        help="Filter output to utterances by %(metavar)s")
    parser.add_argument("-l", "--label-speakers", metavar="X", default=1,
                        type=int, choices=[0, 1],
                        help=("Set to 0 to remove speaker labels. "
                              "defaults to %(default)s"))
    parser.add_argument("-m", "--mapping-file", required=False,
                        default=path.join(here, "mor-to-larc-mapping.csv"),
                        help="""A two-column csv file specifying the mappings
                                between the MOR and the target tagset. see the
                                README for more details. defaults to
                                %(default)s""")
    args = parser.parse_args()
    for line in translate_document(args.filenames, args.mapping_file,
                                   args.speaker, args.label_speakers):
        print line
