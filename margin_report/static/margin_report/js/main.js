function get_val() {
    var control = document.getElementById("ctrl");
    var data1 = new FormData()
    // data1.append('dcn', $('#docn').val())
    // data1.append('dc', $('#doc').val())
    data1.append('test', control.files[0])

    var token = '{{ csrf_token }}';
    alert('csrf generated');

    $.ajax({
        type: 'POST',
        url: 'upl/',
        data: data1,
        processData: false,
        contentType: false,
        headers: {'X-CSRFToken': token},
        success: function (data) {
            alert(data)
        }
    })
}