var Dashboard = Vue.component('dashboard', {
    template: `
        <div class="twelve columns">
            <h3>CORS Exploitation Framework (CEF)</h3>
            <button v-on:click.prevent="logOut">log out</button>
            <p>status: <span class="status">{{ status }}</span></p>
            <panel v-bind:label="'add an attack'">
                <add-attack v-on:click="getAttacks"/>
            </panel>
            <panel v-bind:label="'run an attack'">
                <run-attack
                    v-bind:attacks="attacks"
                    v-bind:files="files"
                    v-on:click="getStatus"
                />
            </panel>
            <panel v-bind:label="'view results ('+results.length+')'">
                <view-results v-bind:results="results"/>
            </panel>
        </div>
    `,
    data: function() {
        return {
            attacks: [],
            files: [],
            results: [],
            status: '',
        }
    },
    evtSource: false,
    methods: {
        setupStream: function(event) {
            this.$options.evtSource = new EventSource(this.URL_RESULTS_STREAM);
            this.$options.evtSource.addEventListener('message', event => {
                var data = JSON.parse(event.data);
                this.results.push(data);
            }, false);
        },
        teardownStream: function(event) {
            if (this.$options.evtSource !== false) {
                this.$options.evtSource.close();
            }
        },
        getAttacks: function(event) {
            fetch(this.URL_ATTACKS_GET)
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.attacks = json.attacks;
                this.files = json.files;
            });
        },
        getStatus: function(event) {
            fetch(this.URL_STATUS_GET)
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.status = json.status.message;
                if (json.status.length > 0) {
                    this.status += ' '+json.status.length;
                }
            });
        },
        getResults: function(event) {
            fetch(this.URL_RESULTS_GET)
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                this.results = json.results;
            });
        },
        logOut: function(event) {
            fetch(this.URL_UNAUTH)
            .then(handleErrors)
            localStorage.clear();
            this.$router.push('login');
        }
    },
    created() {
        // preload attacks
        this.getAttacks();
        // preload status
        this.getStatus();
        // preload results
        this.getResults();
        // setup stream
        //this.setupStream();
        //window.addEventListener('beforeunload', this.teardownStream, false);
    },
    mounted() {
        // maintain results
        setInterval(function () {
            this.getResults();
            this.getStatus();
        }.bind(this), 5000); 
    },
});

Vue.component('panel', {
    props: {
        label: String,
    },
    template: `
        <div>
            <label class="collapsible" v-on:click="collapse">{{ label }}</label>
            <div class="content">
                <slot/>
            </div>
        </div>
    `,
    methods: {
        collapse: function(event) {
            event.target.classList.toggle("active");
            var content = event.target.nextElementSibling;
            // toggle display
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        },
    }
});

Vue.component('add-attack', {
    template: `
        <div>
            <form v-on:submit.prevent="addAttack">
                <input type="text" v-model="attackForm.method" placeholder="method"> <span>http method for the attack</span><br>
                <input type="text" v-model="attackForm.url" placeholder="url"> <span>target url for the attack</span><br>
                <input type="text" v-model="attackForm.payloadExp" placeholder="payload expression"> <span>python expression using 'u' and 'p'</span><br>
                <input type="text" v-model="attackForm.contentType" placeholder="content type"> <span>content type header value of the payload</span><br>
                <input type="text" v-model="attackForm.success" placeholder="success match"> <span>string in response indicating success</span><br>
                <input type="text" v-model="attackForm.fail" placeholder="failure match"> <span>string in response indicating failure</span><br>
                <button type="submit">add attack</button>
            </form>
        </div>
    `,
    data: function() {
        return {
            attackForm: {
                method: '',
                url: '',
                payloadExp: '',
                contentType: '',
                success: '',
                fail: '',
            },
        }
    },
    methods: {
        addAttack: function(event) {
            fetch(this.URL_ATTACKS_POST, {
                  method: 'POST',
                  body: JSON.stringify(this.attackForm),
                  headers:{
                    'Content-Type': 'application/json'
                  }
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => {
                // update the attack select (getAttacks)
                this.$emit('click');
                // reset the form
                Object.keys(this.attackForm).forEach((k) => {
                    this.attackForm[k] = '';
                });
            })
        },
    },
});

Vue.component('run-attack', {
    props: {
        attacks: Array,
        files: Array,
    },
    template: `
        <div>
            <select v-model="attack">
                <option value="" disabled>select a target</option>
                <option v-for="attack in attacks" v-bind:value="attack.id">{{ attack.url }}</option>
            </select><br>
            <select v-model="filename">
                <option value="" disabled>select a list</option>
                <option v-for="file in files" v-bind:value="file">{{ file }}</option>
            </select><br>
            <button v-on:click="runAttack">run attack!</button>
        </div>
    `,
    data: function() {
        return {
            attack: '',
            filename: '',
        }
    },
    methods: {
        runAttack: function(event) {
            fetch(this.URL_ATTACK_RUN, {
                  method: 'POST',
                  body: JSON.stringify({id: this.attack, filename: this.filename}),
                  headers:{
                    'Content-Type': 'application/json'
                  }
            })
            .then(handleErrors)
            .then(response => {
                // update the status (getStatus)
                this.$emit('click');
            })
        },
    },
});

Vue.component('view-results', {
    props: {
        results: Array,
    },
    template: `
        <div>
            <table v-for="result in results" v-bind:key="result.id" v-bind:result="result">
                <tbody>
                    <tr><td>time</td><td>{{ result.created }}</td><tr>
                    <tr><td>target</td><td>{{ result.attack.url }}</td></tr>
                    <tr><td>payload</td><td>{{ result.payload }}</td></tr>
                    <tr><td>node</td><td>{{ result.node.fingerprint }}</td></tr>
                </tbody>
            </table>
        </div>
    `,
});
