import abc


class Cell:
    def __init__(self):
        self.id = id(self)
        self.contents = set()

    def __eq__(self, other):
        return self.id == other.id

    @property
    def is_empty(self):
        return not self.contents

    def add_obj(self, obj_id):
        self.contents.add(obj_id)

    def remove_obj(self, obj_id):
        self.contents.remove(obj_id)


class Grid:
    def __init__(self, num_rows, num_cols, x_min, x_max, y_min, y_max):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.cell_width = (x_max - x_min) // num_cols
        self.cell_height = (y_max - y_min) // num_rows
        self.cells = [Cell()] * num_rows * num_cols

    def get_cell_contents(self, cell_num):
        return self.cells[cell_num].contents

    def get_cell_num(self, x, y):
        row_index = (y - self.y_min) // self.cell_height
        col_index = (x - self.x_min) // self.cell_width
        cell_num = (row_index * self.num_cols) + col_index
        if cell_num < 0 or cell_num >= len(self.cells):
            return -1
        return int(cell_num)

    def insert_into_cell(self, cell_num, obj_id):
        if cell_num == -1:
            return
        self.cells[cell_num].add_obj(obj_id)

    def removeFromCell(self, cell_num, obj_id):
        if cell_num == -1:
            return
        self.cells[cell_num].remove_obj(obj_id)


