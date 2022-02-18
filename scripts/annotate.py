#!/usr/bin/env python
# -*- coding: utf-8 -*-


import omero.scripts as scripts
from omero.gateway import BlitzGateway
from omero.rtypes import rlong, rint, rstring, robject, unwrap, rdouble
from omero.model import RectangleI, EllipseI, LineI, PolygonI, PolylineI, \
    MaskI, LabelI, PointI, RoiI
from math import sqrt, pi
import re


# We have a helper function for creating an ROI and linking it to new shapes
def create_roi(img, shapes, updateService):
    # create an ROI, link it to Image
    roi = RoiI()
    # use the omero.model.ImageI that underlies the 'image' wrapper
    roi.setImage(img._obj)
    for shape in shapes:
        roi.addShape(shape)
    # Save the ROI (saves any linked shapes too)
    return updateService.saveAndReturnObject(roi)


# Another helper for generating the color integers for shapes
def rgba_to_int(red, green, blue, alpha=255):
    """ Return the color as an Integer in RGBA encoding """
    r = red << 24
    g = green << 16
    b = blue << 8
    a = alpha
    rgba_int = r+g+b+a
    if (rgba_int > (2**31-1)):       # convert to signed 32-bit int
        rgba_int = rgba_int - 2**32
    return rgba_int




def run_script():
    """The main entry point of the script, as called by the client."""
    data_types = [rstring('Dataset'), rstring('Image')]

    # Here are some variables you can ask the user before processing
    client = scripts.client(
        'Batch_ROI_Export.py',
        """Annotate image using ROIs for selected Images.""",

        # scripts.String(
        #     "Data_Type", optional=False, grouping="1",
        #     description="The data you want to work with.", values=data_types,
        #     default="Image"),

        scripts.List(
            "IDs", optional=False, grouping="2",
            description="List of Dataset IDs or Image IDs").ofType(rlong(0)),

        # scripts.List(
        #     "Channels", grouping="3", default=[0, 1, 2],
        #     description="Indices of Channels to measure intensity."
        # ).ofType(rint(0)),

        # scripts.Bool(
        #     "Export_All_Planes", grouping="4",
        #     description=("Export all Z and T planes for shapes "
        #                  "where Z and T are not set?"),
        #     default=False),

        # scripts.String(
        #     "File_Name", grouping="5", default=DEFAULT_FILE_NAME,
        #     description="Name of the exported CSV file"),

        authors=["William Moore", "OME Team"],
        institutions=["University of Dundee"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )

    try:
        conn = BlitzGateway(client_obj=client)

        script_params = client.getInputs(unwrap=True)

        # First we load our image and pick some parameters for shapes
        x = 50
        y = 200
        width = 10000
        height = 5000
        image = conn.getObject("Image", script_params["IDs"][0])
        z = 0
        t = 0

        # create a rectangle shape (added to ROI below)
        #client.setOutput("Message", rstring("Adding a rectangle at theZ: "+str(z)+", theT: "+str(t)+", X: "+str(x)+", Y: "+str(y)+", width: "+str(width)+", height: "+str(height)))
        client.setOutput("Message", rstring("Finished Annotating"))
        rect = RectangleI()
        rect.x = rdouble(x)
        rect.y = rdouble(y)
        rect.width = rdouble(width)
        rect.height = rdouble(height)
        rect.theZ = rint(z)
        rect.theT = rint(t)
        rect.textValue = rstring("test-Rectangle")
        rect.fillColor = rint(rgba_to_int(255, 255, 255, 255))
        rect.strokeColor = rint(rgba_to_int(255, 255, 0, 255))

        # create an Ellipse shape (added to ROI below)
        ellipse = EllipseI()
        ellipse.x = rdouble(y)
        ellipse.y = rdouble(x)
        ellipse.radiusX = rdouble(width)
        ellipse.radiusY = rdouble(height)
        ellipse.theZ = rint(z)
        ellipse.theT = rint(t)
        ellipse.textValue = rstring("test-Ellipse")

        # Create an ROI containing 2 shapes on same plane
        # NB: OMERO.insight client doesn't support display
        # of multiple shapes on a single plane.
        # Therefore the ellipse is removed later (see below)
        create_roi(image, [rect, ellipse], conn.getUpdateService())



        # log("script_params:")
        # log(script_params)

        # # call the main script
        # result = batch_roi_export(conn, script_params)

        # # Return message and file_annotation to client
        # if result is None:
        #     message = "No images found"
        # else:
        #     file_ann, message = result
        #     if file_ann is not None:
        #         client.setOutput("File_Annotation", robject(file_ann._obj))

        # client.setOutput("Message", rstring(message))

    finally:
        client.closeSession()


if __name__ == "__main__":
    run_script()