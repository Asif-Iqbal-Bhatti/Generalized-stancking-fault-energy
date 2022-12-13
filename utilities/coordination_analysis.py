#!/usr/bin/env python3

'''
############################################################################
# USAGE  :: python3 coordination_analysis.py sys.argv[1] sys.argv[2]
# Author :: Asif Iqbal -> AIB_EM2R
# DATED  :: 10/11/2020
# NB     :: POSCAR can be in Cartesian/Direct coordinates.
# Remember the counting starts from Zero in Ovito and python.
# Calculate the coordination around the dislocation line and
# count the number and type of atoms within the cutoff radius.
# Two geometries are implemented: Spherical and Cylindrical.
# This code reads the POSCAR file with atomic types appended to the last line.
############################################################################
'''

import numpy as np
import os, sys, random, subprocess, shutil, math
from scipy import stats 
from matplotlib import pyplot as plt
from collections import Counter
from termcolor import colored
from pathlib import Path

# Site index and cutoff radius
rcutoff = float(sys.argv[1]);

def read_POSCAR():
	pos = []
	P_LV1 = []
	P_LV2 = []
	P_LV3 = []
	sum = 0;
	if Path('POSCAR_perfect').is_file():
		with open('POSCAR_perfect','r') as file:
			firstline  = file.readline() # IGNORE first line comment
			alat       = float( file.readline() )# scale
			P1    = file.readline().split()
			P2    = file.readline().split()
			P3    = file.readline().split()
			P_LV1.extend(float(ai) for ai in P1);
			P_LV2.extend(float(bi) for bi in P2);
			P_LV3.extend(float(ci) for ci in P3);
			elementtype= file.readline()
			atomtypes  = file.readline()
			Coordtype  = file.readline().split()
			nat = [int(i) for i in atomtypes.split()]
			for i in nat: sum = sum + i; n_atoms = sum
			Mp = np.transpose( [P_LV1,P_LV2,P_LV3] )
			for _ in range(int(n_atoms)):
				coord = file.readline().split()
							# SWITCHING IF "DIRECT" COORDINATE IS DETECTED
				if Coordtype[0] in ["Direct", "direct"]:
					Xp = float(coord[0]); Yp = float(coord[1]); Zp = float(coord[2])
					Dp = [Xp, Yp, Zp];
					Sp = np.dot(Mp, Dp);	
					pos.append( [ Sp[0], Sp[1], Sp[2], coord[3] ] )
				else:
					pos = pos + [coord] 
					#                      !!! TURN THIS ON IF YOU WANT A FILE IN XYZ FORMAT !!!
					#for j in range( len( elementtype.split() )):
					#	dict[elementtype.split()[j]] =  atomtypes.split()[j]; 
					#for l in dict:
					#	for k in range( int(dict[l]) ):
					#		#print( elementtype.split()[ math.floor( k/int(atomtypes.split()[0] ) ) ], pos[k][:] )
					#		print( l, pos[g][:] )
					#		g +=1
	else:
		print ("File not exist")
	return n_atoms,pos,firstline,alat,P_LV1,P_LV2,P_LV3,elementtype,atomtypes,Coordtype

# THIS function is redundant
def read_CONTCAR():
	C_pos = []
	sum = 0
	C_LV1 = []
	C_LV2 = []
	C_LV3 = []
	with open('CONTCAR','r') as inpfile:
		C_comment  = inpfile.readline() # IGNORE first line comment
		C_alat       = float( inpfile.readline() )# scale
		C1 = inpfile.readline().split();
		C2 = inpfile.readline().split();
		C3 = inpfile.readline().split();
		C_LV1.extend(float(ai) for ai in C1)
		C_LV2.extend(float(bi) for bi in C2)
		C_LV3.extend(float(ci) for ci in C3)
		C_elemtype   = inpfile.readline()
		C_atomtypes  = inpfile.readline()
		C_Coordtype  = inpfile.readline().split()
		#if (Coordtype[0] == 'Direct' or Coordtype[0] == 'direct'): exit("Convert to Cartesian, first!")	
		C_nat = [int(i) for i in C_atomtypes.split()]
		for i in C_nat: sum = sum + i; C_atoms = sum
		C_pos.extend(
			[str(i) for i in inpfile.readline().rstrip(" ").split()[:3]]
			for _ in range(int(C_atoms))
		)

		C_pos = [ [float(C_pos[j][i]) for i in range(3)] for j in range(C_atoms) ]
	return C_atoms,C_pos,C_comment,C_alat,C_LV1,C_LV2,C_LV3,C_elemtype,C_atomtypes,C_Coordtype
	
