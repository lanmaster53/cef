/*
https://paweljw.github.io/2017/09/vue.js-front-end-app-part-3-authentication/
https://gist.github.com/brianboyko/91fdfb492071e743e389d84eee002342
https://designhammer.com/blog/reusable-vuejs-components-part-2-basic-drop-down-and-v-model
*/

var Login = Vue.component('login', {
    template: `
        <div class="four columns offset-by-four">
            <label>log in</label>
            <div>
                <form v-on:submit.prevent="handleSubmit">
                    <input type="text" class="u-full-width" v-model="loginForm.username" placeholder="username" required autofocus><br>
                    <input type="password" class="u-full-width" v-model="loginForm.password" placeholder="password" required><br>
                    <button type="submit">log in</button>
                    <p v-if="error" class="error">{{ error }}</p>
                </form>
            </div>
        </div>
    `,
    data: function() {
        return {
            loginForm: {
                username: '',
                password: '',
            },
            error: false,
        }
    },
    methods: {
        handleSubmit: function() {
            fetch(this.URL_AUTH, {
                  method: 'POST',
                  body: JSON.stringify(this.loginForm),
                  headers:{
                    'Content-Type': 'application/json'
                  }
            })
            .then(handleErrors)
            .then(response => response.json())
            .then(json => this.logIn(json))
            .catch(() => this.loginFailed())
        },
        logIn: function(json) {
            if (!json.user) {
                this.loginFailed();
                return;
            }
            localStorage.setItem("user", JSON.stringify(json.user));
            this.error = false;
            if (this.$route.params.nextUrl != null){
                // originally requested location
                this.$router.push(this.$route.params.nextUrl);
            } else {
                // fallback landing page
                this.$router.push('dashboard');
            }
        },
        loginFailed: function() {
            this.error = 'incorrect username or password';
            localStorage.clear();
        },
    },
});
