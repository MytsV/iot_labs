import asyncio
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer
from datasource import Datasource


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        self.datasource = Datasource()
        self.car_marker = MapMarker(lat=50.4501, lon=30.5234, source="images/car.png")

    def on_start(self):
        self.mapview.add_marker(self.car_marker)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        new_points = self.datasource.get_new_points()
        
        if not new_points:
            print("There is no new points for update")
            return

        for latitude, longitude, road_state in new_points:
            print(f"Updating car position: {latitude}, {longitude}")
            self.update_car_marker((latitude, longitude))
            
            if road_state == "pothole":
                print(f"Adding pothole: {latitude}, {longitude}")
                self.set_pothole_marker((latitude, longitude))
            elif road_state == "bump":
                print(f"Adding bump: {latitude}, {longitude}")
                self.set_bump_marker((latitude, longitude))


    def update_car_marker(self, point):
        self.car_marker.lat, self.car_marker.lon = point
        self.mapview.center_on(point[0], point[1])  

    def set_pothole_marker(self, point):
        pothole_marker = MapMarker(lat=point[0], lon=point[1], source="images/pothole.png")
        self.mapview.add_marker(pothole_marker)

    def set_bump_marker(self, point):
        bump_marker = MapMarker(lat=point[0], lon=point[1], source="images/bump.png")
        self.mapview.add_marker(bump_marker)

    def build(self):
        self.mapview = MapView(zoom=10, lat=50.4501, lon=30.5234)
        return self.mapview


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()