from math import pi
from jolly.sunvec.setting import Setting, SettingRange, Timespan
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
    
        sun_count = 50
        light_intensity = 100
        increment_mode = 0
        # Directory for extension primitives.
        create_scope(self.subdir[0:len(self.subdir)-1])
        
        # READ the user forms and MUTATE [setting_start] to match.
        def set_setting_start():
            lat = read_float(ff_lat)
            long = read_float(ff_long)

            year = read_int(is_start_year)
            month = read_int(is_start_month)
            day = read_int(is_start_day)
            hour = read_int(is_start_hour)
            minute = read_int(is_start_minute)
            second = read_int(is_start_second)
            timezone = read_int(is_timezone)

            self.setting_start = Setting(lat, long, year, month, day, hour, minute, second, timezone)
            lb_start_date.text = str(self.setting_start)

        def set_setting_end():
            lat = read_float(ff_lat)
            long = read_float(ff_long)

            year = read_int(is_end_year)
            month = read_int(is_end_month)
            day = read_int(is_end_day)
            hour = read_int(is_end_hour)
            minute = read_int(is_end_minute)
            second = read_int(is_end_second)
            timezone = read_int(is_timezone)
            self.setting_end = Setting(lat, long, year, month, day, hour, minute, second, timezone)
            lb_end_date.text = str(self.setting_end)

        def set_setting_end_visibility(visible):
            vstack_end_setting.visible = visible
            spacer_end_setting.visible = visible

        def update_incrementer(dummy_arg):
            years = read_int(is_increment_years)
            months = read_int(is_increment_months)
            days = read_int(is_increment_days)
            hours = read_int(is_increment_hours)
            minutes = read_int(is_increment_minutes)
            seconds = read_int(is_increment_seconds)
            self.timespan_increment = Timespan(years, months, days, hours, minutes, seconds)
            self.increment_step = read_int(is_increment_steps)

        def set_incrementer_visibility(visible):
            lb_incremental_step.visible = visible
            sep_incremental_step.visible = visible
            lb_incremental_blank_sep.visible = visible
            hstack_incremental_step.visible = visible
            if self.increment_mode == 1:
                lb_increment_steps.visible = True
                is_increment_steps.visible = True
            else:
                lb_increment_steps.visible = False
                is_increment_steps.visible = False
                
            if self.increment_mode == 0:
                lb_sun_count.visible = True
                is_sun_count.visible = True
            else:
                lb_sun_count.visible = False
                is_sun_count.visible = False

        def update_setting():
            set_setting_start()
            set_setting_end()
        
        def update_simulation(dummy_arg):
            update_setting()
            polysun()
        
        # Remove defaultLight TODO: Disable all non-Jolly lighting instead.
        create_distant_light("/World/", "defaultLight")
        delete("/World/defaultLight") 

        print("JOLLY.SUNVEC..startup")

        ### START OF UI BLOCK ###
        self._window = ui.Window("JOLLY.SUNVEC", width=500, height=1100)
        with self._window.frame:
            with ui.VStack(height=30):
                # Set location.
                ui.Label("Latitude")
                ff_lat = ui.FloatField()
                ui.Label("Longitude")
                ff_long = ui.FloatField()
                ui.Label("Timezone (from UTC)")
                is_timezone = ui.IntSlider(min=-12,max=14)
                ui.Label(""); ui.Separator(height=15)

                ui.Label("Increment Mode",height=15)

                cb_increment_mode = ui.ComboBox(0,"Start to End", "Start and Increment", "Start and Increment Until End").model
                def increment_changed_fn(combo_model : ui.AbstractItemModel, item : ui.AbstractItem):
                    self.increment_mode = combo_model.get_item_value_model().as_int
                    if self.increment_mode == 0:
                        set_setting_end_visibility(True)
                        set_incrementer_visibility(False)
                    elif self.increment_mode == 1:
                        set_setting_end_visibility(False)
                        set_incrementer_visibility(True)
                    elif self.increment_mode == 2:
                        set_setting_end_visibility(True)
                        set_incrementer_visibility(True)
                cb_increment_mode.add_item_changed_fn(increment_changed_fn)
                
                ### VISIBLE IF [incrementer_mode == 1 or 2]
                lb_incremental_blank_sep = ui.Label("", height=15, visible=False)
                sep_incremental_step = ui.Separator(visible=False)
                lb_incremental_step = ui.Label("Incremental Step", height=30, visible=False)

                hstack_incremental_step = ui.HStack(visible=False)
                with hstack_incremental_step:
                    with ui.VStack():
                        ui.Label("Years")
                        is_increment_years = ui.IntSlider(min=0,max=10)
                        is_increment_years.model.add_end_edit_fn(update_incrementer)
                    with ui.VStack():
                        ui.Label("Months")
                        is_increment_months = ui.IntSlider(min=0,max=11)
                        is_increment_months.model.add_end_edit_fn(update_incrementer)
                    with ui.VStack():
                        ui.Label("Days")
                        is_increment_days = ui.IntSlider(min=0,max=31)
                        is_increment_days.model.add_end_edit_fn(update_incrementer)
                    with ui.VStack():
                        ui.Label("Hours")
                        is_increment_hours = ui.IntSlider(min=0,max=23)
                        is_increment_hours.model.add_end_edit_fn(update_incrementer)
                    with ui.VStack():
                        ui.Label("Minutes")
                        is_increment_minutes = ui.IntSlider(min=0,max=59)
                        is_increment_minutes.model.add_end_edit_fn(update_incrementer)
                    with ui.VStack():
                        ui.Label("Seconds")
                        is_increment_seconds = ui.IntSlider(min=0,max=59)
                        is_increment_seconds.model.add_end_edit_fn(update_incrementer)
                ### VISIBLE IF [incrementer_mode == 1]
                lb_increment_steps = ui.Label("Increment Steps",height=30,visible=False)
                is_increment_steps = ui.IntSlider(min=0,max=100,visible=False)
                is_increment_months.model.add_end_edit_fn(update_incrementer)
                ### END VISIBLE
                ### END VISIBLE
                update_incrementer(None)  # Hides the Incrementer by default (mode = 0)

                ui.Label(""); ui.Separator()
                with ui.HStack():
                    # Collects [setting_start] parameters.
                    with ui.VStack(height=15) as start_params:  # Why doesn't "as" do anything here?"
                        ui.Label("Starting Date", height=30)
                        lb_start_date = ui.Label(" ")
                        ui.Label("Year",height=30)
                        is_start_year = ui.IntSlider(min=1901,max=2099)
                        is_start_year.model.add_end_edit_fn(update_simulation)
                        ui.Label("Month")
                        is_start_month = ui.IntSlider(min=1,max=12)
                        is_start_month.model.add_end_edit_fn(update_simulation)
                        ui.Label("Day")
                        is_start_day = ui.IntSlider(min=1,max=31)
                        is_start_day.model.add_end_edit_fn(update_simulation)
                        ui.Label("Hour")
                        is_start_hour = ui.IntSlider(min=0,max=23)
                        is_start_hour.model.add_end_edit_fn(update_simulation)
                        ui.Label("Minute")
                        is_start_minute = ui.IntSlider(min=0,max=59)
                        is_start_minute.model.add_end_edit_fn(update_simulation)
                        ui.Label("Second")
                        is_start_second = ui.IntSlider(min=0,max=59)
                        is_start_second.model.add_end_edit_fn(update_simulation)
                        # start_params == None
                    spacer_end_setting = ui.Spacer(width=10)

                    # Collects [setting_end] parameters.
                    vstack_end_setting = ui.VStack(height=15)
                    with vstack_end_setting:
                        ### VISIBLE IF [increment_mode == 0 or 2]
                        ui.Label("Ending Date", height=30)
                        lb_end_date = ui.Label("")
                        ui.Label("Year",height=30)
                        is_end_year = ui.IntSlider(min=1901,max=2099)
                        is_end_year.model.add_end_edit_fn(update_simulation)
                        ui.Label("Month")
                        is_end_month = ui.IntSlider(min=1,max=12)
                        is_end_month.model.add_end_edit_fn(update_simulation)
                        ui.Label("Day")
                        is_end_day = ui.IntSlider(min=1,max=31)
                        is_end_day.model.add_end_edit_fn(update_simulation)
                        ui.Label("Hour")
                        is_end_hour = ui.IntSlider(min=0,max=23)
                        is_end_hour.model.add_end_edit_fn(update_simulation)
                        ui.Label("Minute")
                        is_end_minute = ui.IntSlider(min=0,max=59)
                        is_end_minute.model.add_end_edit_fn(update_simulation)
                        ui.Label("Second")
                        is_end_second = ui.IntSlider(min=0,max=59)
                        is_end_second.model.add_end_edit_fn(update_simulation)
                        ### END VISIBLE
                ui.Label(""); ui.Separator(height=15)

                # Options for Color & Accessibility
                ui.Label("Color Settings", height=45)
                with ui.VStack():
                    ui.Label("Enable Colors", height=0)
                    cb_colors_on = ui.CheckBox(height=15)
                    cb_colors_on.model.add_value_changed_fn(update_simulation)
                    ui.Label("Colorblind Options", height=0)

                    cb_color_filter = ui.ComboBox(0,"Full Color","Protanopia","Deuteranopia","Tritanopia").model
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
                        update_simulation(None)
                    cb_color_filter.add_item_changed_fn(filter_changed_fn)

                ### VISIBLE IF [increment_mode == 0]
                lb_sun_count = ui.Label("Solar Path Refinement")
                is_sun_count = ui.IntSlider(min=0,max=365)
                def sun_count_changed_fn(sun_count_model : ui.AbstractValueModel):
                    sun_count = sun_count_model.as_int
                    update_simulation(None)
                is_sun_count.model.add_end_edit_fn(sun_count_changed_fn)
                ### END VISIBLE

                ui.Label("Light Intensity")
                is_light_intensity = ui.IntSlider(min=0,max=200)
                def light_intensity_changed_fn(is_light_intensity : ui.AbstractValueModel):
                    light_intensity = is_light_intensity.as_int
                    update_simulation(None)
                is_light_intensity.model.add_end_edit_fn(light_intensity_changed_fn)
                
                ui.Label(""); ui.Separator(height=15)
                ui.Button("Place Sun", clicked_fn=lambda: polysun(), height=50)

                ui.Button("Clean-Up", clicked_fn=lambda: self.cleanup(), height=50)

                ### END OF UI BLOCK ###

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

        write(is_start_year, today_year); write(is_end_year, today_year)
        write(is_start_month, today_month); write(is_end_month, today_month)
        write(is_start_day, today_day); write(is_end_day, today_day)
        write(is_start_hour, today_hour - 1); write(is_end_hour, today_hour + 1)
        write(is_start_minute, today_minute); write(is_end_minute, today_minute)
        write(is_start_second, today_second); write(is_end_second, today_second)
        write(ff_long, my_long); write(ff_lat, my_lat)
        write(is_timezone, my_timezone)

        write(is_sun_count, my_suns)
        write(is_light_intensity, my_intensity)

        # Write to label
        update_setting()

        def place_sun(name, sunvector_sph, color=(1,1,1)):
                        create_distant_light(self.subdir, name)
                        color_distant_light(self.subdir, name, color)
                        intensity_distant_light(self.subdir, name, light_intensity)
                        orient_distant_light(self.subdir, name, sunvector_sph)

        def polysun():
            self.cleanup()  # TODO: Smart cleanup; don't recalculate positions if only color change..etc.
            update_setting()
            if increment_mode == 0:
                sets = SettingRange(self.setting_start, self.setting_end).subdiv_range(sun_count)
            elif increment_mode == 1:
                ts = self.timespan_increment
                sets = SettingRange(self.setting_start, self.setting_end).increment_range(ts)
            elif increment_mode == 2:
                sets = SettingRange(self.setting_start, self.setting_end).increment_until_range(ts)

            myspectrum = Spectrum(sets)
            i = 0
            for s in sets:
                #print(F"{i}-->{s}"); 
                i += 1
                theta, phi = self.sunvec(s)
                sunvector = sunvector_spherical(theta, phi)
                if read_bool(cb_colors_on):
                    place_sun(F"sunVector{i}", sunvector, RingColor(myspectrum, self.vision_type).color(i))
                else:
                    place_sun(F"sunVector{i}", sunvector)

    def on_shutdown(self):
        self.cleanup()
        print("JOLLY.SUNVEC..shutdown")
