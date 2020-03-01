import numpy as np
import math
import sys

def normalizeVector(vector):
    unit_vector = vector / np.linalg.norm(vector)
    return unit_vector


def angleBetween(v1, v2):
    v1_unit = normalizeVector(v1)
    v2_unit = normalizeVector(v2)
    v1_y, v1_x = v1_unit[0], v1_unit[1]
    v2_y, v2_x = v2_unit[0], v2_unit[1]
    # return np.arccos(np.clip(np.dot(v1_unit, v2_unit), -1.0, 1.0))
    return np.arctan2(v1_x*v2_y - v1_y*v2_x, v1_x*v2_x + v1_y*v2_y)

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
                u_vector = asteroid.dir# #     

                print(f"u_vector : {u_vector}")
                closest_point = u_vector*asteroid.radius + asteroid.xy
                distance = math.sqrt((my_ship.xy[0]-closest_point[0])**2 + (my_ship.xy[1] - closest_point[1])**2)
                # weight = abs(my_ship.xy-closest_point)
                # weighted_angles.append(1/weight * u_vector)
                weight = 1/distance
                result_vector += weight * u_vector
                # somme += weight
                # weights.append((u_vector,weight))

            # for vector, w in weights:
            #     print(f"somme : {somme}", file=sys.stderr)
            #     print(f"vector: {vector}", file=sys.stderr)
            #     print(f"w: {w}",file=sys.stderr)
            #     result_vector += vector* (w/somme)
            print(f"result_vector: {result_vector}",file=sys.stderr)
            return result_vector



    @staticmethod
    def checkIfInDeadzone(my_controller, my_ship):
        deadzone_center = my_controller.get_dead_zone_center()
        deadzone_radius = my_controller.get_dead_zone_radius() - 400
        distance = math.sqrt((my_ship.xy[0]-deadzone_center[0])**2 + (my_ship.xy[1] - deadzone_center[1])**2)
        return distance > deadzone_radius


        

    @staticmethod
    def moveShipAccordingToVector(my_controller, my_ship, motion_control, u_vector):
        turn_angle = angleBetween(u_vector, my_ship.dir)
        print(f"angle : {my_ship.angle}")
        print(f"dir : {my_ship.dir}")
        print(f"turn_angle : {turn_angle}")
        if turn_angle > 0.05:
            motion_control.set_rotation(-1.0)
            return True
        elif turn_angle < -0.05:
            motion_control.set_rotation(1.0)
            return True
        else: return False
    
    @staticmethod
    def getDeadZoneResultingVector(asteroids_in_radius):
        pass
        


    @staticmethod
    def getPlayersResultingVector(players):
        pass
    
    @staticmethod
    def getTotalResultingVector():
        pass

        
