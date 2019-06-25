from worker import WorkRequest
import multiprocessing as mp
import time
import heapq


# Defines an Event that will occur at time t between cars a and b
# if neither a & b are None -> collision with another car
# if one of a or b is None -> collision with wall
# if both a & b are None -> do nothing
class Event:
    def __init__(self, t, a, b, cntA, cntB):
        self.time = t  # time from start of simulation
        self.a = a
        self.b = b
        self.countA = cntA
        self.countB = cntB

    # comparators
    def __lt__(self, that):
        return self.time <= that.time

    def __eq__(self, that):
        return self.time == that.time and self.a == that.a and self.b == that.b

    # check if event was invalidated from prior collision
    def isValid(self, cars):
        if (self.a is not None and self.countA != cars[self.a].collision_count):
            return False
        if (
            self.b is not None and isinstance(self.b, int) and
            self.countB != cars[self.b].collision_count
        ):
            return False
        return True

# TODO add support for collisions at intersections
# need to re-predict all collisions at each intersection


# Collision System is used to predict when and how cars will collide
class CollisionSystem:
    # Inserts all predicted collisions with a given car as Events into the queue.
    def predict(a, next_logic_tick, limit, cars, result_q):
        if a is None:
            return

        # insert predicted collision with every other car as an
        # event into the priority queue if collision time is
        # between next_logic_tick and limit
        for b in cars:
            if a == b:
                continue
            dt = a.timeToHit(b)
            evt = Event(
                next_logic_tick + dt, a.index, b.index, a.collision_count, b.collision_count
            )

            if next_logic_tick + dt <= limit:
                result_q.put_nowait(evt)

    def processCompletedWork(result_q, pq):
        while not result_q.empty():
            evt = result_q.get()
            heapq.heappush(pq, evt)

    def processWorkRequests(work_q, result_q):
        print("{0} started".format(mp.current_process().name))
        while True:
            work = work_q.get()  # blocks automatically when q is empty
            print("{0} is working. {1} requests remaining.".format(mp.current_process().name, work_q.qsize()))
            CollisionSystem.predict(
                work.cars[work.car_index], work.time, work.limit, work.cars, result_q
            )

    def processCollisionEvents(cars, pq, nextLogicTick, work_q, result_q):
        lastEvt = None
        while len(pq) > 0 and pq[0].time < nextLogicTick:
            evt = heapq.heappop(pq)

            if evt.isValid(cars) and (lastEvt is None or evt != lastEvt):
                lastEvt = evt  # prevents infinite collision errors
            else:
                continue

            a = evt.a
            b = evt.b
            if isinstance(b, int):
                cars[a].throttleDown(b)
                cars[a].last_collision = b
                cars[b].last_collision = a
                cars[a].collision_count += 1
                cars[b].collision_count += 1
                work_q.put_nowait(WorkRequest(a, nextLogicTick, 10000, cars))
                work_q.put_nowait(WorkRequest(b, nextLogicTick, 10000, cars))
