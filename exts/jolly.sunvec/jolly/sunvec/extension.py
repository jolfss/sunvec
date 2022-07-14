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
    
    def place_sun(self, name, sunvector_sph, color=(1,1,1)):
                create_distant_light(self.subdir, name)
                color_distant_light(self.subdir, name, color)
                intensity_distant_light(self.subdir, name, self.light_intensity)
                orient_distant_light(self.subdir, name, sunvector_sph)
    
    def cleanup(self):
            delete(self.subdir[0:len(self.subdir)-1])

    # Mode types, usually correspond to a visibility group.
    MODE_SUBDIVIDE = 0
    MODE_STEP = 1
    MODE_STEP_UNTIL = 2

    # Default Mode
    mode = MODE_SUBDIVIDE

    #Handles which ui elements are displayed at a time.
    visibles = VisibilityGroups()

    # Visibles are groups elements which are always displayed together and hidden together.
    vg_subdivide = Visibles("subdivide", default=True)
    vg_step = Visibles("step", default=False)
    vg_step_until = Visibles("step until", default=False)
    visibles.register_groups(vg_subdivide, vg_step, vg_step_until)

    def mode_subdivide(self):
        self.mode = self.MODE_SUBDIVIDE
        self.visibles.island_enable(self.vg_subdivide)
    
    def mode_step(self):
        self.mode = self.MODE_STEP
        self.visibles.island_enable(self.vg_step)
        
    def mode_step_until(self):
        self.mode = self.MODE_STEP_UNTIL
        self.visibles.island_enable(self.vg_step_until)


    ################################
    ### omniverse extension main ###
    ################################
    def on_startup(self, ext_id):
        sun_count = 50
        self.light_intensity = 100

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

        def update_incrementer(dummy_arg=None):
            years = read_int(is_increment_years)
            months = read_int(is_increment_months)
            days = read_int(is_increment_days)
            hours = read_int(is_increment_hours)
            minutes = read_int(is_increment_minutes)
            seconds = read_int(is_increment_seconds)
            self.timespan_increment = Timespan(years, months, days, hours, minutes, seconds)
            self.increment_step = read_int(is_increment_steps)

        def update_setting():
            set_setting_start()
            set_setting_end()
        
        def update_simulation(dummy_arg=None):
            update_setting()
            polysun()
        
        # Remove defaultLight TODO: Disable all non-Jolly lighting instead.
        create_distant_light("/World/", "defaultLight")
        delete("/World/defaultLight") 

        print("JOLLY.SUNVEC..startup")

        ### Omniverse UI
        self._window = ui.Window("JOLLY.SUNVEC", width=500, height=1100)
        with self._window.frame:
            with ui.VStack(height=30):
                # Set location.
                ff_lat = float_field("Latitude", -90, 90)
                ff_long = float_field("Longitude", -180, 180)
                is_timezone = int_slider("Timezone (from UTC)",-12, 14)

                separate(15)
                
                # Increment Mode
                def increment_changed_fn(combo_model : ui.AbstractItemModel, item : ui.AbstractItem):
                        mode = combo_model.get_item_value_model().as_int
                        if mode == 0:   self.visibles.island_enable(self.vg_subdivide)
                        elif mode == 1: self.visibles.island_enable(self.vg_step)
                        elif mode == 2: self.visibles.island_enable(self.vg_step_until)
                        update_simulation()
                combo_box("Increment Type",\
                    ("Subdivide", "Step", "Step Until"), (ITEM_CHANGED, increment_changed_fn))
                
                # Incremental Stepsize
                frame_increment = ui.Frame() ### VISION GROUP
                self.vg_step.add(frame_increment)
                self.vg_step_until.add(frame_increment)
                with frame_increment:
                    separate()
                    ui.Label("Incremental Step", height=30)
                    with ui.HStack():
                        with ui.VStack(): is_increment_years = int_slider("Years", 0, 10, (END_EDIT, update_incrementer))
                        with ui.VStack(): is_increment_months = int_slider("Months", 0, 12, (END_EDIT, update_incrementer))
                        with ui.VStack(): is_increment_days = int_slider("Days", 0, 31, (END_EDIT, update_incrementer))  # TODO: Sync with month. Add listener?
                        with ui.VStack(): is_increment_hours = int_slider("Hours", 0, 23, (END_EDIT, update_incrementer))
                        with ui.VStack(): is_increment_minutes = int_slider("Minutes", 0, 59, (END_EDIT, update_incrementer))
                        with ui.VStack(): is_increment_seconds = int_slider("Seconds", 0, 59, (END_EDIT, update_incrementer))

                is_increment_steps = int_slider("Number of Increment Steps", 0, 100, \
                    (END_EDIT, update_incrementer))
                
                separate()

                ### Time and Day Parameters
                with ui.HStack():
                    # Start Setting
                    with ui.VStack(height=15):
                        lb_start_date = labeled_label("Starting Date", height=30)
                        is_start_year = int_slider("Year", 1901, 2099, (END_EDIT, update_simulation))
                        is_start_month = int_slider("Month", 1, 12, (END_EDIT, update_simulation))
                        is_start_day = int_slider("Day", 1, 31, (END_EDIT, update_simulation))  # TODO: Sync with month. Add listener?
                        is_start_hour = int_slider("Hour", 0, 23, (END_EDIT, update_simulation))
                        is_start_minute = int_slider("Minute", 0, 59, (END_EDIT, update_simulation))
                        is_start_second = int_slider("Second", 0, 59, (END_EDIT, update_simulation))
                        ui.Spacer(width=10)

                    ui.Spacer(width=10)

                    # End Setting
                    vstack_end_setting = ui.VStack(height=15) ### VISION GROUP
                    self.vg_subdivide.add(vstack_end_setting)
                    self.vg_step_until.add(vstack_end_setting)
                    with vstack_end_setting:
                        lb_end_date = labeled_label("Ending Date", height=30)
                        is_end_year = int_slider("Year", 1901, 2099, (END_EDIT, update_simulation))
                        is_end_month = int_slider("Month", 1, 12, (END_EDIT, update_simulation))
                        is_end_day = int_slider("Day", 1, 31, (END_EDIT, update_simulation))  # TODO: Sync with month. Add listener?
                        is_end_hour = int_slider("Hour", 0, 23, (END_EDIT, update_simulation))
                        is_end_minute = int_slider("Minute", 0, 59, (END_EDIT, update_simulation))
                        is_end_second = int_slider("Second", 0, 59, (END_EDIT, update_simulation))
                    
                ui.Label(""); ui.Separator(height=15)

                # Options for Color & Accessibility
                ui.Label("Color Settings", height=45)
                with ui.VStack():
                    check_colors = check_box("Enable Colors", (VALUE_CHANGED, update_simulation))

                    def color_filter_changed_fn(combo_model : ui.AbstractItemModel, item : ui.AbstractItem):
                        mode = combo_model.get_item_value_model().as_int
                        if mode == 0:   self.vision_type =  VisionType.FULLCOLOR
                        elif mode == 1: self.vision_type =  VisionType.PROTANOPIA
                        elif mode == 2: self.vision_type =  VisionType.DEUTERANOPIA
                        elif mode == 3: self.vision_type =  VisionType.TRITANOPIA
                        update_simulation()
                    combo_box("Colorblind Options",\
                        ("Full Color", "Protanopia", "Deuteranopia", "Tritanopia"), (ITEM_CHANGED, color_filter_changed_fn))

                def sun_count_changed_fn(sun_count_model : ui.AbstractValueModel):
                    sun_count = sun_count_model.as_int
                    update_simulation()

                is_sun_count = int_slider("Solar Path Refinement", 0, 365, (END_EDIT, sun_count_changed_fn))

                ui.Label("Light Intensity")
                is_light_intensity = ui.IntSlider(min=0,max=200)
                def light_intensity_changed_fn(is_light_intensity : ui.AbstractValueModel):
                    self.light_intensity = is_light_intensity.as_int
                    update_simulation()
                is_light_intensity.model.add_end_edit_fn(light_intensity_changed_fn)
                
                ui.Label(""); ui.Separator(height=15)
                ui.Button("Place Sun", clicked_fn=lambda: polysun(), height=50)

                ui.Button("Clean-Up", clicked_fn=lambda: self.cleanup(), height=50)

                self.vg_subdivide.set_state(True)
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
        
        write(is_start_year, today_year); write(is_end_year, today_year)
        write(is_start_month, today_month); write(is_end_month, today_month)
        write(is_start_day, today_day); write(is_end_day, today_day)
        write(is_start_hour, today_hour - 1); write(is_end_hour, today_hour + 1)
        write(is_start_minute, today_minute); write(is_end_minute, today_minute)
        write(is_start_second, today_second); write(is_end_second, today_second)
        write(ff_long, my_long); write(ff_lat, my_lat)
        write(is_timezone, my_timezone)

        inc_steps = 24
        inc_hours = 1

        write(is_increment_steps, inc_steps)
        write(is_increment_hours, inc_hours)

        my_suns = 50
        my_intensity = 100

        write(is_sun_count, my_suns)
        write(is_light_intensity, my_intensity)

        # Write to label
        update_setting()

        def polysun():
            self.cleanup()  # TODO: Smart cleanup; don't recalculate positions if only color change..etc.
            update_setting()
            update_incrementer()
            if self.mode == 0:
                sets = SettingRange(self.setting_start, self.setting_end).subdiv_range(sun_count)
            elif self.mode == 1:
                timespan = self.timespan_increment
                sets = SettingRange(self.setting_start, self.setting_end).increment_range(timespan)
            elif self.mode == 2:
                timespan = self.timespan_increment
                sets = SettingRange(self.setting_start, self.setting_end).increment_until_range(timespan)

            myspectrum = Spectrum(sets)
            i = 0
            for s in sets:
                #print(F"{i}-->{s}"); 
                i += 1
                theta, phi = self.sunvec(s)
                sunvector = sunvector_spherical(theta, phi)
                if read_bool(check_colors):
                    self.place_sun(F"sunVector{i}", sunvector, RingColor(myspectrum, self.vision_type).color(i))
                else:
                    self.place_sun(F"sunVector{i}", sunvector)

    def on_shutdown(self):
        self.cleanup()
        print("JOLLY.SUNVEC..shutdown")
