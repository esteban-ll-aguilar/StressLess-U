"use strict";
$(document).ready(function() {
    // Función para mostrar/ocultar el loader
    function toggleLoader(show) {
        if (show) {
            $('<div id="updateLayout" class="loader-bg"><div class="loader-track"><div class="loader-fill"></div></div></div>')
                .appendTo('body')
                .fadeIn(300);
        } else {
            $('#updateLayout').fadeOut(300, function() {
                $(this).remove();
            });
        }
    }

    // Función para aplicar las configuraciones
    function applySettings(settings) {
        console.log('Aplicando configuraciones:', settings);
        toggleLoader(true);
        
        setTimeout(() => {
            // Layout type
            $('.layout-type > a').removeClass('active');
            $(`.layout-type > a[data-value="${settings.type}"]`).addClass('active');
            
            if (settings.type == "menu-dark") {
                $('.pcoded-navbar').removeClassPrefix('menu-');
                $('.pcoded-navbar').removeClass('navbar-dark');
            }
            if (settings.type == "menu-light") {
                $('.pcoded-navbar').removeClassPrefix('menu-');
                $('.pcoded-navbar').removeClass('navbar-dark');
                $('.pcoded-navbar').addClass(settings.type);
            }
            if (settings.type == "dark") {
                $('.pcoded-navbar').removeClassPrefix('menu-');
                $('.pcoded-navbar').addClass('navbar-dark');
                $('.layout-css').attr("href", "/static/assets/css/layout-dark.css");
            } else {
                $('.layout-css').attr("href", "");
            }

            // Header color
            $('.header-color > a').removeClass('active');
            $(`.header-color > a[data-value="${settings.headerColor}"]`).addClass('active');
            $('.pcoded-header').removeClassPrefix('header-');
            $('.pcoded-header').addClass(settings.headerColor);

            // RTL
            $('#theme-rtl').prop('checked', settings.rtlEnabled);
            if (settings.rtlEnabled) {
                $('head').append('<link rel="stylesheet" class="rtl-css" href="/static/assets/css/layout-rtl.css">');
            } else {
                $('.rtl-css').attr("href", "");
            }

            // Menu Fixed
            $('#menu-fixed').prop('checked', settings.menuFixed);
            if (settings.menuFixed) {
                $('.pcoded-navbar').addClass('menupos-fixed');
            } else {
                $('.pcoded-navbar').removeClass('menupos-fixed');
            }

            // Header Fixed
            $('#header-fixed').prop('checked', settings.headerFixed);
            if (settings.headerFixed) {
                $('.pcoded-header').addClass('headerpos-fixed');
            } else {
                $('.pcoded-header').removeClass('headerpos-fixed');
            }

            // Box Layout
            $('#box-layouts').prop('checked', settings.boxLayout);
            if (settings.boxLayout) {
                $('body').addClass('container');
                $('body').addClass('box-layout');
            } else {
                $('body').removeClass('container');
                $('body').removeClass('box-layout');
            }

            // Breadcrumb Sticky
            $('#breadcumb-layouts').prop('checked', settings.breadcrumbSticky);
            if (settings.breadcrumbSticky) {
                $('.page-header').addClass('breadcumb-sticky');
            } else {
                $('.page-header').removeClass('breadcumb-sticky');
            }

            setTimeout(() => {
                toggleLoader(false);
            }, 500);
        }, 500);
    }

    // Función para obtener las configuraciones actuales
    function getCurrentSettings() {
        return {
            type: $('.layout-type > a.active').attr('data-value') || 'menu-light',
            headerColor: $('.header-color > a.active').attr('data-value') || 'header-blue',
            rtlEnabled: $('#theme-rtl').is(':checked'),
            menuFixed: $('#menu-fixed').is(':checked'),
            headerFixed: $('#header-fixed').is(':checked'),
            boxLayout: $('#box-layouts').is(':checked'),
            breadcrumbSticky: $('#breadcumb-layouts').is(':checked')
        };
    }

    // Función para guardar las configuraciones en el backend
    function saveSettings(settings) {
        toggleLoader(true);
        $.ajax({
            url: '/update_layout',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ layout: settings }),
            success: function(response) {
                console.log('Configuraciones guardadas:', response);
                // Aplicar los cambios después de guardar exitosamente
                applySettings(settings);
                location.reload();
            },
            error: function(error) {
                console.error('Error al guardar configuraciones:', error);
                toggleLoader(false);
            }
        });
    }

    // Event Listeners
    $('.layout-type > a').on('click', function() {
        var temp = $(this).attr('data-value');
        $('.layout-type > a').removeClass('active');
        $('.pcoded-navbar').removeClassPrefix('navbar-image-');
        $(this).addClass('active');
        
        if (temp == "reset") {
            location.reload();
            return;
        }
        
        var settings = getCurrentSettings();
        settings.type = temp;
        saveSettings(settings);
    });

    $('.header-color > a').on('click', function() {
        var temp = $(this).attr('data-value');
        var settings = getCurrentSettings();
        settings.headerColor = temp;
        saveSettings(settings);
    });

    $('#theme-rtl').change(function() {
        var settings = getCurrentSettings();
        settings.rtlEnabled = $(this).is(':checked');
        saveSettings(settings);
    });

    $('#menu-fixed').change(function() {
        var settings = getCurrentSettings();
        settings.menuFixed = $(this).is(':checked');
        saveSettings(settings);
    });

    $('#header-fixed').change(function() {
        var settings = getCurrentSettings();
        settings.headerFixed = $(this).is(':checked');
        saveSettings(settings);
    });

    $('#box-layouts').change(function() {
        var settings = getCurrentSettings();
        settings.boxLayout = $(this).is(':checked');
        saveSettings(settings);
    });

    $('#breadcumb-layouts').change(function() {
        var settings = getCurrentSettings();
        settings.breadcrumbSticky = $(this).is(':checked');
        saveSettings(settings);
    });

    // Helper function
    $.fn.removeClassPrefix = function(prefix) {
        this.each(function(i, it) {
            var classes = it.className.split(" ").map(function(item) {
                return item.indexOf(prefix) === 0 ? "" : item;
            });
            it.className = classes.join(" ");
        });
        return this;
    };

    // Cargar configuraciones iniciales
    if (typeof userSettings !== 'undefined') {
        try {
            const settings = JSON.parse(userSettings);
            if (settings.layout) {
                console.log('Cargando configuraciones iniciales:', settings.layout);
                applySettings(settings.layout);
            }
        } catch (e) {
            console.error('Error al parsear configuraciones:', e);
        }
    }
});
