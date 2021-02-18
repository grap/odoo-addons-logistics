odoo.define('web_export_view', function (require) {
    "use strict";
    var Sidebar = require('web.Sidebar');
    Sidebar.include({

        _redraw: function () {
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.export_kanban_pdf').on(
                'click',
                self.action_to_call_gocardless.bind(self),
            );
        },

        action_to_call_gocardless: function (event) {
            event.preventDefault();
            var self = this;
            self.do_action(
                'joint_buying_purchase.action_report_order_suppliers'
            );
        },

    });
});
