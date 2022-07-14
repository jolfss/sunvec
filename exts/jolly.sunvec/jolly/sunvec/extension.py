from math import pi
from jolly.sunvec.setting import Setting, SettingRange
from jolly.sunvec.spectrum import RingColor, Spectrum, VisionType
from jolly.sunvec.sunpos import sunpos
from jolly.sunvec.cmds_common import *
from jolly.sunvec.ui_common import *
from jolly.sunvec.util import *
import omni.ext
import omni.ui as ui
import omni.kit.commands
import omni.usd
from datetime import datetime

# Any class derived from `omni.ext.IExt` in top level module (defined in `python.modules` of `extension.toml`) will be
# instantiated when extension gets enabled and `on_startup(ext_id)` will be called. Later when extension gets disabled
# on_shutdown() is called.
class SunVec(omni.ext.IExt):
    # The scope for all content related to this extension.
    # NOTE: Assumes no one would possibly have a /World/JollyBin directory.
    subdir = "/World/JollyBin/"
    vision_type = VisionType.FULLCOLOR  # Assume FULLCOLOR by default.

    def sunvec(self, setting: Setting):
        azimuth, elevation = sunpos(setting.get_date(), setting.get_loc(), True)
        azimuth = rad(azimuth)
        elevation = rad(elevation)
        return(azimuth, pi/2 - elevation)
    
    def cleanup(self):
            delete("/World/JollyBin")

    # ext_id is current extension id. It can be used with extension manager to query additional information, like where
    # this extension is located on filesystem.
    def on_startup(self, ext_id):
        

        self.sun_count = 50
        self.light_intensity = 100
        # Directory for extension primitives.
        create_scope(self.subdir[0:len(self.subdir)-1])
        
        # READ the user forms and MUTATE [setting_start] to match.
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

        def update_setting():
            set_setting_start()
            set_setting_end()
        
        def update_simulation(avm):
            update_setting()
            polysun()
        
        # Remove defaultLight TODO: Disable all non-Jolly lighting instead.
        create_distant_light("/World/", "defaultLight")
        delete("/World/defaultLight") 

        print("JOLLY.SUNVEC..startup")
        
        # Construct UI
        self._window = ui.Window("JOLLY.SUNVEC", width=500, height=800)
        with self._window.frame:
            with ui.VStack(height=30):
                # Set location.
                ui.Label("Latitude")
                self.ff_lat = ui.FloatField()
                ui.Label("Longitude")
                self.ff_long = ui.FloatField()
                ui.Label("Timezone (from UTC)")
                self.is_timezone = ui.IntSlider(min=-12,max=14)
                with ui.HStack():
                    # Collects [setting_start] parameters.
                    with ui.VStack(height=30) as start_params:  # Why doesn't "as do anything here?"
                        ui.Label("Starting Date", height=30)
                        lb_start_date = ui.Label("")
                        ui.Label("Year")
                        self.is_start_year = ui.IntSlider(min=1901,max=2099)
                        self.is_start_year.model.add_end_edit_fn(update_simulation)
                        ui.Label("Month")
                        self.is_start_month = ui.IntSlider(min=1,max=12)
                        self.is_start_month.model.add_end_edit_fn(update_simulation)
                        ui.Label("Day")
                        self.is_start_day = ui.IntSlider(min=1,max=31)
                        self.is_start_day.model.add_end_edit_fn(update_simulation)
                        ui.Label("Hour")
                        self.is_start_hour = ui.IntSlider(min=0,max=23)
                        self.is_start_hour.model.add_end_edit_fn(update_simulation)
                        ui.Label("Minute")
                        self.is_start_minute = ui.IntSlider(min=0,max=59)
                        self.is_start_minute.model.add_end_edit_fn(update_simulation)
                        ui.Label("Second")
                        self.is_start_second = ui.IntSlider(min=0,max=59)
                        self.is_start_second.model.add_end_edit_fn(update_simulation)
                        # start_params == None
                    ui.Separator(width=10)
                    # Collects [setting_end] parameters.
                    with ui.VStack(height=30):
                        ui.Label("Ending Date", height=30)
                        lb_end_date = ui.Label("")
                        ui.Label("Year")
                        self.is_end_year = ui.IntSlider(min=1901,max=2099)
                        self.is_end_year.model.add_end_edit_fn(update_simulation)
                        ui.Label("Month")
                        self.is_end_month = ui.IntSlider(min=1,max=12)
                        self.is_end_month.model.add_end_edit_fn(update_simulation)
                        ui.Label("Day")
                        self.is_end_day = ui.IntSlider(min=1,max=31)
                        self.is_end_day.model.add_end_edit_fn(update_simulation)
                        ui.Label("Hour")
                        self.is_end_hour = ui.IntSlider(min=0,max=23)
                        self.is_end_hour.model.add_end_edit_fn(update_simulation)
                        ui.Label("Minute")
                        self.is_end_minute = ui.IntSlider(min=0,max=59)
                        self.is_end_minute.model.add_end_edit_fn(update_simulation)
                        ui.Label("Second")
                        self.is_end_second = ui.IntSlider(min=0,max=59)
                        self.is_end_second.model.add_end_edit_fn(update_simulation)

                # Options for Color & Accessibility
                ui.Label("Color Settings", height=45)
                with ui.VStack():
                    ui.Label("Enable Colors", height=0)
                    self.cb_colors_on = ui.CheckBox(height=15)
                    self.cb_colors_on.model.add_value_changed_fn(update_simulation)
                    ui.Label("Colorblind Options", height=0)

                    self.cb_color_filter = ui.ComboBox(0,"Full Color","Protanopia","Deuteranopia","Tritanopia").model
                    def filter_changed_fn(combo_model : ui.AbstractItemModel, item : ui.AbstractItem):
                        mode = combo_model.get_item_value_model().as_int
                        if mode == 0:
                            self.vision_type = VisionType.FULLCOLOR
                        elif mode == 1:
                            self.vision_type = VisionType.PROTANOPIA
                        elif mode == 2:
                            self.vision_type = VisionType.DEUTERANOPIA
                        elif mode == 3:
                            self.vision_type = VisionType.TRITANOPIA
                        else:
                            print("JOLLY.SUNVEC..unknown vision_type inputted, resetting to default -> FULLCOLOR")
                        update_simulation(None)
                    self.cb_color_filter.add_item_changed_fn(filter_changed_fn)

                ui.Label("Solar Path Refinement")
                self.is_sun_count = ui.IntSlider(min=0,max=365)
                def sun_count_changed_fn(sun_count_model : ui.AbstractValueModel):
                    self.sun_count = sun_count_model.as_int
                    update_simulation(None)
                self.is_sun_count.model.add_end_edit_fn(sun_count_changed_fn)

                ui.Label("Light Intensity")
                self.is_light_intensity = ui.IntSlider(min=0,max=200)
                def light_intensity_changed_fn(is_light_intensity : ui.AbstractValueModel):
                    self.light_intensity = is_light_intensity.as_int
                    update_simulation(None)
                self.is_light_intensity.model.add_end_edit_fn(light_intensity_changed_fn)

                ui.Button("Place Sun", clicked_fn=lambda: polysun(), height=50)

                ui.Button("Clean-Up", clicked_fn=lambda: self.cleanup(), height=50)

        # For cleanliness, initialize to minimums to current day morning -> evening.
        today_year = datetime.now().year
        today_month = datetime.now().month
        today_day = datetime.now().day
        today_hour = datetime.now().hour
        today_minute = datetime.now().minute
        today_second = datetime.now().second
        my_timezone = -4
        my_lat = 42.4534
        my_long = -76.4735  # -76 E = 76 W
        my_suns = 50
        my_intensity = 100

        write(self.is_start_year, today_year); write(self.is_end_year, today_year)
        write(self.is_start_month, today_month); write(self.is_end_month, today_month)
        write(self.is_start_day, today_day); write(self.is_end_day, today_day)
        write(self.is_start_hour, today_hour - 1); write(self.is_end_hour, today_hour + 1)
        write(self.is_start_minute, today_minute); write(self.is_end_minute, today_minute)
        write(self.is_start_second, today_second); write(self.is_end_second, today_second)
        write(self.ff_long, my_long); write(self.ff_lat, my_lat)
        write(self.is_timezone, my_timezone)

        write(self.is_sun_count, my_suns)
        write(self.is_light_intensity, my_intensity)

        def place_sun(name, sunvector_sph, color=(1,1,1)):
                        create_distant_light(self.subdir, name)
                        color_distant_light(self.subdir, name, color)
                        intensity_distant_light(self.subdir, name, self.light_intensity)
                        orient_distant_light(self.subdir, name, sunvector_sph)

        def polysun():
            self.cleanup()
            update_setting()
            sets = SettingRange(self.setting_start, self.setting_end).subdiv_range(self.sun_count)
            myspectrum = Spectrum(sets)
            i = 0
            for s in sets:
                #print(F"{i}-->{s}"); 
                i += 1
                theta, phi = self.sunvec(s)
                sunvector = sunvector_spherical(theta, phi)
                if read_bool(self.cb_colors_on):
                    place_sun(F"sunVector{i}", sunvector, RingColor(myspectrum, self.vision_type).color(i))
                else:
                    place_sun(F"sunVector{i}", sunvector)

    def on_shutdown(self):
        self.cleanup()
        print("JOLLY.SUNVEC..shutdown")
