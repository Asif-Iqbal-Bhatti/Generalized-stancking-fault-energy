# Stacking fault energy & Screw dislocations for bcc High Entropy Alloys [VASP, ATAT MCSQS code]

**[1] Generate Stacking fault energy & Screw dislocation for bcc crystals**

--> b is a burger vector (b = a/2[111])

GSFE = (E_fault - E_perfect)/Area

**[2] Local-lattice-distortion HEA Alloys**

Analysis of atomic mismatch for High Entropy Alloys. Various definition exists but I have chosen the one given in the paper referenced in the script. These definitions are arbitrary.

The script reads VASP POSCAR & CONTCAR file for initial and final coordinates and then analyse the ions drift from its initial position and compute the atomic mismatch.

**[3] Generating Random Structure using SQS technique**

Python script to generate BCC/FCC/HCP random structures using SQS technique. This program is the MODIFICATION of the NANOHUB code.

https://icet.materialsmodeling.org/advanced_topics/sqs_generation.html 

https://github.com/dgehringer/sqsgenerator 

https://www.brown.edu/Departments/Engineering/Labs/avdw/atat/

**[4] Code to convert file generated from MCSQS ATAT code to VASP POSCAR file.**

**[5] Monte Carlo code for generating strucutre with lower Binding energy for SQS**

**CITATION toward this work should be acknowledged in the publication.**

NB:: For generating the structure you will need to install atomsk. The link is:
https://github.com/pierrehirel/atomsk/ 
it generates POSCAR files and they can be run independently with VASP and after relaxation in the z direction
the energy can be calulated and GSFE can be plotted against normalized burger vector.
http://wolf.ifj.edu.pl/elastic/index.html
