// Navigation (same)
function showDashboard() {
    document.getElementById("home").style.display = "none";
    document.getElementById("features").style.display = "none";
    document.getElementById("dashboard").style.display = "block";
}

function showHome() {
    document.getElementById("home").style.display = "flex";
    document.getElementById("features").style.display = "flex";
    document.getElementById("dashboard").style.display = "none";
}

// DATA
let total = 0;
let data = JSON.parse(localStorage.getItem("energyData")) || [];

// CHART
const chart = new Chart(document.getElementById("chart"), {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Energy Usage",
            data: [],
            borderColor: "#22c55e",
            tension: 0.4
        }]
    }
});

// LOAD OLD DATA
data.forEach((val, i) => {
    chart.data.labels.push("Entry " + (i+1));
    chart.data.datasets[0].data.push(val);
    total += val;
});
document.getElementById("total").innerText = total;
chart.update();

// ADD DATA
function addData() {
    let val = document.getElementById("energyInput").value;

    if (!val) {
        alert("Enter value!");
        return;
    }

    val = Number(val);
    total += val;
    data.push(val);

    localStorage.setItem("energyData", JSON.stringify(data));

    chart.data.labels.push("Entry " + data.length);
    chart.data.datasets[0].data.push(val);
    chart.update();

    document.getElementById("total").innerText = total;
    document.getElementById("energyInput").value = "";
}

// 🔥 NEW FEATURE 1: LIVE TRACKING (Auto update every 2 sec)
let liveInterval;

function startLive() {
    liveInterval = setInterval(() => {
        let randomVal = Math.floor(Math.random() * 50) + 10;

        document.getElementById("energyInput").value = randomVal;
        addData();
    }, 2000);
}

function stopLive() {
    clearInterval(liveInterval);
}

// 🔥 NEW FEATURE 2: RESET DATA
function resetData() {
    localStorage.removeItem("energyData");
    location.reload();
}

// 🔥 NEW FEATURE 3: AVERAGE CALCULATION
function calculateAverage() {
    if (data.length === 0) return 0;
    let sum = data.reduce((a, b) => a + b, 0);
    return (sum / data.length).toFixed(2);
}

// 🔥 NEW FEATURE 4: MAX & MIN
function showStats() {
    if (data.length === 0) {
        alert("No data!");
        return;
    }

    let max = Math.max(...data);
    let min = Math.min(...data);
    let avg = calculateAverage();

    alert(`Max: ${max} kWh\nMin: ${min} kWh\nAvg: ${avg} kWh`);
}

// 🔥 NEW FEATURE 5: HIGH USAGE ALERT
function checkAlert(val) {
    if (val > 80) {
        alert("⚠️ High Energy Usage!");
    }
}

// Modify addData to include alert
const oldAddData = addData;
addData = function() {
    let val = document.getElementById("energyInput").value;
    if (!val) return alert("Enter value!");

    val = Number(val);
    checkAlert(val);
    oldAddData();
}

// 🔥 NEW FEATURE 6: EXPORT DATA (for viva 🔥)
function exportData() {
    let text = data.join(",");
    let blob = new Blob([text], { type: "text/plain" });
    let link = document.createElement("a");

    link.href = URL.createObjectURL(blob);
    link.download = "energy-data.txt";
    link.click();
}