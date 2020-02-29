import numpy as np
import math
import sys

class NavigationMethods():
    @staticmethod
    def getObjectsInRadiusOfMe(my_controller, my_ship, radius):
        my_pose = my_ship.xy
        return my_controller.get_mobs_in_radius(my_pose, radius, enemy_only=False)


    @staticmethod
    def getAsteroidsInRadius(my_controller, objects_in_radius):
        all_asteroids = my_controller.get_data_from_asteroids();
        asteroids_in_radius =[]
        for a in all_asteroids:
            if a in objects_in_radius:
                asteroids_in_radius.append(a)

        return asteroids_in_radius

    @staticmethod
    def getAsteroidResultingVector(my_controller, my_ship, asteroids_in_radius):
        weights = []
        distances = []
        somme = 0
        result_vector = np.ndarray(2)
        if(len(asteroids_in_radius) > 1):
            for asteroid in asteroids_in_radius:
                u_vector = asteroid.dir
                closest_point = u_vector*asteroid.radius + asteroid.xy
                distance = math.sqrt((my_ship.xy[0]-closest_point[0])**2 + (my_ship.xy[1] - closest_point[1])**2)
                # weight = abs(my_ship.xy-closest_point)
                # weighted_angles.append(1/weight * u_vector)
                weight = 1/distance
                somme += weight
                weights.append((u_vector,weight))

            for vector, w in weights:
                print(f"somme : {somme}", file=sys.stderr)
                print(f"vector: {vector}", file=sys.stderr)
                print(f"w: {w}",file=sys.stderr)
                result_vector += vector* (w/somme)
                print(f"result_vector: {result_vector}",file=sys.stderr)
            return result_vector



    @staticmethod
    def checkIfInDeadzone(my_controller, my_ship):
        deadzone_center = my_controller.get_dead_zone_center()
        deadzone_radius = my_controller.get_dead_zone_radius() - 400
        distance = math.sqrt((my_ship.xy[0]-deadzone_center[0])**2 + (my_ship.xy[1] - deadzone_center[1])**2)
        return distance > deadzone_radius


        

    @staticmethod
    def moveShipAccordingToVector(my_controller, my_ship, u_vector):
        pass
        # print(u_vector)
        # angle_direction_to_go = np.angle(u_vector)
        # print(angle_direction_to_go)
    
    @staticmethod
    def getDeadZoneResultingVector(asteroids_in_radius):
        pass
        


    @staticmethod
    def getPlayersResultingVector(players):
        pass
    
    @staticmethod
    def getTotalResultingVector():
        pass

        