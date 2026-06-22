---
title: 'Less is More: Minimizing Code Reorganization using XTREE'
authors:
- Rahul Krishna
- Tim Menzies
- Lucas Layman
date: '2017-01-01'
publishDate: '2026-06-22T21:16:44.375171Z'
publication_types:
- article-journal
publication:
  name: Information and Software Technology
abstract: '© 2017 Elsevier B.V. Context: Developers use bad code smells to guide code reorganization. Yet developers, textbooks, tools, and researchers disagree on which bad smells are important. How can we offer reliable advice to developers about which bad smells to fix? Objective: To evaluate the likelihood that a code reorganization to address bad code smells will yield improvement in the defect-proneness of the code. Method: We introduce XTREE, a framework that analyzes a historical log of defects seen previously in the code and generates a set of useful code changes. Any bad smell that requires changes outside of that set can be deprioritized (since there is no historical evidence that the bad smell causes any problems). Evaluation: We evaluate XTREE''s recommendations for bad smell improvement against recommendations from previous work (Shatnawi, Alves, and Borges) using multiple data sets of code metrics and defect counts. Results: Code modules that are changed in response to XTREE''s recommendations contain significantly fewer defects than recommendations from previous studies. Further, XTREE endorses changes to very few code metrics, so XTREE requires programmers to do less work. Further, XTREE''s recommendations are more responsive to the particulars of different data sets. Finally XTREE''s recommendations may be generalized to identify the most crucial factors affecting multiple datasets (see the last figure in paper). Conclusion: Before undertaking a code reorganization based on a bad smell report, use a framework like XTREE to check and ignore any such operations that are useless; i.e. ones which lack evidence in the historical record that it is useful to make that change. Note that this use case applies to both manual code reorganizations proposed by developers as well as those conducted by automatic methods.'
tags:
- Bad smells
- Decision trees
- Performance prediction
links:
- name: arXiv
  url: https://arxiv.org/abs/1609.03614
- type: pdf
  url: https://arxiv.org/pdf/1609.03614.pdf
hugoblox:
  ids:
    doi: 10.1016/j.infsof.2017.03.012
---
