from graphics import Canvas
import time
import random
import os

WORLD_WIDTH = 40
MAX_WORLD_X = WORLD_WIDTH - 1
MIDDLE_X = MAX_WORLD_X // 2
WORLD_HEIGHT = 15
MAX_WORLD_Y = WORLD_HEIGHT - 1
MIDDLE_Y = MAX_WORLD_Y // 2
TREES_RATIO = 5
WOOD_PER_TREE = 15
CHUNKS_PER_ROCK = 10
HEARTBEAT3 = 0.1
HEARTBEAT2 = 0.25
HEARTBEAT1 = 3
ALLOWED_TO_STEP_ON = ['☼', '♥', '.', 'B']
LIST_OF_ALLOWED_BUILDINGS = ['b', 'w', 'bed', 'wall']
KEYS_USED = ['Left', 'Right', 'Up', 'Down', 'Return', 'm', 'c', 'b', 'g', '1', '2', '3', 'q', 'e', 'd', 'w', 'a', 'l']


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
    # if key is not KEYS_USED:
    #     key = ''
    # it may come in handy later in some shape or form
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


def clear_console():
    # for windows cmd
    os.system('cls' if os.name == 'nt' else 'clear')
    # for CIP IDE
    # for i in range(25):
    #     print()


def greeting_screen(key_event_canvas):
    print("Karel Fortress")
    print("This is dwarf: A")
    print("It ain't much but has an honest hat.")
    print()
    print("It is Dwarf Fortress like game, you are controlling a cursor ☼. You can point at a tree to order dwarf to"
          " chop it for wood, point at rock in order for it to be mined."
          " You can build things on the ground represented by dots")
    print("Dwarf goes to heart representing food when it's hungry(fullness below 50)"
          " and goes to bed at 22 and wakes up at 6")
    print()
    print("Arrows control a cursor ☼, it starts at top left corner.")
    print("By pointing the cursor somewhere and pressing certain key you can order a dwarf to")
    print(" c - chop tree ♠, m - mine rock ■, b - build wooden wall ░ or bed B, g - just go for a walk")
    print("Additionally r - rescue(if dwarf is stuck), 1/2/3 - game speed")
    print("press enter to continue")
    key = ''
    while key != 'enter':
        key_event_canvas.update()
        key = key_event_canvas.stored_key
        key_event_canvas.reset_stored_key()


