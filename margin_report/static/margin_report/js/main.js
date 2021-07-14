function get_val() {
    var control = document.getElementById("ctrl");
    var data1 = new FormData()
    // data1.append('dcn', $('#docn').val())
    // data1.append('dc', $('#doc').val())
    // console.log(control.files[1])
    var arr = control.files
    for (index = 0; index < arr.length; index++) {
        if (arr[index].name == "АМП и АМД.xlsx") {
            data1.append('test', arr[index])
        }
    }


    // data1.append('test', control.files[0])

    var token = '{{ csrf_token }}';
    // alert('csrf generated');

    // $.ajax({
    //     type: 'POST',
    //     url: 'upl/',
    //     data: data1,
    //     processData: false,
    //     contentType: false,
    //     responseType: 'arraybuffer',
    //     headers: {'X-CSRFToken': token},
    //     success: function (data, status, xhr) {
    //
    //         var blob = new Blob([data], {type: 'application/vnd.ms-excel'});
    //         console.log(blob)
    //         var downloadUrl = URL.createObjectURL(blob);
    //         var a = document.createElement("a");
    //         a.href = downloadUrl;
    //         a.download = 'download.xlsx';
    //         document.body.appendChild(a);
    //         a.click();
    //         document.body.removeChild(a);
    //
    //     }
    // })

    let xhr = new XMLHttpRequest();
    xhr.open('POST', 'upl/');
    // xhr.setRequestHeader('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
    xhr.responseType = 'arraybuffer';

    xhr.onload = function (e) {


        if (this.status == 200) {
            let disposition = this.getResponseHeader('Content-Disposition')

            if (disposition && disposition.indexOf('attachment') !== -1) {
                let filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                let matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }

            var blob = new Blob([this.response], { type: 'application/vnd.ms-excel' });
            var downloadUrl = URL.createObjectURL(blob);
            var a = document.createElement("a");
            a.href = downloadUrl;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
        } else {
            Materialize.toast('Invalid data!', 2000);
        }
    }

    xhr.send(data1);
}