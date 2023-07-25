# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 14:09:27 2023

@author: susan
"""

import spikeinterface.full as si
import spikeinterface.extractors as se
import spikeinterface.sorters as ss
import spikeinterface.exporters as sexp
import numpy as np
from probeinterface import read_prb

InFolder = "C:/Users/susan/Desktop/2023-06-04_13-47-08"
OutFolder = "C:/Users/susan/Desktop/klustatest"
Probepath ="C:/Users/susan/Desktop/klustatest"

folder_path_ntt = InFolder #"//nas-bmc1/Archive2/RAW DATA 2/HD part 2/HD199/2023-02-05_12-56-45"

# assign channel numbers, group by tetrode
tetgrouping = np.array([0,2,2,2,3,3,3,3,4,4,4,
               0,4,5,5,5,5,6,6,6,6,7,0,
               7,7,7,8,8,8,8,9,9,9,0,
               9,10,10,10,10,11,11,11,11,12,1,
               12,12,12,13,13,13,13,14,14,14,1,
               14,15,15,15,15,1,1,2])

# read bad channel list, set tetgrouping of bad channels to 16
#TO DO

# read recfile, add grouping labels
recording_ncs = se.read_neuralynx(folder_path_ntt)
recording_ncs.set_channel_groups(channel_ids = recording_ncs.get_channel_ids(),groups = tetgrouping)
all_chan_ids = recording_ncs.get_channel_ids()

# select tetrodes
for tetnum in range(16):

    tet_chan_ids = all_chan_ids[np.where(tetgrouping == tetnum)]

    if np.size(tet_chan_ids)>2:
       
        # 4-wire tetrode
        if np.size(tet_chan_ids) == 4:
           new_chans = [0,1,2,3]
           probename = "tet4_probe.prb"
       
        # 3-wire tetrode
        if np.size(tet_chan_ids) == 3:
            new_chans = [0,1,2]
            probename = "tet3_probe.prb"
       
        myprobe = read_prb(Probepath + "/" + probename)
           
        #select channels and add probe
        thistet = recording_ncs.channel_slice(tet_chan_ids, renamed_channel_ids=new_chans)
        thistet = thistet.set_probegroup(myprobe)
       
        # preprocess (needed?)
       
        # spikesort
        sorting_KL = ss.run_sorter("klusta", thistet, OutFolder + "/TT" + str(tetnum+1))

        # export to phy STILL TO TEST
        sexp.postprocessing.export_to_phy(thistet, sorting_KL, output_folder='phy_K')
