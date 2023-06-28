from graphics import Canvas
import time
import random
import os


def clear_console():
    # for command line
    os.system('cls' if os.name == 'nt' else 'clear')
    # for CIP IDE
    # for i in range(25):
    #     print()


def greeting_screen(world, key_event_canvas):
    print("Karel Fortress".center(2 * world.world_width))
    print("This is dwarf: A".center(2 * world.world_width))
    print("It ain't much but has an honest hat.".center(2 * world.world_width))
    print()
    print("It is Dwarf Fortress like game, you are controlling a cursor ☼. You can point at a tree to order dwarf to"
          " chop it for wood, point at rock in order for it to be mined."
          " You can build things on the ground represented by dots")
    print()
    print()
    print("Dwarf goes to heart representing food when it's hungry(fullness below 50)"
          " and goes to bed at 22 and wakes up at 6")
    print()
    print()
    print()
    print("Arrows control a cursor ☼, it starts at top left corner.".center(2 * world.world_width))
    print()
    print("By pointing the cursor somewhere and pressing key you can order a dwarf to:")
    print()
    print(" c - chop tree ♠".center(2 * world.world_width))
    print("m - mine rock ■".center(2 * world.world_width))
    print("b - build wooden wall ░ or bed B".center(2 * world.world_width))
    print("g - go for a walk".center(2 * world.world_width))
    print("Additionally r - rescue(terminates current task), 1/2/3 - game speed".center(2 * world.world_width))
    print()
    print()
    print("press enter to continue")
    key = ''
    while key != 'enter':
        key_event_canvas.update()
        key = key_event_canvas.stored_key
        key_event_canvas.reset_stored_key()


class KeyEventCanvas:
    def __init__(self, key_handler_function):
        self.canvas = Canvas()
        self.canvas.bind("<Key>", self.on_key_press)
        self.key_handler_function = key_handler_function
        self.stored_key = None

    def on_key_press(self, event):
        key = event.keysym
        self.key_handler_function(self, key)

    def update(self):
        self.canvas.update()

    def reset_stored_key(self):
        self.stored_key = None

    def mainloop(self):
        # IDK if necessary
        self.canvas.mainloop()


def process_key(key_event_canvas, key):
    if key == 'Left':
        key = 'left'
    elif key == 'Right':
        key = 'right'
    elif key == 'Up':
        key = 'up'
    elif key == 'Down':
        key = 'down'
    elif key == 'Return':
        key = 'enter'
    key_event_canvas.stored_key = key


class World(object):
    speed_modes = [0, 1, 0.25, 0.1]
    speed_modes_names = ['placeholder', 'slow', 'normal', 'fast']
    allowed_to_step_on = ['☼', '♥', '.', 'B']
    list_of_allowed_buildings = ['b', 'w', 'bed', 'wall']

    def __init__(self, name):
        self.name = name
        self.world_width = 40
        self.max_world_x = self.world_width - 1
        self.middle_x = self.max_world_x // 2
        self.world_height = 15
        self.max_world_y = self.world_height - 1
        self.middle_y = self.max_world_y // 2
        self.is_it_night_or_day = 'day'
        self.time_of_the_day = 12.0
        self.speed = self.speed_modes[2]
        self.speed_name = self.speed_modes_names[2]

    def world_tick(self):
        self.time_of_the_day += 0.025
        if self.time_of_the_day >= 24:
            self.time_of_the_day = 0
        if self.time_of_the_day >= 22 or self.time_of_the_day < 6:
            self.is_it_night_or_day = 'night'
        else:
            self.is_it_night_or_day = 'day'


