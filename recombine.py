#!/usr/bin/env python
import gzip
import json
import glob

outs = {} # probe_id to file descriptor

for fname in glob.glob("./splits/atlas_first_mile_*.json"):
    print("processing %s" % fname )
    #with gzip.open(fname,'rt') as inf:
    with open(fname,'rt') as inf:
        #with open("firstmile.2020-03-19.json") as inf:
        for line in inf:
            #line = line.decode()
            line = line.rstrip('\n')
            d = json.loads( line )
            try:
                #outs.setdefault( d['prb_id'], gzip.open("atlas_firstmile_p%s.jsonf.gz" % d['prb_id'], 'w' ) )
                if not d['prb_id'] in outs:
                    newfd = open("./splits/atlas_firstmile_p%s.jsonf" % d['prb_id'], 'wt' )
                    outs[ d['prb_id'] ] = newfd
                    print( len( outs.keys() ) )
            except:
                # close 3 random ones, and open another one?
                for i in (1,2,3):
                    (prb_id,fd) = outs.popitem()
                    fd.close()
                    print("closed fd for %s" % prb_id  )
                if not d['prb_id'] in outs:
                    newfd = open("./splits/atlas_firstmile_p%s.jsonf" % d['prb_id'], 'at' )
                    outs[ d['prb_id'] ] = newfd
                    print( len( outs.keys() ) )
                #outs.setdefault( d['prb_id'], gzip.open("atlas_firstmile_p%s.jsonf.gz" % d['prb_id'], 'a' ) ) # make it append, not write! multiple gzstreams written that way ...
                #outs.setdefault( d['prb_id'], open("./splits/atlas_firstmile_p%s.jsonf" % d['prb_id'], 'at' ) )
            print >>outs[ d['prb_id'] ], line
            #outs[ d['prb_id'] ].write( json.dump(s), "\n" )
            #outs[ d['prb_id'] ].write( line )
            #print( json.dumps( d ), file=outs[ d['prb_id' ] ] )
