function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');
    return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
}

function updateTime() {
    const dateTimeElement = document.getElementById("dateTime");
    const now = new Date();
    const formattedDateTime = formatDate(now);
    dateTimeElement.innerText = formattedDateTime;
}

document.addEventListener("DOMContentLoaded", function() {
    updateTime();
    setInterval(updateTime, 1000);

    const toggleButton = document.getElementById("toggleButton");
    const distanceElement = document.getElementById("distance");
    const switchElement = document.getElementById("switch");

    // 나머지 JavaScript 코드...
})

if (data.temperature > 25) {
    document.getElementById('temperatureMessage').innerHTML = '온도가 너무 높습니다. 에어컨을 켜주세요';
} else {
    document.getElementById('temperatureMessage').innerHTML = ''; // Clear the message
};
