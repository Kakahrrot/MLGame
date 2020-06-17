# python MLGame.py -i rule_base.py -i rule_base.py -i rule_base.py -i rule_base.py RacingCar 4 NORMAL



# ML play !!
class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.line = 0
        self.lines =   [70, 140, 210, 280, 350, 420, 490, 560]
        pass

    def update(self, scene_info):
        if scene_info["status"] != "ALIVE":
            return "RESET"
        if len(scene_info[self.player]) == 0:
            return "SPEED"
        self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                self.car_vel = car["velocity"]
                self.car_lane = self.car_pos[0] // 70
                self.line = round(self.car_pos[0] / 70) - 1
                break

        # for model training
        # if self.car_vel == 15:
        #     return ["SPEED", "MOVE_RIGHT"]
        
        doudge = []
        above = []
        # print(self.car_pos, flush = True)
        # print(self.line, self.car_pos, flush = True)
        for car in scene_info["cars_info"]:
            if car["id"] != self.player_no:
                X = car["pos"][0] // 70
                y = self.car_pos[1] - car["pos"][1]
                if ((y <= 200 and y >= 0 ) or (y <= 0 and y >= -80 )):
                    above.append([car, X, y])
                # print("\t", X, car["pos"])
                if (X  == self.line or X == self.line + 1) and ((y >= 0 and  y <= 100) or (y <= 0 and y >= -80 )):
                    # print("\t\t", car["pos"], X, "\n\n", flush = True)
                    doudge.append([car, X, y])


        # return ["MOVE_LEFT", "MOVE_RIGHT", "SPEED", "BRAKE"]
        offset = 0
        left = None
        right = None
        moveLine = self.line
        if len(doudge) <= 1:
            for item in doudge:
                if item[1] == self.line:
                    offset = 10
                else:
                    offset = -10
        else:
            for item in doudge:
                if item[1] == self.line:
                    offset = 10
                    left = item[0]
                else:
                    offset = -10
                    right = item[0]
                if left != None and right != None and self.line < 7:
                    moveLine = self.line + 1

        self.line = moveLine
        if self.car_pos[0] > self.lines[self.line] + offset:
            return ["SPEED", "MOVE_LEFT"]
        else:
            return ["SPEED", "MOVE_RIGHT"]

    def reset(self):
        """
        Reset the status
        """
        pass