class QuadTree:
    def __init__(self, x_min, x_max, y_min, y_max, parent=None):
        self.min_size = 32
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_range = self.x_max - self.x_min
        self.y_range = self.y_max - self.y_min
        self.x_mid = self.x_min + (self.x_range // 2)
        self.y_mid = self.y_min + (self.y_range // 2)

        self.cell = Cell()

        self.parent = parent
        self.top_left = None
        self.top_right = None
        self.bot_left = None
        self.bot_right = None

    def __eq__(self, other):
        return self.cell.id == other.cell.id

    def __hash__(self):
        return hash(self.cell.id)

    @property
    def smallest_possible_tree(self):
        return self.x_range < self.min_size and self.y_range < self.min_size

    @property
    def is_empty(self):
        return (
            self.cell.is_empty and
            self.top_left is None and self.top_right is None and
            self.bot_left is None and self.bot_right is None
        )

    def insert_into_cell(self, x, y, obj_id):
        """Insert object into cell and return the QuadTree that did the insertion"""
        if not self.within_bounds(x, y):
            return None

        if self.smallest_possible_tree:
            self.cell.add_obj(obj_id)
            return self

        # recursively sub-divide tree into quarters
        # top left
        if x < self.x_mid and y < self.y_mid:
            if not self.top_left:
                self.top_left = QuadTree(self.x_min, self.x_mid, self.y_min, self.y_mid, self)
            return self.top_left.insert_into_cell(x, y, obj_id)

        # bottom left
        elif x < self.x_mid and y >= self.y_mid:
            if not self.bot_left:
                self.bot_left = QuadTree(self.x_min, self.x_mid, self.y_mid, self.y_max, self)
            return self.bot_left.insert_into_cell(x, y, obj_id)

        # top right
        elif x >= self.x_mid and y < self.y_mid:
            if not self.top_right:
                self.top_right = QuadTree(self.x_mid, self.x_max, self.y_min, self.y_mid, self)
            return self.top_right.insert_into_cell(x, y, obj_id)

        # bottom right
        else:
            if not self.bot_right:
                self.bot_right = QuadTree(self.x_mid, self.x_max, self.y_mid, self.y_max, self)
            return self.bot_right.insert_into_cell(x, y, obj_id)

    @staticmethod
    def remove_from_cell(cell, obj_id):
        cell.remove_obj(obj_id)

    def get_cell_contents(self, x, y):
        cell = self.find_cell(x, y)
        return cell.contents if cell else None

    def find_cell(self, x, y):
        if not self.within_bounds(x, y):
            return None

        if self.smallest_possible_tree:
            return self.cell

        # top left
        if x < self.x_mid and y < self.y_mid:
            if not self.top_left:
                return None
            return self.top_left.find_cell(x, y)

        # bottom left
        elif x < self.x_mid and y >= self.y_mid:
            if not self.bot_left:
                return None
            return self.bot_left.find_cell(x, y)

        # top right
        elif x >= self.x_mid and y < self.y_mid:
            if not self.top_right:
                return None
            return self.top_right.find_cell(x, y)

        # bottom right
        else:
            if not self.bot_right:
                return None
            return self.bot_right.find_cell(x, y)

    def within_bounds(self, x, y):
        return (
            x >= self.x_min and x <= self.x_max and
            y >= self.y_min and y <= self.y_max
        )

    def remove_tree(self, tree):
        if self.top_left and self.top_left == tree:
            self.top_left = None
        elif self.top_right and self.top_right == tree:
            self.top_right = None
        elif self.bot_left and self.bot_left == tree:
            self.bot_left = None
        elif self.bot_right and self.bot_right == tree:
            self.bot_right = None


class CollisionSystem(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_nearby_objects(self, car):
        pass

    @abc.abstractmethod
    def update_objects(self, cars):
        pass

    def process_collisions(self, cars):
        for car in cars:
            nearby_cars = self.get_nearby_objects(car)
            if not nearby_cars:
                car.throttle_up()

            collision_detected = False
            for car_index in nearby_cars:
                other = cars[car_index]
                if car == other:
                    continue

                if car.check_collision(other):
                    collision_detected = True
                    # other.throttle_up()
                    car.throttle_down()

            if not collision_detected:
                car.throttle_up()


class GridCollisionSystem(CollisionSystem):
    def __init__(self, window, cars):
        self.num_rows = 128
        self.num_cols = 128
        self.x_min = -window.scrollregion_x / 2.0
        self.y_min = -window.scrollregion_y / 2.0
        self.x_max = window.scrollregion_x / 2.0
        self.y_max = window.scrollregion_y / 2.0
        self.grid = Grid(
            self.num_rows, self.num_cols, self.x_min, self.x_max, self.y_min, self.y_max
        )

        for car in cars:
            car.cell = self.grid.get_cell_num(car.x, car.y)
            self.grid.insert_into_cell(car.cell, car.index)

    def getNearbyObjects(self, car):
        return self.grid.get_cell_contents(car.cell)

    def updateObjects(self, cars):
        for car in cars:
            cell_num = self.grid.get_cell_num(car.x, car.y)
            if cell_num != car.cell:
                self.grid.remove_from_cell(cell_num, car.index)
                self.grid.insert_into_cell(cell_num, car.index)
                car.cell = cell_num


class QuadTreeCollisionSystem(CollisionSystem):
    def __init__(self, window, cars):
        self.x_min = -window.scrollregion_x / 2.0
        self.y_min = -window.scrollregion_y / 2.0
        self.x_max = window.scrollregion_x / 2.0
        self.y_max = window.scrollregion_y / 2.0
        self.quad = QuadTree(self.x_min, self.x_max, self.y_min, self.y_max)
        self.cell_to_tree_map = {}
        self.empty_trees = set()
        self.empty_trees_counter = 0

        for car in cars:
            tree = self.quad.insert_into_cell(car.x, car.y, car.index)
            car.cell = tree.cell
            self.cell_to_tree_map[car.cell.id] = tree

    def get_nearby_objects(self, car):
        return car.cell.contents  # speedup/simplification to ignore cars in adjacent cells

    def remove_trees(self):
        """Consolidates subtrees"""
        if self.empty_trees_counter % 100 != 0:  # no need to do this every frame
            self.empty_trees_counter += 1
            return

        for empty_tree in self.empty_trees:
            parent_tree = empty_tree.parent
            parent_tree.remove_tree(empty_tree)

    def update_objects(self, cars):
        for car in cars:
            cell = self.quad.find_cell(car.x, car.y)
            if cell and cell != car.cell:
                current_tree = self.cell_to_tree_map[car.cell.id]
                current_tree.remove_from_cell(car.cell, car.index)
                if current_tree.is_empty:
                    self.cell_to_tree_map.pop(car.cell.id)
                    self.empty_trees.add(current_tree)

                new_tree = self.quad.insert_into_cell(car.x, car.y, car.index)
                car.cell = new_tree.cell
                self.cell_to_tree_map[car.cell.id] = new_tree
                if new_tree in self.empty_trees:
                    self.empty_trees.remove(new_tree)

        self.remove_trees()
