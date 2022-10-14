#!/bin/bash
#PBS -l walltime=48:00:00
#PBS -l select=1:ncpus=1:mem=2gb
#PBS -N Scoring
#PBS -J 0-249
cd $PBS_O_WORKDIR

module load anaconda3/personal
source activate scoring37

python3 script/runXGB.py $PBS_ARRAY_INDEX $processors

