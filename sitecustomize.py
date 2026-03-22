"""sitecustomize.py — loaded automatically by Python's site module at startup.

Currently has no active role: the artiq repo is on the release-8-ucsb branch
which already includes shuttler, GrabberTimeoutException, and all other ARTIQ 8
additions.

This file is kept as an extension point.  If future waxx/kexp code imports
artiq.coredevice submodules that are absent from the local clone, two patterns
are available without modifying any repo file:

  1. Replacement stub — drop a .py in sim/stubs/_artiq/coredevice/ and
     uncomment / re-enable the _ArtiqCoredeviceStubFinder below.

  2. Patch existing module — add the missing name to _patches dict and
     re-enable the finder.
"""
