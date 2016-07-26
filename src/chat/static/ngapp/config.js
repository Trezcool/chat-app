angular
    .module('chat.config', ['chat.urls', 'chat.auth.interceptor', 'chat.loading.interceptor'])
    .config(config)
    .run(run);

    config.$inject = ['$routeProvider', '$resourceProvider', '$httpProvider', '$locationProvider', 'viewProvider', 'ngIntlTelInputProvider'];

    function config($routeProvider, $resourceProvider, $httpProvider, $locationProvider, viewProvider, ngIntlTelInputProvider) {
        $locationProvider.hashPrefix('!');  // default
        var view = viewProvider.view;

        $routeProvider
            .when('/', view('home/views/home.html', {controller: 'HomeCtrl', controllerAs: 'vm', auth: false}))
            .when('/login', view('user/views/login.html', {controller: 'LoginCtrl', controllerAs: 'vm', auth: false, routePermissions: ['publicNotAuthenticated']}))
            //.when('/report/step-:id', view('report/views/report_wizard.html', {controller: 'ReportRegisterCtrl', controllerAs: 'vm', auth: false}))
            //.when('/report/:slug/:id/step-:step', view('report/views/hotel_report_wizard.html', {controller: 'HotelReportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/my-address/:next?', view('report/views/my_address.html', {controller: 'MyAddressCtrl', controllerAs: 'vm', routePermissions: ['reportUser']}))
            //.when('/about', view('support/views/about.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/support', view('support/views/support.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/faq', view('support/views/faq.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/contact-us', view('support/views/contact.html', {controller: 'ContactCtrl', controllerAs: 'vm', auth: false}))
            //.when('/terms-and-conditions', view('support/views/terms_and_conditions.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/permission-denied-403', view('support/views/403.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/page-not-found-404', view('support/views/404.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.when('/something-went-wrong', view('support/views/500.html', {controller: 'SupportCtrl', controllerAs: 'vm', auth: false}))
            //.otherwise({redirectTo: '/page-not-found-404'});
            .otherwise('/');

        //ngIntlTelInputProvider.set({nationalMode:false, defaultCountry: 'ae'});
        $httpProvider.interceptors.push('LoadingInterceptor'); // loading interceptor to show loading indicator
        $httpProvider.interceptors.push('AuthInterceptor'); // add auth token to all requests
        $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
        $resourceProvider.defaults.stripTrailingSlashes = false;
        $locationProvider.html5Mode(true);
    }

    run.$inject = ['$route', '$rootScope', '$location'];

    function run($route, $rootScope, $location){
        $location.updatePath = function (path, keepPreviousPathInHistory) {
            if ($location.path() === path) return;

            var routeToKeep = $route.current;
            $rootScope.$on('$locationChangeSuccess', function () {
                if (routeToKeep) {
                    $route.current = routeToKeep;
                    routeToKeep = null;
                }
            });

            $location.path(path);
            if (!keepPreviousPathInHistory) $location.replace();
        };
        $rootScope.$on("$routeChangeStart", function (event, next, current) {
            var route = next.$$route || {}, user = $rootScope.user;
            // redirect to login page if auth required
            if (route.auth){
                if (!user.authenticated) {
                    $location.path('/login');
                }
            }
        });
    }
