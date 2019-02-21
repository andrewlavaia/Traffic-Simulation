
# TODO
# How to limit # of collision checks?
# should cars only need to check whether there is any other car in front of them?
# implement get closest car function or closest car in front function?
def processCollisions(cars):
    already_processed = []

    for car1 in cars:
        collision_detected = False
        for car2 in cars:
            if car1 == car2 or car1 in already_processed:
                continue

            if car1.checkCollision(car2):
                car1.throttleDown()
                car2.throttleUp()
                already_processed.extend([car1, car2])
                collision_detected = True

        if collision_detected is False:
            car1.throttleUp()
