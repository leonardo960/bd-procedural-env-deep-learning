from keras.models import Sequential
from keras.layers import Dense, Activation, Flatten
from keras.optimizers import Adam
import numpy as np
from collections import deque
import random
import math

class SLAMAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=100000)
        self.tempMemory = deque(maxlen=200)
        self.gamma = 1    # discount rate
        self.epsilon = 1.0  # exploration rate
        self.epsilon_min = 0.025
        self.epsilon_decay = 0.996
        self.learning_rate = 0.01
        self.learning_rate_decay = 0.01
        self.randomActions = [0,1,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2]
        self.model = self._build_model()
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(25, input_shape=(self.state_size, 3), activation='relu'))
        model.add(Flatten())
        model.add(Dense(50, activation='relu'))
        model.add(Dense(100, activation='relu'))
        model.add(Dense(50, activation='relu'))
        model.add(Dense(25, activation='relu'))
        model.add(Dense(self.action_size, activation='softmax'))
        model.compile(loss='mse',
                      optimizer=Adam(lr=self.learning_rate,decay=self.learning_rate_decay))
        return model
    def remember(self, state, action, reward, next_state, done):
            if reward == 0:
                self.memory.append((state, action, reward, next_state, done))
            else:
                self.tempMemory.append((state, action, reward, next_state, done))
    def act(self, state):
        currentMinDistance = 1
        for i in range(len(state[0])):
            if state[0][i][1] < currentMinDistance and not state[0][i][2]:
                currentMinDistance = state[0][i][1]
        if currentMinDistance < 0.049: #(5*sqrt(2)) arrotondato
            return random.randrange(self.action_size-1), False
        if np.random.rand() <= self.epsilon:
            if state[0][18][2] or state[0][19][2] or state[0][20][2]:
                return 2, False
            return self.randomActions[random.randrange(len(self.randomActions)-1)], True
        act_values = self.model.predict(state)
        return np.argmax(act_values[0]), False  # returns action
    def replay(self, batch_size):
        minibatch = []
        
        if len(self.tempMemory) > 0:
            minibatch.extend(self.tempMemory)
            self.memory.extend(self.tempMemory)
            self.tempMemory = []
            
        if len(self.memory) > batch_size:
            minibatch.extend(random.sample(self.memory, batch_size-len(minibatch)))
        else:
            minibatch.extend(random.sample(self.memory, len(self.memory)-len(minibatch)))
        
        
            
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = (reward + self.gamma *
                          np.amax(self.model.predict(next_state)[0]))
            target_f = self.model.predict(state)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        print("epsilon attuale: " + str(self.epsilon))
    def save(self, fn):
        self.model.save(fn) #fn è il file name del file dei pesi dei neuroni alla fine del training
        print("epsilon attuale: " + str(self.epsilon))
    def load(self, name, lastRandomValue):
        self.model.load_weights(name)
        self.epsilon = lastRandomValue
# if __name__ == "__main__":
    # # initialize gym environment and the agent
    # # env = gym.make('CartPole-v0')
	# # env = nostroEnvironment.create()
    # agent = SLAMAgent(60, 4) #60 (ampiezza 120 gradi totali ma un raggio sparato ogni 2 gradi) raggi sparati dagli occhi all'ambiente, 4 azioni: avanti, indietro, destra, sinistra
    # # Iterate the game
    # for e in range(episodes):
        # # reset state in the beginning of each game
        # state = env.reset() #sarebbero i 60 punti che tornano all'occhio del robot in posizione di spawn [(x1,y1,dist1),(x2,y2,dist2)...]
        # # time_t represents each frame of the game
        # # Our goal is to keep the pole upright as long as possible until score of 500
        # # the more time_t the more score
        # for time_t in range(500):
            # # turn this on if you want to render
            # # env.render()
            # # Decide action
            # action = agent.act(state)
			
            # # Advance the game to the next frame based on the action.
            # # Reward is 1 for every frame the pole survived
            # next_state, reward, done = env.step(action) #env.step torna una tupla (next_state, reward, done)
			
            # # Remember the previous state, action, reward, and done
            # agent.remember(state, action, reward, next_state, done)
            # # make next_state the new current state for the next frame.
            # state = next_state
            # # done becomes True when the game ends
            # # ex) The agent drops the pole
            # if done:
                # # print the score and break out of the loop
                # print("episode: {}/{}, score: {}"
                      # .format(e, episodes, time_t))
                # break
        # # train the agent with the experience of the episode
        # agent.replay(32)
    # agent.save("pesi_agente_slam")