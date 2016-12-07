odoo.define('template_configurator.configurate', function(require) {
    var ajax = require('web.ajax');
    (function() {
        window.pricing_init = function(r) {
            function localeString(x, sep, dec, grp, round) {
                var sx = ('' + x).split('.'), s = '', i, j;
                sep || (sep = ' ');
                grp || grp === 0 || (grp = 3);
                i = sx[0].length;
                while (i > grp) {
                    j = i - grp;
                    s = sep + sx[0].slice(j, i) + s;
                    i = j;
                }
                s = sx[0].slice(0, i) + s;
                sx[0] = s;
                if (sx.length == 2) {
                    sx[1] = Number('.' + sx[1]).toFixed(round).split('.')[1];
                }
                return sx.join(dec);
            }
            Number.prototype.toLocaleString = ((1000).toLocaleString('en').length == 5) && Number.prototype.toLocaleString || (function(lang) {
                var s = ' '
                  , c = ',';
                if (!lang || lang.toLowerCase() == 'en') {
                    s = ',';
                    c = '.';
                }
                return localeString(this, s, c, 3, 2);
            }
            )
            function selectedFlavor() {
                var flavor_id = $("[name='flavor']:checked").val();
                if (flavor_id == undefined) {
                    flavor_id = $("[name='flavor']").val();
                }
                return flavor_id;
            }
            var get_depends = function(o) {
                return (o.data('app-depends') || '').split(',').filter(function(n) {
                    return n != ""
                })
            }
            var change_country = function() {
                var sel = $('input[name="force_country"]').val();
                if ($('input[name="force_country"]').val() !== r.current_country && $('input[name="force_country"]').val() !== "") {
                    window.location = _.str.sprintf('/localization?country=%s&redirect=%s', sel.toString(), encodeURIComponent(window.location.pathname + window.location.search + window.location.hash));
                }
            }
            var price_by_changed = function(e) {
                $($(e.target).closest("[data-toggle='tab']").attr('href') + '_by').prop('checked', true).change();
            }
            var colorize_checkbox_app = function(oo) {
                oo = !oo ? $(".openerp_website_pricing_app_checkbox") : $(oo.target);
                oo.each(function(i, o) {
                    var closest = $($(o).closest(".openerp_website_pricing_app"));
                    closest.toggleClass("selected", $(o).prop('checked'));
                });
            }
            var colorize_checkbox_service = function(oo) {
                oo = !oo ? $(".openerp_website_pricing_service_checkbox") : $(oo.target);
                oo.each(function(i, o) {
                    var closest = $($(o).closest(".openerp_website_pricing_service"));
                    closest.toggleClass("selected", $(o).prop('checked'));
                });
            }
            var colorize_amount = function(oo) {
                oo = !oo ? $(".openerp_website_pricing_service_amount") : $(oo.target);
                oo.each(function(i, o) {
                    num_val = parseInt(o.value);
                    if (isNaN(num_val)) {
                        num_val = 0;
                        $(o).val(num_val);
                    }
                    var closest = $($(o).closest(".openerp_website_pricing_service"));
                    closest.toggleClass("selected", num_val != 0);
                });
            }
            var colorize_radio = function(oo) {
                oo = !oo ? $(".openerp_website_pricing_app_radio") : $(oo.target);
                oo.each(function(i, o) {
                    var closest = $($(o).closest(".openerp_website_pricing_app"));
                    closest.toggleClass("selected", $(o).prop('checked'));
                });
            }
            var ensure_constraints = function(e) {
                var checkbox = $(e.target);
                var depends = get_depends(checkbox);
                if (checkbox.prop('checked') && depends.length) {
                    $.each(depends, function(i, j) {
                        $("input[data-app-name=" + j + "]").prop('checked', true).change();
                    });
                } else if (!checkbox.prop('checked')) {
                    var depending = _.filter($("input[data-app-depends]"), function(o) {
                        return _.indexOf(get_depends($(o)), checkbox.data('app-name')) > -1;
                    });
                    $.each(depending, function(i, j) {
                        $(j).prop('checked', false).change();
                    });
                }
            }
            var ensure_amount = function(e) {
                var number = parseInt($(e.target).val());
                var minimum = parseInt($(e.target).data('minimum'));
                if (isNaN(minimum)) {
                    minimum = 0;
                }
                if (isNaN(number) || number < minimum ) {
                    $(e.target).val(minimum);
                }
                update_price();
            }
            var update_price = function() {
                window.location.hash = $(".openerp_website_pricing > form.openerp_website_pricing_form").serialize();
                var p = {
                    "default_modules_num": 0,
                    "default_modules_price_monthly": 0,
                    "optional_modules_num": 0,
                    "optional_modules_price_monthly": 0,
                    "price_monthly": 0,
                };

                var flavor_id = parseInt(selectedFlavor());
                $(".openerp_website_pricing_service_amount").each(function(i, o) {
                    if ((r.services[o.id].flavor == -1 || r.services[o.id].flavor == flavor_id) && o.value > 0) {
                        $("#openerp_website_pricing_optional_tr_" + o.id).prop("hidden", false);
                        $("#openerp_website_pricing_optional_tr_" + o.id).find(".openerp_website_pricing_optional_service_num").text(o.value);

                        total_for_service = parseInt(o.value) * r.services[o.id].price;
                        $("#openerp_website_pricing_optional_tr_" + o.id).find(".openerp_website_pricing_optional_services_price_monthly").text(total_for_service);
                        p.price_monthly += total_for_service;

                    } else {
                        $("#openerp_website_pricing_optional_tr_" + o.id).prop("hidden", true);
                    }

                });
                var has_service_selected = false;
                var one_shot_total = 0
                $(".openerp_website_pricing_service_checkbox").each(function(i,o) {
                    if ((r.services[o.id].flavor == -1 || r.services[o.id].flavor == flavor_id) && o.checked) {
                        $("#openerp_website_pricing_optional_tr_" + o.id).prop("hidden", false);
                        one_shot_total += r.services[o.id].price;
                        has_service_selected = true;
                    } else {
                        $("#openerp_website_pricing_optional_tr_" + o.id).prop("hidden", true);
                    }
                });

                if (has_service_selected) {
                    $(".openerp_website_pricing_table_oneshot").prop("hidden", false);
                    $(".openerp_website_pricing_price_oneshot").text(one_shot_total)
                } else {
                    $(".openerp_website_pricing_table_oneshot").prop("hidden", true);
                }

                p.default_modules_num = $(".openerp_website_pricing_default_modules_num").text().trim();
                p.default_modules_price_monthly = parseFloat($(".openerp_website_pricing_default_modules_price_monthly").text().trim());

                $(".openerp_website_pricing_app_checkbox:checked").each(function(i, o) {
                    p.optional_modules_num++;
                    p.optional_modules_price_monthly += parseFloat(r.apps[$(o).data("app-name")]['price']);
                });

                p.price_monthly += parseFloat(p.default_modules_price_monthly) + parseFloat(p.optional_modules_price_monthly);


                $.each(p, function(k, v) {
                    $(".openerp_website_pricing_" + k).text(v.toLocaleString(r.localeLang[r.currency]));
                })

            };

            var show_hide_modules = function() {
                var flavor_id = selectedFlavor();

                $(".col-md-4").each(function(i, o) {
                    div_flavor_id = $(o).data("flavor");
                    if (div_flavor_id != undefined && div_flavor_id != -1 && div_flavor_id != flavor_id) {
                        $(o).find(".openerp_website_pricing_app_checkbox:checked").prop("checked",false).change();
                        $(o).prop("hidden", true);
                    } else {
                        $(o).prop("hidden", false);
                    }
                });
            };

            $(".openerp_website_pricing").on("change", "input", update_price);
            $(".openerp_website_pricing").on("change", "input[type='checkbox']", function(o) {
                ensure_constraints(o),
                colorize_checkbox_app(o)
                colorize_checkbox_service(o)
            });
            $(".openerp_website_pricing").on("change", "input[type='radio']", function(o) {
                show_hide_modules(),
                colorize_radio()
            });
            $(".openerp_website_pricing").on("change", "input[type='number']", function(o) {
                ensure_amount(o),
                colorize_amount()
            });
            $(".openerp_website_pricing_app").on('click', function(o) {
                if (o.toElement != undefined && o.toElement.type != "checkbox") {
                    $(o.currentTarget).find("input").trigger("click");
                }

            });
            $(".openerp_website_pricing_service").on('click', function(o) {
                if (o.toElement != undefined && o.toElement.type != "checkbox") {
                    $(o.currentTarget).find("input").trigger("click");
                }

            });
            $(".openerp_website_pricing").on('change', '.js_change_country', change_country);
            $('.odoo_pricing_board a[data-toggle="tab"]').on('click', price_by_changed);
            $.each($.deparam(window.location.hash.substring(1)), function(k, v) {
                if (k == 'goto') {
                    $elem = $('#' + v);
                    if ($elem.hasClass('collapse')) {
                        $elem.collapse();
                    }
                    var offset = $elem.offset().top;
                    window.scrollTo(0, offset);
                }
                var $el = $("input[name='" + k + "']");
                var v = decodeURIComponent(v);
                if ($el.attr("type") == "checkbox") {
                    $el.prop("checked", true);
                } else if ($el.attr("type") == "radio") {
                    $el.filter('[value="' + v + '"]').prop("checked", true).change();
                } else {
                    $el.val(v).change();
                }
            })
            $('.odoo_pricing_board a[data-toggle="tab"][href="#' + $("input[name='price_by']:checked").val() + '"]').click();
            $($(".openerp_website_pricing input[type='checkbox']")[0]).change();
            colorize_checkbox_app();
            colorize_checkbox_service();
            colorize_amount();
            colorize_radio();
            show_hide_modules();
            $.each($('.amount_to_localize'), function(i, j) {
                $(j).text(parseInt($(j).text()).toLocaleString(r.localeLang[r.currency]));
            });
            $('[data-toggle="tooltip"]').tooltip();

            function validateEmail(email) {
                var re = /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
                return re.test(email);
            }

            $("[name='email']").on("keyup", function(e) {
                var email = $(this).val();
                if (!validateEmail(email)) {
                   $("#email_warning").remove();
                   $("[name='email']").after('<div class="alert alert-danger alert-dismissable" role="alert" id="email_warning">Invalid email address</div>');
                } else {
                   $("#email_warning").remove();
                }
            });

            $("[name='domain']").on("keyup", function(e) {
                var domain = $(this).val();
                ajax.jsonRpc('/configurator/checkdbname', 'call', {
                    'domain': domain
                }).then(function(result) {
                    if (result.type == "error") {
                        $("#domain_warning").remove();
                        $("[name='domain']").after('<div class="alert alert-danger alert-dismissable" role="alert" id="domain_warning">'+ result.message + '</div>');
                    } else {
                        $("#domain_warning").remove();
                    }
                })
            });

            $( "#dialog" ).dialog({
              modal: true,
              autoOpen: false,
              buttons: {
                Ok: function() {
                  $( this ).dialog( "close" );
                }
              }
            });

            var create_instance = function(e) {
                e.preventDefault();

                if ($("#email_warning").length == 0 && $("#domain_warning").length == 0 &&
                    $("[name='domain']").val() != "" && $("[name='email']").val() != "") {
                    var flavor_id = selectedFlavor();

                    var apps = [];
                    $(".openerp_website_pricing_app_checkbox:checked").each(function(i, o) {
                        apps.push($(o).data('app-name'))
                    });

                    debugger;
                    var services = []
                    $(".openerp_website_pricing_service_amount").each(function(i, o) {
                        if ((r.services[o.id].flavor == -1 || r.services[o.id].flavor == flavor_id) && parseInt(o.value) > 0) {
                            services.push(r.services[o.id].name + "(" + o.value + ") " );
                        }

                    });
                    $(".openerp_website_pricing_service_checkbox").each(function(i,o) {
                        if ((r.services[o.id].flavor == -1 || r.services[o.id].flavor == flavor_id) && o.checked) {
                            services.push(r.services[o.id].name);
                        }
                    });

                    var market_type = $("[name='market_type']").val();
                    var domain = $("[name='domain']").val();
                    var email = $("[name='email']").val();
                    var price = $(".openerp_website_pricing_price_monthly").text();

                    $.blockUI({ message: '<h3><span id="progress">One moment please ...</span></h3><img id="spinner" src="/template_configurator/static/src/img/ajax-loader.gif"/>' });

                    var tid = setInterval(progress, 5000);

                    function abortTimer() {
                      clearInterval(tid);
                    }

                    function progress() {
                        ajax.jsonRpc('/configurator/progress', 'call', {'domain': domain}).then(function(result) {
                            $("#progress").text(result.message);

                                if (result.message == "Done") {
                                    $.unblockUI();
                                    abortTimer();
                                    $("[name='domain']").val("");
                                    $("[name='email']").val("");
                                    $("#dialog-message").html("Your BeOpen exprience is ready at <a target='_blank' href='http://" +
                                        domain +".beopen.be'>http://" +
                                        domain + ".beopen.be.</a> <br/>You can login with your credentials that have been send to " + email);
                                    $("#dialog" ).dialog( "open" );
                                    $(".ui-dialog-titlebar").hide();
                                }
                                if (result.message.startsWith("ERROR")) {
                                    $.unblockUI();
                                    abortTimer();
                                    $("[name='domain']").val("");
                                    $("[name='email']").val("");
                                    $("#dialog-message").html("Oops..., an unexpected error occured.<br/>Please <a href='https://beopen.be/page/contactus'>" +
                                        "contact us</a> to set up your environment manually.");
                                    $("#dialog" ).dialog( "open" );
                                    $(".ui-dialog-titlebar").hide();
                                }
                            })
                    }

                    ajax.jsonRpc('/configurator/createinstance', 'call', {
                        'domain': domain, 'email': email, 'market_type':market_type, 'apps': apps, 'services': services, 'price': price, 'flavor_id': flavor_id
                    }).then(function(result) {
                        if (result.type == "ok") {
                        }
                    })
                }
            };

            $(".openerp_website_button_create_instance").on('click', create_instance);

        };

    })();

});
