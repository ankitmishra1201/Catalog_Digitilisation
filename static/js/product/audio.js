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