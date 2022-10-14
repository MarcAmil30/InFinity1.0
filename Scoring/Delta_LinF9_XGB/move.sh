#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=1gb
#PBS -N move_ligands

cd $PBS_O_WORKDIR


mv $file_dir/Docking/mutants $file_dir/Scoring/mutants