class Grid(object):
    empty = '.'
    rock = '■'
    tree = '♠'
    trees_ratio = 5
    wood_per_tree = 15
    chunks_per_rock = 10

    def __init__(self, world, name):
        self.name = name
        self.height = world.world_height
        self.width = world.world_width
        self.grid = [[Grid.empty for _ in range(self.width)] for _ in range(self.height)]
        self.total_size = self.height * self.width
        self.middle_y = world.middle_y
        self.middle_x = world.middle_x
        self.num_rocks = 0
        self.num_trees = 0
        self.num_dwarfs = 0
        # default sleeping spot
        self.bed_y, self.bed_x = self.find_empty_cell_around()

    def generate_mountain(self, world):
        initial_y = int(world.max_world_y / 2)
        y = initial_y
        next_direction_change = False
        direction_decisions = (True, False)
        direction_change_cooldown = 4
        for x in range(int(world.max_world_y) + int(world.max_world_x)):
            if y <= world.max_world_y and x <= world.max_world_x and not next_direction_change:
                self.grid[y][x] = self.rock
                self.num_rocks += 1
                self.fill_with_rocks_to_south_edge(world, y, x)
            elif y < world.max_world_y and x <= world.max_world_x:
                y += 1
                self.grid[y][x] = self.rock
                self.num_rocks += 1
                self.fill_with_rocks_to_south_edge(world, y, x)
                next_direction_change = False
            else:
                return
            if direction_change_cooldown == 0:
                next_direction_change = random.choice(direction_decisions)
                direction_change_cooldown = 4
            else:
                direction_change_cooldown -= 1

    def fill_with_rocks_to_south_edge(self, world, y, x):
        y += 1
        while y <= world.max_world_y:
            self.grid[y][x] = self.rock
            self.num_rocks += 1
            y += 1

    def generate_trees(self, world):
        # trees must be integer like in a real world
        num_trees = (self.total_size - self.num_rocks) // self.trees_ratio
        for i in range(num_trees):
            while True:
                y = random.randint(0, world.max_world_y)
                x = random.randint(0, world.max_world_x)
                if self.grid[y][x] == self.empty:
                    self.grid[y][x] = self.tree
                    self.num_trees += 1
                    break

    def display_grid(self, dwarf=None, food=None, cursor=None):
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                if cursor is not None and cursor.y_coord == y and cursor.x_coord == x:
                    print(cursor.representation, end=" ")
                elif dwarf is not None and dwarf.y_coord == y and dwarf.x_coord == x:
                    print(dwarf.representation, end=" ")
                elif food is not None and food.y_coord == y and food.x_coord == x:
                    print(food.representation, end=" ")
                else:
                    print(cell, end=" ")
            print()

    def find_empty_cell_around(self, y=None, x=None):
        if y is None or x is None:
            y = self.middle_y
            x = self.middle_x
        direction = 1
        while True:
            if self.grid[y][x] == '.':
                return y, x
            else:
                if direction <= 8:
                    if direction == 1:
                        y -= 1
                    elif direction == 2:
                        y -= 1
                        x += 1
                    elif direction == 3:
                        x += 1
                    elif direction == 4:
                        y += 1
                        x += 1
                    elif direction == 5:
                        y += 1
                    elif direction == 6:
                        y += 1
                        x -= 1
                    elif direction == 7:
                        x -= 1
                    elif direction == 8:
                        y -= 1
                        x -= 1
                    direction += 1
                else:
                    direction = 1


