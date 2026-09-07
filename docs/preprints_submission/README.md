# Preprints.org submission package

This directory contains the Preprints.org-formatted manuscript source built from the
official 2026 LaTeX template supplied by the author.

## Author metadata

The correspondence address is set to `u.mergen@nyu.edu`. Add an ORCID only if the
author has confirmed the identifier.

## Build

Run the following command from this directory:

    tectonic --keep-logs --outdir . preprint_v1.tex

The source package is self-contained: Definitions contains the publisher class files,
and figures contains every image used by the manuscript.

## Scope

The manuscript reports simulation results only. The scientific values remain tied
to the repository's frozen result JSON files and preprint-v1.3 analysis tag.
