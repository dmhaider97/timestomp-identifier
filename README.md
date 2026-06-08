# Timestomp Identifier

## Overview
The Timestomp Identifier is a Python-based incident response tool designed to aid in the idenfication of timestomping on a Windows system.

---

## Problem
Timestomping occurs when threat actors manipulate NTFS file metadata (specifically the Standard Information (SI) attributes) to try and disguise malicious payloads, but this creates chronological contradictions against the kernel-protected File Name (FN) attributes leaving behind identifiable anomalies.

---

```bash
git clone [https://github.com/dmhaider97/timestomp-identifier.git](https://github.com/dmhaider97/timestomp-identifier.git)
cd timestomp-identifier
pip install -r requirements.txt
