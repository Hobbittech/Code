"use strict";

const SIZE = 5;
const SAVE_KEY = "signal-garden-save-v1";
const DIRECTIONS = [
  { name: "north", row: -1, column: 0 },
  { name: "east", row: 0, column: 1 },
  { name: "south", row: 1, column: 0 },
  { name: "west", row: 0, column: -1 },
];

const LEVELS = [
  {
    name: "A sleepy seed",
    subtitle: "Every little turn brings a little light.",
    chapter: "THE FIRST SPARK",
    description: "A seed, a spark, and the tiniest beginning.",
    encouragement: "Some paths have to bend before the light can find its way.",
    path: [[0, 0], [0, 1], [0, 2], [1, 2], [2, 2], [2, 3], [2, 4], [3, 4], [4, 4]],
    scramble: [0, 1, 3, 2, 1, 3, 2, 1, 0],
  },
  {
    name: "A wandering vine",
    subtitle: "The signal took the scenic route.",
    chapter: "A WANDERING VINE",
    description: "Somewhere in here, a little light is waiting.",
    encouragement: "Follow the quiet spaces. The path is never in a hurry.",
    path: [[0, 2], [1, 2], [1, 1], [1, 0], [2, 0], [3, 0], [3, 1], [3, 2], [2, 2], [2, 3], [2, 4], [3, 4], [4, 4]],
    scramble: [1, 2, 1, 3, 2, 1, 3, 1, 2, 3, 1, 2, 0],
  },
  {
    name: "The moonlit pond",
    subtitle: "This one glows a little after dark.",
    chapter: "THE MOONLIT POND",
    description: "A longer walk through a very sleepy garden.",
    encouragement: "The winding path still knows exactly where it goes.",
    path: [[4, 0], [3, 0], [2, 0], [2, 1], [1, 1], [0, 1], [0, 2], [0, 3], [1, 3], [2, 3], [3, 3], [3, 4], [4, 4]],
    scramble: [2, 1, 3, 2, 1, 2, 3, 1, 2, 1, 3, 2, 1],
  },
  {
    name: "The little greenhouse",
    subtitle: "A few more turns, a lot more green.",
    chapter: "THE LITTLE GREENHOUSE",
    description: "A cozy corner with a few twists and turns.",
    encouragement: "Look for a place where the path changes direction.",
    path: [[0, 4], [1, 4], [1, 3], [1, 2], [2, 2], [3, 2], [3, 1], [3, 0], [4, 0], [4, 1], [4, 2], [4, 3], [4, 4]],
    scramble: [1, 3, 2, 1, 3, 2, 1, 3, 2, 1, 2, 3, 0],
  },
  {
    name: "The hidden clearing",
    subtitle: "You found the quietest part of the garden.",
    chapter: "THE HIDDEN CLEARING",
    description: "One last little wander before the clearing.",
    encouragement: "Give every turn a moment. The pattern will come to you.",
    path: [[2, 0], [1, 0], [0, 0], [0, 1], [0, 2], [1, 2], [2, 2], [2, 3], [1, 3], [0, 3], [0, 4], [1, 4], [2, 4], [3, 4], [4, 4]],
    scramble: [3, 2, 1, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 0],
  },
  {
    name: "Home, for now",
    subtitle: "The whole garden is listening.",
    chapter: "HOME, FOR NOW",
    description: "A final path, made of all the turns you learned.",
    encouragement: "The last little flower is already rooting for you.",
    path: [[0, 0], [1, 0], [2, 0], [2, 1], [3, 1], [4, 1], [4, 2], [4, 3], [3, 3], [2, 3], [1, 3], [1, 4], [2, 4], [3, 4], [4, 4]],
    scramble: [2, 1, 3, 1, 2, 3, 1, 2, 3, 1, 2, 3, 1, 2, 0],
  },
];

const board = document.getElementById("board");
const overlay = document.getElementById("win-overlay");
const toast = document.getElementById("toast");
const audio = { enabled: false, context: null };
let state = loadState();
let cells = [];
let powered = new Set();
let toastTimer = 0;

function loadState() {
  try {
    const saved = JSON.parse(localStorage.getItem(SAVE_KEY) || "null");
    if (saved && Number.isInteger(saved.level) && saved.level >= 0 &&
        saved.level < LEVELS.length && Array.isArray(saved.completed) &&
        saved.completed.every((level) => Number.isInteger(level) && level >= 0 && level < LEVELS.length)) {
      return { level: saved.level, completed: [...new Set(saved.completed)] };
    }
  } catch (error) {
    console.warn("Signal Garden could not read its saved progress.", error);
  }
  return { level: 0, completed: [] };
}

