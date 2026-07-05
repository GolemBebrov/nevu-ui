import nevu_ui.core.modules as md
from nevu_ui.core.enums import Backend, PressType
from nevu_ui.fast.nvvector2 import NvVector2


class _BaseMouse:
    __slots__ = (
        "pos",
        "_wheel_side",
        "_states",
        "_up_states",
        "dragging",
        "wheel_y",
        "_mouse_keys",
    )

    def __init__(self):
        self.pos = NvVector2.from_xy(0, 0)
        self._wheel_side = PressType.WheelStill
        self._states = [PressType.Still, PressType.Still, PressType.Still]
        self._up_states = {PressType.Still, PressType.Up}
        self.dragging = False
        self.wheel_y = 0

    # === Left props ===
    @property
    def left_up(self):
        return self._states[0] == PressType.Up

    @property
    def left_fdown(self):
        return self._states[0] == PressType.Fdown

    @property
    def left_down(self):
        return self._states[0] == PressType.Down

    @property
    def left_still(self):
        return self._states[0] == PressType.Still

        # === Center props ===

    @property
    def center_up(self):
        return self._states[1] == PressType.Up

    @property
    def center_fdown(self):
        return self._states[1] == PressType.Fdown

    @property
    def center_down(self):
        return self._states[1] == PressType.Down

    @property
    def center_still(self):
        return self._states[1] == PressType.Still

        # === Right props ===

    @property
    def right_up(self):
        return self._states[2] == PressType.Up

    @property
    def right_fdown(self):
        return self._states[2] == PressType.Fdown

    @property
    def right_down(self):
        return self._states[2] == PressType.Down

    @property
    def right_still(self):
        return self._states[2] == PressType.Still

        # === Any props ===

    @property
    def any_down(self):
        return self.left_down or self.right_down or self.center_down

    @property
    def any_fdown(self):
        return self.left_fdown or self.right_fdown or self.center_fdown

    @property
    def any_up(self):
        return self.left_up or self.right_up or self.center_up

        # === Wheel props ===

    @property
    def wheel_up(self):
        return self._wheel_side == PressType.WheelUp

    @property
    def wheel_down(self):
        return self._wheel_side == PressType.WheelDown

    @property
    def wheel_still(self):
        return self._wheel_side == PressType.WheelStill

    @property
    def wheel_side(self):
        return self._wheel_side

    @property
    def any_wheel(self):
        return self._wheel_side in (PressType.WheelDown, PressType.WheelUp)


class PygameMouse(_BaseMouse):
    def update_wheel(self, events):
        wheel_event_found = False
        MouseWheelType = md.pygame.MOUSEWHEEL
        for event in events:
            if event.type == MouseWheelType:
                wheel_event_found = True
                new_wheel_y = event.y
                if new_wheel_y > 0:
                    self._wheel_side = PressType.WheelUp
                elif new_wheel_y < 0:
                    self._wheel_side = PressType.WheelDown
                else:
                    self._wheel_side = PressType.WheelStill
                self.wheel_y += event.y
                break
        if not wheel_event_found:
            self._wheel_side = PressType.WheelStill

    def update(self, events: list | None = None):
        if self.left_fdown:
            self.dragging = True
        elif self.left_up:
            self.dragging = False
        mouse = md.pygame.mouse
        pg_pos = mouse.get_pos()
        self.pos = NvVector2.from_xy(pg_pos[0], pg_pos[1])
        pressed = mouse.get_pressed()

        if events and len(events) != 0:
            self.update_wheel(events)
        else:
            self._wheel_side = PressType.WheelStill

        states = self._states
        up_states = self._up_states

        for i in range(3):
            current_state = states[i]
            is_up = current_state in up_states
            if pressed[i]:
                states[i] = PressType.Fdown if is_up else PressType.Down
            else:
                states[i] = PressType.Up if is_up else PressType.Still


class RaylibMouse(_BaseMouse):
    def __init__(self):
        super().__init__()
        self._mouse_keys = tuple(
            enumerate(
                (
                    md.rl.MouseButton.MOUSE_BUTTON_LEFT,
                    md.rl.MouseButton.MOUSE_BUTTON_MIDDLE,
                    md.rl.MouseButton.MOUSE_BUTTON_RIGHT,
                )
            )
        )

    def update_wheel(self):  # type: ignore
        wheel_y = md.rl.get_mouse_wheel_move_v().y
        if wheel_y > 0:
            self._wheel_side = PressType.WheelUp
        elif wheel_y < 0:
            self._wheel_side = PressType.WheelDown
        else:
            self._wheel_side = PressType.WheelStill
        self.wheel_y = wheel_y

    def update(self, *args, **kwargs):  # type: ignore
        self.update_wheel()
        rl = md.rl
        if rl.is_mouse_button_pressed(md.rl.MouseButton.MOUSE_BUTTON_LEFT):
            self.dragging = True
        elif rl.is_mouse_button_up(md.rl.MouseButton.MOUSE_BUTTON_LEFT):
            self.dragging = False

        states = self._states
        up_states = self._up_states
        m_btn_down = rl.is_mouse_button_down

        for i, button in self._mouse_keys:
            state = states[i]
            is_up = state in up_states
            if m_btn_down(button):
                states[i] = PressType.Fdown if is_up else PressType.Down
            else:
                states[i] = PressType.Up if is_up else PressType.Still

        screen_pos = rl.get_mouse_position()
        self.pos = NvVector2.from_xy(screen_pos.x, screen_pos.y)


def set_mouse(backend: Backend):
    global mouse
    if not isinstance(mouse, UnselectedMouse):
        mouse = UnselectedMouse()
    mouse.select(backend)


class UnselectedMouse(_BaseMouse):
    def __init__(self):
        pass

    def select(self, backend: Backend):
        match backend:
            case Backend.Pygame | Backend.Sdl:
                self.__class__ = PygameMouse  # type: ignore
            case Backend.RayLib:
                self.__class__ = RaylibMouse  # type: ignore
        self.__init__()


mouse: _BaseMouse = UnselectedMouse()  # type: ignore