class Grid(object):
    empty = '.'
    rock = '■'
    tree = '♠'

    def __init__(self, name, height, width):
        self.name = name
        self.height = height
        self.width = width
        self.grid = [[Grid.empty for _ in range(width)] for _ in range(height)]
        self.total_size = height * width
        self.num_rocks = 0
        self.num_trees = 0
        self.num_dwarfs = 0
        # default sleeping spot
        self.bed_y, self.bed_x = self.find_empty_cell_around()
        self.is_it_night_or_day = 'day'
        self.time_of_the_day = 12.0

    def generate_mountain(self):
        initial_y = int(MAX_WORLD_Y / 2)
        y = initial_y
        next_direction_change = False
        direction_decisions = (True, False)
        direction_change_cooldown = 4
        for x in range(int(MAX_WORLD_Y) + int(MAX_WORLD_X)):
            if y <= MAX_WORLD_Y and x <= MAX_WORLD_X and not next_direction_change:
                self.grid[y][x] = self.rock
                self.num_rocks += 1
                self.fill_with_rocks_to_south_edge(y, x)
            elif y < MAX_WORLD_Y and x <= MAX_WORLD_X:
                y += 1
                self.grid[y][x] = self.rock
                self.num_rocks += 1
                self.fill_with_rocks_to_south_edge(y, x)
                next_direction_change = False
            else:
                return
            if direction_change_cooldown == 0:
                next_direction_change = random.choice(direction_decisions)
                direction_change_cooldown = 4
            else:
                direction_change_cooldown -= 1

    def fill_with_rocks_to_south_edge(self, y, x):
        y += 1
        while y <= MAX_WORLD_Y:
            self.grid[y][x] = self.rock
            self.num_rocks += 1
            y += 1

    def generate_trees(self):
        # trees must be integer like in a real world
        num_trees = (self.total_size - self.num_rocks) // TREES_RATIO
        for i in range(num_trees):
            while True:
                y = random.randint(0, MAX_WORLD_Y)
                x = random.randint(0, MAX_WORLD_X)
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

    def find_empty_cell_around(self, y=MIDDLE_Y, x=MIDDLE_X):
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

    def dwarf_action(self, location, food, cursor, key_event_canvas):
        self.dwarf_move(location, cursor)
        # (cursor.goal is not None) perhaps will need later
        if (cursor.goal in ['go', 'sleep'] and (self.y_coord == cursor.goal_y_coord and
                                                self.x_coord == cursor.goal_x_coord)) or \
                (cursor.goal in ['chop', 'mine', 'build', 'eat'] and
                 [self.y_coord, self.x_coord] in cursor.goal_neighbourhood.values()):
            if cursor.goal == 'chop':
                time.sleep(0.5)
                location.grid[cursor.goal_y_coord][cursor.goal_x_coord] = location.empty
                self.eq['wood'] += WOOD_PER_TREE
            if cursor.goal == 'mine':
                time.sleep(0.5)
                location.grid[cursor.goal_y_coord][cursor.goal_x_coord] = location.empty
                self.eq['rock_chunks'] += CHUNKS_PER_ROCK
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
                        input_building = input_building.lower()
                        if input_building in LIST_OF_ALLOWED_BUILDINGS:
                            break
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

    def dwarf_move(self, location, cursor):
        self.previous_y_coord = self.y_coord
        self.previous_x_coord = self.x_coord
        if (cursor.goal in ['go', 'sleep'] and (self.y_coord != cursor.goal_y_coord or
                                                self.x_coord != cursor.goal_x_coord)) or \
                (cursor.goal in ['chop', 'mine', 'build', 'eat'] and
                 [self.y_coord, self.x_coord] not in cursor.goal_neighbourhood.values()):
            if self.y_coord < cursor.goal_y_coord and \
                    location.grid[self.y_coord + 1][self.x_coord] in ALLOWED_TO_STEP_ON and \
                    self.y_coord + 1 != MAX_WORLD_Y:
                self.y_coord += 1
            elif self.y_coord > cursor.goal_y_coord and \
                    location.grid[self.y_coord - 1][self.x_coord] in ALLOWED_TO_STEP_ON and \
                    self.y_coord - 1 != -1:
                self.y_coord -= 1
            elif self.x_coord < cursor.goal_x_coord and \
                    location.grid[self.y_coord][self.x_coord + 1] in ALLOWED_TO_STEP_ON and \
                    self.x_coord + 1 != WORLD_WIDTH:
                self.x_coord += 1
            elif self.x_coord > cursor.goal_x_coord and \
                    location.grid[self.y_coord][self.x_coord - 1] in ALLOWED_TO_STEP_ON and \
                    self.x_coord - 1 != -1:
                self.x_coord -= 1
            while self.previous_y_coord == self.y_coord and self.previous_x_coord == self.x_coord:
                if self.y_coord == cursor.goal_y_coord:
                    # smart: when on the same y as goal, I want to implement it also for the same x as goal
                    if self.x_coord > cursor.goal_x_coord:
                        if self.y_coord + 1 != WORLD_HEIGHT and self.x_coord - 1 != -1 and \
                                location.grid[self.y_coord + 1][self.x_coord - 1] in ALLOWED_TO_STEP_ON:
                            self.y_coord += 1
                            self.x_coord -= 1
                        elif self.y_coord - 1 != -1 and self.x_coord - 1 != -1 and \
                                location.grid[self.y_coord - 1][self.x_coord - 1] in ALLOWED_TO_STEP_ON:
                            self.y_coord -= 1
                            self.x_coord -= 1
                    if self.x_coord < cursor.goal_x_coord:
                        if self.y_coord + 1 != WORLD_HEIGHT and self.x_coord + 1 != WORLD_WIDTH and \
                                location.grid[self.y_coord + 1][self.x_coord + 1] in ALLOWED_TO_STEP_ON:
                            self.y_coord += 1
                            self.x_coord += 1
                        elif self.y_coord - 1 != -1 and self.x_coord + 1 != WORLD_WIDTH and \
                                location.grid[self.y_coord - 1][self.x_coord + 1] in ALLOWED_TO_STEP_ON:
                            self.y_coord -= 1
                            self.x_coord += 1
                if self.previous_y_coord == self.y_coord and self.previous_x_coord == self.x_coord:
                    for i in range(3):
                        direction = random.randint(1, 4)
                        if direction == 1 and self.y_coord + 1 != WORLD_HEIGHT \
                                and location.grid[self.y_coord + 1][self.x_coord] in ALLOWED_TO_STEP_ON:
                            self.y_coord += 1
                        elif direction == 2 and self.y_coord - 1 != -1 \
                                and location.grid[self.y_coord - 1][self.x_coord] in ALLOWED_TO_STEP_ON:
                            self.y_coord -= 1
                        elif direction == 3 and self.x_coord + 1 != WORLD_WIDTH \
                                and location.grid[self.y_coord][self.x_coord + 1] in ALLOWED_TO_STEP_ON:
                            self.x_coord += 1
                        elif direction == 4 and self.x_coord - 1 != - 1 \
                                and location.grid[self.y_coord][self.x_coord - 1] in ALLOWED_TO_STEP_ON:
                            self.x_coord -= 1

    def status(self, location, cursor, food):
        self.hunger -= 0.1
        if self.hunger < 50:
            cursor.create_goal(location, 'hungry', food)
        if self.hunger < 0:
            self.hp -= 1
        if cursor.goal is None and location.is_it_night_or_day == 'night' and (self.y_coord != location.bed_y or
                                                                               self.x_coord != location.bed_x):
            cursor.create_goal(location, 'sleepy')