function saveState() {
  try {
    localStorage.setItem(SAVE_KEY, JSON.stringify(state));
    document.getElementById("save-status").innerHTML = '<span class="save-dot"></span> Progress saves on this device';
  } catch (error) {
    document.getElementById("save-status").textContent = "Progress won't save on this device";
    console.warn("Signal Garden could not save your progress.", error);
  }
}

function cellIndex(row, column) {
  return row * SIZE + column;
}

function findDirection(from, to) {
  const rowDelta = to[0] - from[0];
  const columnDelta = to[1] - from[1];
  return DIRECTIONS.findIndex((direction) => direction.row === rowDelta && direction.column === columnDelta);
}

function makeLevel(levelIndex) {
  const level = LEVELS[levelIndex];
  const route = new Map();
  level.path.forEach((position, index) => {
    const ports = [];
    if (index > 0) ports.push(findDirection(position, level.path[index - 1]));
    if (index < level.path.length - 1) ports.push(findDirection(position, level.path[index + 1]));
    route.set(cellIndex(...position), { ports, position });
  });

  return Array.from({ length: SIZE * SIZE }, (_, index) => {
    const item = route.get(index);
    if (!item) return { kind: "empty", rotation: 0, solvedRotation: 0, ports: [] };
    const { ports, position } = item;
    const source = index === cellIndex(...level.path[0]);
    const goal = index === cellIndex(...level.path[level.path.length - 1]);
    const solvedRotation = rotationForPorts(ports);
    const scrambleIndex = level.path.findIndex((point) => point[0] === position[0] && point[1] === position[1]);
    const scramble = level.scramble[scrambleIndex] ?? ((index * 3 + levelIndex) % 4);
    return {
      kind: source ? "source" : goal ? "goal" : "pipe",
      rotation: (solvedRotation + scramble) % 4,
      solvedRotation,
      ports: basePorts(ports),
    };
  });
}

function basePorts(ports) {
  if (ports.length === 1) return [0];
  if (ports.length === 2) {
    const opposite = (ports[0] + 2) % 4 === ports[1];
    return opposite ? [0, 2] : [0, 1];
  }
  return [];
}

function rotationForPorts(ports) {
  if (ports.length === 1) return ports[0];
  const opposite = (ports[0] + 2) % 4 === ports[1];
  if (opposite) return ports.includes(0) ? 0 : 1;
  const sorted = [...ports].sort((a, b) => a - b);
  const rotations = [[0, 1], [1, 2], [2, 3], [0, 3]];
  return rotations.findIndex((pair) => pair[0] === sorted[0] && pair[1] === sorted[1]);
}

function portsFor(cell) {
  return cell.ports.map((port) => (port + cell.rotation) % 4);
}

function render() {
  const level = LEVELS[state.level];
  cells = makeLevel(state.level);
  powered = traceSignal(cells);
  board.replaceChildren();
  board.setAttribute("aria-label", `Level ${state.level + 1}: ${level.name}. Rotate the tiles to connect the spark to the flower.`);

  cells.forEach((cell, index) => {
    const row = Math.floor(index / SIZE) + 1;
    const column = (index % SIZE) + 1;
    const tile = document.createElement("button");
    tile.type = "button";
    tile.className = `tile ${cell.kind}${powered.has(index) ? " powered" : ""}`;
    tile.style.gridRow = String(row);
    tile.style.gridColumn = String(column);
    tile.setAttribute("role", "gridcell");
    tile.setAttribute("aria-rowindex", String(row));
    tile.setAttribute("aria-colindex", String(column));
    tile.dataset.index = String(index);

    if (cell.kind === "empty") {
      tile.classList.add("empty");
      tile.tabIndex = -1;
      tile.setAttribute("aria-label", `Empty garden space, row ${row}, column ${column}`);
    } else {
      tile.setAttribute("aria-label", tileDescription(cell, powered.has(index), row, column));
      const pipe = document.createElement("span");
      pipe.className = "pipe";
      pipe.setAttribute("aria-hidden", "true");
      pipe.style.setProperty("--rotation", `${cell.rotation * 90}deg`);
      if (cell.ports.length === 2) {
        const straight = cell.ports[1] === 2;
        pipe.append(makeSegment(0), makeSegment(straight ? 180 : 90));
      } else {
        pipe.append(makeSegment(0));
      }
      const hub = document.createElement("span");
      hub.className = "hub";
      pipe.append(hub);
      tile.append(pipe);
      if (cell.kind === "goal") {
        const flower = document.createElement("span");
        flower.className = "goal-icon";
        flower.setAttribute("aria-hidden", "true");
        flower.textContent = "✿";
        tile.append(flower);
      }
      tile.addEventListener("click", () => rotateTile(index));
      tile.addEventListener("keydown", (event) => handleTileKeydown(event, index));
    }
    board.append(tile);
  });
  updateInterface();
  if (powered.has(cells.length - 1) && cells[cells.length - 1].kind === "goal") winLevel();
}

