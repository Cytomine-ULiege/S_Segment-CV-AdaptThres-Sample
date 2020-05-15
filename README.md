# Cytomine software - Segment-CV-AdaptThres-Sample
Cytomine (https://cytomine.org) app developed by ULiège Cytomine Research team (https://uliege.cytomine.org) for segmentation of samples using Computer Vision (CV) Adaptive Thresholding.

This implementation follows Cytomine (=v3.0) external app conventions based on container technology.

* **Summary:** It applies a thresholding algorithm to a thumbnail of a whole image (downloaded from Cytomine-Core) and upload detected geometries to Cytomine-Core (in a userjob layer)

To launch such an analysis, a user first specify a Cytomine term identifier. The app will then apply the algorithm to all Cytomine images belonging to the current project. Detected objects are labeled with the term identifier.

* **Typical application:** Detect sample regions before applying other algorithms (e.g. segmentation).

* **Based on:** Adaptive Thresholding (https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html) but code can be easily adapted to other thresholding algorithms.

-----------------------------------------------------------------------------

Copyright 2010-2020 University of Liège, Belgium, https://uliege.cytomine.org
