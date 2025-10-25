const monthYearElement = document.getElementById('monthYear');
const datesElement = document.getElementById('dates');
const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

let currentDate = new Date();

function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
}

const unselect = () => {
    const selectedDays = [...document.querySelectorAll(".selected")];
    selectedDays.map(day =>
        day.classList.remove("selected")
    )
}

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

    removeAllChildNodes(datesElement);

    for (let i = firstDayIndex; i > 0; i -= 1) {
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

const btnReservar = document.getElementById('btnReservar');
const popupReserva = document.getElementById('popupReserva');
const confirmarReserva = document.getElementById('confirmarReserva');
const cancelarReserva = document.getElementById('cancelarReserva');
const mensagemReserva = document.getElementById('mensagemReserva');

// Função para abrir o popup se tiver uma data selecionada
btnReservar.addEventListener('click', () => {
    const selectedDay = document.querySelector('.selected');
    if (!selectedDay) {
        alert('Selecione uma data antes de reservar!');
        return;
    }

    const dataSelecionada = selectedDay.getAttribute('day');
    const dataFormatada = new Date(dataSelecionada).toLocaleDateString('pt-BR');

    mensagemReserva.textContent = `Deseja confirmar a reserva para o dia ${dataFormatada}?`;
    popupReserva.style.display = 'flex';
});

// Confirmar reserva - VERSÃO CORRIGIDA
confirmarReserva.addEventListener('click', () => {
    const selectedDay = document.querySelector('.selected');
    if (!selectedDay) {
        alert('Selecione uma data antes de reservar!');
        return;
    }

    const dataSelecionada = selectedDay.getAttribute('day'); // ← Variável declarada aqui
    const dataFormatada = new Date(dataSelecionada).toLocaleDateString('pt-BR');

    mensagemReserva.textContent = `Deseja confirmar a reserva para o dia ${dataFormatada}?`;
    popupReserva.style.display = 'flex';
});

// ✅ CORRIGIR ESTA LINHA ESPECIFICAMENTE:
confirmarReserva.addEventListener('click', () => {
    const selectedDay = document.querySelector('.selected');
    const dataSelecionada = selectedDay.getAttribute('day'); // ← Declarar novamente ou usar a de cima
    
    popupReserva.style.display = 'none';
    alert('Reserva confirmada com sucesso!');
    
    // ✅ CORRETO - sem typo:
    enviarReservaParaBackend(dataSelecionada); // ← "dataSelecionada" não "dataselecionada"
});

// Função para enviar para o backEnd

function enviarReservaParaBackend(dataSelecionada) {
    console.log("🔍 Iniciando agendamento...");
    
    let rota = '';
    if (AMBIENTE_ATUAL === 'salao') {
        rota = '/cadastro_Salao';
    } else if (AMBIENTE_ATUAL === 'churrasqueira') {
        rota = '/cadastro_churrasqueira';  // ← VERIFIQUE SE ESTÁ ESCRITO CORRETO
    }
    
    console.log("🔄 Rota que será usada:", rota);
    
    fetch(rota, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({data_reserva: dataSelecionada})
    })
    .then(response => {
        console.log("📨 Status da resposta:", response.status);
        console.log("📨 URL da resposta:", response.url);
        if (!response.ok) {
            throw new Error(`Erro HTTP: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        console.log("✅ Sucesso:", data);
        alert(data.message);
        setTimeout(() => { window.location.reload(); }, 1000);
    })
    .catch(error => {
        console.error("❌ Erro completo:", error);
        alert('Erro ao agendar: ' + error.message);
    });
}


// Cancelar reserva
cancelarReserva.addEventListener('click', () => {
    popupReserva.style.display = 'none';
});
