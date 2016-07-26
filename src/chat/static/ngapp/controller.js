angular
    .module('chat.controller', ['chat.auth.service'])
    .controller('AppCtrl', AppCtrl);

    AppCtrl.$inject = ['$scope', '$location', 'AuthService', 'AlertFactory'];

    function AppCtrl($scope, $location, AuthService, AlertFactory){
        $scope.closeAlert = AlertFactory.close;

        $scope.doLogout = function () {
            AuthService.logout();
            $location.path('/');
        };

        AuthService.rememberMe();

        $scope.openNav = false;
    }