class Dwarf(object):
    representation = 'A'

    def __init__(self, location, name, y=None, x=None):
        self.name = name
        if y is not None and x is not None:
            self.y_coord, self.x_coord = location.find_empty_cell_around(y, x)
        else:
            self.y_coord, self.x_coord = location.find_empty_cell_around()
        self.previous_y_coord = None
        self.previous_x_coord = None
        self.hp = 30
        self.hunger = 100
        self.eq = {'wood': 0, 'rock_chunks': 0, 'food': 0}
        location.num_dwarfs += 1

    def dwarf_action(self, world, location, food, cursor, key_event_canvas):
        self.dwarf_move(world, location, cursor)
        # (cursor.goal is not None) perhaps will need later
        if (cursor.goal in ['go', 'sleep'] and (self.y_coord == cursor.goal_y_coord and
                                                self.x_coord == cursor.goal_x_coord)) or \
                (cursor.goal in ['chop', 'mine', 'build', 'eat'] and
                 [self.y_coord, self.x_coord] in cursor.goal_neighbourhood.values()):
            # refresh screen after moving to the target and before taking action
            clear_console()
            location.display_grid(self, food, cursor)
            hud(world, location, self, food, cursor)
            time.sleep(world.speed)
            world.world_tick()
            if cursor.goal == 'chop':
                time.sleep(0.5)
                location.grid[cursor.goal_y_coord][cursor.goal_x_coord] = location.empty
                self.eq['wood'] += location.wood_per_tree
            if cursor.goal == 'mine':
                time.sleep(0.5)
                location.grid[cursor.goal_y_coord][cursor.goal_x_coord] = location.empty
                self.eq['rock_chunks'] += location.chunks_per_rock
            if cursor.goal == 'build':
                if self.eq['wood'] < 5:
                    print("Not enough wood, chop some by pointing at a tree ♠ and pressing 'c'")
                    print("Press enter")
                    key = ''
                    while key != 'enter':
                        key_event_canvas.update()
                        key = key_event_canvas.stored_key
                        key_event_canvas.reset_stored_key()
                else:
                    print("What would you like to build?(options are: bed, wall)")
                    key = ''
                    input_building = ''
                    while True:
                        while key != 'enter':
                            key_event_canvas.update()
                            key = key_event_canvas.stored_key
                            key_event_canvas.reset_stored_key()
                            if key != 'enter' and key is not None:
                                input_building += str(key)
                                print(input_building)
                        input_building = input_building.lower()
                        if input_building in world.list_of_allowed_buildings:
                            break
                        key = ''
                        input_building = ''
                        print("Please enter a correct command")
                        print("What would you like to build?(options are: bed, wall)")
                    if input_building in ['w', 'wall']:
                        location.grid[cursor.goal_y_coord][cursor.goal_x_coord] = '░'
                        self.eq['wood'] -= 5
                    elif input_building in ['b', 'bed']:
                        location.grid[cursor.goal_y_coord][cursor.goal_x_coord] = 'B'
                        location.bed_y, location.bed_x = cursor.goal_y_coord, cursor.goal_x_coord
                        self.eq['wood'] -= 5
            if cursor.goal == 'eat':
                food.amount -= 1
                self.hunger = 100
            cursor.goal = None

    def dwarf_move(self, world, location, cursor):
        self.previous_y_coord = self.y_coord
        self.previous_x_coord = self.x_coord
        if (cursor.goal in ['go', 'sleep'] and (self.y_coord != cursor.goal_y_coord or
                                                self.x_coord != cursor.goal_x_coord)) or \
                (cursor.goal in ['chop', 'mine', 'build', 'eat'] and
                 [self.y_coord, self.x_coord] not in cursor.goal_neighbourhood.values()):
            if self.y_coord < cursor.goal_y_coord and \
                    location.grid[self.y_coord + 1][self.x_coord] in world.allowed_to_step_on and \
                    self.y_coord + 1 != world.max_world_y:
                self.y_coord += 1
            elif self.y_coord > cursor.goal_y_coord and \
                    location.grid[self.y_coord - 1][self.x_coord] in world.allowed_to_step_on and \
                    self.y_coord - 1 != -1:
                self.y_coord -= 1
            elif self.x_coord < cursor.goal_x_coord and \
                    location.grid[self.y_coord][self.x_coord + 1] in world.allowed_to_step_on and \
                    self.x_coord + 1 != world.world_width:
                self.x_coord += 1
            elif self.x_coord > cursor.goal_x_coord and \
                    location.grid[self.y_coord][self.x_coord - 1] in world.allowed_to_step_on and \
                    self.x_coord - 1 != -1:
                self.x_coord -= 1
            while self.previous_y_coord == self.y_coord and self.previous_x_coord == self.x_coord:
                if self.y_coord == cursor.goal_y_coord:
                    # smart: when on the same y as goal, I want to implement it also for the same x as goal
                    if self.x_coord > cursor.goal_x_coord:
                        if self.y_coord + 1 != world.world_width and self.x_coord - 1 != -1 and \
                                location.grid[self.y_coord + 1][self.x_coord - 1] in world.allowed_to_step_on:
                            self.y_coord += 1
                            self.x_coord -= 1
                        elif self.y_coord - 1 != -1 and self.x_coord - 1 != -1 and \
                                location.grid[self.y_coord - 1][self.x_coord - 1] in world.allowed_to_step_on:
                            self.y_coord -= 1
                            self.x_coord -= 1
                    if self.x_coord < cursor.goal_x_coord:
                        if self.y_coord + 1 != world.world_width and self.x_coord + 1 != world.world_width and \
                                location.grid[self.y_coord + 1][self.x_coord + 1] in world.allowed_to_step_on:
                            self.y_coord += 1
                            self.x_coord += 1
                        elif self.y_coord - 1 != -1 and self.x_coord + 1 != world.world_width and \
                                location.grid[self.y_coord - 1][self.x_coord + 1] in world.allowed_to_step_on:
                            self.y_coord -= 1
                            self.x_coord += 1
                if self.previous_y_coord == self.y_coord and self.previous_x_coord == self.x_coord:
                    for i in range(3):
                        direction = random.randint(1, 4)
                        if direction == 1 and self.y_coord + 1 != world.world_width \
                                and location.grid[self.y_coord + 1][self.x_coord] in world.allowed_to_step_on:
                            self.y_coord += 1
                        elif direction == 2 and self.y_coord - 1 != -1 \
                                and location.grid[self.y_coord - 1][self.x_coord] in world.allowed_to_step_on:
                            self.y_coord -= 1
                        elif direction == 3 and self.x_coord + 1 != world.world_width \
                                and location.grid[self.y_coord][self.x_coord + 1] in world.allowed_to_step_on:
                            self.x_coord += 1
                        elif direction == 4 and self.x_coord - 1 != - 1 \
                                and location.grid[self.y_coord][self.x_coord - 1] in world.allowed_to_step_on:
                            self.x_coord -= 1

    def status(self, world, location, cursor, food):
        self.hunger -= 0.1
        if self.hunger < 50:
            cursor.create_goal(world, location, 'hungry', food)
        if self.hunger < 0:
            self.hp -= 1
        if cursor.goal is None and world.is_it_night_or_day == 'night' and (self.y_coord != location.bed_y or
                                                                            self.x_coord != location.bed_x):
            cursor.create_goal(world, location, 'sleepy')


