const Http = new XMLHttpRequest()

function flipLightState(identifier) {
    fetch(`${window.origin}/device/${identifier}`)
        .then((response) => response.json())
        .then((deviceMetadata) => {
            var ip = deviceMetadata['data']['controller_gateway']
            var hue_user = deviceMetadata['data']['hue_user']

            fetch(`http://${ip}/api/${hue_user}/lights/${identifier}`)
                .then((response) => response.json())
                .then((data) => {
                    if (data['state']['on'] == false) {
                        var body = { "on": true }
                        var color = "#f4af36"
                    } else {
                        var body = { "on": false }
                        var color = "#898d95"
                    }

                    Http.open('PUT', `http://${ip}/api/${hue_user}/lights/${identifier}/state`)
                    Http.send(JSON.stringify(body))
                    document.getElementById(identifier).style.setProperty('color', color)
                }
                )
        }
        )
};

function flipSwitchState(identifier) {
    fetch(`${window.origin}/device/${identifier}/flip-state`)
        .then((response) => response.json())
        .then((data) => {
            if (data['switch'] == 'off') {
                var color = '#898d95'
            } else if (data['switch'] == 'on') {
                var color = '#f4af36'
            }
            document.getElementById(identifier).style.setProperty('color', color)
        }
        )
};

function getAllStates() {
    fetch(`${window.origin}/devices`)
        .then((response) => response.json())
        .then((data) => {
            data['devices'].forEach(device => {

                fetch(`${window.origin}/device/${device['identifier']}`)
                    .then((response) => response.json())
                    .then((data) => {

                        var device_type = data['data']['device_type']
                        var identifier = device['identifier']

                        if ( device_type === 'light') {
                            // let identifier = data['data']['identifier']
                            let ip = data['data']['controller_gateway']
                            let hue_user = data['data']['hue_user']
                            fetch(`http://${ip}/api/${hue_user}/lights/${identifier}`)
                                .then((response) => response.json())
                                .then((data) => {
                                    if (data['state']['on'] == false) {
                                        var color = "#898d95"
                                    } else {
                                        var color = "#f4af36"
                                    }
                                    document.getElementById(identifier).style.setProperty('color', color)
                                }
                                )

                        } else if (device_type === 'switch') {
                            fetch(`${window.origin}/device/${identifier}/get-state`)
                                .then((response) => response.json())
                                .then((data) => {
                                    if (data['state'] == 'off') {
                                        var color = "#898d95"
                                    } else if (data['state'] == 'on') {
                                        var color = "#f4af36"
                                    }
                                    document.getElementById(identifier).style.setProperty('color', color)
                                }
                                )
                        }
                    }
                    )
            }
            )
        }
        )
}