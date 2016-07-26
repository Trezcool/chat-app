angular
    .module('chat.auth.interceptor', ['chat.user.session'])
    .factory('AuthInterceptor', AuthInterceptor);

    AuthInterceptor.$inject = ["$q", "$location", "UserSession"];

    function AuthInterceptor($q, $location, UserSession) {
        return {
            request: function (config) {
                config.headers = config.headers || {};
                var user = UserSession.getUser();
                if (user !== undefined && user.key) {
                    config.headers.Authorization = 'Token ' + user.key;
                }
                return config;
            },
            responseError: function (response) {
                if (response.status === 401) {
                    UserSession.destroy();
                    $location.path('/');
                }
                return $q.reject(response);
            }
        };
    }
