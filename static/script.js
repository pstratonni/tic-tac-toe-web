let player;
let enemy_player;
let isActive = false;
let idGame;
let joined;

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
      rerenderField(data.field);
      moveGame(data.cell, data.active);
      whoMove();
      break;
    case "break":
      finishGame();
      gameList(data.games);
    case "err":
      console.log(data.msg);
      break;
    case "draw":
      rerenderField(data.field);
      whoMove("draw");
      renderWin("draw")
      break;
    case "win":
      rerenderField(data.field);
      whoMove(data.winner);
      removeListener();
      linelWin(...data.line);
      renderWin(data.winner)
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
  document.querySelector(".field").innerHTML = "";
  const enemy_state = document.querySelector(".enemy-state");
  enemy_state.innerHTML = "";
  const go = document.querySelector(".go");
  go.innerHTML = "";
  document.querySelector("span").remove();
  const span = document.createElement("span")
  document.querySelector(".field-wrap").appendChild(span)
  document.querySelector(".winner").classList.add("hiden")
};

const renderField = () => {
  field = document.querySelector(".field");
  field.innerHTML = ''
  for (let i = 0; i < 3; i++) {
    for (let j = 0; j < 3; j++) {
      cell = document.createElement("div");
      cell.id = `cell_${i}_${j}`;
      cell.classList.add("cell");
      field.appendChild(cell);
    }
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
  whoMove();
  const cells = document.querySelectorAll(".cell");
  for (let cell of cells) {
    cell.addEventListener("click", handlerGo);
  }
};

const whoMove = (msg = "") => {
  const go = document.querySelector(".go");
  if (msg === "draw"){
    go.innerHTML = msg;
    return
  }
  if (msg) {
    go.innerHTML = msg === "X" ? 'Win <i class="fas fa-times"></i>': `Win <i class="far fa-circle"></i>`;
    return;
  }
  go.innerHTML = isActive ? `You go (${player})` : `Enemy go (${enemy_player})`;
};

const handlerGo = (event) => {
  const cell = event.target;
  if (!isActive) {
    return;
  }
  id = cell.id.split("_").slice(1);
  moveSend(id);
};

const rerenderField = (field) => {
  for (i = 0; i < 3; i++) {
    for (j = 0; j < 3; j++) {
      document.getElementById(`cell_${i}_${j}`).innerHTML =
        field[i][j] === "-" ? "" : field[i][j] === "X" ?  '<i class="fas fa-times"></i>': '<i class="far fa-circle"></i>';
    }
  }
};

const moveGame = (cellId, active) => {
  const cell = document.getElementById(`cell_${cellId[0]}_${cellId[1]}`);
  isActive = active;
  cell.style.cursor = "default";
  cell.removeEventListener("click", handlerGo);
};

const linelWin = (x, y) => {
  const span = document.querySelector("span");
  let marg = 100;
  marg += 200 * y;
  if (x === 0) {
    span.classList.add("winH");
    span.style.top = `${marg}px`;
  } else if (x === 1) {
    span.classList.add("winV");
    span.style.left = `${marg}px`;
  } else if (x === 2 && y === 0) {
    span.classList.add("winDM");
  } else {
    span.classList.add("winDS");
  }
};

const renderWin = (win) => {
  const winner = document.querySelector(".winner")
  if (win === "draw"){
    winner.classList.add('draw')
    winner.classList.remove('hiden')
    return
  }
  win = win === "X" ? '<i class="fas fa-times"></i>': `<i class="far fa-circle"></i>`;
  if (win === player){
    winner.classList.add('win')
  } else {
    winner.classList.add('lose')
  }
  winner.classList.remove('hiden')
}

const removeListener = () => {
  const cells = document.querySelectorAll(".cell");
  for (let cell of cells) {
    cell.removeEventListener("click", handlerGo);
    cell.style.cursor = "default";
  }
};

document.getElementById("create-game").addEventListener("click", createGame);
document.querySelector(".finish").addEventListener("click", breakGame);
