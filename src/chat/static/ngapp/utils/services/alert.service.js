angular
    .module('chat.alert', [])
    .factory('AlertFactory', AlertFactory);

    AlertFactory.$inject = ['$rootScope'];

    function AlertFactory($rootScope) {
        $rootScope.alerts = [];
        return {
            add: add,
            close: close
        };

        function add(type, msg, icon) {
            $rootScope.alerts.push({type: type, msg: msg, icon: icon || 'info'});
        }

        function close(index) {
            $rootScope.alerts.splice(index, 1);
        }
    }
