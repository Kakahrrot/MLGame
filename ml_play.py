"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)
data = []
def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        collect_data(scene_info)
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:

           	# comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
            comm.send_instruction(scene_info.frame, decide())

def collect_data(scene_info):
	global data
	data.append(scene_info)
	# print(scene_info.ball, scene_info.platform, "velocity: ({}, {})".format(vx, vy))

def decide():
	bx, by = data[-1].ball
	px, py = data[-1].platform
	px += 20
	if len(data) < 2:
		return PlatformAction.NONE
	vx, vy = (data[-1].ball[0] - data[-2].ball[0], data[-1].ball[1] - data[-2].ball[1])
	if by > 100 and vy > 0:
		desx, desy = bx, by
		while desy < 395:
			desx += vx
			desy += vy
		if desx < 0:
			desx = -desx
		elif desx > 200:
			desx = 400 - desx
		if abs(data[-1].ball[1] - 395) <= 20:
			if vx > 0:
				return PlatformAction.MOVE_RIGHT
			else:
				return PlatformAction.MOVE_RIGHT
		if desx < px:
			return PlatformAction.MOVE_LEFT
		else:
			return PlatformAction.MOVE_RIGHT
	else:
		return PlatformAction.NONE