class Food(object):
    representation = '♥'

    def __init__(self, location, dwarf=None):
        if dwarf is None:
            self.y_coord, self.x_coord = location.find_empty_cell_around()
        else:
            self.y_coord, self.x_coord = location.find_empty_cell_around(dwarf.y_coord + 1, dwarf.x_coord + 1)
        self.amount = 500
        self.neighbourhood = {1: [self.y_coord - 1, self.x_coord], 2: [self.y_coord - 1, self.x_coord + 1],
                              3: [self.y_coord, self.x_coord + 1], 4: [self.y_coord + 1, self.x_coord + 1],
                              5: [self.y_coord + 1, self.x_coord], 6: [self.y_coord + 1, self.x_coord - 1],
                              7: [self.y_coord, self.x_coord - 1], 8: [self.y_coord - 1, self.x_coord - 1]}


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

    def move_cursor(self, location, key=''):
        if key == 'up' and self.y_coord > 0:
            self.y_coord -= 1
        elif key == 'left' and self.x_coord > 0:
            self.x_coord -= 1
        elif key == 'right' and self.x_coord < MAX_WORLD_X:
            self.x_coord += 1
        elif key == 'down' and self.y_coord < MAX_WORLD_Y:
            self.y_coord += 1
        self.target = location.grid[self.y_coord][self.x_coord]

    def create_goal(self, location, key, food=None):
        self.neighbourhood[1] = [self.y_coord - 1, self.x_coord]
        self.neighbourhood[2] = [self.y_coord - 1, self.x_coord + 1]
        self.neighbourhood[3] = [self.y_coord, self.x_coord + 1]
        self.neighbourhood[4] = [self.y_coord + 1, self.x_coord + 1]
        self.neighbourhood[5] = [self.y_coord + 1, self.x_coord]
        self.neighbourhood[6] = [self.y_coord + 1, self.x_coord - 1]
        self.neighbourhood[7] = [self.y_coord, self.x_coord - 1]
        self.neighbourhood[8] = [self.y_coord - 1, self.x_coord - 1]
        if location.is_it_night_or_day == 'day':
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


