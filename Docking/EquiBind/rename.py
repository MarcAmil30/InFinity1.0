import os 

ligand_list = os.listdir("/rds/general/user/rh1119/home/iGEM/EquiBind/decoys_output")
counter = 0
for ligand in ligand_list:
	ligand_new = "trial_ligand_" + str(counter) + ".mol2"
	ligand_old_dir = os.path.join("/rds/general/user/rh1119/home/iGEM/EquiBind/decoys_output",ligand)
	ligand_new_dir = os.path.join("/rds/general/user/rh1119/home/iGEM/EquiBind/decoys_output",ligand_new)
	os.rename(ligand_old_dir, ligand_new_dir)
	counter += 1
