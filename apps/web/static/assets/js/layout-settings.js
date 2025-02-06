"use strict";
$(document).ready(function() {
    // Función para aplicar las configuraciones
    function applySettings(settings) {
        console.log('Aplicando configuraciones globales:', settings);
        
        // Layout type
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
        }

        // Header color
        $('.pcoded-header').removeClassPrefix('header-');
        $('.pcoded-header').addClass(settings.headerColor);

        // RTL
        if (settings.rtlEnabled) {
            $('head').append('<link rel="stylesheet" class="rtl-css" href="/static/assets/css/layout-rtl.css">');
        }

        // Menu Fixed
        if (settings.menuFixed) {
            $('.pcoded-navbar').addClass('menupos-fixed');
        }

        // Header Fixed
        if (settings.headerFixed) {
            $('.pcoded-header').addClass('headerpos-fixed');
        }

        // Box Layout
        if (settings.boxLayout) {
            $('body').addClass('container');
            $('body').addClass('box-layout');
        }

        // Breadcrumb Sticky
        if (settings.breadcrumbSticky) {
            $('.page-header').addClass('breadcumb-sticky');
        }
    }

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
                console.log('Cargando configuraciones globales:', settings.layout);
                applySettings(settings.layout);
            }
        } catch (e) {
            console.error('Error al parsear configuraciones:', e);
        }
    }
});
