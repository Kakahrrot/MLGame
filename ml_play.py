# python MLGame.py -i ml_play_template.py -i ml_play_template.py -i ml_play_template.py -i ml_play_template.py RacingCar 4 NORMAL

import numpy as np
import math
import torch
import torch.nn as nn
import torch.nn.functional as F
import pickle
import os

mode = "retrain"
a1 = -2 / (0 - 15)**2
a2 = -2 / (800 - 385)**2
dqn = None
prestate = None
preprestate = None
preaction = None
prepreaction = None
preprereward = None
previous_carlane = None
previous_carline = None
previous_carpos = None
counter = None
path = ""
feature_size = [17, 3]
# 0 1 2
# 3 4 5
# 6 7 8
actions = [["SPEED", "MOVE_LEFT"], ["SPEED"], ["SPEED", "MOVE_RIGHT"],
           ["MOVE_LEFT"],          [],        ["MOVE_RIGHT"],
           ["BRAKE", "MOVE_LEFT"], ["BRAKE"], ["BRAKE", "MOVE_RIGHT"]]   

posM, posV, velocityM, velocityV = torch.load(os.path.join(os.path.dirname(__file__), "save", "staticstic.pickle"))

class DQN():
    def __init__(self, n_states, n_actions, n_hidden, batch_size, lr, epsilon, gamma, target_replace_iter, memory_capacity):
        self.eval_net, self.target_net = Net(n_states, n_actions, n_hidden), Net(n_states, n_actions, n_hidden)
        self.memory = np.zeros((memory_capacity, n_states * 2 + 2)) # 每個 memory 中的 experience 大小為 (state + next state + reward + action)
        self.optimizer = torch.optim.Adam(self.eval_net.parameters(), lr=lr)
        self.loss_func = nn.MSELoss()
        self.memory_counter = 0
        self.learn_step_counter = 0 # 讓 target network 知道什麼時候要更新

        self.n_states = n_states
        self.n_actions = n_actions
        self.n_hidden = n_hidden
        self.batch_size = batch_size
        self.lr = lr
        self.epsilon = epsilon
        self.gamma = gamma
        self.target_replace_iter = target_replace_iter
        self.memory_capacity = memory_capacity

    def choose_action(self, state):
        x = torch.unsqueeze(torch.FloatTensor(state), 0)

        # epsilon-greedy
        if np.random.uniform() < self.epsilon: # 隨機
            action = np.random.randint(0, self.n_actions)
        else: # 根據現有 policy 做最好的選擇
            actions_value = self.eval_net(x) # 以現有 eval net 得出各個 action 的分數
            action = torch.max(actions_value, 1)[1].data.numpy()[0] # 挑選最高分的 action
        return action

    def store_transition(self, state, action, reward, next_state):
        # 打包 experience
        transition = np.hstack((state, [action, reward], next_state))
        # 存進 memory；舊 memory 可能會被覆蓋
        index = self.memory_counter % self.memory_capacity
        self.memory[index, :] = transition
        self.memory_counter += 1

    def learn(self):
        # 隨機取樣 batch_size 個 experience
        sample_index = np.random.choice(self.memory_capacity, self.batch_size)
        b_memory = self.memory[sample_index, :]
        b_state = torch.FloatTensor(b_memory[:, :self.n_states])
        b_action = torch.LongTensor(b_memory[:, self.n_states:self.n_states+1].astype(int))
        b_reward = torch.FloatTensor(b_memory[:, self.n_states+1:self.n_states+2])
        b_next_state = torch.FloatTensor(b_memory[:, -self.n_states:])

        # 計算現有 eval net 和 target net 得出 Q value 的落差
        q_eval = self.eval_net(b_state).gather(1, b_action) # 重新計算這些 experience 當下 eval net 所得出的 Q value
        q_next = self.target_net(b_next_state).detach() # detach 才不會訓練到 target net
        q_target = b_reward + self.gamma * q_next.max(1)[0].view(self.batch_size, 1) # 計算這些 experience 當下 target net 所得出的 Q value
        loss = self.loss_func(q_eval, q_target)

        # Backpropagation
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # 每隔一段時間 (target_replace_iter), 更新 target net，即複製 eval net 到 target net
        self.learn_step_counter += 1
        if self.learn_step_counter % self.target_replace_iter == 0:
            print("\nmodel refreshed\n", flush = True)
            self.target_net.load_state_dict(self.eval_net.state_dict())


