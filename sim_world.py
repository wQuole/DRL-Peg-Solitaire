from viz import Viz
from hex_grid import Triangle, Diamond
from action import Action


class SimWorld:

    def __init__(self, cfg, viz_toggle=False):
        """ Initialize the SimulationWorld and the game state """
        if cfg.shape.upper() == "TRIANGLE":
            self.board = Triangle(cfg.size, cfg.holes)
            self.num_cells = self.board.size * (self.board.size + 1) / 2
        elif cfg.shape.upper() == "DIAMOND":
            self.board = Diamond(cfg.size, cfg.holes)
            self.num_cells = self.board.size * self.board.size
        else:
            raise Exception("Shape must be 'Triangle' or 'Diamond'")

        self.viz_toggle = viz_toggle
        if self.viz_toggle:
            self.viz = Viz(self.board)

    def get_all_legal_moves(self):
        """ Returns all possible moves given board state """
        legal_moves = []

        for hole in self.board.holes:
            for gets_jumped in hole.neighbours:
                for jumper in gets_jumped.neighbours:

                    x_diff = jumper.x - gets_jumped.x
                    y_diff = jumper.y - gets_jumped.y

                    # Check if jumper and gets_jumped aligned with hole
                    if hole.x == gets_jumped.x - x_diff and hole.y == gets_jumped.y - y_diff:
                        if hole.empty and not jumper.empty and not gets_jumped.empty:
                            legal_moves.append(Action(jumper, gets_jumped, hole))

        return legal_moves

    def is_victory(self):
        if len(self.board.holes) == self.num_cells - 1:
            return True

    def solitaire_jump(self, action: Action):
        if self.viz_toggle:
            self.viz.step(self.board, action)

        jumper = action.jumper
        jumpee = action.jumpee
        hole = action.hole

        """ Update empty """
        jumper.empty = True
        jumpee.empty = True
        hole.empty = False

        """ Update holes """
        self.board.holes.remove(hole)
        self.board.holes.append(jumper)
        self.board.holes.append(jumpee)

        if self.viz_toggle:
            self.viz.step(self.board, None)

    def get_remaining_pegs(self):
        return self.num_cells - len(self.board.holes)

    def get_reward(self):
        reward = 0
        if self.is_victory():
            reward = self.board.size
        elif not self.get_all_legal_moves():
            reward = -1 * self.get_remaining_pegs()
        return reward

    def play_RL(self, agent, epsilon_greedy=0.0, choose_best=False):
        while self.get_all_legal_moves():
            # gets cell IDs from agent
            prev_state = self.board.stringify()
            action = agent.get_move(prev_state, moves=self.get_all_legal_moves(), e_greedy=epsilon_greedy, choose_best=choose_best)

            # plays move
            self.solitaire_jump(action)
            new_state = self.board.stringify()
            reward = self.get_reward()

            agent.update(prev_state, action, reward, new_state)

            if self.is_victory():
                agent.wins += 1
                if self.viz_toggle:
                    self.viz.viz()
                break
            elif not self.get_all_legal_moves():
                if self.viz_toggle:
                    self.viz.viz()
                break

