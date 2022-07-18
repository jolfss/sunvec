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

# NOTE: +Z is the vertical direction; this is not Omniverse's default.
# TODO: Add a +Axis toggle.

#-----------#
#   modes   #
#-----------#

# Modes
MODE_SUBDIVIDE = 0
MODE_STEP = 1
MODE_STEP_UNTIL = 2



class SunVec(omni.ext.IExt):
    """
    SunVec is the main extension class and handles extension execution
    """

    #---------------------------------------#
    #   configuration settings/parameters   #  # TODO: Make a form class that sets all of these. -?
    #---------------------------------------#

    # Omniverse Directory
    extension_dump = "/World/JollyBin/"

    

    # Default Increment Params (default : 1 Hour)
    inc_years = 0
    inc_months = 0
    inc_days = 0
    inc_hours = 1
    inc_minutes = 0
    inc_seconds = 0
    
    inc_steps = 24

    increment = Timespan(inc_years, inc_months, inc_days, inc_hours, inc_minutes, inc_seconds)

    # Default Location Params
    lat = 42.4534  # Negative measurements are south.
    long = -76.4735  # Negative measurements are west.
    timezone = -4  # UTC

    # Default Start Time Params (default : Today - 1 Hour)
    start_year = datetime.today().year
    start_month = datetime.today().month
    start_day = datetime.today().day
    start_hour = datetime.today().hour - 1 if datetime.today().hour > 0 else 0 # Handle Midnight Edge Case
    start_minute = datetime.today().minute
    start_second = datetime.today().second

    setting_start = Setting(lat, long, start_year, start_month, start_day, start_hour, start_minute, start_second, timezone)

    # Default End Time Params (default : Today + 1 Hour)
    end_year = datetime.today().year
    end_month = datetime.today().month
    end_day = datetime.today().day
    end_hour = datetime.today().hour + 1 if datetime.today().hour < 23 else 23 # Handle Midnight Edge Case
    end_minute = datetime.today().minute
    end_second = datetime.today().second

    setting_end = Setting(lat, long, end_year, end_month, end_day, end_hour, end_minute, end_second, timezone)

    # Default Light Params
    intensity = 100

    #-------------------#
    #   accessibility   #
    #-------------------#

    # Colorblind Settings
    color_mode = FULLCOLOR  # Assume FULLCOLOR by default.
    color_toggle = False

    #-----------------------#
    #   visibility groups   #
    #-----------------------#

    # Manages Visibility
    visibles = VisibilityGroups()

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

    #--------------------#
    #   helper methods   #
    #--------------------#

    def cleanup(self):
        """[cleanup()] clears the content folder given by [omniverse_directory]."""
        delete(self.extension_dump[0:len(self.extension_dump)-1])

    def birth_sun(self, name, sunvector_sph, color=(1,1,1)):
        """[birth_sun(name, sunvector_sph, color=(1,1,1)] creates a sun in the direction of [sunvector_sph] 
        with the emission color [color]; the primitive is named [name] and put in the directory [self.extension_dump]."""
        create_distant_light(self.extension_dump, name)
        color_distant_light(self.extension_dump, name, color)
        intensity_distant_light(self.extension_dump, name, self.intensity)
        orient_distant_light(self.extension_dump, name, sunvector_sph)

    def sun_vector(self, setting: Setting):
        """[sun_vector(setting)] is a tuple (azimuth, phi) which designates the sun location in the sky for the time and location of [setting]."""
        azimuth, elevation = sunpos(setting.get_date(), setting.get_loc(), True)
        azimuth = rad(azimuth)
        elevation = rad(elevation)
        return(azimuth, pi/2 - elevation)
    
    def position_suns(self):
        """[position_suns] places suns in the scene according to the mode and user params."""
        if self.mode == MODE_SUBDIVIDE:
            sets = SettingRange(self.setting_start, self.setting_end).subdiv_range(self.inc_steps)
        elif self.mode == MODE_STEP:
            sets = SettingRange(self.setting_start, self.setting_end).increment_range(self.increment, self.inc_steps)
        elif self.mode == MODE_STEP_UNTIL:
            sets = SettingRange(self.setting_start, self.setting_end).increment_until_range(self.increment)
        
        i = 0
        for setting in sets:
            i+=1
            theta, phi = self.sun_vector(setting)
            sun_vector = theta_phi_to_spherical(theta, phi)
            if self.color_toggle:
                self.birth_sun(F"sunVector{i}", sun_vector, RingColor(Spectrum(sets), self.color_mode).color(i))
            else: 
                self.birth_sun(F"sunVector{i}", sun_vector)

    #---------------------#
    #   events/triggers   #
    #---------------------#

    # NOTE: Dummy=None arguments *ARE* needed to satisfy Omniverse's slider/button/field callbacks.

    def stimulate(self):
        """[stimulate()] is the main extension method; it places suns wherever the user has specified.
        NOTE: This should be called after any update to the conditions."""
        self.cleanup()
        self.position_suns()

    def write_defaults(self): 
        """[write_defaults] sets all user forms to their default values."""
        # Write Location Defaults
        write(self.ff_lat, self.lat)
        write(self.ff_long, self.long)
        write(self.is_timezone, self.timezone)

        # Write Increment Defaults
        write(self.is_inc_years, self.inc_years)
        write(self.is_inc_months, self.inc_months)
        write(self.is_inc_days, self.inc_days)
        write(self.is_inc_hours, self.inc_hours)
        write(self.is_inc_minutes, self.inc_minutes)
        write(self.is_inc_seconds, self.inc_seconds)

        # Write Increment Steps Default
        write(self.is_inc_steps, self.inc_steps)

        # Write Starting Date Defaults
        write(self.is_start_year, self.start_year)
        write(self.is_start_month, self.start_month)
        write(self.is_start_day, self.start_day)
        write(self.is_start_hour, self.start_hour)
        write(self.is_start_minute, self.start_minute)
        write(self.is_start_second, self.start_second)

        # Write Ending Date Defaults
        write(self.is_end_year, self.end_year)
        write(self.is_end_month, self.end_month)
        write(self.is_end_day, self.end_day)
        write(self.is_end_hour, self.end_hour)
        write(self.is_end_minute, self.end_minute)
        write(self.is_end_second, self.end_second)

    def location_changed(self, dummy=None):
        """[location_changed(dummy)] updates the location of both settings [self.setting_start], [self.setting_end]."""
        self.lat = read_float(self.ff_lat)  
        self.long = read_float(self.ff_long)
        self.timezone = read_int(self.is_timezone)

        self.stimulate()

    def inc_changed(self, dummy=None):
        """[inc_changed(dummy)] updates the Timespan [self.increment] to match the user forms."""
        self.inc_years = read_int(self.is_inc_years)
        self.inc_months = read_int(self.is_inc_months)
        self.inc_days = read_int(self.is_inc_days)
        self.inc_hours = read_int(self.is_inc_hours)
        self.inc_minutes = read_int(self.is_inc_minutes)
        self.inc_seconds = read_int(self.is_inc_seconds)
        self.increment = Timespan(self.inc_years, self.inc_months, self.inc_days, \
            self.inc_hours, self.inc_minutes, self.inc_seconds)
        
        self.stimulate()

    def inc_steps_changed(self, dummy=None):
        """[inc_steps_changed(dummy)] updates [self.inc_steps] to match the int slider [self.is_inc_steps]."""
        self.inc_steps = read_int(self.is_inc_steps)

        self.stimulate()

    def start_changed(self, dummy=None):
        """[start_changed(dummy)] updates the Setting [self.setting_start] to match the user forms."""
        self.start_year = read_int(self.is_start_year)
        self.start_month = read_int(self.is_start_month)
        self.start_day = read_int(self.is_start_day)
        self.start_hour = read_int(self.is_start_hour)
        self.start_minute = read_int(self.is_start_minute)
        self.start_second = read_int(self.is_start_second)
        self.setting_start = \
            Setting(self.lat, self.long, self.start_year, self.start_month, \
                self.start_day, self.start_hour, self.start_minute, self.start_second, self.timezone)
        self.lb_start_date.text = str(self.setting_start)

        self.stimulate()
    
    def end_changed(self, dummy=None):
        """[end_changed(dummy)] updates the Setting [self.setting_end] to match the user forms."""
        self.end_year = read_int(self.is_end_year)
        self.end_month = read_int(self.is_end_month)
        self.end_day = read_int(self.is_end_day)
        self.end_hour = read_int(self.is_end_hour)
        self.end_minute = read_int(self.is_end_minute)
        self.end_second = read_int(self.is_end_second)

        self.setting_end = \
            Setting(self.lat, self.long, self.end_year, self.end_month, \
                self.end_day, self.end_hour, self.end_minute, self.end_second, self.timezone)
        self.lb_end_date.text = str(self.setting_end)

        self.stimulate()

    def toggle_colors(self, dummy=None):
        """[toggle_colors(check_box)] matches the state of [self.color_toggle]
                           with the state of the checkbox [self.chbx_color_toggle]."""
        self.color_toggle = read_bool(self.chbx_color_toggle)
        self.stimulate()

    def color_filter_changed(self, dummyA=None, dummyB=None):
        """[color_filter_changed] changes [color_type] to match the combo box [cmbx_color_filter];
        NOTE: will bring user out of GRAYSCALE if they choose a color mode from the combo box. """
        self.color_toggle = True; write(self.chbx_color_toggle, True); self.toggle_colors(self.chbx_color_toggle)
        color_type = self.cmbx_color_filter.model.get_item_value_model().as_int
        if color_type == 0: self.color_mode =  FULLCOLOR
        elif color_type == 1: self.color_mode =  PROTANOPIA
        elif color_type == 2: self.color_mode =  DEUTERANOPIA
        elif color_type == 3: self.color_mode =  TRITANOPIA

        self.stimulate()

    def intensity_changed(self, dummy=None):
        """[intensity_changed(intensity) updates the solar intensity."""
        self.intensity = self.is_intensity.model.as_int
        self.stimulate()

    #----------------------#
    #   startup routines   #
    #----------------------#

    def pre_initialization(self):
        """[pre_initialization()] creates extension scope and removes default world lighting; cleans remnants."""
        # Make directory for extension primitives.
        create_scope(self.extension_dump[0:len(self.extension_dump)-1])
        
        # Remove defaultLight TODO: Disable all non-sunVec lighting instead.
        create_distant_light("/World/", "defaultLight")
        delete("/World/defaultLight") 

        print("JOLLY.SUNVEC..startup")

    def post_initialize(self):
        """[post_initialize()] links the scene to the UI and begins simulation."""
        self.mode_subdivide()  # Puts user in MODE_SUBDIVIDE.
        self.write_defaults()  # Write default values into

        self.location_changed()  # Updates latitude, longitude, and timezone.
        self.inc_changed()  # Updates the increment Timescale object [self.increment : Timescale]
        self.inc_steps_changed()  # Updates how many increments/divisions of the sunpath are registered.
        self.start_changed()  # Presets the starting Setting object.
        self.end_changed()  # Presets the starting End object.

        self.color_filter_changed(self.cmbx_color_filter)

        self.stimulate()

    #------------------------------#
    #   omniverse extension main   #
    #------------------------------#
    def on_startup(self, ext_id):

        self.pre_initialization()

        ############################
        #   Begin User Interface   #
        ############################
        self._window = ui.Window("JOLLY.SUNVEC", width=500, height=1100)
        with self._window.frame:
            with ui.VStack(height=30):
                # Set location.
                self.ff_lat = float_field("Latitude", -90, 90, (END_EDIT, self.location_changed))
                self.ff_long = float_field("Longitude", -180, 180, (END_EDIT, self.location_changed))
                self.is_timezone = int_slider("Timezone (from UTC)",-12, 14, (END_EDIT, self.location_changed))

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
                        with ui.VStack(): self.is_inc_months = int_slider("Months", 0, 11, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_days = int_slider("Days", 0, 31, (END_EDIT, self.inc_changed))  # TODO: Sync with month. Add listener?
                        with ui.VStack(): self.is_inc_hours = int_slider("Hours", 0, 23, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_minutes = int_slider("Minutes", 0, 59, (END_EDIT, self.inc_changed))
                        with ui.VStack(): self.is_inc_seconds = int_slider("Seconds", 0, 59, (END_EDIT, self.inc_changed))

                self.is_inc_steps = int_slider("Number of Increments", 0, 100, \
                    (END_EDIT, self.inc_steps_changed))
                
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
                    vstack_setting_end = ui.VStack(height=15) ### VISION GROUP
                    self.vg_subdivide.add(vstack_setting_end)
                    self.vg_step_until.add(vstack_setting_end)
                    with vstack_setting_end:
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
                    self.chbx_color_toggle = check_box("Enable Colors", (VALUE_CHANGED, self.toggle_colors))
                    self.cmbx_color_filter = combo_box("Colorblind Options",\
                        ("Full Color", "Protanopia", "Deuteranopia", "Tritanopia"), (ITEM_CHANGED, self.color_filter_changed))
                self.is_intensity = int_slider("Light Intensity", 0, 200, (END_EDIT, self.intensity_changed))

                separate()

                # Place should be irrelevant now by listeners.
                # ui.Button("Place Sun", clicked_fn=lambda: self.stimulate(), height=50)
                ui.Button("Place Suns", clicked_fn=lambda: self.position_suns(), height=50)
                ui.Button("Clean-Up", clicked_fn=lambda: self.cleanup(), height=50)
            ##########################
            #   End User Interface   #
            ##########################

        self.post_initialize()

        # on_startup() ends here
            
    def on_shutdown(self):
        self.cleanup()
        print("JOLLY.SUNVEC..shutdown")