class Food(object):
    representation = '♥'

    def __init__(self, location, dwarf=None):
        if dwarf is None:
            self.y_coord, self.x_coord = location.find_empty_cell_around()
        else:
            self.y_coord, self.x_coord = location.find_empty_cell_around(dwarf.y_coord + 1, dwarf.x_coord + 1)
        self.amount = 500
        self.neighbourhood = {1: [self.y_coord - 1, self.x_coord],
                              2: [self.y_coord, self.x_coord + 1],
                              3: [self.y_coord + 1, self.x_coord],
                              4: [self.y_coord, self.x_coord - 1]}


class Cursor(object):
    representation = '☼'

    def __init__(self, location):
        self.y_coord = 0
        self.x_coord = 0
        self.neighbourhood = {}
        self.target = location.grid[self.y_coord][self.x_coord]
        self.goal = None
        self.goal_y_coord = None
        self.goal_x_coord = None
        self.goal_neighbourhood = {}

    def move_cursor(self, world, location, key=''):
        if key == 'up' and self.y_coord > 0:
            self.y_coord -= 1
        elif key == 'left' and self.x_coord > 0:
            self.x_coord -= 1
        elif key == 'right' and self.x_coord < world.max_world_x:
            self.x_coord += 1
        elif key == 'down' and self.y_coord < world.max_world_y:
            self.y_coord += 1
        self.target = location.grid[self.y_coord][self.x_coord]

    def create_goal(self, world, location, key, food=None):
        self.neighbourhood = {1: [self.y_coord - 1, self.x_coord],
                              2: [self.y_coord, self.x_coord + 1],
                              3: [self.y_coord + 1, self.x_coord],
                              4: [self.y_coord, self.x_coord - 1]}
        if world.is_it_night_or_day == 'day':
            if key == 'm' and self.target == '■':
                self.goal = 'mine'
                self.goal_y_coord = self.y_coord
                self.goal_x_coord = self.x_coord
                self.goal_neighbourhood = self.neighbourhood
            elif key == 'c' and self.target == '♠':
                self.goal = 'chop'
                self.goal_y_coord = self.y_coord
                self.goal_x_coord = self.x_coord
                self.goal_neighbourhood = self.neighbourhood
            elif key == 'b' and self.target == '.':
                self.goal = 'build'
                self.goal_y_coord = self.y_coord
                self.goal_x_coord = self.x_coord
                self.goal_neighbourhood = self.neighbourhood
            elif key == 'g' and self.target == '.':
                self.goal = 'go'
                self.goal_y_coord = self.y_coord
                self.goal_x_coord = self.x_coord
        if key == 'hungry' and food is not None:
            self.goal = 'eat'
            self.goal_y_coord = food.y_coord
            self.goal_x_coord = food.x_coord
            self.goal_neighbourhood = food.neighbourhood
        if key == 'sleepy':
            self.goal = 'sleep'
            self.goal_y_coord = location.bed_y
            self.goal_x_coord = location.bed_x


