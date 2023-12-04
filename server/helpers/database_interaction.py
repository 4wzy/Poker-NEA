import math

from helpers.database_base import DatabaseBase
from datetime import datetime, date
import mysql.connector


class DatabaseInteraction(DatabaseBase):
    def create_database_and_tables(self):
        # SQL commands to create tables
        commands = [
            """
            CREATE DATABASE IF NOT EXISTS poker_game;
            """,

            """
            USE poker_game;
            """,

            """
            CREATE TABLE users (
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(20) UNIQUE NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            salt VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            profile_picture VARCHAR(255) DEFAULT 'default.png',
            chips_balance INT DEFAULT 500
            );
            """,

            """
            CREATE TABLE user_statistics(
            stat_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT UNIQUE,
            games_played INT DEFAULT 0,
            games_won INT DEFAULT 0,
            rgscore INT DEFAULT 0,
            average_aggressiveness_score FLOAT DEFAULT 0,
            average_conservativeness_score FLOAT DEFAULT 0,
            total_play_time INT DEFAULT 0,
            streak INT DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """,

            """
            INSERT INTO user_statistics (user_id, games_played, games_won, rgscore, aggressiveness_score, 
            conservativeness_score, total_play_time, streak)
            SELECT user_id, 0, 0, 0, 0.0, 0.0, 0, 0
            FROM users
            WHERE user_id NOT IN (SELECT user_id FROM user_statistics);
            """,

            """
            CREATE TABLE user_game_limits (
            user_id INT UNIQUE PRIMARY KEY,
            daily_game_limit INT DEFAULT 10,
            last_logged_in TIMESTAMP,
            games_played_today INT DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """,

            """
            INSERT INTO user_game_limits (user_id, daily_game_limit, last_logged_in, games_played_today)
            SELECT user_id, 10, NOW(), 0
            FROM users;
            """,

            """
            CREATE TABLE lobbies (
            lobby_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            host_user_id INT,
            status ENUM('waiting', 'in_progress', 'completed', 'abandoned') DEFAULT 'waiting',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            player_limit INT DEFAULT 6,
            buy_in INT NOT NULL,
            CONSTRAINT CHK_PlayerLimit CHECK (player_limit >= 3 AND player_limit <= 6),
            FOREIGN KEY (host_user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """,

            """
            CREATE TABLE player_lobbies (
            user_id INT UNIQUE,
            lobby_id INT,
            show_odds BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, lobby_id)
            );
            """,

            """
            CREATE TABLE games (
            game_id INT AUTO_INCREMENT PRIMARY KEY,
            lobby_id INT,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            FOREIGN KEY (lobby_id) REFERENCES lobbies(lobby_id) ON DELETE CASCADE
            );
            """,

            """
            CREATE TABLE game_results (
            result_id INT AUTO_INCREMENT PRIMARY KEY,
            game_id INT,
            user_id INT,
            pos INT,
            winnings INT,
            aggressiveness_score FLOAT DEFAULT 0,
            conservativeness_score FLOAT DEFAULT 0,
            FOREIGN KEY (game_id) REFERENCES games(game_id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            );
            """
        ]

        with self._db_cursor() as cursor:
            for command in commands:
                cursor.execute(command)

    def set_user_profile_picture(self, user_id, profile_picture_filename):
        print("setting user profile picture in db_interaction")
        try:
            with self._db_cursor() as cursor:
                query = """UPDATE users
                SET profile_picture = %s
                WHERE user_id = %s;
                """
                cursor.execute(query, (profile_picture_filename, user_id))
                return {"success": True}
        except Exception as e:
            print(f"Exception in set_user_profile_picture: {e}")
            return {"success": False, "error": str(e)}

    def get_user_profile_picture(self, user_id):
        try:
            with self._db_cursor() as cursor:
                query = """
                        SELECT profile_picture
                        FROM users
                        WHERE user_id = %s;
                        """
                cursor.execute(query, (user_id,))
                result = cursor.fetchone()
                return result[0] if result else "default.png"
        except Exception as e:
            print(f"Exception in get_user_profile_picture: {e}")
            return "default.png"

    def add_to_attribute_for_user(self, user_id, attribute, amount):
        valid_attributes = ["games_played", "games_won", "rgscore", "aggressiveness_score", "conservativeness_score",
                            "total_play_time", "streak", "total_play_time"]
        if attribute not in valid_attributes:
            raise ValueError("Invalid attribute provided")

        with self._db_cursor() as cursor:
            query = f"""
            UPDATE user_statistics
            SET {attribute} = {attribute} + %s
            WHERE user_id = %s;
            """
            cursor.execute(query, (amount, user_id))

    def get_attribute_from_user(self, user_id, attribute):
        valid_attributes = ["games_played", "games_won", "rgscore", "aggressiveness_score", "conservativeness_score",
                            "total_play_time", "streak", "total_play_time"]
        if attribute not in valid_attributes:
            raise ValueError("Invalid attribute provided")

        with self._db_cursor() as cursor:
            query = f"""
                    SELECT {attribute}
                    FROM user_statistics
                    WHERE user_id = %s;
                    """
            cursor.execute(query, (user_id, ))
            result = cursor.fetchone()
            return result[0] if result else "Invalid"

    def get_attribute_from_user_games_played(self, user_id, attribute, num_games):
        valid_attributes = ["pos", "winnings", "aggressiveness_score", "conservativeness_score"]
        if attribute not in valid_attributes:
            # This code prevents against SQL Injections!
            raise ValueError("Invalid attribute provided")

        with self._db_cursor() as cursor:
            query = f"""
                    SELECT game_results.{attribute}
                    FROM game_results
                    INNER JOIN games ON game_results.game_id = games.game_id
                    WHERE game_results.user_id = %s
                    ORDER BY games.end_time DESC
                    LIMIT %s;
                    """
            cursor.execute(query, (user_id, num_games))
            results = cursor.fetchall()
            return [result[0] for result in results] if results else []

    def get_recent_games_details(self, user_id, num_games):
        with self._db_cursor() as cursor:
            query = """
            SELECT games.game_id, games.start_time, games.end_time, game_results.pos, lobbies.buy_in
            FROM games
            INNER JOIN game_results ON games.game_id = game_results.game_id
            INNER JOIN lobbies ON games.lobby_id = lobbies.lobby_id
            WHERE game_results.user_id = %s
            ORDER BY games.end_time DESC
            LIMIT %s;
            """
            cursor.execute(query, (user_id, num_games))
            games_info = cursor.fetchall()

            game_details_list = []
            for game_info in games_info:
                game_id, start_time, end_time, position, buy_in = game_info
                participants = self.get_game_participants(game_id)
                if end_time:
                    game_details = {
                        "game_id": game_id,
                        "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "position": position,
                        "buy_in": buy_in,
                        "participants": participants
                    }
                    game_details_list.append(game_details)
            return game_details_list

    def get_game_participants(self, game_id):
        with self._db_cursor() as cursor:
            query = """
            SELECT users.username
            FROM game_results
            INNER JOIN users ON game_results.user_id = users.user_id
            WHERE game_results.game_id = %s;
            """
            cursor.execute(query, (game_id,))
            return [row[0] for row in cursor.fetchall()]

    def get_user_statistics(self, user_id):
        valid_attributes = ["games_played", "games_won", "rgscore", "average_aggressiveness_score",
                            "average_conservativeness_score", "total_play_time", "streak"]

        attributes_to_select = ", ".join(valid_attributes)

        with self._db_cursor() as cursor:
            query = f"""
                    SELECT {attributes_to_select}
                    FROM user_statistics
                    WHERE user_id = %s;
                    """
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()

            # If there's a result, return it as a dictionary
            if result:
                return dict(zip(valid_attributes, result))
            else:
                # Return False if the user is not found
                return False

    def update_average_scores(self, user_id, game_aggressiveness_score, game_conservativeness_score):
        with self._db_cursor() as cursor:
            # Fetch current statistics
            cursor.execute("""
                SELECT games_played, average_aggressiveness_score, average_conservativeness_score
                FROM user_statistics
                WHERE user_id = %s;
            """, (user_id,))
            user_data = cursor.fetchone()

            if user_data:
                games_played, current_avg_aggressiveness, current_avg_conservativeness = user_data

                # Calculate the new average scores
                new_avg_aggressiveness = round(((current_avg_aggressiveness * (
                            games_played - 1)) + game_aggressiveness_score) / games_played, 2)
                new_avg_conservativeness = round(((current_avg_conservativeness * (
                            games_played - 1)) + game_conservativeness_score) / games_played, 2)

                # Update the average scores in the user_statistics table
                cursor.execute("""
                    UPDATE user_statistics
                    SET average_aggressiveness_score = %s,
                        average_conservativeness_score = %s
                    WHERE user_id = %s;
                """, (new_avg_aggressiveness, new_avg_conservativeness, user_id,))

    def insert_game(self, lobby_id):
        with self._db_cursor() as cursor:
            query = """
            INSERT INTO games (lobby_id, start_time)
            VALUES (%s, CURRENT_TIMESTAMP);
            """
            cursor.execute(query, (lobby_id,))
            # Get the last inserted game_id
            game_id = cursor.lastrowid
            return game_id

    def end_game(self, game_id):
        with self._db_cursor() as cursor:
            query = """
            UPDATE games
            SET end_time = CURRENT_TIMESTAMP
            WHERE game_id = %s;
            """
            cursor.execute(query, (game_id,))

    def insert_game_results(self, game_id, user_id, pos, winnings, aggressiveness_score, conservativeness_score):
        with self._db_cursor() as cursor:
            query = """
            INSERT INTO game_results (game_id, user_id, pos, winnings, aggressiveness_score, conservativeness_score)
            VALUES (%s, %s, %s, %s, %s, %s);
            """
            cursor.execute(query, (game_id, user_id, pos, winnings, aggressiveness_score, conservativeness_score))

    def get_game_duration(self, game_id):
        with self._db_cursor() as cursor:
            # Get the duration of the game in seconds
            query_duration = """
            SELECT TIMESTAMPDIFF(SECOND, start_time, end_time) AS game_duration
            FROM games
            WHERE game_id = %s;
            """
            cursor.execute(query_duration, (game_id,))
            result = cursor.fetchone()
            return result[0] if result else 0

    def update_user_play_time(self, user_id, additional_time_seconds):
        with self._db_cursor() as cursor:
            # Update the total play time for a user
            query_update_play_time = """
            UPDATE user_statistics
            SET total_play_time = total_play_time + %s
            WHERE user_id = %s;
            """
            cursor.execute(query_update_play_time, (additional_time_seconds, user_id))

    def update_game_limit_after_completion(self, user_id):
        with self._db_cursor() as cursor:
            # Increment the amount of games played today by 1
            query = """
            UPDATE user_game_limits
            SET games_played_today = games_played_today + 1
            WHERE user_id = %s;
            """
            cursor.execute(query, (user_id,))

    def update_rg_score(self, user_id):
        with self._db_cursor() as cursor:
            # Fetch the current RGScore and streak
            cursor.execute("""
                    SELECT rgscore, streak
                    FROM user_statistics
                    WHERE user_id = %s;
                    """, (user_id,))
            rgscore_data = cursor.fetchone()

            current_rgscore, current_streak = rgscore_data or (100, 0)

            # Fetch the daily game limit and games played today
            cursor.execute("""
                    SELECT daily_game_limit, games_played_today, last_logged_in
                    FROM user_game_limits
                    WHERE user_id = %s;
                    """, (user_id,))
            limit_data = cursor.fetchone()

            daily_game_limit, games_played_today, last_logged_in = limit_data or (10, 0, None)
            print(f"UPDATING RGSCORE FOR USER {user_id}. Current_rgscore: {current_rgscore}, current_streak:"
                  f" {current_streak}, daily_game_limit: {daily_game_limit}, games_played_today: "
                  f"{games_played_today}, last_logged_in: {last_logged_in}")

            if last_logged_in is not None:
                last_logged_in_date = last_logged_in.date()
                print(f"LAST_LOGGED_IN_DATE: {last_logged_in_date}")
            else:
                last_logged_in_date = None

            today = datetime.today().date()

            if last_logged_in_date is None or last_logged_in_date < today:
                # Calculate games played above limit for yesterday
                games_played_above_limit = games_played_today - daily_game_limit
                if games_played_above_limit < 0:
                    games_played_above_limit = 0
                print(f"updated games_played_above_limit to: {games_played_above_limit}")

                # Check if the user stayed within their limit yesterday
                if games_played_today <= daily_game_limit:
                    current_streak += 1
                else:
                    current_streak = 0
                print(f"current_streak: {current_streak}")

                # Calculate the new RGScore making sure it doesn't go below 0
                influence = 0.5  # Example value
                rgscore_adjustment = -math.log2(1 + games_played_above_limit) + influence * current_streak
                new_rgscore = round(current_rgscore + rgscore_adjustment, 2)
                if new_rgscore < 0:
                    new_rgscore = 0
                print(f"rgscore_adjustment: {rgscore_adjustment}, new_rgscore: {new_rgscore}")

                # Update the user_statistics with the new RGScore and streak
                cursor.execute("""
                        UPDATE user_statistics
                        SET rgscore = %s, streak = %s
                        WHERE user_id = %s;
                        """, (new_rgscore, current_streak, user_id,))

                # Reset games_played_today and update last_logged_in
                cursor.execute("""
                        UPDATE user_game_limits
                        SET games_played_today = 0, last_logged_in = CURRENT_TIMESTAMP
                        WHERE user_id = %s;
                        """, (user_id,))

            return current_rgscore

    def check_if_within_limit(self, user_id, daily_game_limit):
        # Logic to check if the user stayed within the daily game limit yesterday
        pass

    def get_games_played_above_limit(self, user_id, daily_game_limit):
        # Logic to determine how many games the user played over the limit yesterday
        pass

    def get_and_check_to_reset_daily_games_played(self, user_id):
        with self._db_cursor() as cursor:
            # Check if the user has logged in today
            select_query = """
                    SELECT DATE(last_logged_in), games_played_today
                    FROM user_game_limits
                    WHERE user_id = %s;
                    """
            cursor.execute(select_query, (user_id,))
            last_login_date, games_played_today = cursor.fetchone() or (None, 0)

            # Reset daily games played if the last login was not today
            if last_login_date is not None and last_login_date < date.today():
                reset_query = """
                        UPDATE user_game_limits
                        SET games_played_today = 0
                        WHERE user_id = %s;
                        """
                cursor.execute(reset_query, (user_id,))
                games_played_today = 0  # Reset the count

            # Update the last_logged_in to the current timestamp
            update_login_query = """
                    UPDATE user_game_limits
                    SET last_logged_in = CURRENT_TIMESTAMP
                    WHERE user_id = %s;
                    """
            cursor.execute(update_login_query, (user_id,))

            return games_played_today

    def update_daily_game_limit(self, user_id, new_limit):
        with self._db_cursor() as cursor:
            query = """
            UPDATE user_game_limits
            SET daily_game_limit = %s
            WHERE user_id = %s;
            """
            cursor.execute(query, (new_limit, user_id))

            return new_limit

    def get_daily_game_limit(self, user_id):
        with self._db_cursor() as cursor:
            query = "SELECT daily_game_limit FROM user_game_limits WHERE user_id = %s;"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            print(f"Result from get_daily_game_limit: {result}")
            return result[0] if result else None

    def get_top_players_by_attribute(self, attribute, limit=50):
        if attribute not in ["rgscore", "average_aggressiveness_score", "average_conservativeness_score", "games_won"]:
            raise ValueError("Invalid attribute provided")

        with self._db_cursor() as cursor:
            query = f"""
            SELECT users.user_id, users.username, users.profile_picture, user_statistics.{attribute}
            FROM user_statistics
            JOIN users ON user_statistics.user_id = users.user_id
            ORDER BY user_statistics.{attribute} DESC
            LIMIT %s;
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            return results

    def get_top_players_by_chips(self, limit=50):
        with self._db_cursor() as cursor:
            query = """
            SELECT user_id, username, profile_picture, chips_balance
            FROM users
            ORDER BY chips_balance DESC
            LIMIT %s;
            """
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            return results

    def get_buy_in_for_lobby(self, lobby_id):
        with self._db_cursor() as cursor:
            cursor.execute("SELECT buy_in FROM lobbies WHERE lobby_id = %s", (lobby_id,))
            result = cursor.fetchone()
            return result[0] if result else None  # Return None if the lobby isn't found

    def get_chip_balance_for_user(self, user_id):
        with self._db_cursor() as cursor:
            cursor.execute("SELECT chips_balance FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result == 0:
                return 0  # Avoids a very specific error I was dealing with
            return result[0] if result else False  # Return False if the user isn't found

    def update_chip_balance_for_user(self, user_id, new_balance):
        with self._db_cursor() as cursor:
            cursor.execute("UPDATE users SET chips_balance = %s WHERE user_id = %s", (new_balance, user_id))
        return {"success": True, "balance": new_balance}

    def add_to_chip_balance_for_user(self, user_id, amount_to_add):
        current_balance = self.get_chip_balance_for_user(user_id)

        if current_balance is False:
            return {"success": False, "message": "User not found"}

        # Calculate the new balance
        new_balance = current_balance + amount_to_add

        # A user should never have a negative amount of chips. Set to 0 if this is the case.
        if new_balance < 0:
            new_balance = 0

        # Update the new balance in the database
        return self.update_chip_balance_for_user(user_id, new_balance)

    def get_username(self, user_id):
        with self._db_cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else "Invalid"

    def set_username(self, user_id, new_username):
        with self._db_cursor() as cursor:
            # Check if the new username already exists
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (new_username,))
            if cursor.fetchone():
                # Username already exists
                return {"success": False, "error": "Username already exists"}

            # Username is unique, proceed with update
            query = """
                    UPDATE users
                    SET username = %s
                    WHERE user_id = %s;
                    """
            cursor.execute(query, (new_username, user_id))
            return {"success": True}

    def get_all_lobbies(self, status_filter, odds_filter):
        try:
            with self._db_cursor() as cursor:

                cursor.execute("""
                    SELECT l.lobby_id, l.name, l.status, COUNT(pl.user_id), l.created_at, l.show_odds, 
                    l.player_limit, l.buy_in
                    FROM lobbies l
                    LEFT JOIN player_lobbies pl ON l.lobby_id = pl.lobby_id
                    WHERE l.status = %s AND l.show_odds = %s
                    GROUP BY l.lobby_id
                """, (status_filter, odds_filter))

                lobbies = cursor.fetchall()

                lobbies_list = [{
                    'lobby_id': lobby[0],
                    'name': lobby[1],
                    'status': lobby[2],
                    'player_count': lobby[3],
                    'created_at': lobby[4].strftime('%Y-%m-%d %H:%M:%S'),
                    'show_odds': lobby[5],
                    'player_limit': lobby[6],
                    'buy_in': lobby[7]
                } for lobby in lobbies]

                # I have decided to use a merge sort here
                sorted_lobbies = self.sort_lobbies_using_merge(lobbies_list)

                return sorted_lobbies
        except Exception as e:
            print(f"Error: {e}")
            return []

    def merge_sorted_lobbies(self, left_lobbies, right_lobbies):
        merged_lobbies = []
        left_index, right_index = 0, 0

        while left_index < len(left_lobbies) and right_index < len(right_lobbies):
            # Comparing player counts for sorting
            if left_lobbies[left_index]['player_count'] > right_lobbies[right_index]['player_count']:
                merged_lobbies.append(left_lobbies[left_index])
                left_index += 1
            else:
                merged_lobbies.append(right_lobbies[right_index])
                right_index += 1

        # Append any remaining lobbies from both lists (one of them will be empty)
        while left_index < len(left_lobbies):
            merged_lobbies.append(left_lobbies[left_index])
            left_index += 1
        while right_index < len(right_lobbies):
            merged_lobbies.append(right_lobbies[right_index])
            right_index += 1

        return merged_lobbies

    def sort_lobbies_using_merge(self, lobbies):
        if len(lobbies) <= 1:
            return lobbies

        middle_index = len(lobbies) // 2
        left_part = self.sort_lobbies_using_merge(lobbies[:middle_index])
        right_part = self.sort_lobbies_using_merge(lobbies[middle_index:])

        return self.merge_sorted_lobbies(left_part, right_part)

    def create_lobby(self, lobby_data):
        response = {"success": True, "error": None, "lobby_id": None}
        with self._db_cursor() as cursor:
            # Check if a lobby with the same name and the status "waiting" already exists
            check_sql = """
            SELECT COUNT(*) FROM lobbies WHERE name = %s AND (status = 'waiting')
            """
            cursor.execute(check_sql, (lobby_data['name'],))
            existing_lobby_count = cursor.fetchone()[0]

            if existing_lobby_count > 0:
                response["success"] = False
                response["error"] = "A lobby with this name already exists and is currently active"
                return response

            # If no such lobby exists, proceed with the insert

            if lobby_data["player_limit"] < 3 or lobby_data["player_limit"] > 6:
                response["success"] = False
                response["error"] = "Player limit can only be 3 to 6"
                return response

            sql = """
            INSERT INTO lobbies (host_user_id, name, status, show_odds, player_limit, buy_in)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (lobby_data['host_user_id'], lobby_data['name'], 'waiting', lobby_data['show_odds'],
                                 lobby_data['player_limit'], lobby_data['buy_in']))

            # Get the last inserted ID
            lobby_id = cursor.lastrowid
            response["lobby_id"] = lobby_id

        return response

    def set_lobby_status(self, lobby_id, lobby_status):
        response = {"success": True, "error": None}
        with self._db_cursor() as cursor:
            try:
                sql = """
                UPDATE lobbies 
                SET status = %s 
                WHERE lobby_id = %s
                """
                cursor.execute(sql, (lobby_status, lobby_id))
            except Exception as e:
                response["success"] = False
                response["error"] = f"Error: {e}"

        print(f"set lobby status to {lobby_status}")
        return response

    def join_lobby(self, user_id, lobby_id):
        print("(database interaction): joining lobby")
        response = {"success": True, "error": None}

        try:
            with self._db_cursor() as cursor:
                # Update the lobby to include the new player
                sql = """
                INSERT INTO player_lobbies (user_id, lobby_id) 
                VALUES (%s, (SELECT lobby_id FROM lobbies WHERE lobby_id = %s AND status = 'waiting'))
                """
                cursor.execute(sql, (user_id, lobby_id))

        except Exception as e:
            response["success"] = False
            response["error"] = f"Error: {e}"

        return response["success"], response["error"]

    def remove_player_from_lobby(self, user_id, lobby_id):
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor()

            query = "DELETE FROM player_lobbies WHERE user_id = %s AND lobby_id = %s"
            cursor.execute(query, (user_id, lobby_id))
            connection.commit()

        except Exception as e:
            print(f"Error removing player from lobby database: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

    def get_game_id_from_lobby_id(self, lobby_id):
        with self._db_cursor() as cursor:
            query = "SELECT game_id FROM games WHERE lobby_id = %s;"
            cursor.execute(query, (lobby_id,))
            result = cursor.fetchone()
            print(f"Result from get_game_id_from_lobby_id: {result}")
            return result[0] if result else None
