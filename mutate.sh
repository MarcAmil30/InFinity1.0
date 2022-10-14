#!/bin/bash
#PBS -l walltime=72:00:00
#PBS -l select=1:ncpus=1:mem=10gb
#PBS -N mutate_permutations_array
#PBS -J 1-20 

module load anaconda3/personal 
source activate equibind

cd $file_dir/Docking/mutants
python3 $file_dir/modified_permutation.py $limit_r 