class Net(nn.Module):
    def __init__(self, n_states, n_actions, n_hidden):
        super(Net, self).__init__()

        # 輸入層 (state) 到隱藏層，隱藏層到輸出層 (action)
        self.fc1 = nn.Linear(n_states, n_hidden)
        self.out = nn.Linear(n_hidden, n_actions)

    def forward(self, x):
        x = self.fc1(x)
        x = F.relu(x) # ReLU activation
        actions_value = self.out(x)
        return actions_value

class MLPlay:
    def __init__(self, player):
        global dqn
        global path
        global mode
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        path = os.path.join("save", "DQN_" + self.player + ".pickle")
        self.status = 0
        self.car_vel = 0                            # speed initial
        self.car_pos = (0,0)                        # pos initial
        self.distance = 0
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315, 385, 455, 525, 595]  # lanes center
        self.line = 0
        self.lines =   [70, 140, 210, 280, 350, 420, 490, 560]
        if(mode == "retrain"):
            dqn = torch.load(path)
            # with open(path, "rb") as file:
            #     dqn = pickle.load(file)
        pass

    def update(self, scene_info):
        global prestate
        global preaction 
        global dqn
        global actions
        global path
        global posM, posV, velocityM, velocityV
        global penalty
        global previous_carlane
        global previous_carline
        global preprestate
        global prepreaction
        global preprereward
        global previous_carpos
        global counter
        global a1, a2
        self.car_pos = scene_info[self.player]
        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                self.car_vel = car["velocity"]
                self.distance = car["distance"]
                self.car_lane = self.car_pos[0] // 70
                self.line = round(self.car_pos[0] / 70) - 1
                break

        if len(self.car_pos) == 0 and self.status == 0:
            self.status += 1
            prestate = np.zeros(feature_size[0] * feature_size[1])
            preaction = 1
            previous_carlane = self.car_lane
            counter = 0
            return actions[preaction]

        elif self.car_pos == () and (self.status == 1 or self.status == 2):
            if self.status == 1:
                self.status += 1
                if self.distance >= 20000:
                    preprereward += 2
                else:
                    preprereward -= 3.2
                #     print(self.player, "\n\n\t\tcongratulations!!", flush = True)
                # elif self.car_pos[0] == 19 or self.car_pos[0] == 611:
                #     print("side\n\n", flush = True)
                #     preprereward -= 3.2
                # else:
                #     print("cars\n\n", flush = True)
                #     preprereward -= 3
                # print(self.player, preprereward, self.car_pos, flush = True)
                dqn.store_transition(preprestate, prepreaction, preprereward, prestate)
                if dqn.memory_counter > dqn.memory_capacity:
                    dqn.learn()
                torch.save(dqn, path)
            return actions[preaction]

        if scene_info["status"] != "ALIVE":
            if self.status == 1:
                # learn from mistake
                if self.distance >= 20000:
                    preprereward += 2
                    print(self.player, "\n\n\t\tcongratulations!!", flush = True)
                elif self.car_pos[0] == 19 or self.car_pos[0] == 611:
                    print("side\n\n", flush = True)
                    preprereward -= 3.2
                else:
                    print("cars\n\n", flush = True)
                    preprereward -= 3.2
                print(self.player, preprereward, self.car_pos, flush = True)
                dqn.store_transition(preprestate, prepreaction, preprereward, prestate)
                if dqn.memory_counter > dqn.memory_capacity:
                    dqn.learn()
                torch.save(dqn, path)
            return "RESET"
        ratio = 0.5
        if counter % 35 == 0:
            previous_carpos = self.car_pos
        counter += 1
        prereward = self.distance / 20000
        # prereward = (a1 * ((self.car_vel - 15 ) ** 2) + 1) * ratio + (a2 * ((self.car_pos[1] - 385) ** 2) + 1 ) * (1 - ratio)
        if (self.car_pos[0] < 35 and (preaction == 0 or preaction == 3 or preaction == 6)) or (self.car_pos[0] > 595 and (preaction == 2 or preaction == 5 or preaction == 8)):
            print(self.player,"\n\n\t\tstay away!!!\n\n", flush = True)
            prereward -= 2
        elif (self.car_pos[0] < 35 and (preaction == 2 or preaction == 5 or preaction == 8)) or (self.car_pos[0] > 595 and (preaction == 0 or preaction == 3 or preaction == 6)):
            prereward += 2
        if abs(previous_carpos[0] - self.car_pos[0]) < 40:
            prereward += 1
        else:
            print(self.player,"\n\n\t\tdon't change lane!!!\n\n", flush = True)
            # prereward -= 2

        # doudge = []
        # above = []
        # print(self.car_pos, flush = True)
        # print(self.line, self.car_pos, flush = True)
        # for car in scene_info["cars_info"]:
        #     if car["id"] != self.player_no:
        #         X = car["pos"][0] // 70
        #         y = self.car_pos[1] - car["pos"][1]
        #         if ((y <= 200 and y >= 0 ) or (y <= 0 and y >= -80 )):
        #             above.append([car, X, y])
        #         # print("\t", X, car["pos"])
        #         if ((X  == self.car_lane or abs(X - self.car_lane) == 1) and ((y >= 0 and  y <= 100) or (y <= 0 and y >= -100 )) ) or  ((X  == self.line or X == self.line + 1) and ((y >= 0 and  y <= 100) or (y <= 0 and y >= -100 ))):
        #             # print("\t\t", car["pos"], X, "\n\n", flush = True)
        #             print("\n\n\t\twarning!!\n\n")
        #             doudge.append([car, X, y])
        # if len(doudge) == 0 and previous_carline != self.line:
        #     print(self.player,"\n\n\t\tdon't change lane!!!\n\n", flush = True)
        #     prereward -= 0.8
        # if len(doudge) != 0 :
        #     success = True
        #     for car, X, y in doudge:
        #         if X == self.car_lane:
        #             print(self.player,"\n\n\n\t\tdont suicide!!!\n\n\n\n", flush = True)
        #             prereward -= 1.6
        #             success = False
        #     if success:
        #         print(self.player,"\n\n\t\tnice job!!!\n\n", flush = True)
        #         prereward += 1.6
        
        print(self.player, prereward, self.car_pos, flush = True)


        state = np.zeros(feature_size[0] * feature_size[1])
        data = np.array(np.hstack([np.array((self.car_pos - posM)/posV), np.array((self.car_vel - velocityM)/velocityV)]))     
        # {'id': 0, 'pos': (299, 385), 'distance': 15352.2, 'velocity': 0, 'coin_num': 0}
        num = 1
        for car in scene_info["cars_info"]:
            if car["id"] != self.player_no:
                num += 1
                data = np.hstack([data, (car['pos'] - posM)/posV, (car['velocity'] - velocityM)/velocityV])
        # print(data, flush = True)
        state[0 : num * feature_size[1]] = data
        action = dqn.choose_action(state)
        dqn.store_transition(prestate, preaction, prereward, state)
        if dqn.memory_counter > dqn.memory_capacity:
            # print("learning", self.player, flush = True)
            dqn.learn()

        prestate = state
        preaction = action
        preprestate = prestate
        prepreaction = preaction
        preprereward = prereward
        previous_carlane = self.car_lane
        previous_carline = self.line
        return actions[action]

    def reset(self):
        """
        Reset the status
        """
        pass

def model_setup(): 
    global dqn

    n_actions = 3
    n_states = feature_size[0] * feature_size[1] # max * (pos, vel) 17 3 

    # Hyper parameters
    n_hidden = 100
    batch_size = 64
    lr = 0.01                 # learning rate
    epsilon = 0.1             # epsilon-greedy
    gamma = 0.9               # reward discount factor
    target_replace_iter = 100 # target network 更新間隔
    memory_capacity = 4000

    # 建立 DQN
    dqn = DQN(n_states, n_actions, n_hidden, batch_size, lr, epsilon, gamma, target_replace_iter, memory_capacity)
    

if mode == "restart":
    # print("restart")
    model_setup()
    
