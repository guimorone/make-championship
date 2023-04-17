import sys
import logging
from random import randint
from functools import total_ordering
from typing import List, Tuple, Dict, Self

IN_FILE_PATH = "entry.txt"
OUT_FILE_PATH = "out.txt"

# from itertools import groupby
# from typing import Any, Iterable

# def all_equal(iterable: Iterable) -> bool:
#     g = groupby(iterable)
#     return next(g, True) and not next(g, False)


# def are_tuples_the_same(*tuples: Tuple[Any, ...]) -> bool:
#     return all_equal((sorted(t) for t in tuples))


@total_ordering
class Team:
    def __init__(self, team_name: str) -> None:
        if not team_name:
            raise ValueError("Team name cannot be empty or null.")

        self.team_name: str = team_name
        self.__possible_games: List[Tuple[Self, Team, bool]] | None = None

    def get_possible_games(self, teams=None):
        if self.__possible_games == None:
            if not teams:
                raise ValueError("Teams array cannot be empty or null.")

            self.__set_possible_games(teams)

        return self.__possible_games

    def __set_possible_games(self, teams) -> None:
        self.__possible_games = []

        for team in teams:
            if team.__str__() == self.__str__():
                continue

            self.__possible_games.append((self, team, True))  # home
            self.__possible_games.append((self, team, False))  # away

    def __str__(self) -> str:
        return self.team_name

    __repr__ = __str__

    def __lt__(self, other):
        if type(self) == type(other):
            return self.team_name < other.team_name

        return 1


class Championship:
    def __init__(
        self, in_file_path: str = IN_FILE_PATH, out_file_path: str = OUT_FILE_PATH
    ) -> None:
        self.in_file_path: str = in_file_path
        self.out_file_path: str = out_file_path

        self.__teams: List[Team] = []
        self.__all_games: Dict[int, Dict[int, str]] = {}
        self.__rounds: int = 0
        self.__games_per_round: int = 0

        self.__set_teams()
        logging.debug(f"Teams := {self.get_teams()}")

    def get_teams(self) -> List[Team]:
        return self.__teams

    def __set_teams(self) -> None:
        with open(self.in_file_path, "r") as entry_file:
            self.__teams = [Team(team.strip()) for team in entry_file]

        self.__rounds = (len(self.__teams) - 1) * 2
        self.__games_per_round = len(self.__teams) // 2

    def __write_to_file(self) -> None:
        logging.info(f"Writing result to file {self.out_file_path}")
        with open(self.out_file_path, "w") as out_file:
            for rodada, jogos_por_rodada in self.__all_games.items():
                title = "\n"
                if rodada == 1:
                    title = ""

                title += f"Rodada {rodada}\n"
                out_file.write(title)
                out_file.writelines(
                    [
                        f"{num_jogo}º jogo: {jogo}\n"
                        for num_jogo, jogo in jogos_por_rodada.items()
                    ]
                )

    def generate_all_possibilites(self) -> None:
        games = []
        for team in self.__teams:
            possible_games = team.get_possible_games(self.__teams)
            if not possible_games:
                logging.critical("It was not possible to generate games. Sorry!")
                sys.exit()

            games.extend(possible_games)

        # games = list(set(tuple(sorted(game)) for game in games))

        if 2 * self.__rounds * self.__games_per_round != len(games):
            logging.critical("It was not possible to generate games. Sorry!")
            sys.exit()

        for r in range(self.__rounds):
            games_in_round = {}
            already_in_round = []
            for gpr in range(self.__games_per_round):
                new_games_array = [
                    g
                    for g in games
                    if g[0].__str__() not in already_in_round
                    and g[1].__str__() not in already_in_round
                ]

                lucky_game = randint(0, len(new_games_array) - 1)
                lucky_game = games.index(new_games_array[lucky_game])
                team1, team2, local = games.pop(lucky_game)
                team1, team2 = team1.__str__(), team2.__str__()
                already_in_round.append(team1)
                already_in_round.append(team2)

                text = f"{team1} x {team2}" if local else f"{team2} x {team1}"
                games_in_round[gpr + 1] = text

            if len(games_in_round.keys()):
                self.__all_games[r + 1] = games_in_round

        self.__write_to_file()
        logging.info(
            f"Possibilities generated: {self.__rounds} rounds and {self.__games_per_round} games per round."
        )


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    try:
        championship = Championship()
        championship.generate_all_possibilites()
    except Exception as err:
        logging.error(err)
