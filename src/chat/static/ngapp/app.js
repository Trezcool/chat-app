(function() {
    'use strict';

    angular
        .module('chat', [
            // angular modules
            'ngResource',
            'ngRoute',
            'ngAnimate',
            'ngCookies',
            'ngFileUpload',
            'ui.bootstrap',
            'ui.bootstrap.showErrors',
            'ngIntlTelInput',

            // chat modules:
            'chat.config',
            'chat.controller',
            'chat.login',
            'chat.home',
            'chat.settings',
            'chat.alert',

            // directives
            'enterSubmit.directive'
        ]);
})();
