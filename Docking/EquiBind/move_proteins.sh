#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l select=1:ncpus=1:mem=1gb
#PBS -N move_ligands

cd $PBS_O_WORKDIR

mv proteins/proteins/* /rds/general/user/rh1119/home/iGEM/Scoring/delta_LinF9_XGB/mutants/proteins/.




