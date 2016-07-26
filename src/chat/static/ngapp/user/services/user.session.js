angular
    .module('chat.user.session', [])
    .factory('UserSession', UserSession);

    UserSession.$inject = ["$window", "$rootScope"];

    function UserSession($window, $rootScope) {
        var storage = $window.sessionStorage;
        return {
            getUser: function () {
                return $rootScope.user
            },
            setUser: function (user) {
                $rootScope.user = user;
            },
            save: function (user) {
                storage.setItem('user', angular.toJson(user));
            },
            load: function(){
                return (storage.user) ? angular.fromJson(storage.user) : {authenticated: false};
            },
            // public:
            init: function () {
                var user = this.load();
                this.setUser(user);
                return this.getUser();
            },
            //setProfile: function (profile) {
            //    var profileData = _.omit(profile, function (val, key) {return key[0] == '$'});
            //    var user = angular.extend(this.getUser(), profileData);
            //    if (user.is_hotel_user){
            //        if(user.hotel.is_admin || user.hotel.is_supervisor){
            //            user.permission = 'hotelAdmin';
            //        }else{
            //            user.permission = 'hotelUser';
            //        }
            //    }else{
            //        user.permission = 'reportUser';
            //    }
            //    this.setUser(user);
            //    this.save(user);
            //},
            //setAddress: function(address){
            //    var user = this.getUser();
            //    user.address = address;
            //    this.setUser(user);
            //    this.save(user);
            //},
            //setHotelProfile: function(hotelProfile){
            //    $rootScope.user.hotel.hotel_name = hotelProfile.name;
            //    this.setUser($rootScope.user);
            //    this.save($rootScope.user)
            //},
            login: function (userdata) {
                var user = angular.extend({authenticated: true}, userdata);
                this.setUser(user);
                this.save(user);
            },
            destroy: function () {
                var user = {authenticated: false};
                this.setUser(user);
                this.save(user);
            }
        }
    }
