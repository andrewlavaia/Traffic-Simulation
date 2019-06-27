class Cell:
    def __init__(self):
        self.contents = set()

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
        index = (row_index * self.num_cols) + col_index
        if index < 0 or index >= len(self.cells):
            return -1
        return int(index)

    def insertIntoCell(self, cell_num, obj_id):
        if cell_num == -1:
            return
        self.cells[cell_num].addObj(obj_id)

    def removeFromCell(self, cell_num, obj_id):
        if cell_num == -1:
            return
        self.cells[cell_num].removeObj(obj_id)


class CollisionSystem:
    def __init__(self, window, cars):
        self.num_rows = 32
        self.num_cols = 32
        self.x_min = -window.scrollregion_x/2.0
        self.y_min = -window.scrollregion_y/2.0
        self.x_max = window.scrollregion_x/2.0
        self.y_max = window.scrollregion_y/2.0
        self.grid = Grid(
            self.num_rows, self.num_cols, self.x_min, self.x_max, self.y_min, self.y_max
        )

        for car in cars:
            car.cell_num = self.grid.getCellNum(car.x, car.y)
            self.grid.insertIntoCell(car.cell_num, car.index)

    def processCollisions(self, cars):
        already_processed = set()
        for car in cars:
            collision_detected = False
            cars_indices_in_cell = self.grid.getCellContents(car.cell_num)
            for car_index in cars_indices_in_cell:
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

    def updateCells(self, cars):
        for car in cars:
            cell_num = self.grid.getCellNum(car.x, car.y)
            if cell_num != car.cell_num:
                self.grid.removeFromCell(cell_num, car.index)
                self.grid.insertIntoCell(cell_num, car.index)
                car.cell_num = cell_num
