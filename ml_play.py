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
        self.car_pos = (0,0)                      # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.way = [[-1, 0], [1, 0], [0,1], [0, -1]]
        self.p_car_vel = 15
        self.p_car_pos = 999
        self.way = [0 for i in range(18)]
        pass

    def update(self, scene_info):
 
        def check_matrix():
            matrix = [[-1 for x in range(18)] for y in range(18)] #-1 is can run
            
            
            count = 0
            x_wall = self.car_pos[0]
            while(x_wall > 0):
                x_wall -= 40
                for i in range(18):
                    if(8 - count > -1):
                        matrix[i][8-count] = 0
                count += 1
        
            count = 0
            x_wall = self.car_pos[0]
            while(x_wall < 630):
                x_wall += 40
                for i in range(18):
                    if(8 + count < 18):
                        matrix[i][8+count] = 0
                count += 1
            self.p_car_pos = 0
            count = 0
            #print("car pos", self.car_pos)
            # #print("car spd", self.car_vel)
         
            for coin in scene_info["coins"]:
                
                
                x = coin[0] - self.car_pos[0]
                y = coin[1] - self.car_pos[1]#23
                
                if(x > 0 and coin[0] < 590):
                    x+=23
                elif(x < 0 and coin[0] > 30):
                    x -= 23
                
     
                if(y < 0):
                    y -= 30
                elif(y > 0):
                    y += 30
                
                x_matrix = x // 40
                y_matrix = y // 80
                # if(x_matrix < 0):
                #     x_matrix += 1
                #print("coin", coin, x_matrix, y_matrix)
                ##print(x_matrix, y_matrix)
                # if(x % 40 > 0 and y % 80 > 0):
                #     if(x_matrix < 9 and y_matrix < 10):
                #         matrix[8+y_matrix][x_matrix+8+1] = 100
                #     if(x_matrix < 9 and y_matrix < 9):
                #         matrix[8+y_matrix+1][x_matrix+8+1] = 100
                #     if(y_matrix < 9 and x_matrix < 10):
                #         matrix[8+y_matrix+1][x_matrix+8] = 100
                # if x % 40 > 0:
                #     if(x_matrix < 9 and y_matrix < 10):
                #         matrix[y_matrix+8][x_matrix+8+1] = 100
                # elif y % 80 > 0:
                #     if(y_matrix < 9 and x_matrix < 10):
                #         matrix[y_matrix+8+1][x_matrix+8] = 100
                if(x_matrix < 10 and y_matrix < 10):
                    matrix[y_matrix+8][x_matrix+8] = 100
            
                
            right_car_exist = False
            left_car_exist = False
            for car in scene_info["cars_info"]:
                x = (car["pos"][0] - self.car_pos[0])  #x relative matrix
                y = (car["pos"][1] - self.car_pos[1])  #y relative matrix
                if(x < 48 and x > 0 and y < 80 and y > -80):
                    right_car_exist = True
                if(x > -48 and x < 0 and y < 80 and y > -80):
                    left_car_exist = True
                if(x > -40 and x < 40 and y < 0):
                    if(car['pos'][1] < self.car_pos[1] 
                    and self.p_car_pos < car['pos'][1]):
                        self.p_car_pos = car['pos'][1]
                        self.p_car_vel = car['velocity']
                        count += 1
                x_matrix = x // 40
                y_matrix = y // 80
                ##print(x_matrix, y_matrix)
                if(x % 40 > 0 and y % 80 > 0):
                    if(x_matrix < 9 and y_matrix < 10):
                        matrix[8+y_matrix][x_matrix+8+1] = car["velocity"]
                    if(x_matrix < 9 and y_matrix < 9):
                        matrix[8+y_matrix+1][x_matrix+8+1] = car["velocity"]
                    if(y_matrix < 9 and x_matrix < 10):
                        matrix[8+y_matrix+1][x_matrix+8] = car["velocity"]
                elif x % 40 > 0:
                    if(x_matrix < 9 and y_matrix < 10):
                        matrix[y_matrix+8][x_matrix+8+1] = car["velocity"]
                elif y % 80 > 0:
                    if(y_matrix < 9 and x_matrix < 10):
                        matrix[y_matrix+8+1][x_matrix+8] = car["velocity"]
                if(x_matrix < 10 and y_matrix < 10):
                    matrix[y_matrix+8][x_matrix+8] = car["velocity"]
                    

            
            
            matrix[8][8] = 2
            if(left_car_exist):
                matrix[8][7] = 16
            if(right_car_exist):
                matrix[8][9] = 16
            
            # target_x = 0
            # target_y = 0     
            for i in range(18):
                self.way[i] = 0
            #count car way
            for i in range(8):
                if(matrix[7-i][8]  == 100):
                    self.way[8] = self.way[8] - (8-i)*4 + i*2
                if(matrix[7-i][8] != 0 and matrix[7-i][8] != 100):
                    #self.p_car_vel = matrix[7-i][8]
                    self.way[8] = 7-i + self.way[8]
                    break
                if(i == 7):
                    pass
                    #self.p_car_vel = 15
            for i in range(18):
                for j in range(8):
                    if(i == 8):
                        continue
                    if(matrix[7-j][i]  == 100):
                        self.way[i] = self.way[i] - (8-j)*4 + j*2
                    if(matrix[7 - j][i] != 0 and matrix[7-j][i] != 100):
                        self.way[i] = 7-j + self.way[i]
                        break
            if(matrix[8][7] == 100):
                self.way[7] = self.way[7] - 30
            if(matrix[8][9] == 100):
                self.way[9] = self.way[9] - 30
            if(matrix[8][7] == 0 and matrix[8][6] == 100):
                self.way[6] = self.way[6] - 15
            if(matrix[8][9] == 0 and matrix[8][10] == 100):
                self.way[10] = self.way[10] - 15
        
            # for i in range(18):
            #     for j in range(18):
            #         print("{:>3}".format(int(matrix[i][j])) , end=' ')
            #         pass
            #     print()
                    
            # print()
            # for i in range(18):
            #     print("{:>3}".format(self.way[i]) , end=' ')
            #     pass
                
            
            l =  move(matrix, left_car_exist, right_car_exist)
            # print(l)
            return l
            
        def move(matrix, left_car_exist, right_car_exist):
            m_way = 8
            tmp = 8
            '''
            for i in range(4, 13):
                if(self.way[i] < tmp):
                    m_way = i
                    tmp = self.way[i]
            '''
            right_car = True
            left_car = True
            for i in range(8):
                if(i == 0):
                    if(self.way[8] < tmp):
                        m_way = 8
                        tmp = self.way[8]
                else:
                    if((matrix[8][8+i] == 0 or matrix[8][8+i] == 100) and right_car):
                        if(self.way[8+i] < tmp):
                            m_way = i+8
                            tmp = self.way[8+i]
                    elif(matrix[8][8+i] != 0 and matrix[8][8+i] != 100):
                        right_car = False
                    ##print(8+i)
                    if((matrix[8][8-i] == 0 or matrix[8][8-i] == 100) and left_car):
                        if(self.way[8-i] < tmp):
                            m_way = 8-i
                            tmp = self.way[8-i]
                    elif((matrix[8][8-i] != 0 and matrix[8][7] != 100)):
                        left_car = False

            # print("select way:", m_way,' ' ,tmp)
            # print('gap pos', abs(self.p_car_pos - self.car_pos[1]))
            # print('gap speed ', self.car_vel - self.p_car_vel)
            # print('p speed', self.p_car_vel)
            # print('car speed ', self.car_vel)
            gap = abs(self.p_car_pos - self.car_pos[1])
            if(scene_info["frame"] < 10):
                gap = 1000
            #diff 1 distance
            
            if(gap < 150 and self.car_vel - self.p_car_vel > 0
            and self.way[7] <= self.way[9]):
                return ['BRAKE', 'MOVE_LEFT']
            elif(gap < 150 and self.car_vel - self.p_car_vel > 0
            and self.way[7] > self.way[9]):
                return ['BRAKE', 'MOVE_RIGHT']
            elif(self.car_vel - self.p_car_vel > 5 and gap < 220 
            and self.way[7] <= self.way[9] and matrix[8][7] == 0 ):
                return['BRAKE', 'MOVE_LEFT']
            elif(self.car_vel - self.p_car_vel > 5 and gap < 220
            and self.way[7] > self.way[9] and matrix[8][9] == 0):
                return['BRAKE', 'MOVE_RIGHT']
            elif(self.car_vel - self.p_car_vel > 10 and gap < 290 
            and self.way[7] <= self.way[9] and matrix[8][7] == 0):
                return['BRAKE', 'MOVE_LEFT']
            elif(self.car_vel - self.p_car_vel > 10 and gap < 290
            and self.way[7] > self.way[9] and matrix[8][9] == 0):
                return['BRAKE', 'MOVE_RIGHT']

            if(left_car_exist and (matrix[8][9] == 0 or matrix[8][9] == 100)):
                return ["SPEED", 'MOVE_RIGHT']
            elif(right_car_exist and (matrix[8][7] == 0 or matrix[8][7] == 100)):
                return ["SPEED", 'MOVE_LEFT']
            # if(abs(self.p_car_vel - self.car_vel) < 15 and gap < 240 and self.way[7] < self.way[9] and matrix[7][8] == 0):
            #     return['BRAKE', 'MOVE_LEFT']
            # elif(abs(self.p_car_vel - self.car_vel) < 15 and gap < 240 and self.way[7] > self.way[9] and matrix[7][9] == 0):
            #     return['BRAKE', 'MOVE_RIGHT']
            if(m_way == 8):
                return ['SPEED']
            elif(m_way < 8  and matrix[8][7] == 0 
            and matrix[7][7] == 0 and self.car_pos[0] > 315):
                return ["SPEED", 'MOVE_LEFT']
            # elif(m_way < 8 and matrix[8][7] == 0 and self.way[8] >= 7 
            # and matrix[8][9] == 0):
            #     return ['MOVE_LEFT']
            elif(matrix[8][9] == 0  and matrix[7][9] == 0 
            and m_way > 8 and self.car_pos[0] > 315):
                return ['SPEED', 'MOVE_RIGHT']
            elif(matrix[8][9] == 0  and matrix[7][9] == 0 
            and m_way > 8 and self.car_pos[0] <= 315):
                return ['SPEED', 'MOVE_RIGHT']
            elif(m_way < 8  and matrix[8][7] == 0 
            and matrix[7][7] == 0 and self.car_pos[0] <= 315):
                return ["SPEED", 'MOVE_LEFT']
            # elif(matrix[8][9] == 0 and self.way[8] >= 7):
            #     return ['MOVE_RIGHT']
            else:
                return["SPEED"]

        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]

        for car in scene_info["cars_info"]:
            if car["id"]==self.player_no:
                self.car_vel = car["velocity"]

        if scene_info["status"] != "ALIVE":
            return "RESET"
        self.car_lane = self.car_pos[0] // 70
        return check_matrix()

    def reset(self):
        """
        Reset the status
        """
        pass
