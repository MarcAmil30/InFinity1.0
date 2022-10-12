#!/bin/bash
#PBS -l walltime=02:00:00
#PBS -l select=1:ncpus=1:mem=8gb
#PBS -N rename

cd $PBS_O_WORKDIR

module load anaconda3/personal

python3 rename.py



