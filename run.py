# -*- coding: utf-8 -*-

# * Copyright (c) 2009-2019. Authors: see NOTICE file.
# *
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# *
# *      http://www.apache.org/licenses/LICENSE-2.0
# *
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


import os
import cv2
import logging
import numpy as np
from tempfile import TemporaryDirectory
from cytomine import CytomineJob
from cytomine.models import ImageInstance, ImageInstanceCollection, AnnotationCollection, Annotation
from cytomine.utilities.software import parse_domain_list
from shapely.geometry import Polygon
from sldc.locator import mask_to_objects_2d
from shapely.affinity import affine_transform

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Stévens Benjamin", "Romain Mormont <romain.mormont@cytomine.com>"]
__copyright__ = "Copyright 2010-2022 University of Liège, Belgium, https://uliege.cytomine.org/"

logging.basicConfig()
logger = logging.getLogger("cytomine.client")
logger.setLevel(logging.INFO)


def main(argv):
    with CytomineJob.from_cli(argv) as cj:
        
        images = ImageInstanceCollection()
        if cj.parameters.cytomine_id_images is not None:
            id_images = parse_domain_list(cj.parameters.cytomine_id_images)
            images.extend([ImageInstance().fetch(_id) for _id in id_images])
        else:
            images = images.fetch_with_filter("project", cj.parameters.cytomine_id_project)
        
        for image in cj.monitor(images, prefix="Running detection on image", period=0.1):
            # Resize image if needed
            resize_ratio = max(image.width, image.height) / cj.parameters.max_image_size
            if resize_ratio < 1:
                resize_ratio = 1

            resized_width = int(image.width / resize_ratio)
            resized_height = int(image.height / resize_ratio)

            bit_depth = image.bitDepth if image.bitDepth is not None else 8
            
            # download file in a temporary directory for auto-removal
            with TemporaryDirectory() as tmpdir:
                download_path = os.path.join(tmpdir, "{id}.jpg")           
                image.dump(dest_pattern=download_path, max_size=max(resized_width, resized_height), bits=bit_depth)
                img = cv2.imread(image.filename, cv2.IMREAD_GRAYSCALE)

            if cj.parameters.threshold_blocksize % 2 == 0:
                logging.warning(
                    "The threshold block size must be an odd number! "
                    "It will be incremented by one."
                )
                cj.parameters.threshold_blocksize += 1

            thresholded_img = cv2.adaptiveThreshold(
                img,
                2 ** bit_depth,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                cj.parameters.threshold_blocksize,
                cj.parameters.threshold_constant
            )

            kernel = np.ones((5, 5), np.uint8)
            eroded_img = cv2.erode(thresholded_img, kernel, iterations=cj.parameters.erode_iterations)
            dilated_img = cv2.dilate(eroded_img, kernel, iterations=cj.parameters.dilate_iterations)

            extension = 10
            extended_img = cv2.copyMakeBorder(
                dilated_img,
                extension,
                extension,
                extension,
                extension,
                cv2.BORDER_CONSTANT,
                value=2 ** bit_depth
            )

            # extract foreground polygons 
            fg_objects = mask_to_objects_2d(extended_img, background=255, offset=(-extension, -extension))
            zoom_factor = image.width / float(resized_width)

            # Only keep components greater than {image_area_perc_threshold}% of whole image
            min_area = int((cj.parameters.image_area_perc_threshold / 100) * image.width * image.height)

            transform_matrix = [zoom_factor, 0, 0, -zoom_factor, 0, image.height]
            annotations = AnnotationCollection()
            for i, (fg_poly, _) in enumerate(fg_objects):
                upscaled = affine_transform(fg_poly, transform_matrix)
                if upscaled.area <= min_area:
                    continue
                annotations.append(Annotation(
                    location=upscaled.wkt,
                    id_image=image.id,
                    id_terms=[cj.parameters.cytomine_id_predicted_term],
                    id_project=cj.parameters.cytomine_id_project
                ))

            annotations.save()

        cj.job.update(statusComment="Finished.")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])

