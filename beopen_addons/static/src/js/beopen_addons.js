odoo.define('beopen_addons', function(require) {
    debugger;
    var Model = require('web.DataModel');
    var core = require('web.core');
    var Dialog = require('web.Dialog');
    var _t = core._t;

    $(function() {
        $("[data-menu='5']").click(function() {
            setTimeout(function(){

                var message = _t("Installing extra modules may affect your hosting cost.");

                var options = {
                    title: _t("Warning"),
                    buttons: [{
                                text: _t("Ok"),
                                close: true,
                             },
                             {
                                text: _t("Check module prices"),
                                close: true,
                                click: function() {
                                        var win = window.open('http://beopen.be/configurator/prices', '_blank');
                                        if (win) {
                                            win.focus();
                                        } else {
                                            alert('Please allow popups for this website');
                                        }
                                    },
                             }],
                };
                Dialog.alert(self, message, options);
            }, 1000);
        })

        var companies = new Model("res.company");

        companies.query()
         .filter([['name', '=', "My Company"]])
         .count().then(function (count) {
            if (count > 0) {
                setTimeout(function(){ $(".oe_logo_edit_admin").click(); }, 1000);

            }
        });
    });
});
