usage: xml2slashtags.py [-h] [-s SPEAKER] [-l X] [-m MAPPING_FILE]
                        filenames [filenames ...]

Convert an XML Talbank file to slash/tag format in an alternate tagset.

positional arguments:
  filenames             Talbank XML files.

optional arguments:
  -h, --help            show this help message and exit
  -s SPEAKER, --speaker SPEAKER
                        Filter output to utterances by SPEAKER
  -l X, --label-speakers X
                        Set to 0 to remove speaker labels. defaults to 1
  -m MAPPING_FILE, --mapping-file MAPPING_FILE
                        A two-column csv file specifying the mappings between
                        the MOR and the target tagset. defaults to
			/path/to/script/dir/mor-to-larc-mapping.csv


The mapping csv file is in the following format:

MOR-PATTERN, NEWTAG

where NEWTAG is the user-defined target tag to translate to, and MOR-PATTERN is
in the following format:

  pos:feature&fusion-suffix|wordform

this mostly comes from the notation in cha files. the operators :, &, - and |
bind to the text following them, and all except for pos and |wordform may occur
multiple times. pos _must_ be specified. ordering is arbitrary for all but pos,
which must occur first.

examples of MOR-PATTERNS:

  adj - matches all words tagged as adjectives.

  v:cop&PAST&13S - matches words tagged as past tense, first/third person copular
		   verbs.

  aux|be - matches all words with stem "be" tagged as aux.


TODO:
  - allow MOR-PATTERNS lacking a pos component
  - add syntax for matching literal words

