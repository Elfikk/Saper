from AdapterML import Adapter
from Grid import SquareGrid
from GameLogic import Game

import numpy as np
import tensorflow as tf
# import matplotlib.pyplot as plt
from random import randint

from numpy import float32

from tf_agents.environments import py_environment, batched_py_environment, tf_py_environment
from tf_agents.specs import array_spec
from tf_agents.trajectories import time_step as ts
from tf_agents.environments import utils
from tf_agents.specs import tensor_spec
from tf_agents.networks import sequential
from tf_agents.agents.dqn import dqn_agent
from tf_agents.utils import common
from tf_agents.replay_buffers import py_uniform_replay_buffer
from tf_agents.policies import py_tf_eager_policy, random_tf_policy
from tf_agents.drivers import py_driver, dynamic_step_driver, dynamic_episode_driver

class MinesweeperEnv(py_environment.PyEnvironment):

    def __init__(self, width, height, n_mines):

        grid = SquareGrid(width, height, n_mines)
        self.gaming = Game(grid)
        self.adapter = Adapter(width, height)

        self.__n_mines = n_mines
        self.__n_tiles = width * height
        self.__standard_reward = 1.0 #float32(self.__n_tiles - self.__n_mines)

        self._action_spec = array_spec.BoundedArraySpec(
        shape=(), dtype= np.int32, minimum=0, maximum = self.__n_tiles - 1, name = 'action')
        self._observation_spec = array_spec.BoundedArraySpec(
        shape=(3 * self.__n_tiles,), dtype = np.int32, minimum = 0, maximum = 8, name = 'observation')
        
        # self._episode_ended = False

        random_index = randint(0, self.__n_tiles  - n_mines - 1)
        self.adapter.reveal_starting_tile(self.gaming, random_index)
        self._state = self.adapter.map_to_observation(self.gaming)

    def action_spec(self):
        return self._action_spec

    def observation_spec(self):
        return self._observation_spec

    def _reset(self):
        self.gaming.reset()
        random_index = randint(0, self.__n_tiles  - self.__n_mines - 1)
        self.adapter.reveal_starting_tile(self.gaming, random_index)
        self._state = self.adapter.map_to_observation(self.gaming)
        # self._episode_ended = False

        return ts.restart(self._state)

    def _step(self, action):

        # if self._episode_ended:
        #     return self.reset()

        if 0 <= action < self.__n_tiles:
            self.adapter.reveal_with_action(self.gaming, action)
        else:
            raise ValueError('`action` should be between 0 and less than\
                            the number of tiles on the board.')

        self._state = self.adapter.map_to_observation(self.gaming)

        if self.adapter.game_is_won(self.gaming):
            return ts.termination(self._state, self.__standard_reward)
        elif self.adapter.game_is_lost(self.gaming):
            return ts.termination(self._state, -self.__standard_reward)
        else:
            return ts.transition(self._state, self.adapter.get_reward(), 1.0)

def dense_layer(num_units):
  return tf.keras.layers.Dense(
      num_units,
      activation=tf.keras.activations.relu,
      kernel_initializer=tf.keras.initializers.VarianceScaling(
          scale=2.0, mode='fan_in', distribution='truncated_normal'))

def compute_avg_return(environment, policy, num_episodes=10, max_steps = 53):
    #Used for evaluating a model by calculating an average reward when
    #using a policy.
    total_return = 0.0
    total_steps = 0
    wins = 0
    for _ in range(num_episodes):

        # print(_, total_return)

        time_step = environment.reset()
        episode_return = 0.0

        steps = 0

        while not time_step.is_last() and steps < max_steps:
            steps += 1
            action_step = policy.action(time_step)
            time_step = environment.step(action_step.action)
            episode_return += time_step.reward
        total_return += episode_return
        total_steps += steps
        wins += 1 if time_step.reward.numpy() == 1.0 else 0

    avg_return = total_return / num_episodes    
    avg_steps = total_steps / num_episodes
    win_rate = wins / num_episodes

    return avg_return.numpy()[0], avg_steps, win_rate