def main():
    key_event_canvas = KeyEventCanvas(process_key)
    clear_console()
    # greeting_screen(key_event_canvas)
    clear_console()
    # load world
    home = Grid('home', WORLD_HEIGHT, WORLD_WIDTH)
    home.generate_mountain()
    home.generate_trees()
    # load creatures
    dwarf = Dwarf(home, 'Lee')
    # load items
    food = Food(home, dwarf)

    cursor = Cursor(home)
    print("loading...")  # can be useful for testing
    if home and dwarf and food and cursor:
        print('OK')
    else:
        print('OOPS')
        time.sleep(2)
        return
    # print("Zoom out (Ctrl + -) so page doesn't scroll when using arrows")
    # print()
    # time.sleep(1)
    # print("Build bed before night!")
    # print()
    # time.sleep(1)
    # print("press enter")
    # key = ''
    # while key != 'enter':
    #     key_event_canvas.update()
    #     key = key_event_canvas.stored_key
    #     key_event_canvas.reset_stored_key()
    speed = HEARTBEAT3
    what_speed = 'fast'
    clear_console()
    home.display_grid(dwarf, food, cursor)
    time.sleep(speed)
    while True:
        if home.time_of_the_day >= 24:
            home.time_of_the_day = 0
        key_event_canvas.update()
        key = key_event_canvas.stored_key
        key_event_canvas.reset_stored_key()
        if key == '1':
            speed = HEARTBEAT1  # slow
            what_speed = 'slow'
        elif key == '2':
            speed = HEARTBEAT2  # normal
            what_speed = 'normal'
        elif key == '3':
            # noinspection SpellCheckingInspection
            speed = HEARTBEAT3  # fast boiiii
            what_speed = 'fast'
        elif key == 'q':
            # noinspection SpellCheckingInspection
            break  # like urwał mi od internetu
        cursor.move_cursor(home, key)
        dwarf.status(home, cursor, food)
        if cursor.goal is None and key in ['c', 'm', 'g', 'b', 'r']:
            cursor.create_goal(home, key, food)
        if cursor.goal is not None:
            dwarf.dwarf_action(home, food, cursor, key_event_canvas)
        clear_console()
        home.display_grid(dwarf, food, cursor)
        # Debugging time!
        # Which will actually use log or sth in future
        # print('dwarf', dwarf, 'cursor', cursor, 'goal', goal)
        # vitals bar
        print()
        print("time:", int(home.time_of_the_day), "it is", home.is_it_night_or_day, "| HP:", dwarf.hp,
              "| stomach fullness:", int(dwarf.hunger), "| game speed:", what_speed)
        # EQ bar
        print("Equipment:", "wood:", dwarf.eq['wood'],
              "| rock chunks:", dwarf.eq['rock_chunks'],
              "| food:", dwarf.eq['food'])
        # controls
        print("arrows - move cursor, c - chop tree ♠, m - mine rock ■, b - build wooden wall ░ or bed B,"
              " g - go fo a walk, r - rescue if stuck, q - quit")
        # logic for displaying info about current position od cursor
        if cursor.target == '♠':
            print("Currently pointing at: green ♠")
        if cursor.target == 'A':
            print("Currently pointing at: nice dwarf A")
        if cursor.target == '■':
            print("Currently pointing at: rocky ■")
        if cursor.target == '░':
            print("Currently pointing at: wooden ░")
        # if cursor['original_tenant'] == '♥':
        #     print("Currently pointing at:""food in quantity: " + str(food[2])
        print()
        time.sleep(speed)
        home.time_of_the_day += 0.025
        if home.time_of_the_day >= 22 or home.time_of_the_day < 6:
            home.is_it_night_or_day = 'night'
        else:
            home.is_it_night_or_day = 'day'


if __name__ == '__main__':
    main()
