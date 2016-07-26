'use strict';

angular
    .module('chat.api', ['chat.settings'])
    .factory('API', API);

    API.$inject = ['$resource', 'API_ROOT'];

    function API ($resource, API_ROOT) {
        // API_ROOT: the base URL of the REST API
        var res = function (url_pattern) {
            return API_ROOT + url_pattern
        };
        return {
            Login: $resource(res('login/')),
            Logout: $resource(res('logout/'))
            //UserProfile: $resource(res('user/'), {}, {
            //    partial: {
            //        method: 'PATCH'
            //    }
            //}),
            //HotelFoundItems: $resource(res('hotel-found-items/:id/'), {}, {
            //    query: {method: 'GET'},
            //    partial: {
            //        method: 'PATCH'
            //    }
            //}),
            //KnownOwnerMatch: $resource(res('matched-items/:id/known_owner_feedback/'), {}, {
            //    query: {method: 'GET'},
            //    update: {
            //        method: 'PUT'
            //    }
            //}),
        }
    }
