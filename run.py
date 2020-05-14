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

from operator import attrgetter

import cv2
import numpy as np
from cytomine import CytomineJob
from cytomine.models import ImageInstanceCollection, AnnotationCollection, Annotation
from shapely.geometry import Polygon

__author__ = "Rubens Ulysse <urubens@uliege.be>"
__contributors__ = ["Marée Raphaël <raphael.maree@uliege.be>", "Stévens Benjamin"]
__copyright__ = "Copyright 2010-2019 University of Liège, Belgium, https://uliege.cytomine.org/"


def find_components(image):
    contours, hierarchy = cv2.findContours(image, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    components = []
    if len(contours) > 0:
        top_index = 0
        tops_remaining = True
        while tops_remaining:
            exterior = contours[top_index][:, 0, :].tolist()

            interiors = []
            # check if there are children and process if necessary
            if hierarchy[0][top_index][2] != -1:
                sub_index = hierarchy[0][top_index][2]
                subs_remaining = True
                while subs_remaining:
                    interiors.append(contours[sub_index][:, 0, :].tolist())

                    # check if there is another sub contour
                    if hierarchy[0][sub_index][0] != -1:
                        sub_index = hierarchy[0][sub_index][0]
                    else:
                        subs_remaining = False

            # add component tuple to components only if exterior is a polygon
            if len(exterior) > 3:
                components.append((exterior, interiors))

            # check if there is another top contour
            if hierarchy[0][top_index][0] != -1:
                top_index = hierarchy[0][top_index][0]
            else:
                tops_remaining = False
    return components


def main(argv):
    with CytomineJob.from_cli(argv) as cj:

        images = ImageInstanceCollection().fetch_with_filter("project", cj.parameters.cytomine_id_project)
        for image in cj.monitor(images, prefix="Running detection on image", period=0.1):
            # Resize image if needed
            resize_ratio = max(image.width, image.height) / cj.parameters.max_image_size
            if resize_ratio < 1:
                resize_ratio = 1

            resized_width = int(image.width / resize_ratio)
            resized_height = int(image.height / resize_ratio)

            bit_depth = image.bitDepth if image.bitDepth is not None else 8

            image.dump(dest_pattern="/tmp/{id}.jpg", max_size=max(resized_width, resized_height), bits=bit_depth)
            img = cv2.imread(image.filename, cv2.IMREAD_GRAYSCALE)

            thresholded_img = cv2.adaptiveThreshold(img, 2**bit_depth, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                    cv2.THRESH_BINARY, cj.parameters.threshold_blocksize,
                                                    cj.parameters.threshold_constant)

            kernel = np.ones((5, 5), np.uint8)
            eroded_img = cv2.erode(thresholded_img, kernel, iterations=cj.parameters.erode_iterations)
            dilated_img = cv2.dilate(eroded_img, kernel, iterations=cj.parameters.dilate_iterations)

            extension = 10
            extended_img = cv2.copyMakeBorder(dilated_img, extension, extension, extension, extension,
                                              cv2.BORDER_CONSTANT, value=2**bit_depth)

            components = find_components(extended_img)
            zoom_factor = image.width / float(resized_width)
            for i, component in enumerate(components):
                converted = []
                for point in component[0]:
                    x = int((point[0] - extension) * zoom_factor)
                    y = int(image.height - ((point[1] - extension) * zoom_factor))
                    converted.append((x, y))

                components[i] = Polygon(converted)

            # Find largest component (whole image)
            largest = max(components, key=attrgetter('area'))
            components.remove(largest)

            # Only keep components greater than 5% of whole image
            min_area = int((cj.parameters.image_area_perc_threshold/100) * image.width * image.height)

            annotations = AnnotationCollection()
            for component in components:
                if component.area > min_area:
                    annotations.append(Annotation(location=component.wkt, id_image=image.id,
                                                  id_terms=[cj.parameters.cytomine_id_predicted_term],
                                                  id_project=cj.parameters.cytomine_id_project))

                    if len(annotations) % 100 == 0:
                        annotations.save()
                        annotations = AnnotationCollection()

            annotations.save()

        cj.job.update(statusComment="Finished.")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