def coordination_analysis_single_supercell(n_atoms, pos):
	# First select the atom around which to measure the coordination.
	# I've used (x-x0)**2 + (y-y0)**2 + (z-z0)**2 < R**2; (r-r0)**2 < R**2
	cnt = 0
	bar_graph = [];
	for x in range(int(n_atoms)):
		i = float(pos[x][0]) - float(pos[r0][0]) 
		j = float(pos[x][1]) - float(pos[r0][1]) 
		k = float(pos[x][2]) - float(pos[r0][2]) 
		if ( ( i*i + j*j + k*k ) <= rcutoff**2 ): #FILTER
			cnt +=1; bar_graph.append( pos[x][3] )	
			print ( "{:4d} {}".format(x,pos[x][:]) )
	print(f"Coordination # {cnt}")
	element_counts = Counter(bar_graph)
	return element_counts, bar_graph

def replicate_cell(pos,n_atoms,Latvec1,Latvec2,Latvec3):
	# KEEP THESE SETTINGS FIXED !!!
	Nx,Ny,Nz = 2,2,2; mag_atoms_pos=[]; atm_pos=[]; atm_typ=[]; six=[]; sev=[];
	Latvec1  = [ float(Latvec1[0]), float(Latvec1[1]), float(Latvec1[2]) ]
	Latvec2  = [ float(Latvec2[0]), float(Latvec2[1]), float(Latvec2[2]) ]
	Latvec3  = [ float(Latvec3[0]), float(Latvec3[1]), float(Latvec3[2]) ]
	Latvect  = np.array( [Latvec1[:], Latvec2[:], Latvec3[:]] )
	for l in range(n_atoms):
		atm_pos.append( [float(pos[l][0]), float(pos[l][1]), float(pos[l][2]), pos[l][3] ] )	
		
# Creating First and Second layer		
	for i in range(0,Nx,1):            
		for j in range(0,Ny,1):
			for k in range(0,Nz,1): 
				for l in atm_pos:	
					cartesian_basis = np.inner(Latvect.T, np.array( [i,j,k] ) )				
					mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
					atm_typ.append( l[3:4] )	
				six.append(elementtype )
				sev.append(atomtypes)			

	for i in range(-int(Nx/2),np.mod(Nx,2),1):   
		for k in range(0,Nz,1):   
			for l in atm_pos:	
				cartesian_basis = np.inner(Latvect.T, np.array( [i,0,k] ) )				
				mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
				atm_typ.append( l[3:4] )	
			six.append(elementtype)
			sev.append(atomtypes)	

	for j in range(-int(Ny/2),np.mod(Ny,2),1):            
		for k in range(0,Nz,1):   
			for l in atm_pos:	
				cartesian_basis = np.inner(Latvect.T, np.array( [0,j,k] ) )				
				mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
				atm_typ.append( l[3:4] )	
			six.append(elementtype)
			sev.append(atomtypes)

	for k in range(0,Nz,1):   
		for l in atm_pos:	
			cartesian_basis = np.inner(Latvect.T, np.array( [-1,-1,k] ) )				
			mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
			atm_typ.append( l[3:4] )	
		six.append(elementtype)
		sev.append(atomtypes)
		
	for k in range(0,Nz,1):   
		for l in atm_pos:	
			cartesian_basis = np.inner(Latvect.T, np.array( [+1,-1,k] ) )				
			mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
			atm_typ.append( l[3:4] )	
		six.append(elementtype)
		sev.append(atomtypes)
		
	for k in range(0,Nz,1):   
		for l in atm_pos:	
			cartesian_basis = np.inner(Latvect.T, np.array( [-1,+1,k] ) )				
			mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
			atm_typ.append( l[3:4] )	
		six.append(elementtype)
		sev.append(atomtypes)
		
