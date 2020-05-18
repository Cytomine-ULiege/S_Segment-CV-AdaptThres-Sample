# Cytomine software - Segment-CV-AdaptThres-Sample
Cytomine (https://cytomine.org) app developed by ULiège Cytomine Research team (https://uliege.cytomine.org) for segmentation of samples using Computer Vision (CV) Adaptive Thresholding.

This implementation follows Cytomine (=v3.0) external app conventions based on container technology.

* **Summary:** It applies a thresholding algorithm to a thumbnail of a whole image (downloaded from Cytomine-Core) and upload detected geometries to Cytomine-Core (in a userjob layer)

To launch such an analysis, a user first specify a Cytomine term identifier. The app will then apply the algorithm to all Cytomine images belonging to the current project. Detected objects are labeled with the term identifier.

* **Typical application:** Detect sample regions before applying other algorithms (e.g. segmentation).

* **Based on:** Adaptive Thresholding (https://docs.opencv.org/3.4/d7/d4d/tutorial_py_thresholding.html) but code can be easily adapted to other thresholding algorithms.

* **Example on [CMU-1 open image](https://cytomine.coop/collection/cmu-1/cmu-1-ndpi)**  with the *Image Area Percentile Threshold* parameter to 3.
![AdaptThreshold](https://user-images.githubusercontent.com/8018298/82058049-8063c500-96c4-11ea-966e-52d8669a2898.png)

* **Parameters:** 
  * *cytomine_host*, *cytomine_public_key*, *cytomine_private_key*, *cytomine_id_project* and *cytomine_id_software* are parameter needed for all Cytomine external app. They will allow the app to be run on the Cytomine instance (determined with its host), connect and communicate with the instance (with the key pair). An app is always run into a project (*cytomine_id_project*) and to be run, the app must be previously declared to the plateforme (*cytomine_id_software*).
  * *cytomine_id_predicted_term* : The detected components will be associated to a term corresponding to the given id.
  * *max_image_size* : During the run, the analyzed images will be resized if the width or the height are larger than the corresponding value of this parameter. Default value is 2048. Be careful that if you allow bigger image size, the download will take more time and, for high value, timeout can occur.
  * *image_area_perc_threshold* : The detected component with an area less than a specific value (calculated as a percentil of the image area) will not be kept. Default value is 5%. Modify this value to be able to kept smaller object. In the previous CMU-1 exemple, the input value was 3 to catch the smaller two Region Of Interest.
  * *threshold_blocksize* and *threshold_constant* are used as parameter of the [adaptiveThreshold function of OpenCV](https://docs.opencv.org/3.4/d7/d1b/group__imgproc__misc.html#ga72b913f352e4a1b1b397736707afcde3)
  * *erode_iterations* is the number of erosion applied to an image and *dilate_iterations* is the number of dilation applied to an image after the erosion step. Find more about eroding and dilating on the [OpenCV documentation](https://docs.opencv.org/2.4/doc/tutorials/imgproc/erosion_dilatation/erosion_dilatation.html)
  * Finally, you can modify the *log_level* by setting one of these values 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL' or unset.


-----------------------------------------------------------------------------

Copyright 2010-2020 University of Liège, Belgium, https://uliege.cytomine.org
