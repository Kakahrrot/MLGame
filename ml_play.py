# python MLGame.py -i rule_base.py -i rule_base.py -i rule_base.py -i rule_base.py RacingCar 4 NORMAL



# ML play !!
def nearst(obj):
    if len(obj) == 1:
        return obj[0]
    else:
        tmp = obj[0]
        for car, X, y in obj[1:]:
            if tmp[2] < y :
                tmp = [car, X, y]
        return tmp

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
        self.moveL = None
        self.moveR = None
        self.nlcar = None
        self.nrcar = None
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
                if (X  == self.line or X == self.line + 1) and ((y >= 0 and  y <= 200) or (y <= 0 and y >= -100 )):
                # if (X  == self.line or X == self.line + 1) and ((y >= 0) or (y <= 0 and y >= -100 )):
                
                    # print("\t\t", car["pos"], X, "\n\n", flush = True)
                    doudge.append([car, X, y])

        # print(doudge, "\n", flush = True)
        # [[{'id': 152, 'pos': (105, 360), 'distance': 0, 'velocity': 13, 'coin_num': 0}, 1, 37], [{'id': 185, 'pos': (175, 248), 'distance': 0, 'velocity': 13, 'coin_num': 0}, 2, 149]]

        # return ["MOVE_LEFT", "MOVE_RIGHT", "SPEED", "BRAKE"]
        offset = 0
        left = []
        right = []
        change = False
        if len(doudge) <= 1:
            for car, X, y in doudge:
                if X == self.line:
                    offset = 10
                else:
                    offset = -10
        else:
            for car, X, y in doudge:
                if X == self.line:
                    offset = 10
                    left.append([car, X, y])
                else:
                    offset = -10
                    right.append([car, X, y])
            if len(left) != 0 and len(right) != 0:
                for lcar, lX, ly in left:
                    for rcar, rX, ry in right:
                        if abs(ly - ry) < 81:
                            change = True
                            break
                    if change:
                        break
        if not change:
            # if offset != 0:
                # print(self.player, "doudge", flush = True)
            self.moveL = None
            self.moveR = None
            if self.car_pos[0] > self.lines[self.line] + offset:
                return ["SPEED", "MOVE_LEFT"]
            else:
                return ["SPEED", "MOVE_RIGHT"]
        else:
            # print(self.player, "die", flush = True)
            # check for lane of self.line - 1 and self.line + 2
            if self.moveL == None and self.moveR == None:
                self.moveR = True
                self.moveL = True
                self.nlcar, nlX, nly = nearst(left)
                self.nrcar, nrX, nry = nearst(right)
                for acar, aX, ay in above:
                    if aX == self.line - 1 and self.moveL:
                        if abs(ay - nly) < 81 or abs(ay) < 81:
                            self.moveL = False
                    if aX == self.line + 2 and self.moveR:
                        if abs(ay - nry) < 81  or abs(ay) < 81:
                            self.moveR = False
                    if (not self.moveL) and (not self.moveR):
                        break
            if self.moveL:
                print(self.player, "move left", flush = True)
                if self.car_pos[1] - self.nlcar["pos"][1] < 120:
                    print("\tBREAK!!\n\n", flush = True)
                    return ["BRAKE", "MOVE_LEFT"]
                else:
                    return ["SPEED", "MOVE_LEFT"]
            elif self.moveR:
                print(self.player, "move right", flush = True)
                if self.car_pos[1] - self.nrcar["pos"][1] < 120:
                    print("\tBREAK!!\n\n", flush = True)
                    return ["BRAKE", "MOVE_RIGHT"]
                else:
                    return ["SPEED", "MOVE_RIGHT"]
            else:
                print(self.player, "die", flush = True)
                return ["BRAKE"]





        

    def reset(self):
        """
        Reset the status
        """
        pass
