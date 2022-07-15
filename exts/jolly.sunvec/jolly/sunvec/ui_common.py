
from typing import Set
import omni.ui as ui
from omni.ui import AbstractValueModel as avm
from omni.ui import AbstractItemModel as aim

DEFAULT_LABEL_HEIGHT = 0
DEFAULT_LABEL_WIDTH = 0

VALUE_CHANGED = avm.add_value_changed_fn
ITEM_CHANGED = aim.add_item_changed_fn
END_EDIT = avm.add_end_edit_fn

def write(field: ui.AbstractValueModel, value):
    field.model.set_value(value)

def read_int(field: ui.AbstractValueModel):
    return(field.model.as_int)

def read_float(field: ui.AbstractValueModel):
    return(field.model.as_float)

def read_bool(field: ui.AbstractValueModel):
    return(field.model.as_bool)

def separate(height=0):
    return (ui.Label(""), ui.Separator(height=height))

def labeled_label(name, height=DEFAULT_LABEL_HEIGHT, width=DEFAULT_LABEL_WIDTH, *register_fns):
    ui.Label(name, height=height, width=width)
    new_element = ui.Label("")
    for trigger, response in register_fns:
        trigger(new_element, response)
    return new_element

def int_slider(name, min=0, max=10, *register_fns):
    ui.Label(name)
    new_element = ui.IntSlider(min=min, max=max)
    for trigger, response in register_fns:
        trigger(new_element.model, response)
    return new_element

def float_field(name, min=0, max=10, *register_fns):
    ui.Label(name)
    new_element = ui.FloatField(min=min, max=max)
    for trigger, response in register_fns:
        trigger(new_element.model, response)
    return new_element

def button(name, clicked_fn, height=50, *register_fns):
    new_element = ui.Button(text=name, height=height, clicked_fn=lambda : clicked_fn())
    for trigger, response in register_fns:
        trigger(new_element, response)
    return new_element

def check_box(name, *register_fns):
    ui.Label(name)
    new_element = ui.CheckBox()
    for trigger, response in register_fns:
        trigger(new_element.model, response)
    return new_element

def combo_box(name, options, *register_fns):
    ui.Label(name)
    new_element = ui.ComboBox(0, *(options))
    for trigger, response in register_fns:
        trigger(new_element.model, response)
    return new_element

class Visibles():
    def __init__(self, name, default=False):
        self._members = []
        self._state = False
        self.name = name
        self.visibility = default
    
    def add(self, *new_members):
        for new_member in new_members:
            self._members.append(new_member)
            new_member.visible = self._state

    def toggle(self):
        self._state = not(self._state)
        for member in self._members:
            member.visible = self._state
        
    def set_state(self, new_state):
        self._state = new_state
        for member in self._members:
            member.visible = new_state
    
    def is_visible(self):
        return self._state
    
class VisibilityGroups():
    _visibility_groups = []

    def register_groups(self, *vgs):
        for vg in vgs:
            self._visibility_groups.append(vg)
    
    def island_enable(self, *keep_true):
        """ Disables everything but the groups in [*keep_true], which are all enabled. """
        for vg in self._visibility_groups:
            vg.set_state(False)
        for vg in keep_true:
            vg.set_state(True)

