odoo.define("ezee_project_portal.eezee_project_portal.js", function(require) {

    var ajax = require('web.ajax');

    $(document).on('click', '.button-slot-details', function(e) {
        e.preventDefault();
        ajax.jsonRpc("/get_planning", 'call', {
            'slot_id': $(this).data('slot_id'),
        }).then(function (modal) {
            $('#eezee-slot-modal').modal("show");
            $('.modal-content').html(modal)
        })
    })

});
