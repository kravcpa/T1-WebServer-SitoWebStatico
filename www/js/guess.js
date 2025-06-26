const displayBox = document.getElementById("displayBox");
const numberRow = document.getElementById("numberRow");

let targetNumber = -1;
let canClick = true;

function generateNewNumber() {
    targetNumber = Math.floor(Math.random() * 10);
    displayBox.textContent = "?";
    displayBox.className = "";
    canClick = true;
}

function handleGuess(guess) {
    if (!canClick) return;
    canClick = false;

    displayBox.textContent = targetNumber;

    if (guess === targetNumber) {
        displayBox.className = "correct";
    } else {
        displayBox.className = "wrong";
    }

    setTimeout(() => {
        generateNewNumber();
    }, 1000);
}

function init() {
    for (let i = 0; i <= 9; i++) {
        const btn = document.createElement("button");
        btn.className = "numberButton";
        btn.textContent = i;
        btn.addEventListener("click", () => handleGuess(i));
        numberRow.appendChild(btn);
    }

    generateNewNumber();
}

init();