def hud(world, location, dwarf, food, cursor):
    print()
    print("time:", int(world.time_of_the_day),
          "it is", world.is_it_night_or_day,
          "| HP:", dwarf.hp,
          "| stomach fullness:", int(dwarf.hunger),
          "| game speed:", world.speed_name)
    # EQ bar
    print("Equipment:", "wood:", dwarf.eq['wood'],
          "| rock chunks:", dwarf.eq['rock_chunks'],
          "| food:", dwarf.eq['food'])
    # controls
    print("arrows - move cursor, c - chop tree ♠, m - mine rock ■, b - build wooden wall ░ or bed B,"
          " g - go fo a walk, r - rescue(stop current task), q - quit")
    # logic for displaying info about current position od cursor
    if cursor.target == '♠':
        print("Currently pointing at: green ♠")
    if cursor.target == '■':
        print("Currently pointing at: rocky ■")
    if cursor.target == '░':
        print("Currently pointing at: wooden ░")
    if [cursor.y_coord, cursor.x_coord] == [dwarf.y_coord, dwarf.x_coord]:
        print("Currently pointing at: nice dwarf A")
    if [cursor.y_coord, cursor.x_coord] == [food.y_coord, food.x_coord]:
        print("Currently pointing at: food in quantity: " + str(food.amount))
    print()


def main():
    # assuming future option for multiple locations it is one "world" class to bond them all
    world = World('home-world')
    # keyboard input capturing class, hated to leave it be in peace partially useless,
    # so beware, it may have some wired shit inside
    key_event_canvas = KeyEventCanvas(process_key)
    greeting_screen(world, key_event_canvas)
    # create world
    home = Grid(world, 'home')
    home.generate_mountain(world)
    home.generate_trees(world)
    # create creatures
    dwarf = Dwarf(home, 'Lee')
    # create items
    food = Food(home, dwarf)
    # create other stuff
    cursor = Cursor(home)
    clear_console()
    while True:
        key_event_canvas.update()
        key = key_event_canvas.stored_key
        key_event_canvas.reset_stored_key()
        if key in ['1', '2', '3']:
            world.speed = world.speed_modes[int(key)]
            world.speed_name = world.speed_modes_names[int(key)]
        elif key == 'q':
            break
        cursor.move_cursor(world, home, key)
        dwarf.status(world, home, cursor, food)
        if cursor.goal is None and key in ['c', 'm', 'g', 'b']:
            cursor.create_goal(world, home, key, food)
        if key == 'r':
            cursor.goal = None
        if cursor.goal is not None:
            dwarf.dwarf_action(world, home, food, cursor, key_event_canvas)
        clear_console()
        home.display_grid(dwarf, food, cursor)
        hud(world, home, dwarf, food, cursor)
        time.sleep(world.speed)
        world.world_tick()


if __name__ == '__main__':
    main()
