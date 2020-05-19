"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import numpy as np
from os import path
import random
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor
from sklearn.neural_network import MLPClassifier
import pickle
clf = None
scalerx_clf = None
def ml_loop(side: str):
    pre_blocker = -1
    global clf
    global scalerx_clf
    """
    The main loop for the machine learning process

    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```

    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    rand_move = random.randint(-20, 20)
    rand_time = random.randint(0, 56)

    if side == "1P":
        filename = path.join(path.dirname(__file__),"save/Classification1p.pickle")
        with open(filename, 'rb') as file:
            clf, scalerx_clf = pickle.load(file)
        filename = path.join(path.dirname(__file__),"save/Regressor1p.pickle")
        with open(filename, 'rb') as file:
            rgs, scalerx, scalery = pickle.load(file)
    else:
        filename = path.join(path.dirname(__file__),"save/Classification2p.pickle")
        with open(filename, 'rb') as file:
            clf, scalerx_clf = pickle.load(file)
        filename = path.join(path.dirname(__file__),"save\\Regressor2p.pickle")
        with open(filename, 'rb') as file:
            rgs, scalerx, scalery = pickle.load(file)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False
            rand_move = random.randint(-20, 20)
            rand_time = random.randint(0, 56)

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information
        if not ball_served:
            if rand_move > 0:
                # comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
                rand_move -= 1
                rand_time -= 1
            elif rand_move < 0:
                # comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
                rand_move += 1
                rand_time -= 1
            elif rand_time > 0:
                # comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
                rand_time -= 1
            else:
                if random.randint(0, 1):
                    # comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
                    comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
                else:
                    # comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
                    comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
                ball_served = True
        else:
        # 3.4 Send the instruction for this frame to the game process
            if pre_blocker == -1:
                pre_blocker = scene_info["blocker"][0]
                blocker_speed = 3
            blocker_speed = scene_info["blocker"][0] - pre_blocker
            pre_blocker = scene_info["blocker"][0]
            X = [scene_info["ball"], scene_info["ball_speed"], scene_info["platform_1P"], scene_info["platform_2P"], scene_info["blocker"]]
            X = np.asarray(X)
            X = X.reshape(1, 10)
            X = X[0, [0, 1, 2, 3, 8, 9]] # without platform
            X = np.append(X, blocker_speed).reshape(1, -1)

            # X = scalerx.transform(X.astype(float))
            # bx = scalery.inverse_transform(rgs.predict(X))
            bx = scalery.inverse_transform(rgs.predict(scalerx.transform(X.astype(float))))
            # print(X, flush = True)
            if side == "1P":
                # comm.send_instruction(scene_info.frame,decide1p(scene_info))
                comm.send_to_game({"frame": scene_info["frame"], "command": decide1p(scene_info, bx, X)})
            else:
                # comm.send_instruction(scene_info.frame,decide2p(scene_info))
                comm.send_to_game({"frame": scene_info["frame"], "command": decide2p(scene_info, bx, X)})
            
            # result = clf.predict(X)
            # print(result, flush = True)
            # if side == "1P":
            #     if result[0][0] > 0:
            #         comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            #     else:
            #         comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            # else:
            #     if result[0][1] > 0:
            #         comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            #     else:
            #         comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})

def decide1p(scene_info, bx, X):
    global clf
    global scalerx_clf
    vx, vy = scene_info["ball_speed"]
    if (bx > 5 and bx < 190) and abs(scene_info["ball"][1] - 415) <= vy and (bx > scene_info["platform_1P"][0] + 5 and bx < scene_info["platform_1P"][0] + 40 - 5):
    # if (bx > 5 and bx < 190) and abs(scene_info["ball"][1] - 420) <= vy and (bx > scene_info["platform_1P"][0] and bx < scene_info["platform_1P"][0] + 40):
        print("1p", flush = True)
        X[0, 3] = - X[0, 3]
        if vx > 0:
            X[0, 2] = abs(X[0, 3]) + 3
            X[0, 0] += vx
            if X[0, 0] > 195:
                X[0, 0] = 195
            X[0, 1] = 420
            # X = scalerx_clf.transform(X.astype(float))
            # print(X)
            C = clf.predict(scalerx_clf.transform(X.astype(float)))[0]
            if C == "U":
                # print("right", flush = True)
                return "MOVE_RIGHT"
            else:
                # print("left", flush = True)
                return "MOVE_LEFT"
        if vx < 0:
            X[0, 2] = -abs(X[0, 3]) - 3
            X[0, 0] += vx
            if X[0, 0] < 0:
                X[0, 0] = 0
            X[0, 1] = 420
            # print(X)
            C = clf.predict(scalerx_clf.transform(X.astype(float)))[0]
            if C == "U":
                # print("left", flush = True)
                return "MOVE_LEFT"
            else:   
                # print("right", flush = True)
                return "MOVE_RIGHT"
        # print()
    if abs((scene_info["platform_1P"][0] + 20) - (bx + 2.5)) < 5:
        return "NONE"
    if (scene_info["platform_1P"][0] + 20) > (bx + 2.5):
        return "MOVE_LEFT"
    else:
        return "MOVE_RIGHT"

def decide2p(scene_info, bx, X):
    vx, vy = scene_info["ball_speed"]
    if (bx > 5 and bx < 190) and abs(scene_info["ball"][1] - 80) <= -vy and (bx > scene_info["platform_2P"][0] and bx < scene_info["platform_2P"][0] + 40):
        print("\t2p", flush = True)
        X[0, 3] = - X[0, 3]
        if vx > 0:
            X[0, 2] = abs(X[0, 3]) + 3
            X[0, 0] += vx
            if X[0, 0] > 195:
                X[0, 0] = 195
            X[0, 1] = 420
            # X = scalerx_clf.transform(X.astype(float))
            # print(X)
            C = clf.predict(scalerx_clf.transform(X.astype(float)))[0]
            if C == "D":
                # print("right", flush = True)
                return "MOVE_RIGHT"
            else:
                # print("left", flush = True)
                return "MOVE_LEFT"
        if vx < 0:
            X[0, 2] = -abs(X[0, 3]) - 3
            X[0, 0] += vx
            if X[0, 0] < 0:
                X[0, 0] = 0
            X[0, 1] = 420
            # print(X)
            C = clf.predict(scalerx_clf.transform(X.astype(float)))[0]
            if C == "D":
                # print("left", flush = True)
                return "MOVE_LEFT"
            else:   
                # print("right", flush = True)
                return "MOVE_RIGHT"
        # print()

    if abs((scene_info["platform_2P"][0] + 20) - (bx + 2.5)) < 5:
        return "NONE"
    if (scene_info["platform_2P"][0] + 20) > (bx + 2.5):
        return "MOVE_LEFT"
    else:
        return "MOVE_RIGHT"
