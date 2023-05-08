function submit_data(){
	document.getElementById("submit_button").onclick = event => {
		data = document.querySelectorAll("[data-section='dem']");
		data_dem = {}
		for (let i = 0; i < data.length; i++) {
			if ((data[i].type == "radio" && data[i].checked == false) || data[i].value == "") {
				continue
			} else {
				data_dem[data[i].name] = data[i].value;
			}
		}

		data = document.querySelectorAll("[data-section='exp']")
		data_exp = []
		for (let i = 0; i < data.length; i++) {
			if ((data[i].type == "radio" && data[i].checked == false) || data[i].value == "") {
				continue
			} else {
				datum = {experiment:data[i].dataset.experiment, item:data[i].dataset.item, condition:data[i].dataset.condition,
					response:data[i].value, literal_response:data[i].dataset.literal_response, presentation_order:data[i].dataset.presentation_order}
				data_exp.push(datum)
			}
		}
		survey_id = document.getElementById("experiment_id").innerHTML;
		const requestOptions = {
			"method": "POST",
			"headers": {"Content-Type":"application/json"},
			"body": JSON.stringify({"data_dem":data_dem, "data_exp":data_exp, "survey_id":survey_id})
		};

		fetch("/submit_data", requestOptions)
			.then((response) =>
				{window.location.href = document.getElementById("redirect_link").innerHTML}
			);
	}
}
