#!/usr/bin/env python
import sys, os, re
import numpy as np
from scipy.spatial import distance
from scipy.spatial.distance import cdist
import pandas as pd
from rdkit import Chem
from rdkit.ML.Descriptors.MoleculeDescriptors import MolecularDescriptorCalculator
import fileinput
from pharma import pharma
import featureSASA
import xgboost as xgb
import pickle
from openbabel import openbabel as ob
from openbabel import pybel
import alphaspace2 as al
import mdtraj
import csv
import traceback
import openbabel

import calc_bridge_wat
import calc_ligCover_betaScore
import calc_rdkit
import calc_sasa
import calc_vina_features
import prepare_betaAtoms

Vina = '[USER_DIR]/InFinity/Scoring/Delta_LinF9_XGB/software/smina_feature'
Smina = '[USER_DIR]/InFinity/Scoring/Delta_LinF9_XGB/software/smina.static'
SF = '[USER_DIR]/InFinity/Scoring/Delta_LinF9_XGB/software/sf_vina.txt'
ADT = '[USER_DIR]/InFinity/Scoring/Delta_LinF9_XGB/script/prepare_receptor4.py'
model_dir = '[USER_DIR]/InFinity/Scoring/Delta_LinF9_XGB/saved_model'
protein_dir = '[USER_DIR]/InFinity/Scoring/mutants'
ligand_dir = '[USER_DIR]/InFinity/Scoring/binding_poses'
tot_proc = int(sys.argv[2])
session = int(sys.argv[1])
print(tot_proc)
print(session)
protein_n = len(os.listdir(ligand_dir))
split_start = int((protein_n // tot_proc) * session)
print(split_start)
split_e  = int((protein_n // tot_proc) * (session + 1))
if split_e != protein_n:
	split_end = split_e
elif split_e == protein_n:
	split_end = split_e + 1
print(split_end)
protein_list = os.listdir(protein_dir)
ligand_list = os.listdir(ligand_dir)
counter = int(split_start)
while counter >= split_start and counter < split_end:
	for ligand in ligand_list:
		if str(counter) in ligand and len(str(counter)) == (len(ligand) - 5):
			try:
				lig = os.path.join(ligand_dir, ligand, "lig_equibind_corrected.sdf")
				protein_prefix = ligand.rsplit('_')[0]
				protein_name = protein_prefix + "_protein_processed.pdb"
				pro = os.path.join(protein_dir, ligand, protein_name)
				if lig.endswith('.mol2'):
					mol = Chem.MolFromMol2File(lig, removeHs=False)
					lig = lig[:-5]+'.pdb'
					Chem.MolToPDBFile(mol, lig)
				elif lig.endswith('.sdf'):
					mol = Chem.MolFromMolFile(lig, removeHs=False)
					lig = lig[:-4]+'.pdb'
					Chem.MolToPDBFile(mol, lig)

				## 1. prepare_betaAtoms
				beta_atoms = "betaAtoms_" + str(session) + ".pdb"
				beta = os.path.join(os.path.dirname(pro),beta_atoms)
				pro_pdbqt = prepare_betaAtoms.Prepare_beta(pro, beta, ADT)

				## 2. Vina_features
				v = calc_vina_features.vina(pro_pdbqt, lig, Vina, Smina)
				vinaF = [v.LinF9]+v.features(48)

				## 3. Beta_features
				betaScore, ligCover = calc_ligCover_betaScore.calc_betaScore_and_ligCover(lig, beta)

				## 4. sasa_features
				datadir = os.path.dirname(os.path.abspath(pro))
				pro_ = os.path.abspath(pro)
				lig_ = os.path.abspath(lig)
				sasa_features = calc_sasa.sasa(datadir,pro_,lig_,session)
				sasaF = sasa_features.sasa+sasa_features.sasa_lig+sasa_features.sasa_pro

				## 5. ligand_features
				ligF = list(calc_rdkit.GetRDKitDescriptors(mol))

				## 6. water_features
				df = calc_bridge_wat.Check_bridge_water(pro, lig)
				if len(df) == 0:
					watF = [0,0,0]
				else:
					Nbw, Epw, Elw = calc_bridge_wat.Sum_score(pro, lig, df, Smina)
					watF = [Nbw, Epw, Elw]

				## calculate XGB
				LinF9 = vinaF[0]*(-0.73349)
				LE = LinF9/vinaF[-4]
				sasa = sasaF[:18]+sasaF[19:28]+sasaF[29:]
				metal = vinaF[1:7]
				X = vinaF[7:]+[ligCover,betaScore,LE]+sasa+metal+ligF+watF
				X = np.array([X]).astype(np.float64)

				y_predict_ = []
				for i in range(1,11):
					xgb_model = pickle.load(open("%s/mod_%d.pickle.dat"%(model_dir,i),"rb"))
					y_i_predict = xgb_model.predict(X, ntree_limit=xgb_model.best_ntree_limit)
					y_predict_.append(y_i_predict)

				y_predict = np.average(y_predict_, axis=0)
				XGB = round(y_predict[0]+LinF9,3)

				fields = [protein_prefix,counter,XGB]
				csv_file = 'scores_' + str(session) +'.csv'
				with open(csv_file, 'a') as f:
					writer = csv.writer(f)
					writer.writerow(fields)
				counter += 1
			except Exception:
				traceback.print_exc()
				pass
				counter += 1
