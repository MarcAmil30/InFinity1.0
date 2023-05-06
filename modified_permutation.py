import sys
import time 
import math
from  itertools import combinations_with_replacement, permutations, combinations, islice, product
import pandas as pd 
from pymol import cmd
import os 
import random 
from random import randrange as rr
import numba 
from numba import jit, njit, prange

limit_r = int(sys.argv[1])
indexlist2 = []
reslist2 = []

aminoacid = 'ARNDCQEGHILKMFPSTWYV'

#Input data 
csvread = pd.read_csv('input_trial.csv')
sequence = csvread.iloc[0, 1]
inputpositions = csvread.iloc[0, 2]
inputpositions = inputpositions.split(',')
positions_n = len(inputpositions)
positionstomutate = [int(positionstomutate) - 1 for positionstomutate in inputpositions] 

def generate(length):
    code=[]
    for _ in range(length):
        random_number=rr(0,len(aminoacid))
        code.append(aminoacid[random_number])
    return code

peptide = []
count = 0 

limit = [generate(positions_n) for _ in range(limit_r)] #different permutations to mutate sequence to 


def string_perms(s, indices): #different combinations given to PyMOL 
    for x in limit:
        peptide.append(''.join(x))
        aa = iter(x)  
        yield ','.join(a if j not in indices else next(aa) for j, a in enumerate(s)).split(',')

NUM_WORKERS = 8

def splitter(list_id, NUM_WORKERS):
    step = math.ceil(len(list_id) / NUM_WORKERS)
    grouped_sequences = [list_id[i:i+step] for i in range(0, len(list_id), step)]
    return grouped_sequences

def detectres(wild_type, mutated_seq):
    for seq in mutated_seq:
        indexlist = [str(1 +index) for index,(first, second) in enumerate(zip(wild_type, seq)) if first != second]
        reslist = [second for index,(first, second) in enumerate(zip(wild_type, seq)) if first != second]
        indexlist2.append(indexlist)
        reslist2.append(reslist) 

def get_resi(selection): 
    #checks the residue of a given protein
    model = cmd.get_model(selection) 
    return {at.resi for at in model.atom}

def get_chains(selection):
    #checks the chains of a given protein
    model = cmd.get_model(selection)
    return {at.chain for at in model.atom}

def is_one_residue(selection):
    "Check if selection is a single residue"
    objects = {*cmd.get_object_list(selection)}
    chains = get_chains(selection)
    resi = get_resi(selection)
    return len(chains) == 1 and len(resi) == 1 and len(objects) == 1

def mutate_one(selection, aa):
    """
    Selection must be one residue
    """
    assert is_one_residue(selection)
    cmd.select(selection)
    cmd.get_wizard().do_select('''sele''')
    cmd.get_wizard().set_mode(aa)
    cmd.get_wizard().apply()
    print(f"Mutated {selection} to {aa}")
    
def iter_residues(selection):
    "return selection string for a single residue"
    objects = cmd.get_object_list(selection)
    for obj in objects:
        for chain in get_chains(f"{selection} and {obj}"):
            for resi in get_resi(f"{selection} and {obj}"):
                yield f"resi {resi} and chain {chain} and {obj}"

aminos = { 
    'A': "ALA",    'C': "CYS",
    'D': "ASP",    'E': "GLU",
    'F': "PHE",    'G': "GLY",
    'H': "HIS",    'I': "ILE",
    'K': "LYS",    'L': "LEU",
    'M': "MET",    'N': "ASN",
    'P': "PRO",
    'Q': "GLN",    'R': "ARG",
    'S': "SER",    'T': "THR",
    'V': "VAL",
    'W': "TRP",    'Y': "TYR"
    }
extra = ["ARGN", "ASPH", "GLUH", "HID", "HIE", 
         "HIP", "LYSN"]
        
def fix_aa(aa):
    aa = aa.upper()
    if len(aa) == 1:
        # Deal with a letter coding
        aa = aminos[aa].upper()
    elif len(aa) not in (1,3):
        raise ValueError(
        f"""Amino acid encoding must be 
        one or three letter, was {aa}""")
    return aa

