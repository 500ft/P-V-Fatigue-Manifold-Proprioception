# Preprints.org submission package

> **Historical package; publication stopped.** The study is closed and v1.4 is
> [withdrawn](../corrections/v1.4-withdrawn-2026-10-02.md). This package does not
> authorize a new submission. The [v1.3 methods correction](../corrections/v1.3-methods-2026-09-05.md)
> remains in force. [Current scope](../../ROADMAP.md).

This directory contains the Preprints.org-formatted manuscript source built from the
official 2026 LaTeX template supplied by the author.

## Author metadata

The correspondence address is set to `u.mergen@nyu.edu`. Add an ORCID only if the
author has confirmed the identifier.

## Historical build command

Run the following command from this directory:

    tectonic --keep-logs --outdir . preprint_v1.tex

The source package is self-contained: Definitions contains the publisher class files,
and figures contains every image used by the manuscript.

## Scope

The manuscript reports simulation results only. The scientific values remain tied
to the repository's frozen result JSON files and preprint-v1.3 analysis tag.
