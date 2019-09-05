const routes = [
    {
        path: "/dashboard",
        name: "Dashboard",
        component: Dashboard,
        meta: {
            authRequired: true
        }
    },
    {
        path: "/login",
        name: "Login",
        component: Login,
    },
    {
        path: "*",
        redirect: "/login"
    }
];

const router = new VueRouter({
    routes: routes,
});

router.beforeEach((to, from, next) => {
    if (to.matched.some(record => record.meta.authRequired)) {
        if (localStorage.getItem("user") == null) {
            next({
                name: "Login",
                params: { nextUrl: to.fullPath }
            })
        } else {
            next()
        }
    } else {
        next()
    }
});

// define tha vue app
var app = new Vue({
    el: "#app",
    router,
});