def mutate(selection, aa):
    aa = fix_aa(aa)
    cmd.set("retain_order", 0)
    cmd.wizard("mutagenesis")
    cmd.refresh_wizard()
    for single_res in iter_residues(selection):
        mutate_one(single_res, aa) 
    cmd.set_wizard()
    cmd.sort()

WT  = ['P', 'I', 'F', 'L', 'N', 'V', 'L', 'E', 'A', 'I', 'E', 'P', 'G', 'V', 'V', 'C', 'A', 'G', 'H', 'D', 'N', 'N', 'Q', 'P', 'D', 'S', 'F', 'A', 'A', 'L', 'L', 'S', 'S', 'L', 'N', 'E', 'L', 'G', 'E', 'R', 'Q', 'L', 'V', 'H', 'V', 'V', 'K', 'W', 'A', 'K', 'A', 'L', 'P', 'G', 'F', 'R', 'N', 'L', 'H', 'V', 'D', 'D', 'Q', 'M', 'A', 'V', 'I', 'Q', 'Y', 'S', 'W', 'M', 'G', 'L', 'M', 'V', 'F', 'A', 'M', 'G', 'W', 'R', 'S', 'F', 'T', 'N', 'V', 'N', 'S', 'R', 'M', 'L', 'Y', 'F', 'A', 'P', 'D', 'L', 'V', 'F', 'N', 'E', 'Y', 'R', 'M', 'H', 'K', 'S', 'R', 'M', 'Y', 'S', 'Q', 'C', 'V', 'R', 'M', 'R', 'H', 'L', 'S', 'Q', 'E', 'F', 'G', 'W', 'L', 'Q', 'I', 'T', 'P', 'Q', 'E', 'F', 'L', 'C', 'M', 'K', 'A', 'L', 'L', 'L', 'F', 'S', 'I', 'I', 'P', 'V', 'D', 'G', 'L', 'K', 'N', 'Q', 'K', 'F', 'F', 'D', 'E', 'L', 'R', 'M', 'N', 'Y', 'I', 'K', 'E', 'L', 'D', 'R', 'I', 'I', 'A', 'C', 'K', 'R', 'K', 'N', 'P', 'T', 'S', 'C', 'S', 'R', 'R', 'F', 'Y', 'Q', 'L', 'T', 'K', 'L', 'L', 'D', 'S', 'V', 'Q', 'P', 'I', 'A', 'R', 'E', 'L', 'H', 'Q', 'F', 'T', 'F', 'D', 'L', 'L', 'I', 'K', 'S', 'H', 'M', 'V', 'S', 'V', 'D', 'F', 'P', 'E', 'M', 'M', 'A', 'E', 'I', 'I', 'S', 'V', 'Q', 'V', 'P', 'K', 'I', 'L', 'S', 'G', 'K', 'V', 'K', 'P', 'I', 'Y', 'F', 'H', 'T', 'Q']

if __name__ == "__main__":
    mutated_seqlist = list(string_perms(sequence, positionstomutate)) #sequence permutation 
    grouped_seq = splitter(mutated_seqlist, NUM_WORKERS)
    counter = 0 
    array_index = int(os.environ['PBS_ARRAY_INDEX'])
    for t in range(0, len(grouped_seq)):
        counter = counter+1
        if counter == array_index:
            index_group = grouped_seq[t]
            detectres(WT, index_group)
            mutate.__doc__ = __doc__
            cmd.reinitialize()
            cmd.extend('mutate', mutate)
            cmd.load('3b5r.pdb')
            # for j, x in zip(indexlist2[t], reslist2[t]): #the code here is without using parallelization and multi-threading 
            #     mutate('resi' + ' ' + j,x)
            #     cmd.save('trial_protein_{0}.pdb'.format(t))
            for i in range(len(indexlist2)):
                for j, x in zip(indexlist2[i], reslist2[i]):
                    mutate('resi' + ' ' + j,x)
                    cmd.save('trial_{0}k_protein_{1}.pdb'.format(i, t))
        



    