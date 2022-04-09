import logging
from math import cos, pi, sin, sqrt
from random import randint, uniform
from secrets import choice

from PIL import Image, ImageDraw
from pitop.miniscreen import Miniscreen

from pt_miniscreen.core import App as AppBase
from pt_miniscreen.core import Component
from pt_miniscreen.core.components import Text
from pt_miniscreen.core.utils import apply_layers, layer, offset_to_center

logger = logging.getLogger(__name__)


def rotate(point, center, degrees):
    # rotate about circle center by spin_angle degrees
    rad_angle = 2 * pi * degrees / 360

    # translate point by circle center
    translated_point = (point[0] - center[0], point[1] - center[1])

    # rotate point by rad_angle
    sin_angle = sin(rad_angle)
    cos_angle = cos(rad_angle)
    rotated_point = (
        translated_point[0] * cos_angle - translated_point[1] * sin_angle,
        translated_point[0] * sin_angle + translated_point[1] * cos_angle,
    )

    # translate point back to original reference
    return (rotated_point[0] + center[0], rotated_point[1] + center[1])


class Asteroid(Component):
    def __init__(self, radius, fps=15, **kwargs):
        super().__init__(**kwargs, initial_state={"spin_angle": 0})

        # store asteroid properties
        self.radius = radius
        self.verticies = self._create_verticies(5)

        # calculate rotation parameters
        rotation_time = uniform(0.5, 10)
        rotation_steps = rotation_time * fps
        spin_direction = choice((1, -1))
        self.spin_step = int(360 / rotation_steps) * spin_direction

        # start rotating
        self.create_interval(self._rotation_step, rotation_time / rotation_steps)

    def _create_verticies(self, num_verticies):
        start_degrees = randint(1, 360)
        degrees_step = int(360 / num_verticies)

        angles = []
        for angle in range(start_degrees, start_degrees + 360, degrees_step):
            offset = int(randint(-degrees_step, degrees_step) / 3)
            angles.append(angle + offset)

        verticies = []
        for angle in angles:
            radians = pi * 2 * angle / 360
            distance = randint(int(self.radius * 2 / 3), self.radius)
            x = self.radius + int(distance * cos(radians))
            y = self.radius + int(distance * sin(radians))
            verticies.append((x, y))

        return verticies

    def _rotation_step(self):
        self.state.update({"spin_angle": self.state["spin_angle"] + self.spin_step})

    def _rotate(self, vertex):
        center = (self.radius, self.radius)
        return rotate(vertex, center, self.state["spin_angle"])

    def _center(self, vertex):
        if not hasattr(self, "size"):
            return vertex

        x_offset = offset_to_center(self.size[0], self.radius * 2)
        y_offset = offset_to_center(self.size[1], self.radius * 2)

        return (vertex[0] + x_offset, vertex[1] + y_offset)

    def render(self, image):
        draw = ImageDraw.Draw(image)
        for index in range(len(self.verticies)):
            start_vertex = self._center(self._rotate(self.verticies[index - 1]))
            end_vertex = self._center(self._rotate(self.verticies[index]))

            draw.line((start_vertex, end_vertex), width=1, fill="white")

        return image


class Ship(Component):
    def __init__(self, base, length, initial_angle=0, **kwargs):
        super().__init__(**kwargs, initial_state={"angle": initial_angle})

        self.base = base
        self.length = length
        self._rotation_interval = None
        self._rotation_interval_time = 1 / 20
        self._rotation_direction = None
        self._rotation_step = 0
        self._max_rotation_step = 15

    def _rotate(self, degrees):
        self.state.update({"angle": self.state["angle"] + degrees})

    def _rotate_clockwise(self):
        if self._rotation_step < self._max_rotation_step:
            self._rotation_step = min(self._max_rotation_step, self._rotation_step + 2)

        self._rotate(self._rotation_step)

    def _rotate_anticlockwise(self):
        if self._rotation_step > -self._max_rotation_step:
            self._rotation_step = max(-self._max_rotation_step, self._rotation_step - 2)

        self._rotate(self._rotation_step)

    def _decelerate_rotation(self):
        if self._rotation_step > 0:
            self._rotation_step = max(0, self._rotation_step - 2)

        if self._rotation_step < 0:
            self._rotation_step = min(0, self._rotation_step + 2)

        self._rotate(self._rotation_step)

        if (
            self._rotation_step == 0
            and self._rotation_interval
            and self._rotation_direction is None
        ):
            self._rotation_interval.cancel()
            self._rotation_interval = None

    def _stop_rotating(self):
        self._rotation_direction = None
        if self._rotation_interval:
            self._rotation_interval.cancel()
            self._rotation_interval = self.create_interval(
                self._decelerate_rotation, self._rotation_interval_time
            )

    def start_rotating_clockwise(self):
        if self._rotation_interval:
            self._rotation_interval.cancel()

        self._rotation_direction = "clockwise"
        self._rotation_interval = self.create_interval(
            self._rotate_clockwise, self._rotation_interval_time
        )

    def start_rotating_anticlockwise(self):
        if self._rotation_interval:
            self._rotation_interval.cancel()

        self._rotation_direction = "anticlockwise"
        self._rotation_interval = self.create_interval(
            self._rotate_anticlockwise, self._rotation_interval_time
        )

    def stop_rotating_clockwise(self):
        if self._rotation_direction == "clockwise":
            self._stop_rotating()

    def stop_rotating_anticlockwise(self):
        if self._rotation_direction == "anticlockwise":
            self._stop_rotating()

    def render(self, image):
        draw = ImageDraw.Draw(image)
        center = (int(image.width / 2), int(image.height / 2))
        verticies = [
            (center[0], center[1] - int(self.length / 2)),
            (center[0] + int(self.base / 2), center[1] + int(self.length / 2)),
            (center[0] - int(self.base / 2), center[1] + int(self.length / 2)),
        ]
        for index, vertex in enumerate(verticies):
            verticies[index] = rotate(vertex, center, self.state["angle"])

        draw.polygon(verticies, fill="white")

        return image


