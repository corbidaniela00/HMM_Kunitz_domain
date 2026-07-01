# 

This project addresses the identification of Kunitz-type serine protease inhibitors through a custom-trained HMM

## Project overview

The Kunitz-type domain is a highly conserved $\alpha+\beta$ structural motif crucial for regulating serine protease activity. 
Due to deep evolutionary divergence, its primary sequence often falls into the "twilight zone," making traditional sequence-based tools like BLAST less effective for remote homology detection.
To overcome this limitation, a computational pipeline was developed to leverage 3D structural data for enhanced database annotation. 

## Project workflow

### 1. High-quality Kunitz structures were retrieved from UniProt and filtered using MMseqs2 to remove redundancy. 
* Uniprot filters (python code:`filter_PDB_sequences.py` output: `sequences_for_clustering.fasta`)
  * Pfam ID: PF00014
  * Resolution ≤ 3 Å
  * Sequence length between 40–70 residues
        
* MMSEQ filters (python code:`update_with_resolution_MMSEQ.py`, `select_one_seq_per_cluster.py` output: `seed_alignemet_input.fasta`)
  - sequence identity: 0.95
  - coverage: 0.85
          
### 2. Non-redundant domains were then aligned spatially via Foldseek to capture structural conservation independent of sequence identity. 


### 3. This structure-derived alignment was used as a seed to train a custom Profile Hidden Markov Model (HMMER3), which was subsequently deployed to screen the curated Swiss-Prot database. 
after creating a CONDA environment with `hmmer` installed and having downloaded from SwissProt respectively the proteins with/without the kunitz domain ( that I'm goint to use to validate my model) I proceed with the following commands

- I start building the HMM model, based on the structure alignement downloades from FoldSeek `hmmbuild name_model.hmm alignment_fasta.fa`
- `zcat uniprotkb_reviewed_true_AND_xref_pfam_P_2026_04_24.fasta.gz > positive_kunitz.fasta`
- `zcat uniprotkb_reviewed_true_NOT_xref_pfam_P_2026_04_24.fasta.gz > negative_kunitz.fasta`
- `hmmsearch --noali --max --tblout positive_kunitz.search -Z 1000 Kunitz_model.hmm positive_kunitz.fasta`
- `hmmsearch --noali --max --tblout negative_kunitz.search -Z 1000 Kunitz_model.hmm negative_kunitz.fasta`
- 
Finally, newly identified homologs were structurally validated using PDBeFold through RMSD and Q-score analysis.

This workflow demonstrates how integrating structural biology with probabilistic sequence profiles significantly improves the sensitivity and accuracy of functional domain annotation.

## 
