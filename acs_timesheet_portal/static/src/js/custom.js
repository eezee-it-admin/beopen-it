odoo.define('acs_project_issue_portal.acs_project_issue_portal', function (require) {
    "use strict";
    
    require('web.dom_ready');

    var ajax = require('web.ajax');

    $('.acs_datetimepicker').datepicker();
    $(".acs_datetimepicker").datepicker("setDate", new Date());

    $('.acs_select_project').each(function () {
        var project = this;

        var clickwatch = (function(){
              var timer = 0;
              return function(callback, ms){
                clearTimeout(timer);
                timer = setTimeout(callback, ms);
              };
        })();

        $(project).on('change', "select[name='project']", function () {
            clickwatch(function() {
                if ($("#project").val()) {
                    var project_id = $("#project").val();
                } else {
                    var project_id = 0;
                }
                    
                ajax.jsonRpc("/acs/tasks/" + project_id, 'call', {}).then(
                    function(data) {
                        // populate tasks and display
                        var selectTasks = $("select[name='task']");
                        // dont reload tasks at first loading (done in qweb)
                        if (selectTasks.data('init')===0 || selectTasks.find('option').length===1) {
                            if (data) {
                                selectTasks.html('');
                                _.each(data, function(x) {
                                    var opt = $('<option>').text(x[1])
                                        .attr('value', x[0]);
                                    selectTasks.append(opt);
                                });
                                selectTasks.parent('div').show();
                            }
                            else {
                                selectTasks.val('').parent('div').hide();
                            }
                            selectTasks.data('init', 0);
                        }
                        else {
                            selectTasks.data('init', 0);
                        }

                    }
                );
                
            }, 500);
        });
        $("select[name='project']").change();
    });

});

