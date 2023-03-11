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
	if (chunks[0].length > 0 && chunks[1].length > 0 && chunks[2].length > 0) {
		document.getElementById("submitButton").disabled = false;
	}
}

function submitRecordings() {
	let formData = new FormData();
	for (let i = 0; i < 3; i++) {
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