class Root(Component):
    default_state = {
        "asteroid_positions": {},
        "ship_position": (62, 28),
        "game_over": False,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self._gameover_text = self.create_child(
            Text, text="Game Over\nPress O to restart"
        )

        self.canvas_gutter = 10
        self._ship_area_size = (10, 10)
        self._max_ship_speed = 5
        self._ship_acceleration = 0.1  # speed change per thrust step
        self._thrust_interval_time = 1 / 20
        self._thrust_interval = None

        self.max_asteroid_diameter = 9

        self._start_game()

    def _start_game(self):
        self.ship = self.create_child(Ship, base=6, length=8)
        self._previous_ship_angle = self.ship.state["angle"]
        self._ship_speed = 0

        max_asteroid_step = 0.5
        self.asteroids = []
        self.asteroid_position_steps = {}
        for _ in range(2):
            asteroid = self.create_child(Asteroid, radius=self.max_asteroid_diameter)
            self.asteroid_position_steps[asteroid] = (
                uniform(-max_asteroid_step, max_asteroid_step),
                uniform(-max_asteroid_step, max_asteroid_step),
            )
            self.state["asteroid_positions"][asteroid] = (
                randint(0, 64),
                randint(0, 128),
            )
            self.asteroids.append(asteroid)

        self._move_asteroids_interval = self.create_interval(
            self._move_asteroids, 1 / 24
        )

    def _stop_game(self):
        if self._move_asteroids_interval:
            self.remove_interval(self._move_asteroids_interval)
            self._move_asteroids_interval = None

        if self._thrust_interval:
            self.remove_interval(self._thrust_interval)
            self._thrust_interval = None

    def _get_next_pos(self, current_pos, step):
        next_pos = (current_pos[0] + step[0], current_pos[1] + step[1])

        if next_pos[0] < -self.canvas_gutter:
            next_pos = (self.width + self.canvas_gutter, next_pos[1])
        elif next_pos[0] > self.width + self.canvas_gutter:
            next_pos = (-self.canvas_gutter, next_pos[1])

        if next_pos[1] < -self.canvas_gutter:
            next_pos = (next_pos[0], self.height + self.canvas_gutter)
        elif next_pos[1] > self.height + self.canvas_gutter:
            next_pos = (next_pos[0], -self.canvas_gutter)

        return next_pos

    def _move_asteroids(self):
        asteroid_positions = self.state["asteroid_positions"]

        for asteroid in self.asteroids:
            current_pos = asteroid_positions[asteroid]
            step = self.asteroid_position_steps[asteroid]
            asteroid_positions[asteroid] = self._get_next_pos(current_pos, step)
            if self._has_ship_collided(asteroid):
                return self.state.update({"game_over": True})

        self.state.update({"asteroid_positions": asteroid_positions})

    def _vector(self, degrees, speed):
        # transform angle for our reference
        rads = (degrees * 2 * pi / 360) - pi / 2
        return (cos(rads) * speed, sin(rads) * speed)

    def _update_ship_position(self, step):
        next_step = (int(step[0]), int(step[1]))
        ship_pos = self.state["ship_position"] or (
            offset_to_center(self.width, self._ship_area_size[0]),
            offset_to_center(self.height, self._ship_area_size[1]),
        )
        self.state.update({"ship_position": self._get_next_pos(ship_pos, next_step)})

    # TODO:- improve this to take into account vertices of ship and asteroid
    def _has_ship_collided(self, asteroid):
        ship_x, ship_y = self.state["ship_position"]
        asteroid_x, asteroid_y = self.state["asteroid_positions"][asteroid]
        print("has_ship_collided", ship_x, ship_y, asteroid_x, asteroid_y)

        return not (
            # ship is to the right of asteroid
            ship_x > asteroid_x + (2 * asteroid.radius)
            # ship is to the left of asteroid
            or ship_x + self._ship_area_size[0] < asteroid_x
            # ship is below asteroid
            or ship_y < asteroid_y - (2 * asteroid.radius)
            # ship is above asteroid
            or ship_y + self._ship_area_size[1] > asteroid_y
        )

    def _accelerate_ship(self):
        prev_step = self._vector(self._previous_ship_angle, self._ship_speed)
        step_delta = self._vector(self.ship.state["angle"], self._ship_acceleration)
        next_step = (prev_step[0] + step_delta[0], prev_step[1] + step_delta[1])
        next_speed = sqrt(pow(next_step[0], 2) + pow(next_step[1], 2))
        clamp_factor = min(1, self._max_ship_speed / next_speed)
        clamped_step = (next_step[0] * clamp_factor, next_step[1] * clamp_factor)

        # update ship speed and save current angle
        self._ship_speed = min(next_speed, self._max_ship_speed)
        self._previous_ship_angle = self.ship.state["angle"]
        self._update_ship_position(clamped_step)

    def _decelerate_ship(self):
        prev_step = self._vector(self._previous_ship_angle, self._ship_speed)
        step_delta = self._vector(self._previous_ship_angle, -self._ship_acceleration)
        next_step = (prev_step[0] + step_delta[0], prev_step[1] + step_delta[1])
        next_speed = sqrt(pow(next_step[0], 2) + pow(next_step[1], 2))

        # update ship speed and position
        self._ship_speed = next_speed
        self._update_ship_position(next_step)

        # stop decelerating when speed is low enough
        if next_speed < self._ship_acceleration:
            self._ship_speed = 0
            self._thrust_interval.cancel()
            self._thrust_interval = None

    def start_thrusting_ship(self):
        if self._thrust_interval:
            self._thrust_interval.cancel()

        self._thrust_interval = self.create_interval(
            self._accelerate_ship, self._thrust_interval_time
        )

    def stop_thrusting_ship(self):
        if self._thrust_interval:
            self._thrust_interval.cancel()
            self._thrust_interval = self.create_interval(
                self._decelerate_ship, self._thrust_interval_time
            )

    def start_rotating_ship_clockwise(self):
        self.ship.start_rotating_clockwise()

    def start_rotating_ship_anticlockwise(self):
        self.ship.start_rotating_anticlockwise()

    def stop_rotating_ship_clockwise(self):
        self.ship.stop_rotating_clockwise()

    def stop_rotating_ship_anticlockwise(self):
        self.ship.stop_rotating_anticlockwise()

    def reset(self):
        self.state.update(self.default_state)
        self._start_game()

    def on_state_change(self, previous_state):
        if self.state["game_over"]:
            self._stop_game()
            return

        for asteroid in self.asteroids:
            if self._has_ship_collided(asteroid):
                self.state.update({"game_over": True})

    def render(self, image):
        if self.state["game_over"]:
            return self._gameover_text.render(image)

        ship_pos = self.state["ship_position"]
        canvas_width = self.width + self.canvas_gutter * 2
        canvas_height = self.height + self.canvas_gutter * 2

        layers = []
        for asteroid in self.asteroids:
            position = self.state["asteroid_positions"][asteroid]
            layers.append(
                layer(
                    asteroid.render,
                    size=(asteroid.radius * 2, asteroid.radius * 2),
                    pos=(int(position[0]), int(position[1])),
                )
            )

        canvas = apply_layers(Image.new("1", (canvas_width, canvas_height)), layers)

        image.paste(
            canvas.crop(
                (
                    self.canvas_gutter,
                    self.canvas_gutter,
                    canvas_width - self.canvas_gutter,
                    canvas_height - self.canvas_gutter,
                )
            )
        )

        return apply_layers(
            image,
            [layer(self.ship.render, size=self._ship_area_size, pos=ship_pos)],
        )


class App(AppBase):
    def __init__(self):
        self.miniscreen = Miniscreen()
        super().__init__(display=self.miniscreen.device.display, Root=Root)

        self.miniscreen.up_button.when_pressed = self.handle_up_pressed
        self.miniscreen.up_button.when_released = self.handle_up_released
        self.miniscreen.down_button.when_pressed = self.handle_down_pressed
        self.miniscreen.down_button.when_released = self.handle_down_released
        self.miniscreen.select_button.when_pressed = self.handle_select_pressed
        self.miniscreen.select_button.when_released = self.handle_select_released

    def handle_up_pressed(self):
        self.root.start_rotating_ship_clockwise()

    def handle_down_pressed(self):
        self.root.start_rotating_ship_anticlockwise()

    def handle_up_released(self):
        self.root.stop_rotating_ship_clockwise()

    def handle_down_released(self):
        self.root.stop_rotating_ship_anticlockwise()

    def handle_select_pressed(self):
        if self.root.state["game_over"]:
            self.root.reset()

        self.root.start_thrusting_ship()

    def handle_select_released(self):
        self.root.stop_thrusting_ship()
