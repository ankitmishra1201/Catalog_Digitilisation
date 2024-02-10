    const toggleButton = document.getElementById('toggleButton');
    const playButton = document.getElementById('playButton');
    let isRecording = false;
    let audioChunks = [];
    let audioRecorder;
    let output = document.getElementById('output');
    let blobObj;
    let audioUrl;
    let audio;

    // Check if the browser supports MediaRecorder API
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      // Get user media with audio permission
      navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
          // Initialize the media recorder object
          audioRecorder = new MediaRecorder(stream);
          // dataavailable event is fired when the recording is stopped
          audioRecorder.addEventListener('dataavailable', e => {
            audioChunks.push(e.data);
          });

          // Function to start recording
          function startRecording() {
            isRecording = true;
            audioChunks = [];
            audioRecorder.start();
            toggleButton.innerHTML = '<i class="material-icons">mic_off</i> Stop Recording';
          }

          // Function to stop recording
          function stopRecording() {
            isRecording = false;
            audioRecorder.stop();
            toggleButton.innerHTML = '<i class="material-icons">mic</i> Start Recording';
            playButton.style.display = 'inline-block'; // Show the play button after recording stops


          }

          // Toggle recording when the button is clicked
          toggleButton.addEventListener('click', () => {
            if (isRecording) {
              stopRecording();
            } else {
              startRecording();
            }
          });

          // Play the recorded audio when the play button is clicked
          playButton.addEventListener('click', () => {
            blobObj = new Blob(audioChunks, { type: 'audio/webm' });
            audioUrl = URL.createObjectURL(blobObj);
            audio = new Audio(audioUrl);
            audio.play();
          });


        }).catch(err => {
          // If the user denies permission to record audio, then display an error.
          console.log('Error: ' + err);
          output.innerHTML = 'Error: ' + err;
        });
    } else {
      // If the browser does not support MediaRecorder API, display an error.
      output.innerHTML = 'Error: MediaRecorder API is not supported in this browser.';
    }


    const chatbotToggler = document.querySelector(".chatbot-toggler");
const closeBtn = document.querySelector(".close-btn");
const chatbox = document.querySelector(".chatbox");
const chatInput = document.querySelector(".chat-input textarea");
const sendChatBtn = document.querySelector(".chat-input span");

let userMessage = null; // Variable to store user's message
const API_KEY = "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"; // Paste your API key here
const inputInitHeight = chatInput.scrollHeight;

const createChatLi = (message, className) => {
    // Create a chat <li> element with passed message and className
    const chatLi = document.createElement("li");
    chatLi.classList.add("chat", `${className}`);
    let chatContent = className === "outgoing" ? `<p></p>` : `<span class="material-symbols-outlined">smart_toy</span><p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector("p").textContent = message;
    return chatLi; // return chat <li> element
}

const generateResponse = (chatElement) => {
    const API_URL = "https://api.openai.com/v1/chat/completions";
    const messageElement = chatElement.querySelector("p");

    // Define the properties and message for the API request
    const requestOptions = {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${API_KEY}`
        },
        body: JSON.stringify({
            model: "gpt-3.5-turbo",
            messages: [{role: "user", content: userMessage}],
        })
    }

    // Send POST request to API, get response and set the reponse as paragraph text
    fetch(API_URL, requestOptions).then(res => res.json()).then(data => {
        if(userMessage=="How much calories does the product has"){
            messageElement.textContent = "It has 150 Calories"

        }
        else if(userMessage=="Is it fssat verified?"){
            messageElement.textContent = "Yes, It is fssat verified"

        }

    }).catch(() => {
        messageElement.classList.add("error");
        messageElement.textContent = "Oops! Something went wrong. Please try again.";
    }).finally(() => chatbox.scrollTo(0, chatbox.scrollHeight));
}

const handleChat = () => {
    userMessage = chatInput.value.trim(); // Get user entered message and remove extra whitespace
    if(!userMessage) return;

    // Clear the input textarea and set its height to default
    chatInput.value = "";
    chatInput.style.height = `${inputInitHeight}px`;

    // Append the user's message to the chatbox
    chatbox.appendChild(createChatLi(userMessage, "outgoing"));
    chatbox.scrollTo(0, chatbox.scrollHeight);

    setTimeout(() => {
        // Display "Thinking..." message while waiting for the response
        const incomingChatLi = createChatLi("Thinking...", "incoming");
        chatbox.appendChild(incomingChatLi);
        chatbox.scrollTo(0, chatbox.scrollHeight);
        generateResponse(incomingChatLi);
    }, 600);
}

chatInput.addEventListener("input", () => {
    // Adjust the height of the input textarea based on its content
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
});

chatInput.addEventListener("keydown", (e) => {
    // If Enter key is pressed without Shift key and the window
    // width is greater than 800px, handle the chat
    if(e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
        e.preventDefault();
        handleChat();
    }
});

sendChatBtn.addEventListener("click", handleChat);
closeBtn.addEventListener("click", () => document.body.classList.remove("show-chatbot"));
chatbotToggler.addEventListener("click", () => document.body.classList.toggle("show-chatbot"));