# Creating Third layer
	for i in range(-int(Nx/2),Nx,1):            
		for j in range(-int(Ny/2),Ny,1):
			for k in range(-int(Nz/2),np.mod(Nz,2),1): 
				for l in atm_pos:	
					cartesian_basis = np.inner(Latvect.T, np.array( [i,j,k] ) )				
					mag_atoms_pos.append( cartesian_basis + l[0:3] ) 	
					atm_typ.append( l[3:4] )	
				six.append(elementtype)
				sev.append(atomtypes)			

	###	WRITING TO A FILE for DEBUGGING ONLY
	Nx,Ny,Nz = 1,1,1
	ff = open("POSCAR_222", 'w')
	ff.write("POSCAR_{}x{}x{}\n".format(Nx,Ny,Nz))
	ff.write("1.0\n")
	ff.write("{:9.7f} {:9.7f} {:9.7f}\n".format(Nx*Latvec1[0], Ny*Latvec1[1], Nz*Latvec1[2] ) )
	ff.write("{:9.7f} {:9.7f} {:9.7f}\n".format(Nx*Latvec2[0], Ny*Latvec2[1], Nz*Latvec2[2] ) )
	ff.write("{:9.7f} {:9.7f} {:9.7f}\n".format(Nx*Latvec3[0], Ny*Latvec3[1], Nz*Latvec3[2] ) )			
	for i in six[:]:
		ff.write( "{}".format(str(i).rstrip("\n")) )	
	ff.write("\n")	
	for i in sev[:]:
		ff.write( "{}".format( i.rstrip("\n") ) )
	ff.write("\nCartesian\n")
	for g in range(len(mag_atoms_pos)):
		ff.write( "{:12.7f} {:12.7f} {:12.7f}\n" .format(mag_atoms_pos[g][0], mag_atoms_pos[g][1], mag_atoms_pos[g][2] ))
	ff.close()
	
	return  mag_atoms_pos, atm_typ

def coordination_analysis_spherical_shell(n_atoms, pos, atm_typ):
	# First select the atom around which to measure the coordination.
	# I've used (x-x0)**2 + (y-y0)**2 + (z-z0)**2 < R**2; 
	# (r-r0)**2 < R**2
	cnt = 0; bar_graph = []; t = 0; writ_graph = []
	hh = open("coord.dat", "w")
	
	r0 = 213
	# centering the atom in the Original supercell
	for q in range(n_atoms): 
		#if (atm_typ[np.mod(q,n_atoms)][0] == "Hf" ): # FILTERING only Nb !!!
			hh.write("{:3d} {}\t".format(q, atm_typ[q][0] ))
			for x in range(0, len(pos), 1): # q > x
				i = float(pos[x][0]) - float(pos[q][0]) 
				j = float(pos[x][1]) - float(pos[q][1]) 
				k = float(pos[x][2]) - float(pos[q][2]) 
				if ( ( i*i + j*j + k*k ) <= rcutoff * rcutoff ): # FILTER !!!
					if ( x != q ): # NOTE: an atom is *never* counted as its own neighbor
						cnt +=1; 
						bar_graph.append( atm_typ[np.mod(x,n_atoms)][0] ); 
						writ_graph.append( atm_typ[np.mod(x,n_atoms)][0] );
						# TURN this ON if atom positions are required
						#print("{:3d} {:4d} {} {}".format( cnt, np.mod(x,n_atoms), pos[x][:], atm_typ[x][0] ))
			elem_counts = Counter( writ_graph );	
			hh.write("{}\n".format( sorted(elem_counts.items()) ) )
			writ_graph = []
	
	print("{:_^50}".format("*"))	
	print("Neighbors around r0=[{},{}] are {} within {} radius (n=1)". \
	format( atm_typ[r0][0], r0, cnt, rcutoff ) );
	element_counts = Counter(bar_graph); 
	print ( element_counts.items() );

	# Calculating the probability of pairs within a cutoff radius & summing over all the atoms
	for k, v in element_counts.items():
		p = v/(1*sum(element_counts.values()));
		t = p + t; # Total probability should equal to 1
		print("P({}-{}) pair -> {:6.5f}({:6.5f})".format(atm_typ[r0][0], k, p, t ) )	

	return element_counts, bar_graph
	
