# NORD
Execution Environment:<br />
Operation System: Microsoft Windows 10, 64bit.<br />
Physical Memory (RAM)	16.0 GB. <br />
Python 3.9. <br />
PyCharm Community Edition 2021.2. <br />
Alib utility for VNE simulation.  <br />





Step 1: Download ALIB_Utility tool unzip(alib utility in par with python 2.7)  and copy to the execution drive. 
	1a. Configure the alib by following the steps mentioned in the link(https://github.com/vnep-approx/alib).
	1b. Generate the input.pickle file and save it it the P3_ALIB_MASTER\input path.
	1b. Make sure "P3_ALIB_MASTER\input" path contain  senario_RedBestel.pickle. If not, generate the substrate network senario for senario_RedBestel in folder P3_ALIB_MASTER\input and this pickle file contain substrate network information. 

Step 2: Download NORD and keep in the drive where P3_ALIB_MASTER  present. The NORD file contain all executable files related to proposed appraoch and baselines appraoches.
	topsis.py -> Main file related proposed NORD appraoch.<br />
	greedy.py -> Main file related VNE-MWF baselines.<br />
	nrm.py	  -> Main file related VNE-NRM. <br /> 
	rethinking.py -> Main file related DPGA. <br />
	nodeRankCal.py -> Main file related VNE-NTANRC-D. <br />
	pageRank.py -> Main file related VNE-NTANRC-S. <br />


Step 3: In vne_u.py,  we can set the various parameters related to Virtula network requests(VNRs).

	3a. We can set the minimum and maximum number of VMs of a VNRs in create_vne function.
	
	3b. We can set the virtual network requests demands like BandWidth(min,max), CRB(min,max), LocationX(min,max), LocationY(min,max), Delay(min,max) in vne.append function. 
	EX: (1, 5, 1, 10, 0, 100, 0, 100, 1, 4) 

	3c. Run vne_u.py after doing any modification.


Step 4: In grpah_extraction_uniform.py:

	4a. In sude the get_graphs function mention the pickle file related to substrate network generation, same is available in the folder P3_ALIB_MASTER.
	EX:
	 os.path.join(
            os.path.dirname(current),
            "P3_ALIB_MASTER",
            "input",
            "senario_RedBestel.pickle",)

	4b. In graph.parameters function  set substrate network resources like BandWidth(min,max), CRB(min,max), LocationX(min,max), LocationY(min,max), Delay(min,max). 
		Ex: (500, 1000, 200, 1000, 0, 100, 0, 100, 1, 1)

	4c. Run grpah_extraction_uniform.py after doing any modification.

Step 5: In automate.py file set the VNRs size such as [250, 500, 750, 1000] and also mnetion the number iteration need to execute for each VNRs size in the iteration variable.

Step 6: Finally run the automate.py file. After succesful running a 1_uniform.pickle file is created and it is having all input parameters realted to both substrate network and Virtual network request parameeters and final embedding results are captured in the Results.xlsx.


