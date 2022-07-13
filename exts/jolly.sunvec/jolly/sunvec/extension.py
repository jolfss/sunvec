from math import cos, pi, sin
from time import altzone
from jolly.sunvec.setting import Setting, SettingRange
from jolly.sunvec.sunpos import sunpos
from jolly.sunvec.kit_cmds_interface import *
from jolly.sunvec.omni_ui_interface import *
from jolly.sunvec.util import *
import omni.ext
import omni.ui as ui
import omni.kit.commands
import omni.usd

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class SunVec(omni.ext.IExt):
    # The scope for all content related to this extension.
    # NOTE: Assumes no one would possibly have a /JollyBin directory.
    subdir = "/World/JollyBin/"
    def sunvec(self, setting: Setting):
        azimuth, elevation = sunpos(setting.get_date(), setting.get_loc(), True)
        azimuth = rad(azimuth)
        elevation = rad(elevation)
        return(azimuth, pi/2 - elevation)

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):

        create_scope(self.subdir)
        
        def set_setting_start():
            lat = read_float(self.ff_lat)
            long = read_float(self.ff_long)

            year = read_int(self.is_start_year)
            month = read_int(self.is_start_month)
            day = read_int(self.is_start_day)
            hour = read_int(self.is_start_hour)
            minute = read_int(self.is_start_minute)
            second = read_int(self.is_start_second)
            timezone = read_int(self.is_timezone)

            self.setting_start = Setting(lat, long, year, month, day, hour, minute, second, timezone)
            lb_start_date.text = str(self.setting_start)

        def set_setting_end():
            lat = read_float(self.ff_lat)
            long = read_float(self.ff_long)

            year = read_int(self.is_end_year)
            month = read_int(self.is_end_month)
            day = read_int(self.is_end_day)
            hour = read_int(self.is_end_hour)
            minute = read_int(self.is_end_minute)
            second = read_int(self.is_end_second)
            timezone = read_int(self.is_timezone)
            self.setting_end = Setting(lat, long, year, month, day, hour, minute, second, timezone)
            lb_end_date.text = str(self.setting_end)
        

        create_distant_light("/World/", "defaultLight")
        delete("/World/defaultLight") #Apparently it's easier to just create and remove...

        print("JOLLY.SUNVEC..startup")
        
        self._window = ui.Window("JOLLY.SUNVEC", width=500, height=750)
        with self._window.frame:
            with ui.VStack(height=30):
                ui.Label("Latitude")
                self.ff_lat = ui.FloatField()
                ui.Label("Longitude")
                self.ff_long = ui.FloatField()
                ui.Label("Timezone (from UTC)")
                self.is_timezone = ui.IntSlider(min=-12,max=14)
                with ui.HStack():
                    with ui.VStack(height=30):
                        ui.Label("Starting Date", height=30)
                        lb_start_date = ui.Label("")
                        ui.Label("Year")
                        self.is_start_year = ui.IntSlider(min=1901,max=2099)
                        ui.Label("Month")
                        self.is_start_month = ui.IntSlider(min=1,max=12)
                        ui.Label("Day")
                        self.is_start_day = ui.IntSlider(min=1,max=31)
                        ui.Label("Hour")
                        self.is_start_hour = ui.IntSlider(min=0,max=23)
                        ui.Label("Minute")
                        self.is_start_minute = ui.IntSlider(min=0,max=59)
                        ui.Label("Second")
                        self.is_start_second = ui.IntSlider(min=0,max=59)
                    ui.Separator(width=10)
                    with ui.VStack(height=30):
                        ui.Label("Ending Date", height=30)
                        lb_end_date = ui.Label("")
                        ui.Label("Year")
                        ##YOOOOOOOOO
                        self.is_end_year = ui.IntSlider(min=1901,max=2099)
                        ui.Label("Month")
                        self.is_end_month = ui.IntSlider(min=1,max=12)
                        ui.Label("Day")
                        self.is_end_day = ui.IntSlider(min=1,max=31)
                        ui.Label("Hour")
                        self.is_end_hour = ui.IntSlider(min=0,max=23)
                        ui.Label("Minute")
                        self.is_end_minute = ui.IntSlider(min=0,max=59)
                        ui.Label("Second")
                        self.is_end_second = ui.IntSlider(min=0,max=59)

                ui.Label("Incremental Input", height=30)
                self.increment = ui.StringField(min=1,max=12)

                def place_sun(name, sunvector_sph):
                    create_distant_light(self.subdir, name)
                    orient_distant_light(self.subdir, name, sunvector_sph)

                def polysun(n):
                    set_setting_start()
                    set_setting_end()
                    i = 0
                    sets = SettingRange(self.setting_start, self.setting_end).subdiv_range(n)
                    for s in sets:
                        print(F"{i}-->{s}"); i += 1
                        theta, phi = self.sunvec(s, True)
                        sunvector = sunvector_spherical(theta, phi)
                        place_sun(F"sunVector{i}", sunvector)
                    
                ui.Button("Place Sun", clicked_fn=lambda: polysun(50), height=50)


                def cleanup():
                    delete("/World/JollyBin")
                ui.Button("Clean-Up", clicked_fn=lambda: cleanup(), height=50)

        # For cleanliness, initialize to minimums for sliders.
        write(self.is_end_year, 1901); write(self.is_start_year, 1901)
        write(self.is_end_month, 1); write(self.is_start_month, 1)
        write(self.is_end_day, 1); write(self.is_start_day, 1)
        write(self.is_end_hour, 0); write(self.is_start_hour, 0)
        write(self.is_end_minute, 0); write(self.is_start_minute, 0)
        write(self.is_end_second, 0); write(self.is_start_second, 0)

    def on_shutdown(self):
        print("JOLLY.SUNVEC..shutdown")
