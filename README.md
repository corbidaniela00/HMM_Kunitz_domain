# 

This project addresses the identification of Kunitz-type serine protease inhibitors through a custom-trained HMM

## Project overview

The Kunitz-type domain is a highly conserved $\alpha+\beta$ structural motif crucial for regulating serine protease activity. 
Due to deep evolutionary divergence, its primary sequence often falls into the "twilight zone," making traditional sequence-based tools like BLAST less effective for remote homology detection.
To overcome this limitation, a computational pipeline was developed to leverage 3D structural data for enhanced database annotation. 

## Project workflow

### 1. High-quality Kunitz structures were retrieved from UniProt and filtered using MMseqs2 to remove redundancy. 
* Uniprot filters (output: sequences_for_clustering.fasta)
  * Pfam ID: PF00014
  * Resolution ≤ 3 Å
  * Sequence length between 50–70 residues
        
* MMSEQ filters (output: seed_alignemet_input.fasta)
  - sequence identity: 0.9
  - coverage: 0.8
          
### 2. Non-redundant domains were then aligned spatially via Foldseek to capture structural conservation independent of sequence identity. 


### 3. This structure-derived alignment was used as a seed to train a custom Profile Hidden Markov Model (HMMER3), which was subsequently deployed to screen the curated Swiss-Prot database. 
Finally, newly identified homologs were structurally validated using PDBeFold through RMSD and Q-score analysis.

This workflow demonstrates how integrating structural biology with probabilistic sequence profiles significantly improves the sensitivity and accuracy of functional domain annotation.

## 
