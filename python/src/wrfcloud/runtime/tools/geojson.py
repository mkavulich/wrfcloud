"""
Module to convert WRF output to GeoJSON
"""


from typing import Union
import json
import netCDF4
from matplotlib import colors
from matplotlib import contour
from matplotlib import pyplot
import numpy


class GeoJson:
    """
    Class to convert WRF output to GeoJSON MultiPolygon format
    """
    def __init__(self, wrf_file: str, variable: str, z_level: Union[int, None] = None):
        """
        Construct a WRF to GeoJSON converter
        :param wrf_file: Full path to the WRF output file
        :param variable: Name of the variable in the NetCDF file to convert
        :param z_level: Height level in the to convert
        """
        self.wrf_file = wrf_file
        self.variable = variable
        self.z_level = z_level
        self.grid = None
        self.grid_lat = None
        self.grid_lon = None

    def convert(self, out_file: Union[str, None]) -> Union[None, dict]:
        """
        Convert a field in a WRF output file to GeoJSON
        :param out_file: Full path to the output file (directory must exist) or None to get the
                         GeoJSON data returned as a dictionary
        """
        # open the NetCDF file and get the requested horizontal slice
        # pylint thinks that the Dataset class does not exist in netCDF4 pylint: disable=E1101
        wrf = netCDF4.Dataset(self.wrf_file)
        data = wrf[self.variable]
        time_index = 0
        grid = data[time_index][self.z_level] if self.z_level else data[time_index]

        # get the latitude and longitude grids
        self.grid_lat = wrf['XLAT'][0]
        self.grid_lon = wrf['XLONG'][0]

        # create a set of contours from the data grid
        contours: contour.QuadContourSet = pyplot.contourf(grid)

        # create a set of features for the GeoJSON file
        features = []

        # loop over each contour level
        for i, contour_line in enumerate(contours.collections):
            # get the hex color for this level
            level_color = colors.rgb2hex(contours.tcolors[i][0])

            # loop over each outer polygon and set of interior holes
            for path in contour_line.get_paths():

                # get the list of polygons for this set
                path_polygons = path.to_polygons()

                # skip if there are no polygons
                if len(path_polygons) == 0:
                    continue

                # the first polygon in the list is the outer polygon
                outer_polygon = self.polygon_to_coord_array(path_polygons[0])

                # the remaining polygons are holes in the outer polygon
                holes = [self.polygon_to_coord_array(hole) for hole in path_polygons[1:]]

                # get the string of the MultiPolygon coordinates for outer polygon and holes
                polygon_string = self.polygon_and_holes_to_multi_polygon(outer_polygon, holes)

                # create a GeoJSON feature as a dictionary
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [json.loads(polygon_string)]
                    },
                    "properties": {
                        "stroke-width": 0,
                        "fill": level_color,
                        "fill-opacity": 1
                    }
                }

                # add this MultiPolygon feature to the set of features
                features.append(feature)

        # create the GeoJSON document
        doc = {
            "type": "FeatureCollection",
            "features": features
        }

        # return the document if no output file was provided
        if out_file is None:
            return doc

        # write the data to a file or return as a string if no data were
        with open(out_file, 'w') as file:
            file.write(json.dumps(doc))
            file.flush()
            file.close()
        return None

    def grid_to_lonlat(self, x: float, y: float) -> (float, float):
        """
        Convert grid XY coordinates to longitude and latitude
        :param x: The X position on the grid
        :param y: The Y position on the grid
        :return: Longitude and latitude
        """
        # get the integer grid indices
        x1 = int(x)
        y1 = int(y)
        x2 = int(x) + 1 if x1 != round(x, 5) else x1
        y2 = int(y) + 1 if y1 != round(y, 5) else y1

        # get bounding lat/lon values for a linear interpolation
        lat1 = self.grid_lat[y1][x1]
        lon1 = self.grid_lon[y1][x1]
        lat2 = self.grid_lat[y2][x2]
        lon2 = self.grid_lon[y2][x2]

        # get the x and y grid value fractions for a linear interpolation
        x_frac = x - x1
        y_frac = y - y1

        # compute lat/lon values with a linear interpolation
        lat = lat1 + ((lat2 - lat1) * y_frac)
        lon = lon1 + ((lon2 - lon1) * x_frac)

        return round(lon, 5), round(lat, 5)

    def polygon_to_coord_array(self, polygon: numpy.ndarray) -> list[(float, float)]:
        """
        Convert a polygon contour path to a coordinate array
        """
        points = []
        for point in polygon:
            lonlat_point = self.grid_to_lonlat(point[0], point[1])
            points.append(lonlat_point)

        return points

    @staticmethod
    def polygon_and_holes_to_multi_polygon(polygon: list[list[float]], holes: list[list[list[float]]]) -> str:
        """
        Convert a polygon and zero or more holes to a GeoJSON multi-polygon coordinate string
        :param polygon: List of polygon coordinates
        :param holes: List of holes, where each hole is a list of polygon coordinates
        :return: GeoJSON-formatted MultiPolygon coordinate string
        """
        mp_str = str([[point[0], point[1]] for point in polygon])
        for hole in holes:
            mp_str += ',' + str([[point[0], point[1]] for point in hole])
        return '[' + mp_str + ']'


def main():
    """
    Command line entry point to run the converter
    """
    from argparse import ArgumentParser

    # parse the command line parameters
    parser = ArgumentParser(description='Convert WRF to GeoJSON format')
    parser.add_argument('--in-file', type=str, help='Full path to the WRF file', required=True)
    parser.add_argument('--out-file', type=str, help='Full path to the output file', required=False)
    parser.add_argument('--variable', type=str, help='Variable from the WRF file', required=True)
    parser.add_argument('--z-level', type=int, help='Z-level if a 3D field', required=False)
    args = parser.parse_args()

    # get the command line parameters
    wrf_file = args.in_file
    out_file = args.out_file or None
    variable = args.variable
    z_level = args.z_level or None

    # convert the WRF data to GeoJSON
    converter = GeoJson(wrf_file, variable, z_level)
    output = converter.convert(out_file)

    # print the output to stdout if we do not have an output file
    if output is not None:
        print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