if __name__ == "__main__":

    # environment = MinesweeperEnv(8, 8, 10)
    # utils.validate_py_environment(environment, episodes=5)

    train_py_env = batched_py_environment.BatchedPyEnvironment([MinesweeperEnv(8, 8, 10)])
    eval_py_env = batched_py_environment.BatchedPyEnvironment([MinesweeperEnv(8, 8, 10)])

    #Tensorflowd environments for compability.
    train_env = tf_py_environment.TFPyEnvironment(train_py_env)
    eval_env = tf_py_environment.TFPyEnvironment(eval_py_env)

    print('action_spec:', train_env.action_spec())
    print('time_step_spec.observation:', train_env.time_step_spec().observation)
    print('time_step_spec.step_type:', train_env.time_step_spec().step_type)
    print('time_step_spec.discount:', train_env.time_step_spec().discount)
    print('time_step_spec.reward:', train_env.time_step_spec().reward)

    fc_layer_params = (512, 512, 512, 512, 512)
    # fc_layer_params = (128, 128)

    action_tensor_spec = tensor_spec.from_spec(train_env.action_spec())
    num_actions = action_tensor_spec.maximum - action_tensor_spec.minimum + 1

    dense_layers = [dense_layer(num_units) for num_units in fc_layer_params]
    q_values_layer = tf.keras.layers.Dense(
    num_actions,
    activation=None,
    kernel_initializer=tf.keras.initializers.RandomUniform(
        minval=-0.03, maxval=0.03),
    bias_initializer=tf.keras.initializers.Constant(-0.2))
    #And here comes the QNetwork actually used by the DeepQ agent.
    q_net = sequential.Sequential(dense_layers + [q_values_layer])

    #Optimiser needed by agent - in this case using Adam, as per the tf
    #documentation example of DeepQ.
    optimizer = tf.keras.optimizers.Adam()
    #Integer step counter used by the DeepQ agent.
    train_step_counter = tf.Variable(0)

    # start_epsilon = 0.9
    # n_of_steps = 10000
    # end_epsilon = 0.0001
    # epsilon = tf.compat.v1.train.polynomial_decay(
    #   start_epsilon,
    #   train_step_counter,
    #   n_of_steps,
    #   end_learning_rate=end_epsilon)

    #The RL algo is represented by an "agent" object. Needs optimisation
    #method and step counter (step counter is discrete in the case of DeepQ).
    agent = dqn_agent.DqnAgent(
        train_env.time_step_spec(),
        train_env.action_spec(),
        q_network=q_net,
        optimizer=optimizer,
        td_errors_loss_fn=common.element_wise_squared_loss,
        train_step_counter=train_step_counter)
        #epsilon_greedy=epsilon)

    agent.initialize()

    #Policy defines the behaviour of the agent - can have random policy where
    #steps are taken randomly, or fixed behaviour policy, where agent repeats
    #a sequence of steps over and over - or you know, the actual wanted, 
    #complicated trained policy.
    eval_policy = agent.policy
    collect_policy = agent.collect_policy

    data_spec = agent.collect_data_spec

    batch_size = train_env.batch_size
    max_length = 1000
    replay_buffer_capacity = max_length * 32

    # replay_buffer = tf_uniform_replay_buffer.TFUniformReplayBuffer(
    #     data_spec,
    #     batch_size=batch_size,
    #     max_length=max_length)

    replay_buffer = py_uniform_replay_buffer.PyUniformReplayBuffer(
    capacity=replay_buffer_capacity,
    data_spec=tensor_spec.to_array_spec(data_spec))

    replay_observer = [replay_buffer.add_batch]

    dataset = replay_buffer.as_dataset(
    num_parallel_calls=None,
    sample_batch_size=batch_size,
    num_steps=2).prefetch(3)

    iterator = iter(dataset)

    random_policy = random_tf_policy.RandomTFPolicy(train_env.time_step_spec(),
                                                    train_env.action_spec())

    initial_collect_steps = 1

    # print(train_py_env.reset())

    random_driver = py_driver.PyDriver(
        train_py_env,
        py_tf_eager_policy.PyTFEagerPolicy(
        random_policy, use_tf_function=True),
        replay_observer, #Observers - includes the replay buffer.
        max_steps=initial_collect_steps
    )

    # print("1")

    # time_step = eval_env.reset()
    # print(time_step.reward.numpy())

    random_driver.run(train_py_env.reset())

    # print("2")

    agent.train = common.function(agent.train)

    # Reset the train step.
    agent.train_step_counter.assign(0)

    # print("3")
    # print(returns)

    # Reset the environment.
    time_step = train_env.reset()

    collect_driver = dynamic_episode_driver.DynamicEpisodeDriver(
    train_env,
    agent.collect_policy,
    observers= replay_observer,
    num_episodes=1)

    train_checkpointer = common.Checkpointer(
    ckpt_dir="checkpoint",
    max_to_keep=20,
    agent=agent,
    policy=agent.policy,
    replay_buffer=replay_buffer,
    global_step=agent.train_step_counter
    )

    train_checkpointer.initialize_or_restore()

    num_eval_episodes = 50

    if agent.train_step_counter.numpy() == 0:
        # Evaluate the agent's policy once before training - before its been trained.
        avg_return, avg_steps, win_rate = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
        # returns =  [avg_return]
        with open("checkpoint/returns.txt", "a") as f:
            f.write(str(avg_return) + "," + str(avg_steps) + "," + str(win_rate))
            f.write("\n")
    # else:
    #     returns = []

    num_iterations = 50000
    eval_interval = 100
    save_interval = 2500

    for _ in range(num_iterations):

        # Collect a few steps and save to the replay buffer.
        for i in range(10):
            time_step, _ = collect_driver.run(time_step, maximum_iterations=53)

        # Sample a batch of data from the buffer and update the agent's network.
        # print(next(iterator))
        experience = next(iterator)
        train_loss = agent.train(experience).loss

        step = agent.train_step_counter.numpy()

        if step % 10 == 0:
            print('step = {0}: loss = {1}'.format(step, train_loss))

        if step % eval_interval == 0:
            avg_return, avg_steps, win_rate  = compute_avg_return(eval_env, agent.policy, num_eval_episodes)
            print('step = {0}: Average Return = {1}, Average Steps in Game = {2}, Win Rate = {3}'.format(step, avg_return, avg_steps, win_rate))
            # returns.append(avg_return)
            with open("checkpoint/returns.txt", "a") as f:
                f.write(str(avg_return) +  "," + str(avg_steps) + "," + str(win_rate))
                f.write("\n")

        if step % save_interval == 0:
            train_checkpointer.save(agent.train_step_counter)

    # iterations = range(0, num_iterations + 1, eval_interval)

    # with open("checkpoint/returns.txt", "a") as f:
    #     for score in returns:
    #         f.write(str(score))
    #         f.write("\n")

    # plt.plot(iterations, returns)
    # plt.show()