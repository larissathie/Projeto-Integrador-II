const monthYearElement = document.getElementById('monthYear');
const datesElement = document.getElementById('dates');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentDate = new Date();

const updateCalendar = () => {
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth();

    const firstDay = new Date(currentYear, currentMonth, 1);
    console.log(typeof (firstDay));
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
        const todayClass = (date.toDateString() === new Date().toDateString()) ? ' today' : '';
        datesHTML += `<div class="date${todayClass}" day="${date}">${i}</div>`;
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
    const activeDays = document.querySelectorAll(".date")
    activeDays.forEach(day =>
        day.classList.remove('selected')
    )
    const day = event.target.innerHTML;
    const dateString = event.target.getAttribute('day');
    const dateParts = dateString.split(' ');
    const arrayMonth = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    const shortMonth = arrayMonth.indexOf(dateParts[1]);
    const dateObject = new Date(dateParts[3], shortMonth, dateParts[2]);
    localStorage.setItem('currentDate', `${dateObject}`);
    localStorage.setItem('day', `${dateObject.getDate()}`);
    const position = localStorage.getItem('day');
    activeDays[position - 1].classList.add('selected');
}

datesElement.addEventListener('click', addClass);