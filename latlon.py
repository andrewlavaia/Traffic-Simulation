import math


class LatLonConverter:
    def __init__(self, canvas, bot_lat, left_lon, top_lat, right_lon):
        self.canvas_width = canvas.width
        self.canvas_height = canvas.height
        self.top_lat = top_lat
        self.left_lon = left_lon
        self.bot_lat = bot_lat
        self.right_lon = right_lon

        # get global reference points to scale local x y appropriately
        self.tlx, self.tly = self.latLonToGlobalXY(self.top_lat, self.left_lon)
        self.brx, self.bry = self.latLonToGlobalXY(self.bot_lat, self.right_lon)
        self.x_range = abs(self.brx - self.tlx)
        self.y_range = abs(self.bry - self.tly)

    def latLonToGlobalXY(self, lat, lon):
        """converts latitude and longitude to global planar coordinates"""
        # equirectangular projection
        earth_radius = 6.371  # in km
        center_lat = (self.top_lat + self.bot_lat) / 2
        x = earth_radius * float(lon) * math.cos(math.radians(float(center_lat)))
        y = earth_radius * float(lat)
        return x, y

    def globalXYToLocalXY(self, x, y):
        """converts global planar coordinates to local coordinates"""
        local_x = (abs(self.tlx - x)/self.x_range) * self.canvas_width
        local_y = (abs(self.tly - y)/self.y_range) * self.canvas_height
        return local_x, local_y

    def latLonToLocalXY(self, lat, lon):
        global_x, global_y = self.latLonToGlobalXY(lat, lon)
        return self.globalXYToLocalXY(global_x, global_y)
