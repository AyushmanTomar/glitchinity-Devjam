var speechRecognition = window.webkitSpeechRecognition

var recognition = new speechRecognition()

var textbox = $("#memory")
var instructions = $("#instructions")
var startButton = $("#start-btn")
var postbtn = $("#post-btn")


var content = ''
var isRecognitionActive = false

recognition.continuous = true

recognition.onstart = function () {
    instructions.text("Voice Recognition is On")
    startButton.text("Stop")
    isRecognitionActive = true
}

recognition.onspeechend = function () {
    instructions.text("No Activity")
}

recognition.onerror = function () {
    instructions.text("Try Again")
}

recognition.onend = function() {
    instructions.text("Voice Recognition is Off")
    startButton.text("Start Mic")
    isRecognitionActive = false
}

recognition.onresult = function (event) {
    var current = event.resultIndex;
    var transcript = event.results[current][0].transcript
    content += transcript
    textbox.val(content)
}

startButton.click(function (event) {
    if (isRecognitionActive) {
        recognition.stop()
    } else {
        recognition.start()
    }
})

textbox.on('input', function () {
    content = $(this).val()
})

postbtn.click(function (event) {
    content="/post "
    textbox.val(content)
    })