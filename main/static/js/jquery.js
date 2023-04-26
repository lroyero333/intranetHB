mobiscroll.setOptions({
    locale: mobiscroll.localeEs,
    theme: 'ios',
    themeVariant: 'light'
});

$(function () {
    $('#demo').mobiscroll().datepicker({
        controls: ['calendar', 'time'],
        display: 'inline'
    });

    $('#demo-timegrid').mobiscroll().datepicker({
        controls: ['calendar', 'timegrid'],
        display: 'inline'
    });
});