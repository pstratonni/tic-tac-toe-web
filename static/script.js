let player;
let enemy_player;
let isActive = false;
let idGame;

const ws = new WebSocket("ws://127.0.0.1:8000/ws");

ws.onopen = function (event) {
  newUser();
};

ws.onmessage = function (event) {
  const data = JSON.parse(event.data);
  switch (data.action) {
    case "new":
      finishGame();
      gameList(data.games);
      break;
    case "create":
      initialGame(data.game, data.player);
      renderField();
      break;
    case "join":
      initialGame(data.game, (player = false), (joined = "true"));
      renderField();
      startGame(data.player, data.enemy_player, data.active);
      break;
    case "move":
      moveGame(data.cell, data.active);
      break;
    case "break":
      finishGame();
      gameList(data.games);
    case 'err':
      console.log(data.msg)
      break
    default:
      break;
  }
};

const send = (data) => {
  ws.send(JSON.stringify(data));
};

const newUser = () => {
  send({ action: "new" });
};

const createGame = (event) => {
  send({ action: "create" });
};

const moveSend = (id) => {
  send({ action: "move", cell: id, game: idGame });
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
    }" class="game-button">Game #${+i + 1}</button></li>`;
    gameList.innerHTML += li;
  }

  const buttons = document.querySelectorAll(".game-button");
  for (let button of buttons) {
    button.addEventListener("click", joinGame);
  }
};

const initialGame = (idx, player_state, joined = "false") => {
  const createField = document.querySelector(".initial-game");
  createField.classList.remove("on");
  createField.classList.add("off");

  const gameField = document.querySelector(".game");
  gameField.classList.remove("off");
  gameField.classList.add("on");

  const finishButton = document.querySelector(".finish");
  finishButton.id = `finish_${joined}_${idx}`;

  if (player_state) {
    player =
      player_state == "X"
        ? '<i class="fas fa-times"></i>'
        : '<i class="far fa-circle"></i>';
    document.querySelector(".state").innerHTML = "";
    document.querySelector(".state").innerHTML = `You go with ${player}`;
  }
  idGame = idx;
};

const breakGame = () => {
  const id = document.querySelector(".finish").id.split("_");
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

const renderField = () => {
  field = document.querySelector(".field");
  for (let i = 0; i < 9; i++) {
    cell = document.createElement("div");
    cell.id = `cell_${i}`;
    cell.classList.add("cell");
    field.appendChild(cell);
  }
};

const startGame = (player_state, enemy_player_state, active) => {
  isActive = active;
  player =
    player_state == "X"
      ? '<i class="fas fa-times"></i>'
      : '<i class="far fa-circle"></i>';
  enemy_player =
    enemy_player_state == "X"
      ? '<i class="fas fa-times"></i>'
      : '<i class="far fa-circle"></i>';
  const state = document.querySelector(".state");
  state.innerHTML = "";
  state.innerHTML = `You go with ${player}`;
  const enemy_state = document.querySelector(".enemy-state");
  enemy_state.innerHTML = "";
  enemy_state.innerHTML = `Enemy go with ${enemy_player}`;
  whoMove(active);
  const cells = document.querySelectorAll(".cell");
  for (let cell of cells) {
    cell.addEventListener("click", handlerGo);
  }
};

const whoMove = () => {
  const go = document.querySelector(".go");
  go.innerHTML = "";
  go.innerHTML = isActive ? `You go (${player})` : `Enemy go (${enemy_player})`;
};

const handlerGo = (event) => {
  const cell = event.target;
  if (!isActive) {
    return;
  }
  id = cell.id.split("_")[1];
  moveSend(id);
};

const moveGame = (cellId, active) => {
  const cell = document.getElementById(`cell_${cellId}`);
  isActive = active;
  cell.style.cursor = "default";
  cell.removeEventListener("click", handlerGo);
  cell.innerHTML = isActive ? enemy_player : player;
  whoMove();
};

document.getElementById("create-game").addEventListener("click", createGame);
document.querySelector(".finish").addEventListener("click", breakGame);