def coordination_analysis_Cylindrical_cell(n_atoms, pos):
	# First construct the cylinder around the dislocation line
	# I've used (x-x0)**2 + (y-y0)**2 < R**2; theta0 = arctan(y/x); z=z
	cnt = 0;  bar_graph = [];	ggZ = [];
	
	# Atom # can be picked by visually looking at the supercell and noticing
	# the index of the site. 
	s1 = 72; s2 = 63; s3 = 269

	### Atom positions corresponding to 3rd (111) plane
	bz = alat/2 * np.sqrt(3)
	for i in range(n_atoms):
		ggZ.append( pos[i][2]  )
	
	### This code selects the atoms in the 3rd Layer
	#for counter, value in enumerate(ggZ):
	#	if ( value > 2.8 ):
	#		print('{} {:14.6f} {:14.6f} {:14.6f}'.format(counter, pos[counter][0], pos[counter][1], pos[counter][2] ) )
		
	# To find the centroid of the triangle geometry around the screw dislocation line	
	# bounded by s1, s2, and s3 atoms.
	A = ( float(pos[s1][0]), float(pos[s1][1]), float(pos[s1][2]) )
	B = ( float(pos[s2][0]), float(pos[s2][1]), float(pos[s2][2]) )
	C = ( float(pos[s3][0]), float(pos[s3][1]), float(pos[s3][2]) ) 
	x0 = np.mean( [ A[0],B[0],C[0] ] ) 
	y0 = np.mean( [ A[1],B[1],C[1] ] ) 
	z0 = np.mean( [ A[2],B[2],C[2] ] ) 
	
	r0 = np.sqrt( x0*x0 + y0*y0 )
	theta = math.degrees( np.arctan(y0/x0) )
	#print("r0,theta=({:5.5f},{:5.5f})".format( r0, theta ) )
	#print("Centroid=({:5.5f},{:5.5f},{:5.5f})".format(x0,y0,z0))

	for x in range(0, len(pos), 1):
		i = float(pos[x][0]) - x0 
		j = float(pos[x][1]) - y0 
		if ( ( np.sqrt(i*i + j*j)  < rcutoff )): # FILTER
			cnt +=1; 
			bar_graph.append( pos[x][3] )	
			print ( "{:4d} {:9.6f} {:9.6f} {:9.6f} {:9.6s} ".format(x,pos[x][0],pos[x][1],pos[x][2],pos[x][3] ) )
	print ("# of atoms in N shell: {}".format( cnt ) )
	element_counts = Counter(bar_graph)
	
	print (element_counts)
	return element_counts, bar_graph
	
def plot_bar_from_counter(counter, bar_graph, ax=None):
	if ax is None:
		fig = plt.figure()
		ax = fig.add_subplot(111)
	frequencies = counter.values()
	names = counter.keys()
	ax.bar(names, frequencies, align='center', alpha=0.5)
	#plt.hist(bar_graph, bins=10, facecolor='red', alpha=0.75)
	plt.rcParams.update({'figure.figsize':(7,5), 'figure.dpi':300})
	plt.gca().set(title='Frequency Histogram', ylabel='Frequency');
	#plt.savefig('Coordination_barPlot.eps', format='eps', dpi=300)
	plt.show()

#---------------------MAIN ENGINE--------------------------
if __name__ == "__main__":
	n_atoms,pos,firstline,alat,Latvec1,Latvec2,Latvec3,elementtype,atomtypes,Coordtype = read_POSCAR();
	
	# B = a<111>/2 which is length along Z=<111>
	BurgZ = float(Latvec3[2]); 	
	alat = ( (1) * BurgZ ) / np.sqrt(3)
	EA = [];
	
	for j in range( len( elementtype.split() )):
		EA.append( elementtype.split()[j]+atomtypes.split()[j] )
	EA = ''.join(EA)	
	
	subscript = str.maketrans("0123456789", "₀₁₂₃₄₅₆₇₈₉")
	print(colored("USAGE :: python3 sys.argv[0] <sys.argv[1], site_index> <sys.argv[2], radius> ", 'red'))
	print ("Atom types are not appended in the last column of POSCAR file")
	print("alat={:5.4f}, #atoms={}, {}".format(alat, n_atoms, EA.translate(subscript)))
	
	print("{:20.5s} {:20.12s} {:10.12s}".format("atom#", "position", "atom type"))
	#element_counts, bar_graph = coordination_analysis_single_supercell(n_atoms, pos)
	
	''' Uncomment these two lines to turn on the coordination with replicate cells '''
	mag_atoms_pos, atm_typ = replicate_cell(pos,n_atoms,Latvec1,Latvec2,Latvec3)	
	element_counts, bar_graph = coordination_analysis_spherical_shell(n_atoms, mag_atoms_pos, atm_typ)
	print("{:-^50}".format("*"))	

	''' Uncomment this line to turn on the Cylindrical coordination '''
	#element_counts, bar_graph = coordination_analysis_Cylindrical_cell(n_atoms, pos)
	
	''' For plotting turn this on '''
	#plot_bar_from_counter(element_counts, bar_graph)
	
	
