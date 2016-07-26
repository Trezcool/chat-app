angular
    .module('chat.urls', ['chat.settings'])
    .provider('view', view);

    view.$inject = ["STATIC_VIEWS_URL"];

    function view(STATIC_VIEWS_URL) {
        var TEMPLATE_BASE = STATIC_VIEWS_URL;

        this.setTemplateBase = function (templateBase) {
          TEMPLATE_BASE = templateBase;
        };

        this.view = function (template, opts) {
          var defaults = {auth: true, routePermissions: ['public']};
          opts = opts || {};
          var templateBase = opts.template_base || TEMPLATE_BASE;
          return angular.extend(defaults, {templateUrl: templateBase + template}, opts)
        };

        this.$get = function () {
          return {view: view}
        };
    }

