// You are a good boy and won't abuse the API, will you?

let mode;
let identity;
let room;

let poller;
let last_event = -1;
let question_number = -1;

function apply_event(gotit) {
    if (gotit['event_index'] === last_event || gotit['event_index'] === -1) {
        return
    }
    last_event = gotit['event_index'];
    let event = gotit['event'];

    ['text_field', 'button_container', 'image', 'stat_container'].forEach(
        el => document.getElementById(el).style.display = 'none'
    )

    if (event['type'] === 't') {
        document.getElementById('text_field').textContent = event['text'];
        document.getElementById('text_field').style.removeProperty('display');
    }
    if (event['type'] === 'q') {
        document.getElementById('question').textContent = event['question']
        for (let i = 0; i < 4; i++) {
            document.getElementById('bn' + i).textContent = event['options'][i];
        }
        question_number = event['number'];
        document.getElementById('button_container').style.removeProperty('display');
    }
    if (event['type'] === 'p') {
        document.getElementById('image').style.removeProperty('display');
    }
    if (event['type'] === 's') {
        for (let i = 0; i < 4; i++) {
            document.getElementById('stat' + i).textContent = event['stats'][i];
            document.getElementById('stat' + i).style.height = (25 + 50 * parseInt(event['stats'][i])).toString() + 'px';
        }
        document.getElementById('text_field').textContent = 'Question was: ' + event['question'];
        document.getElementById('text_field').style.removeProperty('display');
        document.getElementById('text_field').style.removeProperty('display');
        document.getElementById('stat_container').style.removeProperty('display');
    }
}

function pool_for_puppets() {
    const req = new XMLHttpRequest();
    req.open( "GET", 'pool_for_puppets' + '?identity=' + identity + '&skip=' + last_event, true)
    req.onreadystatechange = function() {
        if(req.readyState !== 4 || req.status !== 200) return
        console.log("pool_for_puppets output:", JSON.parse(req.responseText))
        apply_event(JSON.parse(req.responseText))

        // Long polling
        poller = setTimeout(function () {
            pool_for_puppets()
        }, 200)
    }
    console.log("pool_for_puppets input:", identity, last_event)
    req.send()
}

function caac_puppet(value) {
    const req = new XMLHttpRequest()
    req.open("POST", 'caac_puppet', true)
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    let data = {"identity": identity, "number": question_number, "picked": value}
    console.log("caacPuppeteer", data)
    req.send(JSON.stringify(data))
}


function caac_puppeteer() {
    let text = document.getElementById("command").value
    document.getElementById("command").value = ""

    const req = new XMLHttpRequest()
    req.open( "POST", 'caac_puppeteer', true)
    req.setRequestHeader("Content-Type", "application/json;charset=UTF-8")
    let data = {'prompt': text, 'room': room, 'identity': identity}
    console.log("caacPuppeteer", data)
    req.send(JSON.stringify(data))
}


document.addEventListener('DOMContentLoaded', function() {
    console.log("I AM ALIIIIIIIIVE!!!")

    mode = document.getElementById("mode").textContent
    identity = document.getElementById("identity").textContent
    room = document.getElementById("room").textContent
    const element = document.getElementById('loader_constants')
    element.remove()

    if (mode === "puppet") {
        poller = setTimeout(function () {
            pool_for_puppets()
        }, 200)
    }
})
