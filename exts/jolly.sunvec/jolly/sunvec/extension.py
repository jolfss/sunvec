from math import pi
from jolly.sunvec.setting import Setting, SettingRange, Timespan
from jolly.sunvec.spectrum import *
from jolly.sunvec.sunpos import sunpos
from jolly.sunvec.cmds_common import *
from jolly.sunvec.ui_common import *
from jolly.sunvec.util import *
import omni.ext
import omni.ui as ui
import omni.kit.commands
import omni.usd
from datetime import datetime

#-----------#
#   modes   #
#-----------#

# Modes
MODE_SUBDIVIDE = 0
MODE_STEP = 1
MODE_STEP_UNTIL = 2


class SunVec(omni.ext.IExt):

    #---------------------------------------#
    #   configuration settings/parameters   #  # TODO: Make a form class that sets all of these.
    #---------------------------------------#

    # Omniverse Directory
    extension_dump = "/World/JollyBin/"

    # Default Increment Params (default : 1 Hour)
    default_inc_years = 0
    default_inc_months = 0
    default_inc_days = 0
    default_inc_hours = 1
    default_inc_minutes = 0
    default_inc_seconds = 0

    # Default Location Params
    default_lat = 42.4534  # Negative measurements are south.
    default_long = -76.4735  # Negative measurements are west.
    default_timezone = -4  # UTC

    # Default Start Time Params (default : Today - 1 Hour)
    default_start_year = datetime.today().year
    default_start_month = datetime.today().month
    default_start_day = datetime.today().day
    default_start_hour = datetime.today().hour - 1 if datetime.today().hour > 0 else 0 # Handle Midnight Edge Case
    default_start_minute = datetime.today().minute
    default_start_second = datetime.today().second

    # Default End Time Params (default : Today + 1 Hour)
    default_end_year = datetime.today().year
    default_end_month = datetime.today().month
    default_end_day = datetime.today().day
    default_end_hour = datetime.today().hour + 1 if datetime.today().hour < 23 else 23 # Handle Midnight Edge Case
    default_end_minute = datetime.today().minute
    default_end_second = datetime.today().second

    #-----------------------#
    #   visibility groups   #
    #-----------------------#

    # Manages Visibility
    visibles = VisibilityGroups()

    #-------------------#
    #   accessibility   #
    #-------------------#

    # Colorblind Settings
    color_mode = FULLCOLOR  # Assume FULLCOLOR by default.

    # Visibles are groups of elements which are always displayed together and hidden together.
    vg_subdivide = Visibles("subdivide", default=True)
    vg_step = Visibles("step", default=False)
    vg_step_until = Visibles("step until", default=False)
    visibles.register_groups(vg_subdivide, vg_step, vg_step_until)

    #-----------#
    #   modes   #
    #-----------#

    # Default Mode
    mode = MODE_SUBDIVIDE

    def mode_subdivide(self):
        self.mode = MODE_SUBDIVIDE
        self.visibles.island_enable(self.vg_subdivide)

    def mode_step(self):
        self.mode = MODE_STEP
        self.visibles.island_enable(self.vg_step)
        
    def mode_step_until(self):
        self.mode = MODE_STEP_UNTIL
        self.visibles.island_enable(self.vg_step_until)
    
    #---------------------#
    #   events/triggers   #
    #---------------------#

    def write_defaults(self): 
        # Write Location Defaults
        write(self.ff_lat, self.default_lat)
        write(self.ff_long, self.default_long)
        write(self.is_timezone, self.default_timezone)

        # Write Increment Defaults
        write(self.is_inc_years, self.default_inc_years)
        write(self.is_inc_months, self.default_inc_months)
        write(self.is_inc_days, self.default_inc_days)
        write(self.is_inc_hours, self.default_inc_hours)
        write(self.is_inc_minutes, self.default_inc_minutes)
        write(self.is_inc_seconds, self.default_inc_seconds)

        # Write Starting Date Defaults
        write(self.is_start_year, self.default_start_year)
        write(self.is_start_month, self.default_start_month)
        write(self.is_start_day, self.default_start_day)
        write(self.is_start_hour, self.default_start_hour)
        write(self.is_start_minute, self.default_start_minute)
        write(self.is_start_second, self.default_start_second)

        # Write Ending Date Defaults
        write(self.is_end_year, self.default_end_year)
        write(self.is_end_month, self.default_end_month)
        write(self.is_end_day, self.default_end_day)
        write(self.is_end_hour, self.default_end_hour)
        write(self.is_end_minute, self.default_end_minute)
        write(self.is_end_second, self.default_end_second)

    def location_changed(self):  
        self.lat = read_float(self.ff_lat)  
        self.long = read_float(self.ff_long)
        self.timezone = read_int(self.is_timezone)
        
        self.start_changed()
        self.end_changed()

    def inc_changed(self):
        self.inc_years = read_int(self.is_inc_years)
        self.inc_months = read_int(self.is_inc_months)
        self.inc_days = read_int(self.is_inc_days)
        self.inc_hours = read_int(self.is_inc_hours)
        self.inc_seconds = read_int(self.is_inc_minutes)
        self.inc_minutes = read_int(self.is_inc_seconds)

        self.increment = Timespan(self.inc_years, self.inc_months, self.inc_days, \
            self.inc_hours, self.inc_minutes, self.inc_seconds)
    
    def inc_steps_changed(self):
        self.inc_steps = read_int(self.is_inc_steps)

        self.increment = Timespan(self.inc_years, self.inc_months, self.inc_days, \
            self.inc_hours, self.inc_minutes, self.inc_seconds)

    def start_changed(self):
        self.start_year = read_int(self.is_start_year)
        self.start_month = read_int(self.is_start_month)
        self.start_day = read_int(self.is_start_day)
        self.start_hour = read_int(self.is_start_hour)
        self.start_minute = read_int(self.is_start_minute)
        self.start_second = read_int(self.is_start_second)

        self.start_setting = \
            Setting(self.lat, self.long, self.start_year, self.start_month, \
                self.start_day, self.start_hour, self.start_minute, self.start_second)
        self.lb_start_date.text = str(self.start_setting)
    
    def end_changed(self):
        self.end_year = read_int(self.is_end_year)
        self.end_month = read_int(self.is_end_month)
        self.end_day = read_int(self.is_end_day)
        self.end_hour = read_int(self.is_end_hour)
        self.end_minute = read_int(self.is_end_minute)
        self.end_second = read_int(self.is_end_second)

        self.end_setting = \
            Setting(self.lat, self.long, self.end_year, self.end_month, \
                self.end_day, self.end_hour, self.end_minute, self.end_second)
        self.lb_end_date.text = str(self.end_setting)

    def color_mode_changed(self):
        pass

    def sunVec(self, setting: Setting):
        azimuth, elevation = sunpos(setting.get_date(), setting.get_loc(), True)
        azimuth = rad(azimuth)
        elevation = rad(elevation)
        return(azimuth, pi/2 - elevation)
    
    sunVec
    def birth_sun(self, name, sunvector_sph, color=(1,1,1)):
                create_distant_light(self.extension_dump, name)
                color_distant_light(self.extension_dump, name, color)
                intensity_distant_light(self.extension_dump, name, self.light_intensity)
                orient_distant_light(self.extension_dump, name, sunvector_sph)

    #------------------------------#
    #   omniverse extension main   #
    #------------------------------#
    def on_startup(self, ext_id):
        
        # Make directory for extension primitives.
        create_scope(self.extension_dump[0:len(self.extension_dump)-1])
        
        # Remove defaultLight TODO: Disable all non-sunVec lighting instead.
        create_distant_light("/World/", "defaultLight")
        delete("/World/defaultLight") 

        print("JOLLY.SUNVEC..startup")

        ### Omniverse UI
        self._window = ui.Window("JOLLY.SUNVEC", width=500, height=1100)
        with self._window.frame:
            with ui.VStack(height=30):
                # Set location.
                self.ff_lat = float_field("Latitude", -90, 90, (END_EDIT, self.start_changed))
                self.ff_long = float_field("Longitude", -180, 180, (END_EDIT, self.start_changed))
                self.is_timezone = int_slider("Timezone (from UTC)",-12, 14, (END_EDIT, self.start_changed))

                separate(15)
                
                # Increment Mode
                def mode_changed_fn(combo_model : ui.AbstractItemModel, item : ui.AbstractItem):
                        self.mode = combo_model.get_item_value_model().as_int
                        if self.mode    == 0:   self.visibles.island_enable(self.vg_subdivide)
                        elif self.mode  == 1:   self.visibles.island_enable(self.vg_step)
                        elif self.mode  == 2:   self.visibles.island_enable(self.vg_step_until)
                combo_box("Increment Type",\
                    ("Subdivide", "Step", "Step Until"), (ITEM_CHANGED, mode_changed_fn))
                
                # Incremental Stepsize
                frame_increment = ui.Frame() ### VISION GROUP
                self.vg_step.add(frame_increment)
                self.vg_step_until.add(frame_increment)
                with frame_increment:
                    separate()
                    ui.Label("Incremental Step", height=30)
                    with ui.HStack():
                        with ui.VStack(): self.is_inc_years = int_slider("Years", 0, 10, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_months = int_slider("Months", 0, 12, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_days = int_slider("Days", 0, 31, (END_EDIT, self.inc_changed))  # TODO: Sync with month. Add listener?
                        with ui.VStack(): self.is_inc_hours = int_slider("Hours", 0, 23, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_minutes = int_slider("Minutes", 0, 59, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_seconds = int_slider("Seconds", 0, 59, (END_EDIT, self.inc_changed))

                self.is_inc_steps = int_slider("Number of Increments", 0, 100, \
                    (END_EDIT, self.update_incrementer))
                
                separate()

                ### Time and Day Parameters
                with ui.HStack():
                    # Start Setting
                    with ui.VStack(height=15):
                        self.lb_start_date = labeled_label("Starting Date", height=30)
                        self.is_start_year = int_slider("Year", 1901, 2099, (END_EDIT, self.start_changed))
                        self.is_start_month = int_slider("Month", 1, 12, (END_EDIT, self.start_changed))
                        self.is_start_day = int_slider("Day", 1, 31, (END_EDIT, self.start_changed))  # TODO: Sync with month. Add listener?
                        self.is_start_hour = int_slider("Hour", 0, 23, (END_EDIT, self.start_changed))
                        self.is_start_minute = int_slider("Minute", 0, 59, (END_EDIT, self.start_changed))
                        self.is_start_second = int_slider("Second", 0, 59, (END_EDIT, self.start_changed))
                        ui.Spacer(width=10)

                    ui.Spacer(width=10)

                    # End Setting
                    vstack_end_setting = ui.VStack(height=15) ### VISION GROUP
                    self.vg_subdivide.add(vstack_end_setting)
                    self.vg_step_until.add(vstack_end_setting)
                    with vstack_end_setting:
                        self.lb_end_date = labeled_label("Starting Date", height=30)
                        self.is_end_year = int_slider("Year", 1901, 2099, (END_EDIT, self.end_changed))
                        self.is_end_month = int_slider("Month", 1, 12, (END_EDIT, self.end_changed))
                        self.is_end_day = int_slider("Day", 1, 31, (END_EDIT, self.end_changed))  # TODO: Sync with month. Add listener?
                        self.is_end_hour = int_slider("Hour", 0, 23, (END_EDIT, self.end_changed))
                        self.is_end_minute = int_slider("Minute", 0, 59, (END_EDIT, self.end_changed))
                        self.is_end_second = int_slider("Second", 0, 59, (END_EDIT, self.end_changed))
                    
                separate(15)

                # Options for Color & Accessibility
                ui.Label("Color Settings", height=45)
                with ui.VStack():
                    check_box("Enable Colors", (VALUE_CHANGED, self.color_mode_changed))

                    def color_filter_changed_fn(combo_model : ui.AbstractItemModel, item : ui.AbstractItem):
                        mode = combo_model.get_item_value_model().as_int
                        if mode == -1:   self.color_mode =  FULLCOLOR
                        elif mode == 0:   self.color_mode =  FULLCOLOR
                        elif mode == 1: self.color_mode =  PROTANOPIA
                        elif mode == 2: self.color_mode =  DEUTERANOPIA
                        elif mode == 3: self.color_mode =  TRITANOPIA
                    combo_box("Colorblind Options",\
                        ("Full Color", "Protanopia", "Deuteranopia", "Tritanopia"), (ITEM_CHANGED, color_filter_changed_fn))

                ui.Label("Light Intensity")
                is_light_intensity = ui.IntSlider(min=0,max=200)
                def light_intensity_changed_fn(is_light_intensity : ui.AbstractValueModel):
                    self.light_intensity = is_light_intensity.as_int
                is_light_intensity.model.add_end_edit_fn(light_intensity_changed_fn)
                
                ui.Label(""); ui.Separator(height=15)
                ui.Button("Place Sun", clicked_fn=lambda: polysun(), height=50)

                ui.Button("Clean-Up", clicked_fn=lambda: self.cleanup(), height=50)

                self.vg_subdivide.set_state(True)
                ### END OF UI BLOCK ###

    def on_shutdown(self):
        self.cleanup()
        print("JOLLY.SUNVEC..shutdown")

def cleanup(self):
        delete(self.extension_dump[0:len(self.extension_dump)-1])