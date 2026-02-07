let questions = [];
let answers = {};
let index = 0;

function start() {
    fetch("/questions", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            category: document.getElementById("category").value,
            lang: document.getElementById("lang").value
        })
    })
    .then(res => res.json())
    .then(data => {
        questions = data;
        answers = {};
        index = 0;
        document.getElementById("chat").innerHTML = "";
        showQuestion();
    });
}

function showQuestion() {
    if (index >= questions.length) {
        submit();
        return;
    }

    const q = questions[index];
    document.getElementById("chat").innerHTML = `
        <div class="bot">${q.text}</div>
        <div class="buttons">
            <button class="yes" onclick="answer(1)">YES</button>
            <button class="no" onclick="answer(0)">NO</button>
        </div>
    `;
}

function answer(val) {
    answers[questions[index].id] = val;
    index++;
    showQuestion();
}

function submit() {
    fetch("/submit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
            name: document.getElementById("name").value || "anonymous",
            age: document.getElementById("age").value || 0,
            lang: document.getElementById("lang").value,
            category: document.getElementById("category").value,
            answers: answers
        })
    })
    .then(res => res.json())
    .then(res => {
        document.getElementById("chat").innerHTML = `
            <div class="result">
                <h2>Condition: ${res.condition}</h2>
                <p><b>Severity:</b> ${res.severity}</p>
                <p>${res.advice}</p>
            </div>
        `;
    });
}
