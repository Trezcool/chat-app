angular
    .module('chat.auth.service', ['chat.user.session', 'chat.api'])
    .factory('AuthService', AuthService);

    AuthService.$inject = ['$q', '$cookies', 'UserSession', 'API'];

    function AuthService($q, $cookies, UserSession, API) {
        return {
            user: UserSession.init(),
            login: function (data) {
                var deferred = $q.defer();
                var date = new Date();
                date.setDate(date.getDate() + 5);
                API.Login.save(data, function (res) {
                    if (data.rememberMe){$cookies.put('__user', res.key, {expires: date.toString()})}
                    UserSession.login({key:res.key});
                    //API.UserProfile.get(function (res) {
                    //    UserSession.setProfile(res);
                    //    deferred.resolve(UserSession.getUser());
                    //});
                    deferred.resolve(UserSession.getUser());
                }, function (res_err) {
                    deferred.reject(res_err)
                });
                return deferred.promise;
            },
            rememberMe: function(){
                if ($cookies.get('__user') && !this.user.authenticated) {
                    UserSession.login({key:$cookies.get('__user')});
                    //API.UserProfile.get(function (res) {
                    //    UserSession.setProfile(res);
                    //})
                }
            },
            autoLogin: function(token){
                UserSession.login({key: token});
                //return API.UserProfile.get(function (res) {
                //    UserSession.setProfile(res);
                //})
            },
            logout: function () {
                API.Logout.save({}, function(res){
                    $cookies.remove('__user');
                    UserSession.destroy();
                })
            }
        };

    }
