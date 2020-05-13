"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import random

block_x = 0
def ml_loop(side: str):
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
            comm.send_to_game({"frame": scene_info["frame"], "command":"NONE"})
            ball_served = True
            # if rand_move > 0:
            #     # comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            #     comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            #     rand_move -= 1
            #     rand_time -= 1
            # elif rand_move < 0:
            #     # comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            #     comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            #     rand_move += 1
            #     rand_time -= 1
            # elif rand_time > 0:
            #     # comm.send_instruction(scene_info.frame, PlatformAction.NONE)
            #     comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            #     rand_time -= 1
            # else:
            #     if random.randint(0, 1):
            #         # comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            #         comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            #     else:
            #         # comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_RIGHT)
            #         comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_RIGHT"})
                    # ball_served = True
            #     if scene_info["blocker"] != None:
            #         block_x = scene_info["blocker"][0]
        else:
        # 3.4 Send the instruction for this frame to the game process
            if side == "1P":
                # comm.send_instruction(scene_info.frame,decide1p(scene_info))
                comm.send_to_game({"frame": scene_info["frame"], "command": decide1p(scene_info)})
            else:
                # comm.send_instruction(scene_info.frame,decide2p(scene_info))
                comm.send_to_game({"frame": scene_info["frame"], "command": decide2p(scene_info)})




def decide1p(scene_info):
    global block_x
    bx, by = scene_info["ball"]
    bx += 2.5
    vx, vy = scene_info["ball_speed"]
    px, py = scene_info["platform_1P"]

    px += 20
    if vy > 0:
        desx, desy = bx, by
        # if abs(vy) < 13  or scene_info.blocker == None:
        while desy < 420:
            desx += vx
            desy += vy
        desx -= vx
        desy -= vy
        if desx < 0:
            desx = -desx
        elif desx > 200:
            desx = 400 - desx
        if abs(scene_info["ball"][1] - 420) <= abs(vy)  and abs(vy) < 20:
            if vx > 0:
                return "MOVE_RIGHT"
            else:
                return "MOVE_LEFT"
        # if abs(desx - px) < abs(vx):
        #     return PlatformAction.NONE
        if desx < px:
            return "MOVE_LEFT"
        else:
            return "MOVE_RIGHT"
    else:
        if bx < px:
            return "MOVE_LEFT"
        else:
            return "MOVE_RIGHT"

def decide2p(scene_info):
    bx, by = scene_info["ball"]
    bx += 2.5
    # by += 2.5
    vx, vy = scene_info["ball_speed"]
    px, py = scene_info["platform_2P"]
    px += 20
    if vy < 0:
        desx, desy = bx, by
        while desy > 80:
            desx += vx
            desy += vy
        desx -= vx
        desy -= vy
        if desx < 0:
            desx = -desx
        elif desx > 200:
            desx = 400 - desx
        if abs(scene_info["ball"][1] - 80) <= abs(vy) and abs(vy) < 20:
            if vx > 0:
                return "MOVE_RIGHT"
            else:
                return "MOVE_LEFT"
        if desx < px:
            return "MOVE_LEFT"
        else:
            return "MOVE_RIGHT"
    else:
        # return PlatformAction.NONE
        if bx < px:
            return "MOVE_LEFT"
        else:
            return "MOVE_RIGHT"
