// global constants mixin
// requires vue.js library
// place between vue and custom component code

// can also be done using a JS object, but would
// require importing via the "data" attribute

Vue.mixin({
    data: function() {
        return {
            get URL_AUTH() { return "{{ url_for('auth') }}" },
            get URL_UNAUTH() { return "{{ url_for('unauth') }}" },
            get URL_RESULTS_STREAM() { return "{{ url_for('stream_results') }}" },
            get URL_RESULTS_GET() { return "{{ url_for('get_results') }}" },
            get URL_ATTACKS_GET() { return "{{ url_for('get_attacks') }}" },
            get URL_ATTACKS_POST() { return "{{ url_for('add_attacks') }}" },
            get URL_ATTACK_RUN() { return "{{ url_for('run_attack') }}" },
            get URL_STATUS_GET() { return "{{ url_for('get_status') }}" },
        }
    },
});

// global functions

function handleErrors(response) {
    if (!response.ok) {
        throw Error(response.statusText);
    }
    return response;
}
