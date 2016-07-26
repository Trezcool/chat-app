angular
    .module('chat.login', ['chat.auth.service', 'chat.user.session'])
    .controller('LoginCtrl', LoginCtrl);

    LoginCtrl.$inject = ['$location', 'AuthService'];

    function LoginCtrl($location, AuthService){
        var vm = this;
         vm.defaults = {
            //email: '',
            username: '',
            password: '',
            errors: {}
        };

        vm.doLogin = doLogin;

        function doLogin () {
            vm.defaults.errors = {}; // clear any non_field_errors
            //vm.defaults.errors.email = !vm.defaults.email;
            vm.defaults.errors.username = !vm.defaults.username;
            vm.defaults.errors.password = !vm.defaults.password;

            if (!_.any(_.values(vm.defaults.errors))) {
                AuthService.login(vm.defaults).then(
                    function (resp) {
                        //if (resp.is_hotel_user){
                        //    return $location.path('/hotel-dashboard/log-item');
                        //}
                        $location.path('/dashboard/chats');
                    },
                    function (error) {
                        vm.defaults.errors = error.data;
                    }
                );
            }
        }

    }
