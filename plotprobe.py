#!/usr/bin/env python
import arrow
import numpy as np
import gzip
import glob
import sys
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

if len( sys.argv ) > 1:
    prb_id = str(sys.argv[1])

fname_pre = "./splits-feb3/atlas_firstmile_p%s.jsonf.gz" % prb_id
fname_post = "./splits-mar16/atlas_firstmile_p%s.jsonf.gz" % prb_id

preinfo = {"4": [] , "6": []}
postinfo = {"4": [] , "6": []}
#for fname in glob.glob("atlas_firstmile_0000000000*.json"):
#for fname in ["firstmile.2020-03-19.json"]:
with gzip.open(fname_pre) as inf:
    print("processing %s" % fname_pre )
    for line in inf:
        d = json.loads( line )
        #if d['prbId'] == prb_id:
        if d['prb_id'] == prb_id:
            preinfo[ d['af'] ].append( d )

with gzip.open(fname_post) as inf:
    print("processing %s" % fname_post )
    for line in inf:
        d = json.loads( line )
        #if d['prbId'] == prb_id:
        if d['prb_id'] == prb_id:
            postinfo[ d['af'] ].append( d )

for af in ('4','6'):
    infos = [preinfo, postinfo]
    if len( preinfo[ af ] ) > 0 or len( postinfo[ af ] ) > 0:
        print("plotting prb_id:%s af:%s (len signal: %s/%s)" % (prb_id,af, len( preinfo[af ] ), len( postinfo[af] ) ) )
        fig,axs = plt.subplots(nrows=5, ncols=2, figsize=[20,20])
        cutoffcalc = {} # contains vals from pre and post per hop
        m = [{},{}] # pre and postplot infos ( so m[ info_idx ]['ips'] = blah )
        for info_idx,info in enumerate( infos ):
            if len( info[ af ] ) > 0:
                m[ info_idx ] = {} ## hops
                for d in info[af]:
                    hop = int( d['hop'] )
                    m[ info_idx ].setdefault( hop , {
                        'ips': set(),
                        'tseries': {}
                    })
                    m[ info_idx ][ hop ]['ips'].update( d['ips'].split(',') ) # records the total set of IPs seen at this hop (over time!)
                    ts = arrow.get( d['tsbin'] ).timestamp
                    m[ info_idx ][ hop ]['tseries'][ts] = d['quantiles']
                for h in sorted( m[ info_idx ].keys() ):
                    tsmin = min( m[ info_idx][ h ]['tseries'].keys() )
                    tsmax = max( m[ info_idx][ h ]['tseries'].keys() ) 
                    ts = tsmin
                    matrix = []
                    while ts < tsmax:
                        if ts in m[ info_idx][ h ]['tseries']:
                            vals = m[ info_idx][ h ]['tseries'][ ts ]
                            #medians.append( vals[8] ) #TODO 5 or 4 or 6?
                            cutoffcalc.setdefault(h,[])
                            cutoffcalc[ h ].append( vals[8] )
                        else:
                            vals = [None] * 10
                        # chop off upper weirdnesses
                        ## vals = vals[:-1]
                        matrix.append( vals )
                        ts += 3600
                    m[ info_idx ][ h ]['matrix'] = matrix
        for info_idx in (0,1):
            for h in sorted( m[ info_idx ].keys() ):
                #cutoff=max(cutoffcalc[h]) ## or 80th percentile here too? ## NOTE: cutoffcalc is over both pre and post
                cutoff=np.percentile(cutoffcalc[h],80) ## 80th of the 80 percentile ...
                matrix = m[ info_idx ][h]['matrix']
                if len( matrix ) > 0:
                        #cutoff = max( medians )
                        ##print( matrix )
                        matrix = np.rot90( matrix )[::-1] # sqeeze?  ::-1 reverses ...
                        matrix = np.clip( matrix, 0, cutoff )
                        #im = axs[ h-1 ].imshow( matrix, cmap=plt.get_cmap('YlOrRd'), aspect='auto' )
                        this_ax = axs[ h-1 ][ info_idx ]
                        im = this_ax.pcolor( matrix, cmap=plt.get_cmap('YlOrRd') )
                        cbar = fig.colorbar(im, ax=this_ax, label='RTT (ms)')
                        this_ax.set_xticks(range(0, 168, 24) )
                        #axs[ h-1 ].set_xticklabels([])
                        this_ax.set_xticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
                        this_ax.set_yticks([0,5,8])
                        this_ax.set_yticklabels(['Min','Median','80Pct'] )
                        this_ax.grid(axis='x')
                        ## TODO fix logic error in ipsperhop (currently shows only the last one)
                        this_ax.set_ylabel('RTT deciles at hop %s\n(%s IPs)' % (h,len( m[ info_idx ][h]['ips'] ) ) ) # ips is a set
                #axs[ 4 ].set_xticklabels(['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])
                axs[4][info_idx].set_xlabel('hour of the day (UTC)')
        fig.suptitle("RTT profile of first hops probe %s IPv%s\n(red=high RTT)" % (prb_id,af) )
        plt.savefig("firstmile.v%s.p%s.png" % ( af, prb_id ) )
        plt.close()

'''
{"f0_":[1.1699999570846558,1.434999942779541,1.4720000028610229,1.5080000162124634,1.5729999542236328,1.6720000505447388,1.7369999885559082,1.8619999885559082,1.9579999446868896,2.1760001182556152,112.44699859619141],"tsbin":"2020-03-19 14:00:00 UTC"
'''