function makeSegment(rotation) {
  const segment = document.createElement("span");
  segment.className = "segment";
  segment.style.transform = `rotate(${rotation}deg)`;
  return segment;
}

function tileDescription(cell, isPowered, row, column) {
  const label = cell.kind === "source" ? "Spark" : cell.kind === "goal" ? "Flower" : "Path";
  return `${label}, ${isPowered ? "glowing" : "quiet"}, row ${row}, column ${column}. Turn clockwise.`;
}

function handleTileKeydown(event, index) {
  if (event.key === "Enter" || event.key === " ") {
    event.preventDefault();
    rotateTile(index);
  }
  if (event.key === "ArrowRight" || event.key === "ArrowDown") {
    event.preventDefault();
    focusNeighbor(index, 1);
  }
  if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
    event.preventDefault();
    focusNeighbor(index, -1);
  }
}

function focusNeighbor(index, step) {
  for (let offset = 1; offset < cells.length; offset += 1) {
    const next = (index + offset * step + cells.length) % cells.length;
    if (cells[next].kind !== "empty") {
      board.querySelector(`[data-index="${next}"]`)?.focus();
      return;
    }
  }
}

function traceSignal(levelCells) {
  const start = levelCells.findIndex((cell) => cell.kind === "source");
  const reached = new Set([start]);
  const queue = [start];

  while (queue.length) {
    const current = queue.shift();
    const row = Math.floor(current / SIZE);
    const column = current % SIZE;
    for (const directionIndex of portsFor(levelCells[current])) {
      const direction = DIRECTIONS[directionIndex];
      const nextRow = row + direction.row;
      const nextColumn = column + direction.column;
      if (nextRow < 0 || nextRow >= SIZE || nextColumn < 0 || nextColumn >= SIZE) continue;
      const next = cellIndex(nextRow, nextColumn);
      if (reached.has(next) || levelCells[next].kind === "empty") continue;
      const opposite = (directionIndex + 2) % 4;
      if (portsFor(levelCells[next]).includes(opposite)) {
        reached.add(next);
        queue.push(next);
      }
    }
  }
  return reached;
}

function rotateTile(index, countMove = true) {
  if (overlay.hidden === false || cells[index].kind === "empty") return;
  cells[index].rotation = (cells[index].rotation + 1) % 4;
  if (countMove) moves += 1;
  playTone(330 + cells[index].rotation * 55, .055);

  const previouslyPowered = powered;
  powered = traceSignal(cells);
  const tile = board.querySelector(`[data-index="${index}"]`);
  tile.classList.toggle("powered", powered.has(index));
  tile.querySelector(".pipe").style.setProperty("--rotation", `${cells[index].rotation * 90}deg`);
  tile.setAttribute("aria-label", tileDescription(cells[index], powered.has(index), Math.floor(index / SIZE) + 1, (index % SIZE) + 1));
  for (const connected of powered) {
    const connectedTile = board.querySelector(`[data-index="${connected}"]`);
    if (!connectedTile) continue;
    connectedTile.classList.toggle("powered", true);
    connectedTile.setAttribute("aria-label", tileDescription(cells[connected], true, Math.floor(connected / SIZE) + 1, (connected % SIZE) + 1));
  }
  for (const disconnected of previouslyPowered) {
    if (powered.has(disconnected)) continue;
    const disconnectedTile = board.querySelector(`[data-index="${disconnected}"]`);
    disconnectedTile?.classList.remove("powered");
    if (disconnectedTile) {
      disconnectedTile.setAttribute("aria-label", tileDescription(cells[disconnected], false, Math.floor(disconnected / SIZE) + 1, (disconnected % SIZE) + 1));
    }
  }
  document.getElementById("move-count").textContent = String(moves);
  updateSignalStatus();
  if (powered.has(cells.length - 1) && cells[cells.length - 1].kind === "goal") winLevel();
}

