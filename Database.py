import mysql.connector
from ChessStateEnum import chess_to_char, ChessStateEnum

class Database():
    def __init__(self, host="127.0.0.1", user="root", passwd="123456", database="reversi"):
        self.mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            passwd="123456",
            database="reversi"
        )
        mycursor = self.mydb.cursor()
        sql = 'select max(id) from reversi'
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        self.id = myresult[0][0] + 1

        
    
    def write_finish(self, game):

        mycursor = self.mydb.cursor()

        sql = "INSERT INTO reversi (id, strategy_black, strategy_white, winner, score_black, score_white, uct_timeout_black, uct_iteration_black, uct_c_black, uct_timeout_white, uct_iteration_white, uct_c_white, board) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        board_str = ''
        for x in range(game.board.board_size[0]):
            for y in range(game.board.board_size[1]):
                board_str += chess_to_char(game.reversi.state.chess_status[x][y])
                board_str += ' '
        board_str = board_str[:-1]
        val = (self.id, game.players[0].strategy_enum.name, game.players[1].strategy_enum.name, ChessStateEnum.BLACK.name if game.reversi.state.scores[ChessStateEnum.BLACK] > game.reversi.state.scores[ChessStateEnum.WHITE] else ChessStateEnum.WHITE.name,\
            game.reversi.state.scores[ChessStateEnum.BLACK], game.reversi.state.scores[ChessStateEnum.WHITE],\
            float(game.uct_params[0].time_out), game.uct_params[0].iretation_times, game.uct_params[0].c,\
            float(game.uct_params[1].time_out), game.uct_params[1].iretation_times, game.uct_params[1].c, board_str)
        mycursor.execute(sql, val)

        self.mydb.commit()
        print("write_finish, ID:", mycursor.lastrowid)

    def write_step(self, game):
        mycursor = self.mydb.cursor()
        sql = "INSERT INTO reversi_step (finish_id, current, board) VALUES (%s, %s, %s)"
        board_str = ''
        for x in range(game.board.board_size[0]):
            for y in range(game.board.board_size[1]):
                board_str += chess_to_char(game.reversi.state.chess_status[x][y])
                board_str += ' '
        board_str = board_str[:-1]
        val = (self.id, game.reversi.state.curren_chess_color.name, board_str)
        mycursor.execute(sql, val)

        self.mydb.commit()
        print("write_step, ID:", mycursor.lastrowid)
