const ws = new WebSocket("ws://127.0.0.1:8000/ws");

ws.onopen = function (event) {
  newUser();
};

ws.onmessage = function (event) {
  let data = JSON.parse(event.data);
  switch (data.action) {
    case "new":
      break;
    case "create":
      initialGame(data.idx);
      break;
    case "join":
      initialGame(data.game, (joined = "true"));
      break;
    case "break":
      finishGame();
      gameList(data.games);
    default:
      break;
  }
};

const send = (data) => {
  console.log(data);
  ws.send(JSON.stringify(data));
};

const newUser = () => {
  send({ action: "new" });
};

const createGame = (event) => {
  send({ action: "create" });
};

const joinGame = (event) => {
  const id = event.target.id.split("_")[1];
  send({ action: "join", game: id });
};

const gameList = (games) => {
  const gameList = document.querySelector(".game-list");
  gameList.innerHTML = "";
  for (let i in games) {
    const li = `<li>Connection to <button id="game_${
      games[i]
    }" class="game-button">Game #${i + 1}</button></li>`;
    gameList.innerHTML += li;
  }
  const buttons = document.querySelectorAll(".game-button");
  for (let button of buttons) {
    button.addEventListener("click", joinGame);
  }
};

const initialGame = (idx, joined = "false") => {
  const createField = document.querySelector(".initial-game");
  createField.classList.remove("on");
  createField.classList.add("off");

  const gameField = document.querySelector(".game");
  gameField.classList.remove("off");
  gameField.classList.add("on");

  const finishButton = document.querySelector(".finish");
  finishButton.id = `finish_${joined}_${idx}`;
};

const breakGame = () => {
  const id = document.querySelector(".finish").id.split("_");
  console.log(id);
  send({ action: "break", joined: id[1], game: id[2] });
};

const finishGame = () => {
  const createField = document.querySelector(".initial-game");
  createField.classList.remove("off");
  createField.classList.add("on");
  const gameField = document.querySelector(".game");
  gameField.classList.remove("on");
  gameField.classList.add("off");
};

document.getElementById("create-game").addEventListener("click", createGame);
document.querySelector(".finish").addEventListener("click", breakGame);
