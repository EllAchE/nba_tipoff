import * as util from "./util";
import * as fs from "./fs";

interface odds {
  date: Date;
  gameCode: string;
  gameDatetime: string;
  home: string;
  away: string;
  exchange: string;
  betName: string;
  subBetName: string;
  americanOdds: number;
  currentPriceUp: number;
  currentPriceDown: number;
}

interface GamesResponse {
  events: [{ idfoevent: number }];
}

interface GameResponse {
  participantshortname_away: string;
  participantshortname_home: string;
  tsstart: string;
  eventmarketgroups: [
    {
      name: string;
      markets: [
        {
          name: string;
          selections: [
            {
              name: string;
              currentpriceup: number;
              currentpricedown: number;
            }
          ];
        }
      ];
    }
  ];
}

export const getAmericanOdds = (
  currentpriceup: number,
  currentpricedown: number
) => {
  if (currentpriceup >= currentpricedown) {
    return (currentpriceup / currentpricedown) * 100;
  } else if (currentpriceup < currentpricedown) {
    return (100 / currentpriceup) * currentpricedown * -1;
  } else {
    throw new Error();
  }
};

export const getGameCode = (gameDate: Date, homeTeam: string) => {
  const modifiedGameDate = util.format(gameDate, "YYYYMMDD");
  return modifiedGameDate + "0" + homeTeam;
};

export const collect = async () => {
  const date = new Date();
  let oddsList: odds[] = [];
  const gamesResponse: GamesResponse = await util.get(
    "https://sportsbook.fanduel.com/cache/psmg/UK/63747.3.json"
  );
  const listOfGames = gamesResponse.events.map((game) => game.idfoevent);
  console.log(listOfGames);

  for (const game of listOfGames) {
    const gameResponse: GameResponse = await util.get(
      `https://sportsbook.fanduel.com/cache/psevent/UK/1/false/${game}.json`
    );

    for (const eventMarketGroup of gameResponse.eventmarketgroups) {
      for (const market of eventMarketGroup.markets) {
        for (const selection of market.selections) {
          oddsList.push({
            date: date,
            gameCode: getGameCode(
              new Date(gameResponse.tsstart),
              gameResponse.participantshortname_home.split(" ")[0]
            ),
            gameDatetime: gameResponse.tsstart,
            home: gameResponse.participantshortname_home.split(" ")[0],
            away: gameResponse.participantshortname_away.split(" ")[0],
            exchange: "fanduel",
            betName: market.name,
            subBetName: selection.name,
            americanOdds: getAmericanOdds(
              selection.currentpriceup,
              selection.currentpricedown
            ),
            currentPriceUp: selection.currentpriceup,
            currentPriceDown: selection.currentpricedown,
          });
        }
      }
    }
  }

  await fs.writeFile("./output.json", Buffer.from(oddsList));
};
