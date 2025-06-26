const square = document.getElementById("square");
const gameArea = document.getElementById("gameArea");
const scoreEl = document.getElementById("score");

let score = 0;
let posX = 0;
let posY = 0;

function moveSquare() {
    const maxX = gameArea.clientWidth - square.offsetWidth;
    const maxY = gameArea.clientHeight - square.offsetHeight;

    posX = Math.floor(Math.random() * maxX);
    posY = Math.floor(Math.random() * maxY);

    updateTransform(1);
}

function updateTransform(sizeScale = 1) {
    square.style.transform = `translate(${posX}px, ${posY}px) scale(${sizeScale})`;
}

function createBurst(x, y) {
    const burst = document.createElement("div");
    burst.className = "burst";
    burst.style.left = `${x}px`;
    burst.style.top = `${y}px`;
    gameArea.appendChild(burst);
    setTimeout(() => burst.remove(), 400);
}

function init() {
    let resizeTimeout;
    window.addEventListener("resize", () => {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(() => {
            moveSquare();
        }, 200);
    });

    square.addEventListener("click", () => {
        scoreEl.textContent = ++score;

        const rect = square.getBoundingClientRect();
        const burstX = posX + square.offsetWidth / 2 - 30;
        const burstY = posY + square.offsetHeight / 2 - 30;
        createBurst(burstX, burstY);

        updateTransform(1.2);
        setTimeout(() => {
            updateTransform(1);
            moveSquare();
        }, 100);
    });

    window.onload = moveSquare;
}

init();