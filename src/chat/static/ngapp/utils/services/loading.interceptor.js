angular
    .module('chat.loading.interceptor', [])
    .factory('LoadingInterceptor', LoadingInterceptor);

    LoadingInterceptor.$inject = ["$q", "$rootScope", "$location"];

    function LoadingInterceptor ($q, $rootScope, $location) {
        var xhrCreations = 0;
        var xhrResolutions = 0;

        function exclude(config) {
            return !(config.url.indexOf("contact-list") > -1);
        }

        function handleErrorStatus(status){
            if (status === 404){
                $location.path('/page-not-found-404');
            }else if(status === 403){
                $location.path('/permission-denied-403');
            }else if(status === 500){
                $location.path('/something-went-wrong');
            }
        }

        function isLoading() {
            return xhrResolutions < xhrCreations;
        }

        function updateStatus() {
            $rootScope.loading = isLoading();
        }
        return {
            request: function (config) {
                if (exclude(config)){
                    xhrCreations++;
                    updateStatus();
                }
                return config || $q.when(config)
            },
            requestError: function (rejection) {
                if (exclude(rejection.config)){
                    xhrResolutions++;
                    updateStatus();
                }
                return $q.reject(rejection);
            },
            response: function (response) {
                if (exclude(response.config)) {
                    xhrResolutions++;
                    updateStatus();
                }
                return response;
            },
            responseError: function (error) {
                if (exclude(error.config)){
                    xhrResolutions++;
                    updateStatus();
                }
                handleErrorStatus(error.status);
                return $q.reject(error)
            }
        };
    }
