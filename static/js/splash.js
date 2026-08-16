const splashPage = document.getElementById("splashPage");
const status = document.getElementById("status");

const STATUS_MESSAGES = [
    "Warming up the engine...",
    "Loading compression models...",
    "Almost ready..."
];

let messageIndex = 0;

const statusInterval = setInterval(() => {
    messageIndex++;
    if (messageIndex < STATUS_MESSAGES.length) {
        status.textContent = STATUS_MESSAGES[messageIndex];
    }
}, 950);

function enterApp() {
    clearInterval(statusInterval);
    splashPage.classList.add("leaving");
    setTimeout(() => {
        window.location.href = "/dashboard";
    }, 400);
}

// Auto-advance once the intro animation has played
const AUTO_ADVANCE_MS = 3000;
const autoAdvanceTimer = setTimeout(enterApp, AUTO_ADVANCE_MS);

// Let people skip straight in
splashPage.addEventListener("click", () => {
    clearTimeout(autoAdvanceTimer);
    enterApp();
});
