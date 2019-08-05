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

    def addObj(self, obj_id):
        self.contents.add(obj_id)

    def removeObj(self, obj_id):
        self.contents.remove(obj_id)


class Grid:
    def __init__(self, num_rows, num_cols, x_min, x_max, y_min, y_max):
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.cell_width = (x_max - x_min)//num_cols
        self.cell_height = (y_max - y_min)//num_rows
        self.cells = [Cell()] * num_rows * num_cols

    def getCellContents(self, cell_num):
        return self.cells[cell_num].contents

    def getCellNum(self, x, y):
        row_index = (y - self.y_min)//self.cell_height
        col_index = (x - self.x_min)//self.cell_width
        cell_num = (row_index * self.num_cols) + col_index
        if cell_num < 0 or cell_num >= len(self.cells):
            return -1
        return int(cell_num)

    def insertIntoCell(self, cell_num, obj_id):
        if cell_num == -1:
            return
        self.cells[cell_num].addObj(obj_id)

    def removeFromCell(self, cell_num, obj_id):
        if cell_num == -1:
            return
        self.cells[cell_num].removeObj(obj_id)


class QuadTree:
    def __init__(self, x_min, x_max, y_min, y_max, parent=None):
        self.min_size = 32
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.x_range = self.x_max - self.x_min
        self.y_range = self.y_max - self.y_min
        self.x_mid = self.x_min + (self.x_range//2)
        self.y_mid = self.y_min + (self.y_range//2)

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

    def insertIntoCell(self, x, y, obj_id):
        """Insert object into cell and return the QuadTree that did the insertion"""
        if not self.withinBounds(x, y):
            return None

        if self.smallest_possible_tree:
            self.cell.addObj(obj_id)
            return self

        # recursively sub-divide tree into quarters
        # top left
        if x < self.x_mid and y < self.y_mid:
            if not self.top_left:
                self.top_left = QuadTree(self.x_min, self.x_mid, self.y_min, self.y_mid, self)
            return self.top_left.insertIntoCell(x, y, obj_id)

        # bottom left
        elif x < self.x_mid and y >= self.y_mid:
            if not self.bot_left:
                self.bot_left = QuadTree(self.x_min, self.x_mid, self.y_mid, self.y_max, self)
            return self.bot_left.insertIntoCell(x, y, obj_id)

        # top right
        elif x >= self.x_mid and y < self.y_mid:
            if not self.top_right:
                self.top_right = QuadTree(self.x_mid, self.x_max, self.y_min, self.y_mid, self)
            return self.top_right.insertIntoCell(x, y, obj_id)

        # bottom right
        else:
            if not self.bot_right:
                self.bot_right = QuadTree(self.x_mid, self.x_max, self.y_mid, self.y_max, self)
            return self.bot_right.insertIntoCell(x, y, obj_id)

    @staticmethod
    def removeFromCell(cell, obj_id):
        cell.removeObj(obj_id)

    def getCellContents(self, x, y):
        cell = self.findCell(x, y)
        return cell.contents if cell else None

    def findCell(self, x, y):
        if not self.withinBounds(x, y):
            return None

        if self.smallest_possible_tree:
            return self.cell

        # top left
        if x < self.x_mid and y < self.y_mid:
            if not self.top_left:
                return None
            return self.top_left.findCell(x, y)

        # bottom left
        elif x < self.x_mid and y >= self.y_mid:
            if not self.bot_left:
                return None
            return self.bot_left.findCell(x, y)

        # top right
        elif x >= self.x_mid and y < self.y_mid:
            if not self.top_right:
                return None
            return self.top_right.findCell(x, y)

        # bottom right
        else:
            if not self.bot_right:
                return None
            return self.bot_right.findCell(x, y)

    def withinBounds(self, x, y):
        return (
            x >= self.x_min and x <= self.x_max and
            y >= self.y_min and y <= self.y_max
        )

    def removeTree(self, tree):
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
    def getNearbyObjects(self, car):
        pass

    @abc.abstractmethod
    def updateObjects(self, cars):
        pass

    def processCollisions(self, cars):
        already_processed = set()
        for car in cars:
            collision_detected = False
            nearby_cars = self.getNearbyObjects(car)
            for car_index in nearby_cars:
                other = cars[car_index]
                if car == other or car.index in already_processed:
                    continue

                if car.checkCollision(other):
                    collision_detected = True
                    car.throttleDown()
                    other.throttleUp()
                    already_processed.update({car.index, other.index})

            if not collision_detected:
                car.throttleUp()


class GridCollisionSystem(CollisionSystem):
    def __init__(self, window, cars):
        self.num_rows = 128
        self.num_cols = 128
        self.x_min = -window.scrollregion_x/2.0
        self.y_min = -window.scrollregion_y/2.0
        self.x_max = window.scrollregion_x/2.0
        self.y_max = window.scrollregion_y/2.0
        self.grid = Grid(
            self.num_rows, self.num_cols, self.x_min, self.x_max, self.y_min, self.y_max
        )

        for car in cars:
            car.cell = self.grid.getCellNum(car.x, car.y)
            self.grid.insertIntoCell(car.cell, car.index)

    def getNearbyObjects(self, car):
        return self.grid.getCellContents(car.cell)

    def updateObjects(self, cars):
        for car in cars:
            cell_num = self.grid.getCellNum(car.x, car.y)
            if cell_num != car.cell:
                self.grid.removeFromCell(cell_num, car.index)
                self.grid.insertIntoCell(cell_num, car.index)
                car.cell = cell_num


class QuadTreeCollisionSystem(CollisionSystem):
    # TODO
    # Optimizations:
    # - have insertIntoCell return the cell id
    # - consolidate trees when removing objects to free memory
    # - when removing objects, reverse traverse rather than two full finds
    # - add reference to parent tree to each child tree for easier reverse
    # - store all cells in a hashtable with quick look up by id?

    def __init__(self, window, cars):
        self.x_min = -window.scrollregion_x/2.0
        self.y_min = -window.scrollregion_y/2.0
        self.x_max = window.scrollregion_x/2.0
        self.y_max = window.scrollregion_y/2.0
        self.quad = QuadTree(self.x_min, self.x_max, self.y_min, self.y_max)
        self.cell_to_tree_map = {}
        self.empty_trees = set()
        self.empty_trees_counter = 0

        for car in cars:
            tree = self.quad.insertIntoCell(car.x, car.y, car.index)
            car.cell = tree.cell
            self.cell_to_tree_map[car.cell.id] = tree

    def getNearbyObjects(self, car):
        return car.cell.contents  # speedup/simplification to ignore cars in adjacent cells

    def removeTrees(self):
        """Consolidates subtrees"""
        if self.empty_trees_counter % 100 != 0:  # no need to do this every frame
            self.empty_trees_counter += 1
            return

        for empty_tree in self.empty_trees:
            parent_tree = empty_tree.parent
            parent_tree.removeTree(empty_tree)

    def updateObjects(self, cars):
        for car in cars:
            cell = self.quad.findCell(car.x, car.y)
            if cell and cell != car.cell:
                current_tree = self.cell_to_tree_map[car.cell.id]
                current_tree.removeFromCell(car.cell, car.index)
                if current_tree.is_empty:
                    self.cell_to_tree_map.pop(car.cell.id)
                    self.empty_trees.add(current_tree)

                new_tree = self.quad.insertIntoCell(car.x, car.y, car.index)
                car.cell = new_tree.cell
                self.cell_to_tree_map[car.cell.id] = new_tree
                if new_tree in self.empty_trees:
                    self.empty_trees.remove(new_tree)

        self.removeTrees()
