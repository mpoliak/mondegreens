var trial_number = 0;
var audio_files;	

debug = false;

window.onload = function() {
	if (debug) {
		trial_number = 30
		begin_experiment();
	} else{
		$(document).on('hcHeadphoneCheckEnd', function(event, data) {

		var headphoneCheckDidPass = data.didPass;
		var headphoneCheckData = data.data;
		var didPassMessage = headphoneCheckDidPass ? 'passed' : 'failed';
		if (didPassMessage == "passed") {
			begin_experiment();
		} else {
			alert("Headphone check failed. Please wear headphones and refresh the page. If you don't have headphones you can use for the experiment, please return the task. Thank you!")
		}	
	});

	document.getElementById("loading").hidden = true;
	document.getElementById("prolific_id_div").hidden = false;

	}
}


function calibration_completed() {
	document.getElementById("calibration_task").hidden = true;
	var headphoneCheckConfig = {doCalibration: false};
	HeadphoneCheck.runHeadphoneCheck(headphoneCheckConfig);
}

function wait(ms) {
	return new Promise((resolve, reject) => {
		setTimeout(() => {
			resolve(ms)
		}, ms )
	})
}  

function run_trial() {
	let start_button_div = document.getElementById("button_div");
	var last_trial;
	start_button_div.hidden = true;
	if (trial_number == audio_files.length/2) {
		submit_data();
		return
	}
	if (trial_number == 0) {
		let start_button = document.getElementById("start_button");
		start_button.innerHTML = "next";
		let instructions = document.getElementById("instructions");
		instructions.hidden = true;
		last_trial = trial_number;			
			
	}
	if (trial_number > 0) {
		last_trial = trial_number - 1;
		let previous_div = document.getElementById("part_".concat((1+last_trial).toString()));
		previous_div.hidden = true;
		start_button = document.getElementById("start_button")
		start_button.innerHTML = "next"
	}
	let prime_recording = audio_files[2*(trial_number)]
	let critical_recording = audio_files[2*(trial_number)+1]
	let listen1 = document.getElementById("listen1")
	let listen2 = document.getElementById("listen2")
	listen1.hidden = false;
	let current_div = document.getElementById("part_".concat((1+trial_number).toString()))
	wait(1000).then((result) => {
		prime_recording.play()
		wait(prime_recording.duration*1000 + 1000).then((result) => {
			listen1.hidden = true;
			listen2.hidden = false;
			wait(1000).then((result) => {
				critical_recording.play()
				wait(critical_recording.duration*1000 + 1000).then((result) =>{
					listen2.hidden = true;
					current_div.hidden = false;
					trial_number ++;
					start_button_div.hidden = false;
				});
			});

		});
	});

}

begin_experiment = function() {
	audio_files = document.querySelectorAll("#experimental_audio audio");
	const entire_study_div = document.getElementById("entire_study")
	entire_study_div.hidden = false;
}

begin_calibration = function() {
	if (document.getElementById("prolific_id").value == "") {
		alert("Must provide Prolific ID");
		return
	}
	document.getElementById("prolific_id_div").hidden = true;
	document.getElementById("calibration_task").hidden = false;
}

submit_data = function() {
	var inputs = document.querySelectorAll("input");
	var prolific_id = inputs[0].value;
	var dataset = []
	for (i = 0; i < inputs.length; i++) {
		if (inputs[i].checked) {
			dataset.push(
				{
					prolific_id:prolific_id,
					item:inputs[i].dataset.item,
					language:inputs[i].dataset.language,
					noise_level:inputs[i].dataset.noise_level,
					presentation_order:inputs[i].dataset.presentation_order,
					prime:inputs[i].dataset.prime,
					prime_id:inputs[i].dataset.prime_id,
					rating:inputs[i].value
				}
			);
		}
	}
	const requestOptions = {
		"method":"POST",
		"headers":{"Content-Type":"application/json"},
		"body": JSON.stringify(dataset)
	}

	fetch("/mp/submitdata/", requestOptions)
		.then((response) => 
		{
			if (debug) {
				alert("done")
			} else {
				window.location.href = "https://app.prolific.co/submissions/complete?cc=C1JMDZ0F"
			}
		}
		);

}