let moves = 0;
function updateInterface() {
  const level = LEVELS[state.level];
  document.getElementById("level-number").textContent = String(state.level + 1).padStart(2, "0");
  document.getElementById("level-name").textContent = level.name;
  document.getElementById("level-description").textContent = level.subtitle;
  document.getElementById("chapter-label").textContent = level.chapter;
  document.getElementById("hint-copy").textContent = level.encouragement;
  document.getElementById("move-count").textContent = String(moves);
  const blooms = state.completed.length;
  document.getElementById("blooms-count").textContent = String(blooms);
  document.getElementById("blooms-word").textContent = blooms === 1 ? "bloom" : "blooms";
  document.getElementById("progress-caption").textContent = blooms === LEVELS.length
    ? "The whole garden is glowing. Lovely work."
    : blooms === 0 ? "A tiny garden is waiting for you." : `${LEVELS.length - blooms} little ${LEVELS.length - blooms === 1 ? "path" : "paths"} still to find.`;
  document.getElementById("progress-fill").style.width = `${(blooms / LEVELS.length) * 100}%`;
  document.querySelector(".progress-track").setAttribute("aria-valuenow", String(blooms));
  document.getElementById("signal-label").textContent = powered.size > 1 ? "A little light is travelling" : "The flower is listening";
  document.getElementById("next-button").textContent = state.level === LEVELS.length - 1
    ? "Wander the garden again"
    : "Keep exploring";
}

function updateSignalStatus() {
  document.getElementById("signal-label").textContent = powered.size > 1 ? "A little light is travelling" : "The flower is listening";
}

function winLevel() {
  if (!overlay.hidden) return;
  state.completed = [...new Set([...state.completed, state.level])];
  saveState();
  updateInterface();
  document.getElementById("win-title").textContent = ["A little wonder.", "A lovely little glow.", "The moon says thank you.", "Room to grow.", "You found the clearing.", "The whole garden, home."][state.level];
  document.getElementById("win-copy").textContent = `${moves} little ${moves === 1 ? "turn" : "turns"} to bring the garden back.`;
  overlay.hidden = false;
  playTone(659, .12);
  window.setTimeout(() => playTone(880, .18), 100);
}

function resetLevel() {
  moves = 0;
  overlay.hidden = true;
  render();
}

function showHint() {
  if (!overlay.hidden) return;
  const target = cells.findIndex((cell) => cell.kind !== "empty" && cell.rotation !== cell.solvedRotation);
  if (target < 0) {
    showToast("The paths are already lined up. Give the last turn a try.");
    return;
  }
  const tile = board.querySelector(`[data-index="${target}"]`);
  tile.classList.remove("hint");
  void tile.offsetWidth;
  tile.classList.add("hint");
  tile.focus({ preventScroll: true });
  showToast("This tile is ready for a little turn.");
  window.setTimeout(() => tile.classList.remove("hint"), 1800);
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => toast.classList.remove("show"), 2200);
}

function playTone(frequency, duration) {
  if (!audio.enabled) return;
  try {
    audio.context ??= new AudioContext();
    const oscillator = audio.context.createOscillator();
    const gain = audio.context.createGain();
    oscillator.type = "sine";
    oscillator.frequency.value = frequency;
    gain.gain.setValueAtTime(.035, audio.context.currentTime);
    gain.gain.exponentialRampToValueAtTime(.001, audio.context.currentTime + duration);
    oscillator.connect(gain);
    gain.connect(audio.context.destination);
    oscillator.start();
    oscillator.stop(audio.context.currentTime + duration);
  } catch (error) {
    audio.enabled = false;
    console.warn("Signal Garden audio is unavailable in this browser.", error);
  }
}

document.getElementById("reset-button").addEventListener("click", resetLevel);
document.getElementById("hint-button").addEventListener("click", showHint);
document.getElementById("next-button").addEventListener("click", () => {
  overlay.hidden = true;
  state.level = (state.level + 1) % LEVELS.length;
  moves = 0;
  saveState();
  render();
});
document.getElementById("sound-toggle").addEventListener("click", (event) => {
  audio.enabled = !audio.enabled;
  const button = event.currentTarget;
  button.setAttribute("aria-label", audio.enabled ? "Turn sound off" : "Turn sound on");
  button.title = audio.enabled ? "Turn sound off" : "Turn sound on";
  button.querySelector(".sound-label").textContent = audio.enabled ? "Sound on" : "Sound off";
  if (audio.enabled) playTone(523, .1);
});

render();
