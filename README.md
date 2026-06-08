# Timestomp Identifier

## Overview
The Timestomp Identifier is a Python-based incident response tool designed to aid in the idenfication of timestomping on a Windows system.

---

## Problem
Timestomping occurs when threat actors manipulate NTFS file metadata (specifically the Standard Information (SI) attributes) to try and disguise malicious payloads, but this creates chronological contradictions against the kernel-protected File Name (FN) attributes leaving behind identifiable anomalies.

---

## Usage
python timestomp-identifier.py -f sample-mft.bin  
python timestomp-identifier.py -f sample-mft.bin --keep-csv
