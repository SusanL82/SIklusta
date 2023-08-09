# -*- coding: utf-8 -*-
import spikeinterface.full as si
import spikeinterface.extractors as se
import spikeinterface.sorters as ss
import spikeinterface.exporters as sxp
import numpy as np
from probeinterface import read_prb
from os import path, mkdir


InFolder = "C:/Users/susan/Desktop/2023-06-04_13-47-08"
OutFolder = "C:/Users/susan/Desktop/klustatest"
Probepath ="C:/Users/susan/Desktop/klustatest"
ChanList = 'KKtetlist2.txt' # text file listing good and bad channels
TetList = [1,2,3] #analyse only these tetrodes (1-based, as on drive)

folder_path_ntt = InFolder #"//nas-bmc1/Archive2/RAW DATA 2/HD part 2/HD199/2023-02-05_12-56-45"

# assign channel numbers, group by tetrode
tetgrouping = np.array([0,2,2,2,3,3,3,3,4,4,4,
               0,4,5,5,5,5,6,6,6,6,7,0,
               7,7,7,8,8,8,8,9,9,9,0,
               9,10,10,10,10,11,11,11,11,12,1,
               12,12,12,13,13,13,13,14,14,14,1,
               14,15,15,15,15,1,1,2])

# read bad channel list, set bad channels to 17
tetlist = np.loadtxt(InFolder + '/' + ChanList,
                 delimiter=",")

for tetnum in range(16):
        thistet = np.where(tetgrouping==tetnum)
        thistet = np.array(thistet)
        thesewires = tetlist[tetnum,1:5]
        badwires = np.where(thesewires==0)
        badwires = np.array(badwires)
        badchans = thistet[0][badwires]
        tetgrouping[badchans]=17
 
# read recfile, add grouping labels
recording_ncs = se.read_neuralynx(folder_path_ntt)
recording_ncs.set_channel_groups(channel_ids = recording_ncs.get_channel_ids(),groups = tetgrouping)
all_chan_ids = recording_ncs.get_channel_ids()

# select a tetrode
for tetnum in TetList:

    tet_chan_ids = all_chan_ids[np.where(tetgrouping == tetnum-1)]

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
        
        # preprocess (filter)
        thistet_f = si.bandpass_filter(thistet, freq_min=300, freq_max=6000)
        
        # spikesort (this takes forever)
        sorting_KL = ss.run_sorter("klusta", thistet_f, OutFolder + "/TT" + str(tetnum))
        #set max_possible_clusters to lower number? max_possible_clusters = 100
        
              
        #get waveforms
        waveform_folder = OutFolder +"/WF/TT"+ str(tetnum)
        we = si.extract_waveforms(
            thistet, sorting_KL, waveform_folder,
            max_spikes_per_unit=None,
            ms_before=1.5, ms_after=2.5,
            progress_bar=True)
        
        # export to phy
        if not path.isdir(OutFolder +"/phy"):
            mkdir(OutFolder +"/phy")
            
        phy_folder = OutFolder +"/phy/TT"+ str(tetnum+1)
        sxp.export_to_phy(we, output_folder=phy_folder,max_channels_per_template=4, progress_bar=True)
        
