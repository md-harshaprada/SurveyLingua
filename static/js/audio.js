let streams = [], recorders = [], chunks = [[], [], []];

function startRecording(index) {
    navigator.mediaDevices.getUserMedia({audio: true})
    .then(function(s) {
        streams[index - 1] = s;
        recorders[index - 1] = new MediaRecorder(streams[index - 1]);
        recorders[index - 1].ondataavailable = function(e) {
            chunks[index - 1].push(e.data);
            let preview = document.getElementById("audioPreview" + index);
            preview.src = URL.createObjectURL(new Blob(chunks[index - 1]));
            preview.play();
        };
        recorders[index - 1].start();
        document.getElementById("startButton" + index).disabled = true;
        document.getElementById("stopButton" + index).disabled = false;
        document.getElementById("submitButton").disabled = true;
    });
}

function stopRecording(index) {
    recorders[index - 1].stop();
    streams[index - 1].getTracks().forEach(track => track.stop());
    document.getElementById("startButton" + index).disabled = false;
    document.getElementById("stopButton" + index).disabled = true;
    if (chunks[0].length==1) {
        document.getElementById("submitButton").disabled = false;
    }
}
  

function submitRecordings() {
    s=document.getElementById("name").value;
    r=document.getElementById("email").value;
    rating = document.querySelector('input[name="gender"]:checked').value;
    satisfaction=document.getElementById("satisfaction").value;
    performance=document.getElementById("performance").value;
    ratings=document.getElementById("ratings").value;
    let formData = new FormData();
    formData.append('name',s);
    formData.append('gender', rating);
    formData.append('email',r);
    formData.append('satisfaction',satisfaction);
    formData.append('performance',performance);
    formData.append('ratings',ratings);
    
    for (let i = 0; i < 2; i++) {
        let blob = new Blob(chunks[i], {type: 'audio/webm'});
        formData.append('audio' + (i+1), blob);
    }
    fetch('/upload', {method: 'POST', body: formData})
    .then(function(response) {
        alert("Recordings submitted successfully!");
    })
    .catch(function(error) {
        alert("Error submitting recordings: " + error.message);
    });
    chunks = [[], [], []];
    document.getElementById("submitButton").disabled = true;
}