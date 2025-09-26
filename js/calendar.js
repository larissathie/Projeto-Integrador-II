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

    let datesHTML = '';

    for (let i = firstDayIndex; i > 0; i -= 1) {
        const prevDate = new Date(currentYear, currentMonth, 1 - i);
        // datesHTML += `<div class="date inactive">${prevDate.getDate()}</div>`
        datesHTML += `<div></div>`
    }

    for (let i = 1; i <= totalDays; i += 1) {
        const date = new Date(currentYear, currentMonth, i);
        const todayClass = (date.toDateString() === new Date().toDateString()) ? 'today' : '';
        datesHTML += `<div class="date active ${todayClass}">${i}</div>`;
    }

    for (let i = 1; i < 7 - lastDayIndex; i += 1) {
        const nextDate = new Date(currentYear, currentMonth + 1, i);
        datesHTML += `<div></div>`;
    }

    datesElement.innerHTML = datesHTML;

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

const addClass = (event) => {
    const activeDays = document.querySelectorAll(".active")
    activeDays.forEach(day =>
        day.classList.remove('selected')
    )
    const completeDate = document.getElementById('monthYear');
    const monthYear = completeDate.innerHTML.split(" ");
    const year = monthYear[2];
    const longMonth = monthYear[0];
    const arrayMonth = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];
    const shortMonth = arrayMonth.indexOf(longMonth);
    const day = event.target.innerHTML;
    localStorage.setItem('day', `${day}`);
    localStorage.setItem('longMonth', `${longMonth}`);
    localStorage.setItem('shortMonth', `${shortMonth}`)
    localStorage.setItem('year', `${year}`);
    localStorage.setItem('currentDate', `${new Date(year, shortMonth, day)}`);
    const position = localStorage.getItem('day');
    activeDays[position - 1].classList.add('selected');
}

datesElement.addEventListener('click', addClass);