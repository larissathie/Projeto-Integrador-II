const monthYearElement = document.getElementById('monthYear');
const datesElement = document.getElementById('dates');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentDate = new Date();

const updateCalendar = () => {
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const totalDays = lastDay.getDate();
    const firstDayIndex = firstDay.getDay();
    const lastDayIndex = lastDay.getDay();
    const monthYearString = currentDate.toLocaleString('pt-BR', { month: 'long', year: 'numeric' });
    monthYearElement.textContent = monthYearString;

    const clearBoard = document.querySelector('#dates');
    removeAllChildNodes(clearBoard);

    for (let i = firstDayIndex; i > 0; i -= 1) {
        const prevDate = new Date(currentYear, currentMonth, 1 - i);
        const newDiv = document.createElement("div");
        datesElement.appendChild(newDiv);
    }

    for (let i = 1; i <= totalDays; i += 1) {
        const date = new Date(currentYear, currentMonth, i);
        const newDiv = document.createElement("div");
        newDiv.setAttribute("class", "date");
        newDiv.setAttribute("day", date);
        newDiv.innerHTML = i;
        newDiv.addEventListener('click', (event) => {
            unselect();
            event.target.classList.toggle("selected");
        });
        datesElement.appendChild(newDiv);
    }

    for (let i = 1; i < 7 - lastDayIndex; i += 1) {
        const newDiv = document.createElement("div");
        datesElement.appendChild(newDiv);
    }

}

prevBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    updateCalendar();
})

nextBtn.addEventListener('click', () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    updateCalendar();
})

updateCalendar();

const unselect = () => {
    const selectedDays = [...document.getElementsByClassName("selected")];
    selectedDays.map(day =>
        day.classList.remove("selected")
    )
}

const saveDate = (event) => {
    const dateString = event.target.getAttribute('day');
    const dateParts = dateString.split(' ');
    const arrayMonth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const shortMonth = arrayMonth.indexOf(dateParts[1]);
    const dateObject = new Date(dateParts[3], shortMonth, dateParts[2]);
    localStorage.setItem('currentDate', `${dateObject}`);
    // localStorage.setItem('day', `${dateObject.getDate()}`);
}

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

datesElement.addEventListener('click', saveDate);